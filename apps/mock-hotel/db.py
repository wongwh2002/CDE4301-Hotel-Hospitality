"""SQLite database manager for mock-hotel.

Seeds synthetic guest profiles and can persist up to three local reference
photos per registered guest. Uploaded photos remain in the Docker data volume.
"""

import json
import hashlib
import os
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fixtures.synthetic_data import SYNTHETIC_FACE_JPEG_BYTES, SYNTHETIC_JPEG_BYTES


DEFAULT_DB_PATH = os.environ.get("SQLITE_PATH", "/data/mock-hotel.db")
LEGACY_SYNTHETIC_PHOTO_SHA256 = "d1154dd16490a3e7328288d0e6847576455f8b0f9f4ec59a5421f58505edd309"
PERSON_FREE_SYNTHETIC_PHOTO_SHA256 = hashlib.sha256(SYNTHETIC_JPEG_BYTES).hexdigest()
SYNTHETIC_PLACEHOLDER_HASHES = {
    LEGACY_SYNTHETIC_PHOTO_SHA256,
    PERSON_FREE_SYNTHETIC_PHOTO_SHA256,
}


def get_db_path() -> Path:
    raw_path = os.environ.get("SQLITE_PATH", DEFAULT_DB_PATH)
    path = Path(raw_path)
    # If directory doesn't exist (e.g. running outside Docker and /data doesn't exist), fallback to local path
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError):
        fallback = Path("./data/mock-hotel.db")
        fallback.parent.mkdir(parents=True, exist_ok=True)
        return fallback
    return path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables and seed synthetic data if empty."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guests (
                    guest_ref TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    room_number TEXT,
                    vip_tier TEXT,
                    allergies_json TEXT,
                    preferences_json TEXT,
                    photo_bytes BLOB
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guest_reference_photos (
                    guest_ref TEXT NOT NULL,
                    photo_index INTEGER NOT NULL,
                    photo_bytes BLOB NOT NULL,
                    PRIMARY KEY (guest_ref, photo_index),
                    FOREIGN KEY (guest_ref) REFERENCES guests(guest_ref)
                )
                """
            )

            # Upgrade only known placeholder bytes in existing demo databases.
            # Alex gets the fictional face fixture; all other placeholder photos
            # remain person-free. Digest checks leave custom photos untouched.
            for row in conn.execute("SELECT guest_ref, photo_bytes FROM guests"):
                photo_bytes = bytes(row["photo_bytes"] or b"")
                if hashlib.sha256(photo_bytes).hexdigest() in SYNTHETIC_PLACEHOLDER_HASHES:
                    replacement = (
                        SYNTHETIC_FACE_JPEG_BYTES
                        if row["guest_ref"] == "guest-alex-101"
                        else SYNTHETIC_JPEG_BYTES
                    )
                    conn.execute(
                        "UPDATE guests SET photo_bytes = ? WHERE guest_ref = ?",
                        (replacement, row["guest_ref"]),
                    )

            cursor = conn.execute("SELECT COUNT(*) AS cnt FROM guests")
            row = cursor.fetchone()
            if row and row["cnt"] == 0:
                seed_synthetic_data(conn)
    finally:
        conn.close()


def seed_synthetic_data(conn: sqlite3.Connection) -> None:
    """Insert clearly synthetic profiles for lounge POC testing."""
    synthetic_guests = [
        (
            "guest-alex-101",
            "Alex",
            "401",
            "Diamond",
            json.dumps(["Peanut allergy"]),
            json.dumps(["Sparkling water", "Window seat"]),
            SYNTHETIC_FACE_JPEG_BYTES,
        ),
        (
            "guest-jordan-102",
            "Jordan",
            "512",
            "Gold",
            json.dumps(["Shellfish allergy"]),
            json.dumps(["Earl Grey tea"]),
            SYNTHETIC_JPEG_BYTES,
        ),
        (
            "guest-casey-103",
            "Casey",
            "305",
            "Executive",
            json.dumps([]),
            json.dumps(["Quiet table"]),
            SYNTHETIC_JPEG_BYTES,
        ),
        (
            "guest-samira-104",
            "Samira",
            "620",
            "Platinum",
            json.dumps(["Gluten intolerance"]),
            json.dumps(["Oat milk latte"]),
            SYNTHETIC_JPEG_BYTES,
        ),
    ]

    conn.executemany(
        """
        INSERT INTO guests (
            guest_ref, display_name, room_number, vip_tier,
            allergies_json, preferences_json, photo_bytes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        synthetic_guests,
    )


