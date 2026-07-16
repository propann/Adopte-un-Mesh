#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import re
import secrets
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def run(command: list[str], *, capture: bool = True) -> str:
    print("+", " ".join(command))
    proc = subprocess.run(command, text=True, capture_output=capture)
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"Commande echouee ({proc.returncode})")
    return (proc.stdout or "") + (proc.stderr or "")


def detect_port(explicit: str | None) -> str:
    if explicit:
        return explicit
    candidates = sorted(Path("/dev").glob("ttyACM*")) + sorted(Path("/dev").glob("ttyUSB*"))
    if not candidates:
        raise SystemExit("Aucune radio USB detectee dans /dev/ttyACM* ou /dev/ttyUSB*")
    if len(candidates) > 1:
        print("Plusieurs ports detectes:")
        for idx, port in enumerate(candidates, 1):
            print(f"  {idx}. {port}")
        choice = int(input("Choix: ")) - 1
        return str(candidates[choice])
    return str(candidates[0])


def detect_node_id(port: str) -> str:
    output = run(["meshtastic", "--port", port, "--info"])
    matches = re.findall(r"![0-9a-fA-F]{8}", output)
    if not matches:
        raise SystemExit("Impossible de lire l'ID radio dans la sortie meshtastic --info")
    return matches[0].lower()


def validate_psk(psk: str) -> None:
    try:
        decoded = base64.b64decode(psk, validate=True)
    except Exception as exc:
        raise SystemExit(f"ADOPT_CHANNEL_PSK invalide: {exc}") from exc
    if len(decoded) not in {16, 32}:
        raise SystemExit("ADOPT_CHANNEL_PSK doit decoder vers 16 ou 32 octets")


