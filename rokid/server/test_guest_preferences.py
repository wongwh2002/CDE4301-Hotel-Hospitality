import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from server.guest_preferences import CATALOG, GuestPreferenceStore, ICON_DIR, MARKERS


class GuestPreferenceTests(unittest.TestCase):
    def test_seed_uses_names_and_preserves_existing_assignments_when_gallery_grows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gallery = root / "faces"
            gallery.mkdir()
            (gallery / "Demo Guest.jpg").touch()
            (gallery / "ignored.txt").touch()
            store = GuestPreferenceStore(root / "profiles.sqlite3")
            profiles = store.seed_gallery(gallery)
            self.assertEqual(len(profiles), 1)
            self.assertEqual(profiles[0]["name"], "Demo Guest")
            self.assertTrue(profiles[0]["is_demo"])
            self.assertTrue(profiles[0]['cues'])
            with store.connect() as db:
                db.execute('DELETE FROM guest_preferences')
                db.execute("INSERT INTO guest_preferences VALUES (1,'room_type','suite','prefer','demo_manual','now')")
            saved = store.profiles()[0]
            (gallery / "Another Guest.png").touch()
            store.seed_gallery(gallery)
            reopened = GuestPreferenceStore(store.path).profiles()
            self.assertEqual(len(reopened), 2)
            self.assertEqual(next(p for p in reopened if p["name"] == "Demo Guest"), saved)

    def test_invalid_category_cannot_be_stored_and_every_option_has_an_icon(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GuestPreferenceStore(Path(directory) / "profiles.sqlite3")
            with self.assertRaises(sqlite3.IntegrityError), store.connect() as db:
                db.execute("INSERT INTO guests(name,created_at) VALUES ('Demo','now')")
                db.execute("INSERT INTO guest_preferences VALUES (1,'room_type','black_coffee','prefer','test','now')")
        import xml.etree.ElementTree as ET
        for icon in [item[3] for item in CATALOG] + [marker['icon_file'] for marker in MARKERS.values()]:
            self.assertEqual(ET.parse(ICON_DIR / icon).getroot().tag, "{http://www.w3.org/2000/svg}svg")

    def test_seven_profiles_are_unique_have_one_or_two_cues_and_archive_removed_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gallery = root / 'faces'
            gallery.mkdir()
            for name in ('A','B','C','D','E','F','G'):
                (gallery / f'{name}.png').touch()
            store = GuestPreferenceStore(root / 'db.sqlite3')
            profiles = store.seed_gallery(gallery, regenerate_demo=True)
            signatures = {tuple(sorted((c['code'],c['sentiment']) for c in p['cues'])) for p in profiles}
            self.assertEqual(len(signatures), 7)
            likes = [tuple(sorted(c['code'] for c in p['preferences'])) for p in profiles if p['preferences']]
            allergies = [tuple(sorted(c['code'] for c in p['allergies'])) for p in profiles if p['allergies']]
            self.assertEqual(len(likes), len(set(likes)))
            self.assertEqual(len(allergies), len(set(allergies)))
            self.assertTrue(all(1 <= len(p['cues']) <= 2 for p in profiles))
            self.assertTrue(any(len(p['allergies']) > 1 for p in profiles))
            self.assertTrue(any(len(p['preferences']) > 1 for p in profiles))
            self.assertTrue(any(p['dislikes'] for p in profiles))
            self.assertEqual(store.seed_gallery(gallery), profiles)
            self.assertEqual(store.seed_gallery(gallery, regenerate_demo=True)[0]['cues'][0]['code'], profiles[0]['cues'][0]['code'])
            (gallery / 'A.png').unlink()
            current = store.seed_gallery(gallery)
            self.assertNotIn('A', [p['name'] for p in current])
            with store.connect() as db:
                self.assertEqual(db.execute("SELECT in_gallery FROM guests WHERE name='A'").fetchone()[0], 0)

    def test_v1_migration_and_demo_refresh_preserve_manual_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'legacy.sqlite3'
            with closing(sqlite3.connect(path)) as db, db:
                db.executescript("""
                    CREATE TABLE guests(id INTEGER PRIMARY KEY,name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                        is_demo INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL);
                    CREATE TABLE guest_preferences(guest_id INTEGER,category TEXT,option_code TEXT,
                        source TEXT,updated_at TEXT,PRIMARY KEY(guest_id,category));
                    INSERT INTO guests VALUES(1,'Demo Guest',1,'before');
                    INSERT INTO guest_preferences VALUES(1,'room_type','suite','demo_manual','before');
                """)
            store = GuestPreferenceStore(path)
            original = store.profiles()[0]['preferences'][0]
            self.assertEqual(original['code'], 'suite')
            self.assertEqual(original['sentiment'], 'prefer')
            self.assertEqual(original['marker_file'], 'markers/heart.svg')
            gallery = root / 'faces'
            gallery.mkdir()
            (gallery / 'Demo Guest.png').touch()
            refreshed = store.seed_gallery(gallery, regenerate_demo=True)
            manual = [c for c in refreshed[0]['cues'] if c['source'] == 'demo_manual']
            self.assertEqual(manual, [original])
            self.assertEqual(GuestPreferenceStore(path).profiles(), refreshed)

    def test_same_item_cannot_have_conflicting_markers_and_allergies_cannot_be_rooms(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GuestPreferenceStore(Path(directory) / 'db.sqlite3')
            with store.connect() as db:
                db.execute("INSERT INTO guests(name,created_at) VALUES ('Demo','now')")
                db.execute("INSERT INTO guest_preferences VALUES (1,'room_type','twin_room','prefer','demo_manual','now')")
            with self.assertRaises(sqlite3.IntegrityError), store.connect() as db:
                db.execute("INSERT INTO guest_preferences VALUES (1,'room_type','twin_room','dislike','demo_manual','now')")
            with self.assertRaises(sqlite3.IntegrityError), store.connect() as db:
                db.execute("INSERT INTO guest_preferences VALUES (1,'room_type','suite','allergy','demo_manual','now')")


if __name__ == "__main__":
    unittest.main()
