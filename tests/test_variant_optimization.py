import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import main as run_pipeline
from src.db_manager import DatabaseManager

class TestVariantOptimization(unittest.TestCase):
    @patch('src.analytics.AnalyticsEngine.get_variant_stats')
    @patch('src.ai_engine.AIEngine.vibe_check')
    @patch('src.ai_engine.AIEngine.generate_pitch')
    @patch('src.db_manager.DatabaseManager.add_lead')
    @patch('src.config_manager.ConfigManager.get')
    @patch('main.load_scrapers')
    def test_variant_exploitation(self, mock_load, mock_get, mock_add_lead, mock_gen_pitch, mock_vibe, mock_stats):
        # Setup: Technical variant has 100% conversion, others 0%
        mock_stats.return_value = {
            "Professional": {"conversion_rate": 0, "sent": 10},
            "Underground": {"conversion_rate": 0, "sent": 10},
            "Technical": {"conversion_rate": 100, "sent": 10}
        }

        mock_load.return_value = [MagicMock(search_venues=lambda city, query=None: [{
            'id': 'test-v', 'name': 'Test', 'city': city, 'discovery_genre': 'techno'
        }])]

        def config_get_mock(key):
            if key == "cities": return ["TestCity"]
            if key == "target_genres": return ["techno"]
            return 5

        mock_get.side_effect = config_get_mock
        mock_vibe.return_value = {"vibe_score": 10, "justification": "Good"}

        # Patch random to always exploit (random.random() > epsilon)
        with patch('random.random', return_value=0.5): # Epsilon is 0.2
            # We need to mock more things to let main() run to the assignment part
            with patch('src.db_manager.DatabaseManager.is_city_processed', return_value=False):
                with patch('src.db_manager.DatabaseManager.venue_exists_by_name', return_value=None):
                    with patch('src.db_manager.DatabaseManager.add_venue'):
                        with patch('src.db_manager.DatabaseManager.get_lead_by_venue_id', return_value=None):
                            with patch('src.db_manager.DatabaseManager.mark_city_processed'):
                                with patch('src.outreach_engine.OutreachEngine.run_outreach_cycle'):
                                    with patch('src.follow_up_engine.FollowUpEngine.run_follow_up_cycle'):
                                        with patch('src.outreach_predictor.OutreachPredictor.predict_success_probability'):
                                            run_pipeline()

        # Verify Technical was chosen (exploitation)
        # Find the call where add_lead was called
        args, kwargs = mock_add_lead.call_args
        self.assertEqual(args[0]['pitch_variant'], "Technical")

if __name__ == "__main__":
    unittest.main()
