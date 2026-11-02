"""Small SQLite POC store. No audio or complete conversations are persisted."""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class CaptureConflict(ValueError):
    pass


class PreferenceStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS guests (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS preferences (
                    guest_id TEXT NOT NULL REFERENCES guests(id), preference_key TEXT NOT NULL,
                    value TEXT NOT NULL, evidence TEXT NOT NULL, updated_at TEXT NOT NULL,
                    capture_id TEXT NOT NULL, PRIMARY KEY (guest_id, preference_key)
                );
                CREATE TABLE IF NOT EXISTS captures (
                    id TEXT PRIMARY KEY, name_key TEXT NOT NULL, audio_sha256 TEXT NOT NULL,
                    response_json TEXT NOT NULL, created_at TEXT NOT NULL
                );
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=3)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def existing_capture(self, capture_id: str, name: str, audio_sha256: str) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM captures WHERE id=?", (capture_id,)).fetchone()
        if row is None:
            return None
        if row["name_key"] != name.strip().casefold() or row["audio_sha256"] != audio_sha256:
            raise CaptureConflict("Capture ID already belongs to different audio or guest")
        return json.loads(row["response_json"])

    def save(self, capture_id: str, name: str, audio_sha256: str, preferences: list[dict], timings: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        name = name.strip()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM captures WHERE id=?", (capture_id,)).fetchone()
            if row:
                if row["name_key"] != name.casefold() or row["audio_sha256"] != audio_sha256:
                    raise CaptureConflict("Capture ID already belongs to different audio or guest")
                return json.loads(row["response_json"])
            db.execute("INSERT OR IGNORE INTO guests VALUES (?,?,?,?)", (str(uuid.uuid4()), name, name.casefold(), now))
            guest = db.execute("SELECT id,name FROM guests WHERE name_key=?", (name.casefold(),)).fetchone()
            for preference in preferences:
                db.execute("""INSERT INTO preferences VALUES (?,?,?,?,?,?)
                    ON CONFLICT(guest_id,preference_key) DO UPDATE SET
                    value=excluded.value,evidence=excluded.evidence,updated_at=excluded.updated_at,capture_id=excluded.capture_id""",
                    (guest["id"], preference["key"], preference["value"], preference["evidence"], now, capture_id))
            response = {"capture_id": capture_id, "status": "completed", "guest_id": guest["id"],
                        "name": guest["name"], "preferences": preferences, "saved_count": len(preferences), **timings}
            db.execute("INSERT INTO captures VALUES (?,?,?,?,?)",
                       (capture_id, name.casefold(), audio_sha256, json.dumps(response, ensure_ascii=False), now))
        return response

    def guests(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute("SELECT id,name FROM guests ORDER BY name COLLATE NOCASE").fetchall()
            return [{"guest_id": row["id"], "name": row["name"], "preferences": [dict(p) for p in db.execute(
                "SELECT preference_key AS key,value,evidence,updated_at FROM preferences WHERE guest_id=? ORDER BY preference_key",
                (row["id"],)).fetchall()]} for row in rows]