def configure_radio(port: str, env: dict[str, str], long_name: str, short_name: str, role: str) -> None:
    region = env.get("MESHTASTIC_REGION", "EU_868")
    preset = env.get("MESHTASTIC_MODEM_PRESET", "LONG_FAST")
    hop = env.get("MESHTASTIC_HOP_LIMIT", "3")
    channel = env.get("MESHTASTIC_SECONDARY_CHANNEL", "ADOPT")
    precision = env.get("MESHTASTIC_POSITION_PRECISION", "0")
    psk = env.get("ADOPT_CHANNEL_PSK", "")
    if not psk:
        raise SystemExit("ADOPT_CHANNEL_PSK absent. Lance ./scripts/create_adopt_channel_key.sh")
    validate_psk(psk)

    commands = [
        ["meshtastic", "--port", port, "--set", "lora.region", region, "--set", "lora.modem_preset", preset, "--set", "lora.hop_limit", hop],
        ["meshtastic", "--port", port, "--set-owner", long_name],
        ["meshtastic", "--port", port, "--set-owner-short", short_name],
        ["meshtastic", "--port", port, "--set", "device.role", role],
        ["meshtastic", "--port", port, "--ch-set", "name", channel, "--ch-set", "psk", psk, "--ch-index", "1"],
        ["meshtastic", "--port", port, "--ch-set", "module_settings.position_precision", precision, "--ch-index", "1"],
        ["meshtastic", "--port", port, "--ch-set", "uplink_enabled", "false", "--ch-index", "1"],
        ["meshtastic", "--port", port, "--ch-set", "downlink_enabled", "false", "--ch-index", "1"],
        ["meshtastic", "--port", port, "--set", "mqtt.enabled", "false"],
    ]
    for command in commands:
        run(command, capture=False)


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            public_id TEXT UNIQUE NOT NULL,
            node_id TEXT,
            display_name TEXT NOT NULL,
            age INTEGER,
            genre_recherche TEXT NOT NULL DEFAULT '',
            bio TEXT NOT NULL DEFAULT '',
            intent TEXT NOT NULL DEFAULT 'ami',
            tags TEXT NOT NULL DEFAULT '',
            zone TEXT NOT NULL DEFAULT 'local',
            avatar_seed TEXT NOT NULL,
            avatar_heart TEXT NOT NULL DEFAULT '<3',
            created_at INTEGER NOT NULL,
            last_seen INTEGER NOT NULL,
            active_until INTEGER NOT NULL,
            rssi INTEGER,
            snr REAL,
            contact_hint TEXT,
            blocked INTEGER NOT NULL DEFAULT 0
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_node_unique
        ON profiles(node_id)
        WHERE node_id IS NOT NULL AND node_id <> '';
        """
    )
    columns = {row[1] for row in conn.execute("PRAGMA table_info(profiles)")}
    if "profile_token_hash" not in columns:
        conn.execute("ALTER TABLE profiles ADD COLUMN profile_token_hash TEXT")
    if "provisioned_at" not in columns:
        conn.execute("ALTER TABLE profiles ADD COLUMN provisioned_at INTEGER")


def token_hash(token: str, pepper: str) -> str:
    return hashlib.sha256((pepper + token).encode("utf-8")).hexdigest()


def upsert_profile(db_path: Path, env: dict[str, str], node_id: str, args: argparse.Namespace) -> tuple[str, str]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    ensure_schema(conn)

    existing = conn.execute("SELECT * FROM profiles WHERE node_id = ?", (node_id,)).fetchone()
    public_id = existing["public_id"] if existing else secrets.token_hex(2).upper()
    profile_id = existing["id"] if existing else f"radio-{node_id.removeprefix('!')}"
    token = secrets.token_urlsafe(24)
    pepper = env.get("PROFILE_TOKEN_PEPPER") or env.get("ADMIN_TOKEN")
    if not pepper:
        raise SystemExit("PROFILE_TOKEN_PEPPER ou ADMIN_TOKEN doit etre defini dans .env")
    created = int(time.time())
    ttl = int(env.get("ADOPT_PROFILE_TTL_SECONDS", "86400"))
    avatar_seed = hashlib.sha256(node_id.encode("utf-8")).hexdigest()[:16]
    tags = ",".join([x.strip()[:24] for x in args.tags.split(",") if x.strip()][:8])

    conn.execute(
        """
        INSERT INTO profiles (
            id, public_id, node_id, display_name, age, genre_recherche, bio, intent, tags, zone,
            avatar_seed, avatar_heart, created_at, last_seen, active_until, contact_hint, blocked,
            profile_token_hash, provisioned_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        ON CONFLICT(node_id) DO UPDATE SET
            display_name=excluded.display_name,
            age=excluded.age,
            genre_recherche=excluded.genre_recherche,
            bio=excluded.bio,
            intent=excluded.intent,
            tags=excluded.tags,
            zone=excluded.zone,
            avatar_heart=excluded.avatar_heart,
            last_seen=excluded.last_seen,
            active_until=excluded.active_until,
            contact_hint=excluded.contact_hint,
            profile_token_hash=excluded.profile_token_hash,
            provisioned_at=excluded.provisioned_at,
            blocked=0
        """,
        (
            profile_id,
            public_id,
            node_id,
            args.pseudo,
            args.age,
            args.recherche,
            args.bio,
            args.intent,
            tags,
            args.zone,
            avatar_seed,
            args.heart,
            created,
            created,
            created + ttl,
            node_id,
            token_hash(token, pepper),
            created,
        ),
    )
    conn.commit()
    conn.close()
    return public_id, token


def prompt_missing(args: argparse.Namespace) -> None:
    args.pseudo = args.pseudo or input("Pseudo public: ").strip()
    args.age = args.age or int(input("Age (18+): "))
    args.recherche = args.recherche or input("Genre / recherche: ").strip()
    args.intent = args.intent or input("Intention [ami/date/photo/balade/event]: ").strip() or "ami"
    args.tags = args.tags or input("Tags separes par virgules: ").strip()
    args.bio = args.bio or input("Bio courte: ").strip()
    args.zone = args.zone or input("Zone floutee [local]: ").strip() or "local"
    args.heart = args.heart or input("Signature [♡]: ").strip() or "♡"


def main() -> None:
    parser = argparse.ArgumentParser(description="Station USB de provisioning Adopte un Mesh")
    parser.add_argument("--env", default=str(ROOT / ".env"))
    parser.add_argument("--port")
    parser.add_argument("--db")
    parser.add_argument("--pseudo")
    parser.add_argument("--age", type=int)
    parser.add_argument("--recherche")
    parser.add_argument("--intent")
    parser.add_argument("--tags")
    parser.add_argument("--bio")
    parser.add_argument("--zone")
    parser.add_argument("--heart")
    parser.add_argument("--role", default="CLIENT", choices=["CLIENT", "CLIENT_MUTE", "CLIENT_BASE"])
    parser.add_argument("--short-name")
    parser.add_argument("--skip-radio-config", action="store_true")
    args = parser.parse_args()

    env_path = Path(args.env)
    env = load_env(env_path)
    if not env:
        raise SystemExit(f"Configuration absente: {env_path}")

    port = detect_port(args.port)
    node_id = detect_node_id(port)
    print(f"[OK] Radio detectee: {node_id} sur {port}")

    prompt_missing(args)
    if args.age < 18:
        raise SystemExit("Service reserve aux majeurs")

    short_name = args.short_name or re.sub(r"[^A-Za-z0-9]", "", args.pseudo)[:4].upper() or node_id[-4:].upper()
    if not args.skip_radio_config:
        configure_radio(port, env, args.pseudo[:39], short_name, args.role)

    db_path = Path(args.db or env.get("HOST_DATABASE_PATH", "/srv/adopte-un-mesh/data/adoptmesh.sqlite3"))
    public_id, token = upsert_profile(db_path, env, node_id, args)

    print("\n=== ENROLEMENT TERMINE ===")
    print(f"Radio ID       : {node_id}")
    print(f"Profil public  : {public_id}")
    print(f"URL locale     : {env.get('APP_PUBLIC_BASE_URL', 'http://adopteunmesh.local')}")
    print(f"Token de gestion (affiche une seule fois): {token}")
    print("Conserve ce token hors de Git. Il permettra plus tard de modifier/supprimer le profil.")
    print("\nQR natif des canaux:")
    run(["meshtastic", "--port", port, "--qr-all"], capture=False)
    print("\n[OK] Meme radio rebranchee = meme profil mis a jour. Pas de clone zombie.")


if __name__ == "__main__":
    main()
