import unittest
import os
from src.db_manager import DatabaseManager
from src.inbox_monitor import InboxMonitor
from unittest.mock import MagicMock, patch

class TestBounceDetection(unittest.TestCase):
    def setUp(self):
        self.db_path = 'database/test_bounce.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = DatabaseManager(db_path=self.db_path)
        self.inbox = InboxMonitor(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_is_bounce(self):
        self.assertTrue(self.inbox._is_bounce("mailer-daemon@google.com", "Delivery Failure", "Content"))
        self.assertTrue(self.inbox._is_bounce("someone@else.com", "Undelivered Mail Returned to Sender", "Content"))
        self.assertFalse(self.inbox._is_bounce("promoter@venue.com", "Re: Proposal", "I'm interested!"))

    @patch('src.inbox_monitor.InboxMonitor._match_lead_by_email')
    def test_handle_bounce(self, mock_match):
        # Setup venue and lead
        venue_id = "test-venue-1"
        self.db.add_venue({"id": venue_id, "name": "Test Venue", "city": "Detroit"})
        self.db.add_lead({"venue_id": venue_id, "pipeline_status": "SENT"})
        lead = self.db.get_lead_by_venue_id(venue_id)

        mock_match.return_value = {"id": lead['id'], "name": "Test Venue"}

        body = "Final-Recipient: rfc822; bounced@venue.com\nAction: failed\nStatus: 5.1.1"
        self.inbox._handle_bounce("Delivery Status Notification", body, 123)

        updated_lead = self.db.get_lead(lead['id'])
        self.assertEqual(updated_lead['pipeline_status'], 'BOUNCED')
        self.assertEqual(updated_lead['negotiation_status'], 'BOUNCED')

if __name__ == '__main__':
    unittest.main()
