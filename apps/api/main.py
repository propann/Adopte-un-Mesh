from __future__ import annotations

import io
import os
import re
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import qrcode
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("DATABASE_PATH", "/data/adoptmesh.sqlite3"))
DEFAULT_ZONE = os.getenv("ADOPT_DEFAULT_ZONE", "lyon-nord")
PROFILE_TTL_SECONDS = int(os.getenv("ADOPT_PROFILE_TTL_SECONDS", "86400"))
ACTIVE_WINDOW_SECONDS = int(os.getenv("ADOPT_ACTIVE_WINDOW_SECONDS", "1800"))
PUBLIC_BASE_URL = os.getenv("APP_PUBLIC_BASE_URL", "http://adopteunmesh.local")
AP_SSID = os.getenv("ADOPTE_AP_SSID", "Adopte Un Mesh")
AP_PASSWORD = os.getenv("ADOPTE_AP_PASSWORD", "")
LOCAL_DOMAIN = os.getenv("ADOPTE_LOCAL_DOMAIN", "adopteunmesh.local")
REGION = os.getenv("MESHTASTIC_REGION", "EU_868")
MODEM_PRESET = os.getenv("MESHTASTIC_MODEM_PRESET", "LONG_FAST")
HOP_LIMIT = int(os.getenv("MESHTASTIC_HOP_LIMIT", "3"))
PRIMARY_CHANNEL = os.getenv("MESHTASTIC_PRIMARY_CHANNEL", "LongFast")
SECONDARY_CHANNEL = os.getenv("MESHTASTIC_SECONDARY_CHANNEL", "ADOPT")
POSITION_PRECISION = int(os.getenv("MESHTASTIC_POSITION_PRECISION", "0"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

app = FastAPI(title="Adopte un Mesh API", version="0.3.0")

origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def now() -> int:
    return int(time.time())


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def init_db() -> None:
    with db() as conn:
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
            CREATE TABLE IF NOT EXISTS likes (
                from_public_id TEXT NOT NULL,
                to_public_id TEXT NOT NULL,
                mode TEXT NOT NULL DEFAULT 'soft',
                created_at INTEGER NOT NULL,
                UNIQUE(from_public_id, to_public_id)
            );
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                a_public_id TEXT NOT NULL,
                b_public_id TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                UNIQUE(a_public_id, b_public_id)
            );
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                from_public_id TEXT NOT NULL,
                target_public_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'open'
            );
            CREATE TABLE IF NOT EXISTS blocks (
                blocker_public_id TEXT NOT NULL,
                target_public_id TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                UNIQUE(blocker_public_id, target_public_id)
            );
            CREATE TABLE IF NOT EXISTS mesh_events (
                id TEXT PRIMARY KEY,
                direction TEXT NOT NULL,
                payload TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'unknown',
                node_id TEXT,
                rssi INTEGER,
                snr REAL,
                created_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_profiles_last_seen ON profiles(last_seen DESC);
            CREATE INDEX IF NOT EXISTS idx_profiles_active_until ON profiles(active_until DESC);
            CREATE INDEX IF NOT EXISTS idx_mesh_events_created ON mesh_events(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at DESC);
            """
        )
        # Tiny migration helper for early field tests. The bunker accepts its old skeletons.
        ensure_column(conn, "profiles", "node_id", "TEXT")
        ensure_column(conn, "profiles", "age", "INTEGER")
        ensure_column(conn, "profiles", "genre_recherche", "TEXT NOT NULL DEFAULT ''")
        ensure_column(conn, "profiles", "last_seen", "INTEGER NOT NULL DEFAULT 0")
        ensure_column(conn, "profiles", "rssi", "INTEGER")
        ensure_column(conn, "profiles", "snr", "REAL")
        ensure_column(conn, "profiles", "contact_hint", "TEXT")
        ensure_column(conn, "mesh_events", "source", "TEXT NOT NULL DEFAULT 'unknown'")
        ensure_column(conn, "mesh_events", "node_id", "TEXT")
        ensure_column(conn, "mesh_events", "rssi", "INTEGER")
        ensure_column(conn, "mesh_events", "snr", "REAL")


@app.on_event("startup")
def startup() -> None:
    init_db()


class ProfileIn(BaseModel):
    display_name: str = Field(min_length=2, max_length=32)
    bio: str = Field(default="", max_length=160)
    intent: str = Field(default="ami", max_length=32)
    tags: list[str] = Field(default_factory=list)
    zone: str = Field(default=DEFAULT_ZONE, max_length=32)
    age: Optional[int] = Field(default=None, ge=18, le=120)
    genre_recherche: str = Field(default="", max_length=24)
    avatar_seed: Optional[str] = Field(default=None, max_length=24)
    avatar_heart: str = Field(default="♡", max_length=4)


class LikeIn(BaseModel):
    from_public_id: str = Field(min_length=3, max_length=16)
    mode: str = Field(default="soft", max_length=16)


class ReportIn(BaseModel):
    from_public_id: str = Field(min_length=3, max_length=16)
    reason: str = Field(min_length=3, max_length=80)


class BlockIn(BaseModel):
    from_public_id: str = Field(min_length=3, max_length=16)


class MeshInbound(BaseModel):
    payload: str = Field(min_length=2, max_length=220)
    source: str = Field(default="radio", max_length=32)
    node_id: Optional[str] = Field(default=None, max_length=32)
    rssi: Optional[int] = None
    snr: Optional[float] = None


def require_admin(x_admin_token: Optional[str] = Header(default=None)) -> None:
    if ADMIN_TOKEN and x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="admin token missing; zombie denied")


def make_public_id() -> str:
    return secrets.token_hex(2).upper()


def short_hash(value: str) -> str:
    return secrets.token_hex(4) if not value else f"{abs(hash(value)) & 0xFFFFFFFF:08X}"


def clean_field(value: str | None, max_len: int) -> str:
    value = (value or "").strip().replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\s+", " ", value)
    return value[:max_len]


def freshness(last_seen: int) -> str:
    age = now() - last_seen
    if age <= 600:
        return "green"
    if age <= ACTIVE_WINDOW_SECONDS:
        return "orange"
    return "gray"


def row_to_profile(row: sqlite3.Row) -> dict:
    last_seen = int(row["last_seen"] or row["created_at"])
    return {
        "id": row["id"],
        "public_id": row["public_id"],
        "node_id": row["node_id"],
        "display_name": row["display_name"],
        "age": row["age"],
        "genre_recherche": row["genre_recherche"],
        "bio": row["bio"],
        "intent": row["intent"],
        "tags": [x for x in row["tags"].split(",") if x],
        "zone": row["zone"],
        "avatar_seed": row["avatar_seed"],
        "avatar_heart": row["avatar_heart"],
        "active_until": row["active_until"],
        "last_seen": last_seen,
        "seconds_since_seen": max(0, now() - last_seen),
        "rssi": row["rssi"],
        "snr": row["snr"],
        "contact_hint": row["contact_hint"],
        "freshness": freshness(last_seen),
    }


@app.get("/health")
@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "adopte-un-mesh", "version": "0.3.0", "zombie_density": "manageable"}


@app.get("/api/stats")
def stats() -> dict:
    cutoff = now() - ACTIVE_WINDOW_SECONDS
    with db() as conn:
        total_profiles = conn.execute("SELECT COUNT(*) AS c FROM profiles WHERE blocked = 0").fetchone()["c"]
        active_profiles = conn.execute(
            "SELECT COUNT(*) AS c FROM profiles WHERE blocked = 0 AND active_until > ? AND COALESCE(last_seen, created_at) >= ?",
            (now(), cutoff),
        ).fetchone()["c"]
        reports_open = conn.execute("SELECT COUNT(*) AS c FROM reports WHERE status = 'open'").fetchone()["c"]
        matches = conn.execute("SELECT COUNT(*) AS c FROM matches").fetchone()["c"]
        events_24h = conn.execute("SELECT COUNT(*) AS c FROM mesh_events WHERE created_at >= ?", (now() - 86400,)).fetchone()["c"]
    return {
        "profiles_total": total_profiles,
        "profiles_active": active_profiles,
        "reports_open": reports_open,
        "matches": matches,
        "mesh_events_24h": events_24h,
        "active_window_seconds": ACTIVE_WINDOW_SECONDS,
    }


@app.post("/profiles")
@app.post("/api/profiles")
def create_profile(profile: ProfileIn) -> dict:
    public_id = make_public_id()
    profile_id = secrets.token_urlsafe(12)
    avatar_seed = profile.avatar_seed or secrets.token_hex(4)
    created = now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO profiles (
                id, public_id, display_name, bio, intent, tags, zone, avatar_seed, avatar_heart,
                age, genre_recherche, created_at, last_seen, active_until, contact_hint
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id,
                public_id,
                clean_field(profile.display_name, 32),
                clean_field(profile.bio, 160),
                clean_field(profile.intent, 32),
                ",".join([clean_field(x, 24) for x in profile.tags[:8]]),
                clean_field(profile.zone, 32),
                clean_field(avatar_seed, 24),
                clean_field(profile.avatar_heart, 4),
                profile.age,
                clean_field(profile.genre_recherche, 24),
                created,
                created,
                created + PROFILE_TTL_SECONDS,
                public_id,
            ),
        )
    return {"public_id": public_id, "id": profile_id, "avatar_seed": avatar_seed}


@app.get("/profiles")
@app.get("/api/profiles")
def list_profiles() -> dict:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM profiles WHERE blocked = 0 ORDER BY last_seen DESC, created_at DESC LIMIT 100"
        ).fetchall()
    return {"profiles": [row_to_profile(row) for row in rows]}


@app.get("/profiles/active")
@app.get("/api/active")
def active_profiles() -> dict:
    cutoff = now() - ACTIVE_WINDOW_SECONDS
    with db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM profiles
            WHERE active_until > ? AND blocked = 0 AND COALESCE(last_seen, created_at) >= ?
            ORDER BY last_seen DESC, created_at DESC
            LIMIT 50
            """,
            (now(), cutoff),
        ).fetchall()
    return {"profiles": [row_to_profile(row) for row in rows]}


