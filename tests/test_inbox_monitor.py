import unittest
from unittest.mock import MagicMock, patch
import os
import email
from src.inbox_monitor import InboxMonitor

class TestInboxMonitor(unittest.TestCase):
    def setUp(self):
        self.db_path = "database/test_inbox.db"
        # DatabaseManager will init schema
        from src.db_manager import DatabaseManager
        self.db = DatabaseManager(db_path=self.db_path)

        # Setup test data: a venue and a lead
        self.venue_id = "test-v-1"
        self.db.add_venue({
            'id': self.venue_id,
            'name': 'The Bunker',
            'city': 'Detroit'
        })
        self.db.add_contact({
            'venue_id': self.venue_id,
            'email': 'booking@thebunker.com'
        })
        self.db.add_lead({
            'venue_id': self.venue_id,
            'vibe_score': 10,
            'pipeline_status': 'SENT'
        })
        self.lead = self.db.get_lead_by_venue_id(self.venue_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    @patch('src.inbox_monitor.imaplib.IMAP4_SSL')
    @patch('src.ai_engine.AIEngine.analyze_sentiment')
    @patch('src.ai_engine.AIEngine.generate_reply_draft')
    @patch.dict(os.environ, {"IMAP_SERVER": "imap.test", "IMAP_USER": "test", "IMAP_PASSWORD": "password"})
    def test_fetch_and_match_by_email(self, mock_draft, mock_sentiment, mock_imap):
        # 1. Setup Mocks
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.side_effect = [
            ('OK', [b'123']), # search
            ('OK', [[None, b'From: booking@thebunker.com\r\nSubject: Re: Psytrance\r\n\r\nYes we are interested!']]) # fetch
        ]
        mock_sentiment.return_value = 'INTERESTED'
        mock_draft.return_value = "Drafted response"

        # 2. Run fetch
        monitor = InboxMonitor(db_path=self.db_path)
        count = monitor.fetch_new_replies()

        # 3. Verify
        self.assertEqual(count, 1)
        replies = self.db.get_lead_replies(self.lead['id'])
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0]['sentiment'], 'INTERESTED')
        self.assertEqual(replies[0]['draft_response'], "Drafted response")

    @patch('src.inbox_monitor.imaplib.IMAP4_SSL')
    @patch('src.ai_engine.AIEngine.analyze_sentiment')
    @patch('src.ai_engine.AIEngine.generate_reply_draft')
    @patch.dict(os.environ, {"IMAP_SERVER": "imap.test", "IMAP_USER": "test", "IMAP_PASSWORD": "password"})
    def test_match_by_venue_name_fallback(self, mock_draft, mock_sentiment, mock_imap):
        # Setup mock for name-based matching
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.side_effect = [
            ('OK', [b'124']), # search
            ('OK', [[None, b'From: unknown@gmail.com\r\nSubject: Booking inquiry\r\n\r\nHi, I saw your pitch for The Bunker.']]) # fetch
        ]
        mock_sentiment.return_value = 'INQUIRY'
        mock_draft.return_value = "Drafted response fallback"

        monitor = InboxMonitor(db_path=self.db_path)
        count = monitor.fetch_new_replies()

        self.assertEqual(count, 1)
        replies = self.db.get_lead_replies(self.lead['id'])
        self.assertEqual(len(replies), 1)

if __name__ == "__main__":
    unittest.main()
