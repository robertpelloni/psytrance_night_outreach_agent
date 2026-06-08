import unittest
from unittest.mock import patch, MagicMock
import main

def search_venues(city, query=None):
    return [{'id': f'v-{query}', 'name': f'V-{query}', 'city': city}]

class TestMultiGenreDiscovery(unittest.TestCase):
    @patch('main.load_scrapers')
    @patch('main.ConfigManager.get')
    @patch('main.DatabaseManager')
    @patch('main.AIEngine')
    @patch('main.GeocodingUtility')
    @patch('main.OutreachPredictor')
    def test_multi_genre_loop(self, mock_pred, mock_geo, mock_ai, mock_db_class, mock_config, mock_load):
        # 1. Setup Mock Config with multiple genres
        mock_config.side_effect = lambda k: {
            "cities": ["Test City"],
            "vibe_threshold": 7,
            "target_genres": ["techno", "psytrance"]
        }.get(k)

        # 2. Setup Mock Scraper
        # Using a function to ensure signature matching works
        mock_scraper = MagicMock()
        mock_scraper.search_venues = MagicMock(side_effect=search_venues)
        # Manually set signature since MagicMock might not copy it
        import inspect
        mock_scraper.search_venues.__signature__ = inspect.signature(search_venues)

        mock_load.return_value = ([mock_scraper], [])

        # 3. Setup Mock DB
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.is_city_processed.return_value = False
        mock_db.venue_exists_by_name.return_value = None
        mock_db.get_lead_by_venue_id.return_value = None

        # 4. Setup Mock AI
        mock_ai_inst = MagicMock()
        mock_ai.return_value = mock_ai_inst
        mock_ai_inst.vibe_check.return_value = {"vibe_score": 8, "justification": "OK"}
        mock_ai_inst.extract_venue_traits.return_value = "{}"

        # Mock Geocoder to return a tuple
        mock_geo_inst = MagicMock()
        mock_geo.return_value = mock_geo_inst
        mock_geo_inst.geocode_venue.return_value = (52.5, 13.4)

        # 5. Run Main
        with patch('sys.argv', ['main.py']):
            main.main()

        # 6. Verify Scraper called for BOTH genres
        # Note: build_search_queries now returns 2 queries per genre for non-Detroit cities
        # (underground {genre} club, {genre} venue)
        self.assertEqual(mock_scraper.search_venues.call_count, 4)
        calls = mock_scraper.search_venues.call_args_list

        # Verify queries - should contain techno and psytrance
        queries = [c[1].get('query', '') for c in calls]
        self.assertTrue(any("techno" in q for q in queries))
        self.assertTrue(any("psytrance" in q for q in queries))

        # 7. Verify AI called with correct genre context
        self.assertEqual(mock_ai_inst.vibe_check.call_count, 4)
        vibe_calls = mock_ai_inst.vibe_check.call_args_list

        genres_seen = [c[1].get('genre') for c in vibe_calls]
        self.assertIn("techno", genres_seen)
        self.assertIn("psytrance", genres_seen)

if __name__ == "__main__":
    unittest.main()
