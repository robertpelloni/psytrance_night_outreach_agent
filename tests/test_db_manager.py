import unittest
import os
from src.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_path = 'database/test_outreach.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_venue_and_uniqueness(self):
        venue = {
            'id': 'test-1',
            'name': 'Test Club',
            'city': 'Detroit',
            'website': 'https://testclub.com',
            'google_rating': 4.5,
            'tags': 'techno',
            'raw_about_text': 'About test'
        }
        self.db.add_venue(venue)

        # Check retrieval
        v = self.db.get_venue('test-1')
        self.assertEqual(v['name'], 'Test Club')

        # Check name existence
        v_id = self.db.venue_exists_by_name('Test Club', 'Detroit')
        self.assertEqual(v_id, 'test-1')

        # Test UNIQUE constraint on website (via INSERT OR IGNORE)
        venue2 = venue.copy()
        venue2['id'] = 'test-2'
        venue2['name'] = 'Test Club 2'
        self.db.add_venue(venue2)

        # Verify second venue was ignored because of duplicate website
        v2 = self.db.get_venue('test-2')
        self.assertIsNone(v2)

    def test_add_lead_uniqueness(self):
        lead = {
            'venue_id': 'v-1',
            'vibe_score': 8,
            'qualification_justification': 'Justify',
            'generated_pitch': 'Pitch',
            'pipeline_status': 'PENDING_REVIEW'
        }
        self.db.add_lead(lead)

        # Add duplicate lead for same venue
        self.db.add_lead(lead)

        # Check leads count
        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT count(*) FROM outreach_leads WHERE venue_id = 'v-1'")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

if __name__ == "__main__":
    unittest.main()