@app.post("/profiles/{target_public_id}/like")
@app.post("/api/profiles/{target_public_id}/like")
def like_profile(target_public_id: str, like: LikeIn) -> dict:
    if target_public_id == like.from_public_id:
        raise HTTPException(status_code=400, detail="self-like refused; even zombies need boundaries")
    created = now()
    with db() as conn:
        target = conn.execute("SELECT public_id FROM profiles WHERE public_id = ? AND blocked = 0", (target_public_id,)).fetchone()
        source = conn.execute("SELECT public_id FROM profiles WHERE public_id = ? AND blocked = 0", (like.from_public_id,)).fetchone()
        if not target or not source:
            raise HTTPException(status_code=404, detail="profile not found")
        conn.execute(
            "INSERT OR IGNORE INTO likes (from_public_id, to_public_id, mode, created_at) VALUES (?, ?, ?, ?)",
            (like.from_public_id, target_public_id, clean_field(like.mode, 16), created),
        )
        reverse = conn.execute(
            "SELECT 1 FROM likes WHERE from_public_id = ? AND to_public_id = ?",
            (target_public_id, like.from_public_id),
        ).fetchone()
        if reverse:
            a, b = sorted([like.from_public_id, target_public_id])
            match_id = secrets.token_hex(4).upper()
            conn.execute(
                "INSERT OR IGNORE INTO matches (id, a_public_id, b_public_id, created_at) VALUES (?, ?, ?, ?)",
                (match_id, a, b, created),
            )
            return {"liked": True, "match": True, "match_id": match_id}
    return {"liked": True, "match": False}