def get_guest_profile(guest_ref: str) -> Optional[Dict[str, Any]]:
    """Fetch minimal permitted profile fields for a guest."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT guest_ref, display_name, room_number, vip_tier,
                   allergies_json, preferences_json
            FROM guests
            WHERE guest_ref = ?
            """,
            (guest_ref,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        photo_urls = get_guest_photo_urls(guest_ref)
        return {
            "guest_ref": row["guest_ref"],
            "display_name": row["display_name"],
            "room_number": row["room_number"],
            "vip_tier": row["vip_tier"],
            "allergies": json.loads(row["allergies_json"] or "[]"),
            "preferences": json.loads(row["preferences_json"] or "[]"),
            "photo_url": f"/v1/guests/{row['guest_ref']}/photo",
            "photo_urls": photo_urls,
        }
    finally:
        conn.close()


def get_guest_photo_bytes(guest_ref: str, photo_index: int = 0) -> Optional[bytes]:
    """Fetch one persisted reference photo for candidate enrollment."""
    conn = get_connection()
    try:
        if photo_index == 0:
            cursor = conn.execute(
                "SELECT photo_bytes FROM guests WHERE guest_ref = ?",
                (guest_ref,),
            )
        elif photo_index > 0:
            cursor = conn.execute(
                """SELECT photo_bytes FROM guest_reference_photos
                   WHERE guest_ref = ? AND photo_index = ?""",
                (guest_ref, photo_index),
            )
        else:
            return None
        row = cursor.fetchone()
        if not row or not row["photo_bytes"]:
            return None
        return bytes(row["photo_bytes"])
    finally:
        conn.close()


def get_guest_photo_urls(guest_ref: str) -> List[str]:
    """Return relative URLs for the guest's stored reference photos."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """SELECT g.photo_bytes,
                      (SELECT COUNT(*) FROM guest_reference_photos p
                       WHERE p.guest_ref = g.guest_ref) AS extra_count
               FROM guests g WHERE g.guest_ref = ?""",
            (guest_ref,),
        )
        row = cursor.fetchone()
        if not row or not row["photo_bytes"]:
            return []
        count = 1 + int(row["extra_count"] or 0)
        return [
            f"/v1/guests/{guest_ref}/photos/{photo_index}"
            for photo_index in range(min(count, 3))
        ]
    finally:
        conn.close()


def list_all_guests() -> List[Dict[str, Any]]:
    """List summary of all synthetic guests."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT guest_ref, display_name, room_number, vip_tier,
                   allergies_json, preferences_json
            FROM guests
            ORDER BY guest_ref ASC
            """
        )
        results = []
        for row in cursor.fetchall():
            photo_urls = get_guest_photo_urls(row["guest_ref"])
            results.append(
                {
                    "guest_ref": row["guest_ref"],
                    "display_name": row["display_name"],
                    "room_number": row["room_number"],
                    "vip_tier": row["vip_tier"],
                    "allergies": json.loads(row["allergies_json"] or "[]"),
                    "preferences": json.loads(row["preferences_json"] or "[]"),
                    "photo_url": f"/v1/guests/{row['guest_ref']}/photo",
                    "photo_urls": photo_urls,
                }
            )
        return results
    finally:
        conn.close()


def register_guest(
    display_name: str,
    allergies: Optional[List[str]] = None,
    preferences: Optional[List[str]] = None,
    room_number: Optional[str] = None,
    vip_tier: Optional[str] = None,
    photo_bytes: Optional[bytes] = None,
    photo_bytes_list: Optional[List[bytes]] = None,
    guest_ref: Optional[str] = None,
) -> Dict[str, Any]:
    """Register a new synthetic guest into SQLite.

    Generates a unique guest_ref if not provided and stores up to three reference
    photos. If no photo is provided, it attaches a person-free synthetic fixture.
    """
    clean_name = re.sub(r"[^a-z0-9]", "", display_name.lower())[:16] or "guest"
    conn = get_connection()
    try:
        if not guest_ref:
            while True:
                candidate_ref = f"guest-{clean_name}-{uuid.uuid4().hex[:6]}"
                cursor = conn.execute("SELECT 1 FROM guests WHERE guest_ref = ?", (candidate_ref,))
                if not cursor.fetchone():
                    guest_ref = candidate_ref
                    break

        allergies_list = list(allergies) if allergies else []
        preferences_list = list(preferences) if preferences else []
        supplied_photos = list(photo_bytes_list or [])[:3]
        if supplied_photos:
            final_photo_bytes = supplied_photos[0]
        else:
            final_photo_bytes = photo_bytes if photo_bytes is not None else SYNTHETIC_JPEG_BYTES

        with conn:
            conn.execute(
                """
                INSERT INTO guests (
                    guest_ref, display_name, room_number, vip_tier,
                    allergies_json, preferences_json, photo_bytes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    guest_ref,
                    display_name,
                    room_number,
                    vip_tier,
                    json.dumps(allergies_list),
                    json.dumps(preferences_list),
                    final_photo_bytes,
                ),
            )
            if supplied_photos:
                conn.executemany(
                    """INSERT INTO guest_reference_photos
                       (guest_ref, photo_index, photo_bytes) VALUES (?, ?, ?)""",
                    [
                        (guest_ref, index, image_bytes)
                        for index, image_bytes in enumerate(supplied_photos[1:], start=1)
                    ],
                )

        photo_urls = [
            f"/v1/guests/{guest_ref}/photos/{photo_index}"
            for photo_index in range(len(supplied_photos) or 1)
        ]

        return {
            "guest_ref": guest_ref,
            "display_name": display_name,
            "room_number": room_number,
            "vip_tier": vip_tier,
            "allergies": allergies_list,
            "preferences": preferences_list,
            "photo_url": f"/v1/guests/{guest_ref}/photo",
            "photo_urls": photo_urls,
        }
    finally:
        conn.close()


def update_guest(guest_ref: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update permitted profile fields without changing stored reference photos."""
    column_map = {
        "display_name": "display_name",
        "room_number": "room_number",
        "vip_tier": "vip_tier",
        "allergies": "allergies_json",
        "preferences": "preferences_json",
    }
    assignments = []
    values = []
    for field, column in column_map.items():
        if field not in updates:
            continue
        value = updates[field]
        if field in {"allergies", "preferences"}:
            value = json.dumps(value or [])
        assignments.append(f"{column} = ?")
        values.append(value)

    conn = get_connection()
    try:
        cursor = conn.execute("SELECT 1 FROM guests WHERE guest_ref = ?", (guest_ref,))
        if not cursor.fetchone():
            return None
        if assignments:
            values.append(guest_ref)
            with conn:
                conn.execute(
                    f"UPDATE guests SET {', '.join(assignments)} WHERE guest_ref = ?",
                    values,
                )
        return get_guest_profile(guest_ref)
    finally:
        conn.close()
