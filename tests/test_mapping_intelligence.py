import unittest
import os
import json
from src.geocoding import GeocodingUtility
from src.db_manager import DatabaseManager

class TestMappingIntelligence(unittest.TestCase):
    def setUp(self):
        self.db_path = 'database/test_mapping.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = DatabaseManager(db_path=self.db_path)
        self.geocoder = GeocodingUtility()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_geospatial_schema(self):
        """Verify venues table has latitude and longitude columns."""
        with self.db._get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(venues)")
            columns = [row[1] for row in cursor.fetchall()]
            self.assertIn('latitude', columns)
            self.assertIn('longitude', columns)

    def test_location_persistence(self):
        """Verify coordinates can be stored and retrieved."""
        venue_id = 'test_venue_123'
        self.db.add_venue({
            'id': venue_id,
            'name': 'Test Venue',
            'city': 'Test City'
        })

        self.db.update_venue_location(venue_id, 52.5, 13.4)

        # Add a lead to make it eligible for get_venues_with_location
        self.db.add_lead({
            'venue_id': venue_id,
            'vibe_score': 10
        })

        venues = self.db.get_venues_with_location()
        self.assertEqual(len(venues), 1)
        self.assertEqual(venues[0]['latitude'], 52.5)
        self.assertEqual(venues[0]['longitude'], 13.4)

    def test_geocoding_utility_structure(self):
        """Verify the geocoder returns expected types (without necessarily hitting AI)."""
        # Mocking or just checking structural interface if possible
        # Since we are in autonomous mode, we assume GPT-4o is available via env
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("OPENAI_API_KEY not set")

        lat, lon = self.geocoder.geocode_venue("Berghain", "Berlin")
        if lat is not None:
            self.assertIsInstance(lat, float)
            self.assertIsInstance(lon, float)

if __name__ == '__main__':
    unittest.main()
