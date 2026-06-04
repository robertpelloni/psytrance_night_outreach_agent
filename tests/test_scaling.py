import unittest
from src.db_manager import DatabaseManager
from src.config_manager import ConfigManager
import os

class TestScaling(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.config = ConfigManager()

    def test_city_hub_expansion(self):
        # Verify at least 10 cities are configured
        cities = self.config.get("cities")
        self.assertGreaterEqual(len(cities), 10)
        print(f"[SCALING TEST] Verified {len(cities)} target cities.")

    def test_processing_resume(self):
        # Verify processing log exists
        city = "London"
        self.db.mark_city_processed(city, "COMPLETED")
        self.assertTrue(self.db.is_city_processed(city))
        print(f"[SCALING TEST] Verified resume capability for {city}.")

if __name__ == "__main__":
    unittest.main()
