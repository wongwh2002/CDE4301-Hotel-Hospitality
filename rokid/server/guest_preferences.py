"""SQLite demo profiles, independent of photographs and recognition inference."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import random
import sqlite3
from itertools import combinations

SERVER_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = SERVER_DIR / "data" / "guest-preferences.sqlite3"
ICON_DIR = SERVER_DIR / "preference_icons"
CATALOG = (
    ("king_room", "room_type", "King room", "king-bed.svg"),
    ("twin_room", "room_type", "Twin room", "twin-beds.svg"),
    ("suite", "room_type", "Suite", "suite.svg"),
    ("black_coffee", "food_beverage", "Black coffee", "black-coffee.svg"),
    ("green_tea", "food_beverage", "Green tea", "green-tea.svg"),
    ("still_water", "food_beverage", "Still water", "still-water.svg"),
    ("vegetarian", "food_beverage", "Vegetarian food", "vegetarian.svg"),
    ("smoking_room", "room_type", "Smoking-allowed room", "smoking-room.svg"),
    ("shellfish", "food_beverage", "Shellfish", "shellfish.svg"),
    ("peanut", "food_beverage", "Peanuts", "peanut.svg"),
    ("milk", "food_beverage", "Milk", "milk.svg"),
    ("egg", "food_beverage", "Eggs", "egg.svg"),
)

MARKERS = {
    "prefer": {"label": "Prefers", "icon_file": "markers/heart.svg"},
    "dislike": {"label": "Dislikes", "icon_file": "markers/dislike.svg"},
    "allergy": {"label": "Demo allergy", "icon_file": "markers/warning.svg"},
}
ALLERGEN_CODES = ("shellfish", "peanut", "milk", "egg")


def demo_assignments(names):
    """One or two fictional cues per guest, with distinct demo combinations."""
    plans = ((1, 0, 1), (1, 0, 0), (0, 0, 2), (0, 1, 0), (2, 0, 0), (0, 1, 1), (1, 0, 1))
    used_profiles, used_likes, used_allergies = set(), set(), set()
    result = {}
    for index, name in enumerate(names):
        rng = random.Random(f"hotel-poc-cues-v2:{name.casefold()}")
        likes, dislikes, allergies = plans[index % len(plans)]
        # Only one totally empty profile; larger galleries still receive distinct combinations.
        if (likes, dislikes, allergies) == (0, 0, 0) and () in used_profiles:
            likes = 1
        options = [item[0] for item in CATALOG if item[0] not in ALLERGEN_CODES and item[0] != 'smoking_room']
        for _ in range(1000):
            liked = ([rng.choice(['king_room', 'twin_room', 'suite']),
                      rng.choice(['black_coffee', 'green_tea', 'still_water', 'vegetarian'])]
                     if likes == 2 else rng.sample(options, likes))
            disliked = ['smoking_room'] if dislikes else []
            allergy_sets = list(combinations(ALLERGEN_CODES, allergies))
            available = [s for s in allergy_sets if tuple(sorted(s)) not in used_allergies] or allergy_sets
            allergic = rng.choice(available)
            cues = [(code, 'prefer') for code in liked] + [(code, 'dislike') for code in disliked]
            cues += [(code, 'allergy') for code in allergic]
            signature = tuple(sorted(cues))
            like_signature = tuple(sorted(liked))
            if signature not in used_profiles and (not liked or like_signature not in used_likes):
                used_profiles.add(signature)
                if liked:
                    used_likes.add(like_signature)
                if allergic:
                    used_allergies.add(tuple(sorted(allergic)))
                result[name] = cues
                break
        else:
            raise ValueError("Too many guests for unique demo cue combinations")
    return result


class GuestPreferenceStore:
    def __init__(self, path=DEFAULT_DATABASE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY, name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    is_demo INTEGER NOT NULL DEFAULT 1 CHECK(is_demo IN (0,1)),
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS preference_options (
                    code TEXT PRIMARY KEY, category TEXT NOT NULL
                        CHECK(category IN ('room_type','food_beverage')),
                    label TEXT NOT NULL, icon_file TEXT NOT NULL,
                    UNIQUE(code,category)
                );
            """)
            db.executemany("INSERT OR IGNORE INTO preference_options VALUES (?,?,?,?)", CATALOG)
            columns = {row['name'] for row in db.execute('PRAGMA table_info(guests)')}
            if 'in_gallery' not in columns:
                db.execute('ALTER TABLE guests ADD COLUMN in_gallery INTEGER NOT NULL DEFAULT 1')
            if 'demo_seeded' not in columns:
                db.execute('ALTER TABLE guests ADD COLUMN demo_seeded INTEGER NOT NULL DEFAULT 0')
            existing = {row['name'] for row in db.execute('PRAGMA table_info(guest_preferences)')}
            if existing and 'sentiment' not in existing:
                db.execute('ALTER TABLE guest_preferences RENAME TO guest_preferences_v1')
            db.execute("""CREATE TABLE IF NOT EXISTS guest_preferences (
                guest_id INTEGER NOT NULL REFERENCES guests(id), category TEXT NOT NULL,
                option_code TEXT NOT NULL, sentiment TEXT NOT NULL CHECK(sentiment IN ('prefer','dislike','allergy')),
                source TEXT NOT NULL DEFAULT 'demo_manual', updated_at TEXT NOT NULL,
                PRIMARY KEY(guest_id,option_code),
                CHECK(sentiment != 'allergy' OR category = 'food_beverage'),
                FOREIGN KEY(option_code,category) REFERENCES preference_options(code,category)
            )""")
            if existing and 'sentiment' not in existing:
                db.execute("""INSERT INTO guest_preferences
                    SELECT guest_id,category,option_code,'prefer',source,updated_at FROM guest_preferences_v1""")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=3)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def seed_gallery(self, gallery: Path, regenerate_demo=False):
        # Read filenames only. No face images, templates, or embeddings enter this DB.
        gallery = Path(gallery)
        if not gallery.is_dir():
            raise ValueError(f"Gallery directory does not exist: {gallery}")
        names = sorted({p.stem for p in gallery.iterdir() if p.is_file()
                        and p.suffix.lower() in {'.jpg','.jpeg','.png','.bmp','.webp'}}, key=str.casefold)
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError('Gallery names must be unique ignoring case')
        assignments = demo_assignments(names)
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as db:
            db.execute('UPDATE guests SET in_gallery=0')
            for name in names:
                db.execute("INSERT OR IGNORE INTO guests(name,created_at) VALUES (?,?)", (name, now))
                guest = db.execute("SELECT id,is_demo,demo_seeded FROM guests WHERE name=?", (name,)).fetchone()
                guest_id = guest['id']
                db.execute('UPDATE guests SET in_gallery=1 WHERE id=?', (guest_id,))
                if not guest['is_demo']:
                    continue
                if regenerate_demo:
                    db.execute("DELETE FROM guest_preferences WHERE guest_id=? AND source IN ('demo_random','demo_random_v2')", (guest_id,))
                elif guest['demo_seeded'] or db.execute('SELECT 1 FROM guest_preferences WHERE guest_id=?', (guest_id,)).fetchone():
                    db.execute('UPDATE guests SET demo_seeded=1 WHERE id=?', (guest_id,))
                    continue
                for option, sentiment in assignments[name]:
                    category = next(item[1] for item in CATALOG if item[0] == option)
                    db.execute("""INSERT OR IGNORE INTO guest_preferences
                        (guest_id,category,option_code,sentiment,source,updated_at) VALUES (?,?,?,?,'demo_random_v2',?)""",
                        (guest_id, category, option, sentiment, now))
                db.execute('UPDATE guests SET demo_seeded=1 WHERE id=?', (guest_id,))
        return self.profiles()

    def profiles(self):
        with self.connect() as db:
            guests = db.execute("SELECT id,name,is_demo FROM guests WHERE in_gallery=1 ORDER BY name COLLATE NOCASE").fetchall()
            profiles = []
            for guest in guests:
                cues = [dict(row) for row in db.execute("""
                         SELECT p.category, o.code, o.label, o.icon_file, p.sentiment,
                                p.source, p.updated_at
                         FROM guest_preferences p JOIN preference_options o ON p.option_code=o.code
                         WHERE p.guest_id=? ORDER BY p.sentiment,p.category DESC,o.code
                     """, (guest['id'],))]
                for cue in cues:
                    cue['marker_file'] = MARKERS[cue['sentiment']]['icon_file']
                profiles.append({'guest_id': guest['id'], 'name': guest['name'], 'is_demo': bool(guest['is_demo']),
                                 'cues': cues,
                                 'preferences': [c for c in cues if c['sentiment'] == 'prefer'],
                                 'dislikes': [c for c in cues if c['sentiment'] == 'dislike'],
                                 'allergies': [c for c in cues if c['sentiment'] == 'allergy']})
            return profiles
