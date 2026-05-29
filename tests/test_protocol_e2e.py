import unittest
import os
import subprocess
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from src.db_manager import DatabaseManager
import sync_repo
import main

class TestProtocolE2E(unittest.TestCase):
    """
    End-to-End test for the combined Synchronization and Pipeline protocol.
    Verifies that the sync state and pipeline execution are seamlessly integrated.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "database"))
        os.makedirs(os.path.join(self.test_dir, "src", "scrapers"))

        # Setup mock git environment
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        with open("VERSION.md", "w") as f: f.write("1.1.22")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], capture_output=True)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    @patch('sync_repo.run_command')
    @patch('main.load_scrapers')
    @patch('src.scrapers.base_scraper.ContactExtractor.scrape_website')
    @patch('src.ai_engine.AIEngine.vibe_check')
    @patch('src.ai_engine.AIEngine.extract_venue_traits')
    @patch('src.ai_engine.AIEngine.generate_pitch')
    @patch('src.config_manager.ConfigManager.get')
    def test_seamless_integration(self, mock_config, mock_pitch, mock_traits, mock_vibe, mock_scrape, mock_load_scrapers, mock_sync_run):
        # 1. Setup Mock Data
        def config_side_effect(key):
            vals = {
                "cities": ["Test City"],
                "vibe_threshold": 7,
                "auto_approve_threshold": 11 # Higher than our score to stay PENDING_REVIEW
            }
            return vals.get(key)

        mock_config.side_effect = config_side_effect
        mock_vibe.return_value = {"vibe_score": 10, "justification": "E2E OK"}
        mock_scrape.return_value = {"emails": ["test@v1.test"], "instagrams": ["v1_insta"], "about_text": "Vibe text"}
        mock_traits.return_value = '{"sound": "Funktion-One"}'
        mock_pitch.return_value = "Test Pitch"

        class MockScraper:
            def search_venues(self, city):
                return [{
                    'id': 'v1', 'name': 'V1', 'city': city,
                    'website': 'http://v1.test', 'raw_about_text': 'Vibe'
                }]
        mock_load_scrapers.return_value = [MockScraper()]
        mock_sync_run.return_value = MagicMock(returncode=0, stdout="main")

        # 2. Setup Database with schema
        db_path = os.path.join(self.test_dir, "database/outreach.db")
        schema_path = os.path.join(self.old_cwd, "database/schema.sql")
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            with open(schema_path, "r") as f:
                conn.executescript(f.read())

        test_db = DatabaseManager(db_path=db_path)

        # 3. Run Sync Protocol
        print("\n[E2E] Running Sync Protocol...")
        with patch('sync_repo.db', test_db):
            with patch('sync_repo.validate_system', return_value=True):
                sync_repo.sync()

        # 4. Run Main Outreach Pipeline
        print("[E2E] Running Main Pipeline...")
        with patch('main.DatabaseManager', return_value=test_db):
            with patch('src.outreach_engine.DatabaseManager', return_value=test_db):
                with patch('src.follow_up_engine.DatabaseManager', return_value=test_db):
                    with patch('src.geocoding.GeocodingUtility.geocode_venue', return_value=(52.5, 13.4)):
                         main.main()

        # 5. Verify Integration Results
        print("[E2E] Verifying integration results...")

        # Check System Logs for Pipeline Success
        logs = test_db.get_latest_system_logs()
        self.assertTrue(any(log['component'] == 'PIPELINE' and log['status'] == 'SUCCESS' for log in logs))

        # Check Venue Enrichment (Geocoding + Traits)
        venue = test_db.get_venue('v1')
        self.assertIsNotNone(venue)
        self.assertEqual(venue['latitude'], 52.5)
        self.assertEqual(venue['longitude'], 13.4)
        self.assertEqual(venue['extracted_traits'], '{"sound": "Funktion-One"}')

        # Check Lead Creation
        lead = test_db.get_lead_by_venue_id('v1')
        self.assertIsNotNone(lead)
        self.assertEqual(lead['vibe_score'], 10)
        self.assertEqual(lead['pipeline_status'], 'PENDING_REVIEW')

    def test_script_executability(self):
        # Ensure setup and start scripts exist and are executable
        project_root = self.old_cwd
        setup_script = os.path.join(project_root, "setup.sh")
        start_script = os.path.join(project_root, "start.sh")

        self.assertTrue(os.path.exists(setup_script))
        self.assertTrue(os.path.exists(start_script))
        self.assertTrue(os.access(setup_script, os.X_OK))
        self.assertTrue(os.access(start_script, os.X_OK))

if __name__ == "__main__":
    unittest.main()
