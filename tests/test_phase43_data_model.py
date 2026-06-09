import unittest
import os
import sqlite3
from src.db_manager import DatabaseManager

class TestPhase43DataModel(unittest.TestCase):
    def setUp(self):
        self.db_path = 'database/test_phase43.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_migration_and_new_columns(self):
        # 1. Create a legacy database without Phase 43 columns
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE venues (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                website TEXT UNIQUE,
                google_rating REAL,
                tags TEXT,
                raw_about_text TEXT,
                extracted_traits TEXT,
                latitude REAL,
                longitude REAL,
                image_url TEXT,
                visual_description TEXT
            )
        """)
        conn.close()

        # 2. Instantiate DatabaseManager (should trigger migrations)
        db = DatabaseManager(db_path=self.db_path)

        # 3. Verify columns exist
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(venues)")
            columns = [row[1] for row in cursor.fetchall()]

            expected_new_cols = ['address', 'phone', 'venue_type', 'capacity', 'neighborhood', 'source', 'discovered_at']
            for col in expected_new_cols:
                self.assertIn(col, columns)

    def test_add_venue_with_new_fields(self):
        db = DatabaseManager(db_path=self.db_path)
        venue_data = {
            'id': 'v-phase43',
            'name': 'Modern Club',
            'city': 'Detroit',
            'address': '123 Techno Way',
            'phone': '313-555-1234',
            'venue_type': 'club',
            'capacity': 500,
            'neighborhood': 'Corktown',
            'source': 'test_suite'
        }
        db.add_venue(venue_data)

        venue = db.get_venue('v-phase43')
        self.assertEqual(venue['address'], '123 Techno Way')
        self.assertEqual(venue['phone'], '313-555-1234')
        self.assertEqual(venue['venue_type'], 'club')
        self.assertEqual(venue['capacity'], 500)
        self.assertEqual(venue['neighborhood'], 'Corktown')
        self.assertEqual(venue['source'], 'test_suite')
        self.assertIsNotNone(venue['discovered_at'])

if __name__ == "__main__":
    unittest.main()
