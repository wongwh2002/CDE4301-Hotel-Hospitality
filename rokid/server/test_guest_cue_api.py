import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from server.app import create_app
from server.guest_preferences import GuestPreferenceStore
from server.test_app import FakeRecognizer, face, jpeg


class GuestCueApiTests(unittest.TestCase):
    def test_known_name_gets_its_cues_unknown_and_missing_profiles_get_none(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GuestPreferenceStore(Path(directory) / 'demo.sqlite3')
            with store.connect() as db:
                db.execute("INSERT INTO guests(name,created_at) VALUES ('Demo Guest','now')")
                for item, kind, category in [('twin_room','prefer','room_type'),('shellfish','allergy','food_beverage')]:
                    db.execute('INSERT INTO guest_preferences VALUES (1,?,?,?,?,?)',
                               (category,item,kind,'demo_manual','now'))
                # Even a profile named Unknown must never be exposed as recognized context.
                db.execute("INSERT INTO guests(name,created_at) VALUES ('Unknown','now')")
                db.execute("INSERT INTO guest_preferences VALUES (2,'room_type','suite','prefer','demo_manual','now')")
            fake = FakeRecognizer([face('Demo Guest'), face('Unknown'), face('No Profile')])
            with TestClient(create_app(fake, preference_store=store)) as client:
                response = client.post('/detect?request_id=cue-test', content=jpeg(), headers={'Content-Type':'image/jpeg'})
                self.assertEqual(response.status_code, 200)
                faces = response.json()['faces']
                self.assertEqual([c['code'] for c in faces[0]['cues']], ['shellfish','twin_room'])
                self.assertEqual(faces[0]['cues'][0]['marker_file'], 'markers/warning.svg')
                self.assertEqual(faces[1]['cues'], [])
                self.assertEqual(faces[2]['cues'], [])

    def test_response_caps_cues_at_two_and_keeps_allergy_first(self):
        class Store:
            def profiles(self):
                return [{'name':'Demo', 'cues':[{'code':'twin_room','sentiment':'prefer'},
                        {'code':'black_coffee','sentiment':'prefer'}, {'code':'shellfish','sentiment':'allergy'}]}]
        with TestClient(create_app(FakeRecognizer([face('Demo')]), preference_store=Store())) as client:
            response = client.post('/detect?request_id=cap-test', content=jpeg(), headers={'Content-Type':'image/jpeg'})
            cues = response.json()['faces'][0]['cues']
            self.assertEqual(len(cues), 2)
            self.assertEqual(cues[0]['code'], 'shellfish')


if __name__ == '__main__':
    unittest.main()
