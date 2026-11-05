import unittest
import json
import time
from unittest.mock import patch, MagicMock
from src.dashboard.app import app
from src.db_manager import DatabaseManager

class TestBulkActions(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('src.dashboard.app.db')
    def test_bulk_action_missing_params(self, mock_db):
        res = self.client.post('/bulk_action', json={})
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn("error", data)

    @patch('src.dashboard.app.db')
    def test_bulk_action_reject(self, mock_db):
        res = self.client.post('/bulk_action', json={
            "action": "reject",
            "lead_ids": [101, 102]
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'processing')
        self.assertEqual(data['count'], 2)
        time.sleep(0.2)
        mock_db.update_lead_status.assert_any_call(101, 'REJECTED')
        mock_db.update_lead_status.assert_any_call(102, 'REJECTED')

    @patch('src.dashboard.app.mailer')
    @patch('src.dashboard.app.db')
    def test_bulk_action_approve(self, mock_db, mock_mailer):
        mock_db.get_lead.return_value = {
            'id': 201,
            'venue_id': 'v-201',
            'generated_pitch': 'Excited to pitch our psytrance night!'
        }
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ['booking@detroitclub.com']
        mock_conn.execute.return_value = mock_cursor
        mock_db._get_connection.return_value.__enter__.return_value = mock_conn
        mock_mailer.send_email.return_value = True

        res = self.client.post('/bulk_action', json={
            "action": "approve",
            "lead_ids": [201]
        })
        self.assertEqual(res.status_code, 200)
        time.sleep(0.3)
        mock_db.update_lead_status.assert_any_call(201, 'APPROVED', pitch='Excited to pitch our psytrance night!')
        mock_mailer.send_email.assert_called_once()
        mock_db.update_lead_status.assert_any_call(201, 'SENT')

if __name__ == '__main__':
    unittest.main()