@app.get("/matches")
@app.get("/api/matches")
def list_matches() -> dict:
    with db() as conn:
        rows = conn.execute("SELECT * FROM matches ORDER BY created_at DESC LIMIT 50").fetchall()
    return {"matches": [dict(row) for row in rows]}


@app.post("/profiles/{target_public_id}/report")
@app.post("/api/profiles/{target_public_id}/report")
def report_profile(target_public_id: str, report: ReportIn) -> dict:
    report_id = secrets.token_hex(6)
    with db() as conn:
        conn.execute(
            "INSERT INTO reports (id, from_public_id, target_public_id, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (report_id, clean_field(report.from_public_id, 16), target_public_id, clean_field(report.reason, 80), now()),
        )
    return {"reported": True, "report_id": report_id}


@app.post("/profiles/{target_public_id}/block")
@app.post("/api/profiles/{target_public_id}/block")
def block_profile(target_public_id: str, block: Optional[BlockIn] = None) -> dict:
    with db() as conn:
        conn.execute("UPDATE profiles SET blocked = 1 WHERE public_id = ?", (target_public_id,))
        if block:
            conn.execute(
                "INSERT OR IGNORE INTO blocks (blocker_public_id, target_public_id, created_at) VALUES (?, ?, ?)",
                (clean_field(block.from_public_id, 16), target_public_id, now()),
            )
    return {"blocked": True}


