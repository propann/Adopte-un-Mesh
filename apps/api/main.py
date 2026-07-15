from __future__ import annotations

import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("DATABASE_PATH", "/data/adoptmesh.sqlite3"))
DEFAULT_ZONE = os.getenv("ADOPT_DEFAULT_ZONE", "lyon-nord")
PROFILE_TTL_SECONDS = int(os.getenv("ADOPT_PROFILE_TTL_SECONDS", "86400"))

app = FastAPI(title="Adopte un Mesh API", version="0.1.0")

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


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                public_id TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                bio TEXT NOT NULL DEFAULT '',
                intent TEXT NOT NULL DEFAULT 'ami',
                tags TEXT NOT NULL DEFAULT '',
                zone TEXT NOT NULL DEFAULT 'local',
                avatar_seed TEXT NOT NULL,
                avatar_heart TEXT NOT NULL DEFAULT '<3',
                created_at INTEGER NOT NULL,
                active_until INTEGER NOT NULL,
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

            CREATE TABLE IF NOT EXISTS mesh_events (
                id TEXT PRIMARY KEY,
                direction TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at INTEGER NOT NULL
            );
            """
        )


@app.on_event("startup")
def startup() -> None:
    init_db()


class ProfileIn(BaseModel):
    display_name: str = Field(min_length=2, max_length=32)
    bio: str = Field(default="", max_length=160)
    intent: str = Field(default="ami", max_length=32)
    tags: list[str] = Field(default_factory=list, max_length=8)
    zone: str = Field(default=DEFAULT_ZONE, max_length=32)
    avatar_seed: Optional[str] = Field(default=None, max_length=24)
    avatar_heart: str = Field(default="♡", max_length=4)


class LikeIn(BaseModel):
    from_public_id: str = Field(min_length=3, max_length=12)
    mode: str = Field(default="soft", max_length=16)


class ReportIn(BaseModel):
    from_public_id: str = Field(min_length=3, max_length=12)
    reason: str = Field(min_length=3, max_length=80)


class MeshInbound(BaseModel):
    payload: str = Field(min_length=2, max_length=200)
    source: str = Field(default="radio", max_length=32)


def make_public_id() -> str:
    return secrets.token_hex(2).upper()


def row_to_profile(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "public_id": row["public_id"],
        "display_name": row["display_name"],
        "bio": row["bio"],
        "intent": row["intent"],
        "tags": [x for x in row["tags"].split(",") if x],
        "zone": row["zone"],
        "avatar_seed": row["avatar_seed"],
        "avatar_heart": row["avatar_heart"],
        "active_until": row["active_until"],
    }


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "adopte-un-mesh", "zombie_density": "manageable"}


@app.post("/profiles")
def create_profile(profile: ProfileIn) -> dict:
    public_id = make_public_id()
    profile_id = secrets.token_urlsafe(12)
    avatar_seed = profile.avatar_seed or secrets.token_hex(4)
    created = now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO profiles (id, public_id, display_name, bio, intent, tags, zone, avatar_seed, avatar_heart, created_at, active_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id,
                public_id,
                profile.display_name,
                profile.bio,
                profile.intent,
                ",".join(profile.tags[:8]),
                profile.zone,
                avatar_seed,
                profile.avatar_heart,
                created,
                created + PROFILE_TTL_SECONDS,
            ),
        )
    return {"public_id": public_id, "id": profile_id, "avatar_seed": avatar_seed}


@app.get("/profiles/active")
def active_profiles() -> dict:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM profiles WHERE active_until > ? AND blocked = 0 ORDER BY created_at DESC LIMIT 50",
            (now(),),
        ).fetchall()
    return {"profiles": [row_to_profile(row) for row in rows]}


@app.post("/profiles/{target_public_id}/like")
def like_profile(target_public_id: str, like: LikeIn) -> dict:
    if target_public_id == like.from_public_id:
        raise HTTPException(status_code=400, detail="self-like refused; even zombies need boundaries")
    created = now()
    with db() as conn:
        target = conn.execute("SELECT public_id FROM profiles WHERE public_id = ?", (target_public_id,)).fetchone()
        source = conn.execute("SELECT public_id FROM profiles WHERE public_id = ?", (like.from_public_id,)).fetchone()
        if not target or not source:
            raise HTTPException(status_code=404, detail="profile not found")
        conn.execute(
            "INSERT OR IGNORE INTO likes (from_public_id, to_public_id, mode, created_at) VALUES (?, ?, ?, ?)",
            (like.from_public_id, target_public_id, like.mode, created),
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
def list_matches() -> dict:
    with db() as conn:
        rows = conn.execute("SELECT * FROM matches ORDER BY created_at DESC LIMIT 50").fetchall()
    return {"matches": [dict(row) for row in rows]}


@app.post("/profiles/{target_public_id}/report")
def report_profile(target_public_id: str, report: ReportIn) -> dict:
    report_id = secrets.token_hex(6)
    with db() as conn:
        conn.execute(
            "INSERT INTO reports (id, from_public_id, target_public_id, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (report_id, report.from_public_id, target_public_id, report.reason, now()),
        )
    return {"reported": True, "report_id": report_id}


@app.post("/profiles/{target_public_id}/block")
def block_profile(target_public_id: str) -> dict:
    with db() as conn:
        conn.execute("UPDATE profiles SET blocked = 1 WHERE public_id = ?", (target_public_id,))
    return {"blocked": True}


@app.post("/mesh/inbound")
def mesh_inbound(event: MeshInbound) -> dict:
    payload = event.payload.strip()
    with db() as conn:
        conn.execute(
            "INSERT INTO mesh_events (id, direction, payload, created_at) VALUES (?, ?, ?, ?)",
            (secrets.token_hex(6), "in", payload, now()),
        )
    parsed = parse_am1(payload)
    return {"received": True, "parsed": parsed}


def parse_am1(payload: str) -> dict:
    # AM1 B K7Q2 AD zLN 900 <3
    parts = payload.split()
    if len(parts) < 2 or parts[0] != "AM1":
        return {"type": "unknown", "raw": payload}
    return {"protocol": "AM1", "type": parts[1], "parts": parts[2:]}
