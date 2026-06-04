import unittest
from unittest.mock import patch, MagicMock
from src.dashboard.app import app
from src.db_manager import DatabaseManager
import os
import tempfile
import shutil

class TestReplyDispatch(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_dispatch.db")
        self.db = DatabaseManager(db_path=self.db_path)

        # Setup mock venue, lead, contact, and reply
        self.db.add_venue({'id': 'v1', 'name': 'Dispatch Venue', 'city': 'Dispatch City'})
        self.db.add_contact({'venue_id': 'v1', 'email': 'test@dispatch.test'})
        self.db.add_lead({
            'venue_id': 'v1',
            'vibe_score': 10,
            'qualification_justification': 'Justification',
            'generated_pitch': 'Original Pitch',
            'pipeline_status': 'SENT'
        })
        self.db.add_reply(1, "Interested content", sentiment='INTERESTED', draft_response='AI Draft')

        self.app = app.test_client()
        # Patch the global db instance in app.py
        self.patcher = patch('src.dashboard.app.db', self.db)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir)

    @patch('src.dashboard.app.mailer.send_email')
    def test_send_reply_success(self, mock_send):
        mock_send.return_value = True

        response = self.app.post('/send_reply/1', data={'reply_content': 'Edited AI Draft'})

        self.assertEqual(response.status_code, 302) # Redirects to history
        self.assertTrue(mock_send.called)
        args, kwargs = mock_send.call_args
        self.assertEqual(args[0], 'test@dispatch.test')
        self.assertIn('Edited AI Draft', args[2])

        # Check system logs
        logs = self.db.get_latest_system_logs()
        self.assertTrue(any("Sent manual reply" in log['message'] for log in logs))

if __name__ == "__main__":
    unittest.main()
