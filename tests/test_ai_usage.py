import unittest
import os
from src.db_manager import DatabaseManager
from src.ai_engine import AIEngine
from unittest.mock import MagicMock, patch

class TestAIUsageTracking(unittest.TestCase):
    def setUp(self):
        self.db_path = 'database/test_usage.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = DatabaseManager(db_path=self.db_path)
        self.ai = AIEngine(api_key="fake_key")

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    @patch('src.db_manager.DatabaseManager')
    def test_log_usage(self, mock_db_class):
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        mock_response = MagicMock()
        mock_response.model = "gpt-4o"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        self.ai._log_usage(mock_response)

        mock_db.log_ai_usage.assert_called_with("gpt-4o", 100, 50, 150)

    def test_db_usage_retrieval(self):
        self.db.log_ai_usage("gpt-4o", 100, 50, 150)
        self.db.log_ai_usage("gpt-4o", 200, 100, 300)

        stats = self.db.get_ai_usage_stats(days=1)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]['model'], "gpt-4o")
        self.assertEqual(stats[0]['prompt'], 300)
        self.assertEqual(stats[0]['completion'], 150)
        self.assertEqual(stats[0]['total'], 450)

if __name__ == '__main__':
    unittest.main()