@app.get("/api/admin/reports")
def admin_reports(x_admin_token: Optional[str] = Header(default=None)) -> dict:
    require_admin(x_admin_token)
    with db() as conn:
        rows = conn.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT 50").fetchall()
    return {"reports": [dict(row) for row in rows]}


@app.get("/api/admin/events")
def admin_events(x_admin_token: Optional[str] = Header(default=None)) -> dict:
    require_admin(x_admin_token)
    with db() as conn:
        rows = conn.execute("SELECT * FROM mesh_events ORDER BY created_at DESC LIMIT 50").fetchall()
    return {"events": [dict(row) for row in rows]}


@app.post("/mesh/inbound")
@app.post("/api/mesh/inbound")
def mesh_inbound(event: MeshInbound) -> dict:
    payload = event.payload.strip()
    created = now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO mesh_events (id, direction, payload, source, node_id, rssi, snr, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (secrets.token_hex(6), "in", payload, event.source, event.node_id, event.rssi, event.snr, created),
        )
    parsed = parse_mesh_payload(payload)
    if parsed.get("type") == "profile":
        upsert_mesh_profile(parsed, event, created)
    return {"received": True, "parsed": parsed}


def parse_mesh_payload(payload: str) -> dict:
    if payload.startswith("MM1|"):
        return parse_mm1(payload)
    if payload.startswith("AM1"):
        return parse_am1(payload)
    return {"type": "unknown", "raw": payload}


def parse_mm1(payload: str) -> dict:
    parts = payload.split("|", 5)
    if len(parts) != 6:
        return {"protocol": "MM1", "type": "invalid", "raw": payload, "reason": "expected 6 pipe-separated fields"}
    _, pseudo, genre_recherche, age_raw, hobbies, bio = parts
    try:
        age = int(age_raw)
    except ValueError:
        age = None
    if age is not None and age < 18:
        return {"protocol": "MM1", "type": "invalid", "raw": payload, "reason": "minor profiles refused"}
    tags = [clean_field(x, 24) for x in hobbies.split(",") if clean_field(x, 24)][:8]
    return {
        "protocol": "MM1",
        "type": "profile",
        "display_name": clean_field(pseudo, 32),
        "genre_recherche": clean_field(genre_recherche, 24),
        "age": age,
        "tags": tags,
        "bio": clean_field(bio, 160),
        "intent": "date",
        "zone": DEFAULT_ZONE,
        "avatar_heart": "♡",
    }


def parse_am1(payload: str) -> dict:
    parts = payload.split()
    if len(parts) < 2 or parts[0] != "AM1":
        return {"type": "unknown", "raw": payload}
    if parts[1] == "B" and len(parts) >= 5:
        public_id = clean_field(parts[2], 16)
        intent = clean_field(parts[3], 32)
        zone = clean_field(parts[4], 32).removeprefix("z") or DEFAULT_ZONE
        ttl = int(parts[5]) if len(parts) >= 6 and parts[5].isdigit() else PROFILE_TTL_SECONDS
        heart = clean_field(parts[6], 4) if len(parts) >= 7 else "<3"
        return {
            "protocol": "AM1",
            "type": "profile",
            "public_id": public_id,
            "display_name": f"Mesh {public_id}",
            "genre_recherche": "",
            "age": None,
            "tags": [intent],
            "bio": "Balise AM1 captee. Le zombie a laisse peu de details.",
            "intent": intent,
            "zone": zone,
            "ttl": ttl,
            "avatar_heart": heart,
        }
    if parts[1] == "I" and len(parts) >= 3:
        return {"protocol": "AM1", "type": "avatar", "public_id": clean_field(parts[2], 16), "parts": parts[3:]}
    return {"protocol": "AM1", "type": parts[1], "parts": parts[2:]}


