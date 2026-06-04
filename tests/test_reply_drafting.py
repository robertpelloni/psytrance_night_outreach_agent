import unittest
from unittest.mock import patch, MagicMock
from src.sentiment_analyzer import SentimentAnalyzer
from src.db_manager import DatabaseManager
import os
import tempfile
import shutil

class TestReplyDrafting(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        # Initialize real DB manager to setup schema
        self.db = DatabaseManager(db_path=self.db_path)

        # Setup mock venue and lead
        self.db.add_venue({'id': 'v1', 'name': 'Test Venue', 'city': 'Test City'})
        self.db.add_lead({
            'venue_id': 'v1',
            'vibe_score': 10,
            'qualification_justification': 'Justification',
            'generated_pitch': 'Original Pitch',
            'pipeline_status': 'SENT'
        })
        self.lead_id = 1

        self.analyzer = SentimentAnalyzer(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('src.ai_engine.AIEngine.analyze_sentiment')
    @patch('src.ai_engine.AIEngine.generate_reply_draft')
    def test_interested_reply_generates_draft(self, mock_draft, mock_sentiment):
        mock_sentiment.return_value = 'INTERESTED'
        mock_draft.return_value = 'AI Drafted Reply'

        content = "We love your proposal! Tell us more."
        self.analyzer.process_new_reply(self.lead_id, content)

        replies = self.db.get_lead_replies(self.lead_id)
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0]['sentiment'], 'INTERESTED')
        self.assertEqual(replies[0]['draft_response'], 'AI Drafted Reply')

    @patch('src.ai_engine.AIEngine.analyze_sentiment')
    @patch('src.ai_engine.AIEngine.generate_reply_draft')
    def test_rejected_reply_no_draft(self, mock_draft, mock_sentiment):
        mock_sentiment.return_value = 'REJECTED'

        content = "Not interested."
        self.analyzer.process_new_reply(self.lead_id, content)

        replies = self.db.get_lead_replies(self.lead_id)
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0]['sentiment'], 'REJECTED')
        self.assertIsNone(replies[0]['draft_response'])

if __name__ == "__main__":
    unittest.main()
