import unittest
import os
import json
from src.dashboard.app import app
from unittest.mock import patch, MagicMock

class TestDashboardSync(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('src.dashboard.app.subprocess.run')
    def test_run_sync_endpoint(self, mock_run):
        # Mock successful sync
        mock_run.return_value = MagicMock(returncode=0, stdout="Sync Success", stderr="")

        response = self.app.post('/run_sync')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn("Sync Success", data['output'])

    @patch('src.dashboard.app.subprocess.run')
    def test_run_sync_error(self, mock_run):
        # Mock failed sync
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Git Error")

        response = self.app.post('/run_sync')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'error')
        self.assertIn("Git Error", data['output'])

if __name__ == "__main__":
    unittest.main()
