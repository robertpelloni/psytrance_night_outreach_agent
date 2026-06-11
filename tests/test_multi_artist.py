import unittest
import os
import sqlite3
from src.db_manager import DatabaseManager

class TestMultiArtist(unittest.TestCase):
    def setUp(self):
        self.db_path = 'database/test_multi_artist.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_artist_management(self):
        artist_data = {
            "name": "Test DJ",
            "bio": "A psytrance DJ",
            "genres": "Forest, Darkpsy",
            "epk_link": "http://epk.com",
            "mix_link": "http://mix.com",
            "rate_card": "$500"
        }
        artist_id = self.db.add_artist(artist_data)
        self.assertIsNotNone(artist_id)

        artist = self.db.get_artist(artist_id)
        self.assertEqual(artist['name'], "Test DJ")
        self.assertEqual(artist['genres'], "Forest, Darkpsy")

        artists = self.db.list_artists()
        self.assertEqual(len(artists), 1)

        artist_data['bio'] = "Updated bio"
        self.db.update_artist(artist_id, artist_data)
        artist = self.db.get_artist(artist_id)
        self.assertEqual(artist['bio'], "Updated bio")

        self.db.delete_artist(artist_id)
        self.assertIsNone(self.db.get_artist(artist_id))

    def test_lead_artist_association(self):
        artist_id = self.db.add_artist({"name": "Collective Artist"})
        venue_id = "test_venue"
        self.db.add_venue({"id": venue_id, "name": "Test Club", "city": "Detroit"})
        self.db.add_lead({"venue_id": venue_id, "pipeline_status": "PENDING_REVIEW"})

        lead = self.db.get_lead_by_venue_id(venue_id)
        self.db.update_lead_status(lead['id'], 'APPROVED')

        # Manually associate artist for now as add_lead doesn't support it yet in the UI flow
        with self.db._get_connection() as conn:
            conn.execute("UPDATE outreach_leads SET artist_id = ? WHERE id = ?", (artist_id, lead['id']))

        updated_lead = self.db.get_lead(lead['id'])
        # Since DatabaseManager.get_lead uses Row which I need to check if artist_id is there
        self.assertEqual(updated_lead['artist_id'], artist_id)

if __name__ == '__main__':
    unittest.main()