def upsert_mesh_profile(parsed: dict, event: MeshInbound, created: int) -> None:
    node_key = event.node_id or parsed.get("public_id") or parsed.get("display_name") or secrets.token_hex(3)
    public_id = clean_field(parsed.get("public_id") or short_hash(node_key)[:6], 16)
    profile_id = f"mesh-{public_id}"
    ttl = int(parsed.get("ttl") or PROFILE_TTL_SECONDS)
    active_until = created + min(ttl, PROFILE_TTL_SECONDS)
    tags = parsed.get("tags") or []
    avatar_seed = short_hash(node_key)
    contact_hint = event.node_id or public_id
    with db() as conn:
        conn.execute(
            """
            INSERT INTO profiles (
                id, public_id, node_id, display_name, age, genre_recherche, bio, intent, tags, zone,
                avatar_seed, avatar_heart, created_at, last_seen, active_until, rssi, snr, contact_hint
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(public_id) DO UPDATE SET
                node_id = excluded.node_id,
                display_name = excluded.display_name,
                age = excluded.age,
                genre_recherche = excluded.genre_recherche,
                bio = excluded.bio,
                intent = excluded.intent,
                tags = excluded.tags,
                zone = excluded.zone,
                avatar_heart = excluded.avatar_heart,
                last_seen = excluded.last_seen,
                active_until = excluded.active_until,
                rssi = excluded.rssi,
                snr = excluded.snr,
                contact_hint = excluded.contact_hint
            """,
            (
                profile_id,
                public_id,
                event.node_id,
                clean_field(parsed.get("display_name", f"Mesh {public_id}"), 32),
                parsed.get("age"),
                clean_field(parsed.get("genre_recherche", ""), 24),
                clean_field(parsed.get("bio", ""), 160),
                clean_field(parsed.get("intent", "date"), 32),
                ",".join([clean_field(x, 24) for x in tags[:8]]),
                clean_field(parsed.get("zone", DEFAULT_ZONE), 32),
                avatar_seed,
                clean_field(parsed.get("avatar_heart", "♡"), 4),
                created,
                created,
                active_until,
                event.rssi,
                event.snr,
                contact_hint,
            ),
        )


def png_qr(data: str) -> Response:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/api/radio/config")
def radio_config() -> dict:
    return {
        "region": REGION,
        "modem_preset": MODEM_PRESET,
        "hop_limit": HOP_LIMIT,
        "primary_channel": PRIMARY_CHANNEL,
        "secondary_channel": SECONDARY_CHANNEL,
        "position_precision": POSITION_PRECISION,
        "local_url": PUBLIC_BASE_URL,
        "wifi_ssid": AP_SSID,
        "notes": [
            "Keep primary/default public for maximum compatibility unless using a private event mesh.",
            "Use secondary ADOPT for project-specific short messages.",
            "Generate native Meshtastic channel QR inside the official app when possible.",
        ],
    }


@app.get("/api/radio/commands")
def radio_commands() -> dict:
    commands = [
        f"meshtastic --set lora.region {REGION} --set lora.modem_preset {MODEM_PRESET} --set lora.hop_limit {HOP_LIMIT}",
        f"meshtastic --ch-set name {quote(PRIMARY_CHANNEL)} --ch-set psk default --ch-index 0",
        f"meshtastic --ch-set module_settings.position_precision {POSITION_PRECISION} --ch-index 0",
        f"meshtastic --ch-set name {quote(SECONDARY_CHANNEL)} --ch-set psk random --ch-index 1",
        "meshtastic --info",
        "meshtastic --qr-all",
    ]
    return {"commands": commands, "warning": "Save the generated secondary PSK; lost key, lonely zombie."}


@app.get("/api/qr/site")
def qr_site() -> Response:
    return png_qr(PUBLIC_BASE_URL)


@app.get("/api/qr/wifi")
def qr_wifi() -> Response:
    if AP_PASSWORD:
        data = f"WIFI:T:WPA;S:{AP_SSID};P:{AP_PASSWORD};;"
    else:
        data = f"WIFI:T:nopass;S:{AP_SSID};;"
    return png_qr(data)


@app.get("/api/qr/radio-commands")
def qr_radio_commands() -> Response:
    commands = radio_commands()["commands"]
    return png_qr("\n".join(commands))
