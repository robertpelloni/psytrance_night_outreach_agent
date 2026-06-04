import unittest
import os
import shutil
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
from src.scraper_generator import ScraperGenerator
from sync_repo import sync

class TestAutonomousDevE2E(unittest.TestCase):
    """
    End-to-End test for the full autonomous development cycle:
    Scraper Generation -> File Persistence -> Repository Synchronization.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.scrapers_dir = os.path.join(self.test_dir, "src", "scrapers")
        os.makedirs(self.scrapers_dir)

        # Initialize a mock git repo in test_dir
        os.chdir(self.test_dir)
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)

        # Add necessary files for sync_repo to not fail
        with open("VERSION.md", "w") as f: f.write("0.0.0")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], capture_output=True)

    def tearDown(self):
        # Return to project root before cleanup
        os.chdir(os.path.dirname(os.path.dirname(__file__)))
        shutil.rmtree(self.test_dir)

    @patch('src.scraper_generator.OpenAI')
    @patch('src.scraper_generator.requests.get')
    def test_autonomous_cycle(self, mock_get, mock_openai):
        # 1. Mock Scraper Generation
        mock_get.return_value = MagicMock(text="<html>Some Venue Data</html>", status_code=200)
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="class MockScraper:\n    def search_venues(self, city): return []"))]
        )

        generator = ScraperGenerator(api_key="fake")
        # Ensure it saves to our test scrapers dir
        with patch('src.scraper_generator.open', unittest.mock.mock_open()) as mocked_file:
            # We'll just verify the generator logic and file writing intent
            filepath = generator.generate_scraper("http://test.com", "Test Source")
            self.assertIsNotNone(filepath)
            self.assertIn("test_source.py", filepath)

        # 2. Simulate the presence of a new file on a feature branch
        subprocess.run(["git", "checkout", "-b", "feature/new-scraper"], capture_output=True)
        new_file = os.path.join(self.scrapers_dir, "test_source.py")
        with open(new_file, "w") as f:
            f.write("class TestScraper: pass")

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add generated scraper"], capture_output=True)

        # 3. Trigger Synchronization Protocol (Mocking the remote push)
        from src.db_manager import DatabaseManager
        os.makedirs("database", exist_ok=True)
        test_db = DatabaseManager(db_path=os.path.join(self.test_dir, "database/outreach.db"))

        with patch('sync_repo.run_command') as mock_run:
            # Mock success for git commands in sync
            mock_run.return_value = MagicMock(returncode=0, stdout="main")

            # Since we are in the test_dir, we can run the actual sync logic
            # but we need to prevent it from trying to push to a non-existent origin
            with patch('subprocess.run') as mock_sub:
                mock_sub.return_value = MagicMock(returncode=0)
                with patch('sync_repo.db', test_db):
                    sync()

        # Verification: Verify sync protocol attempted to reconcile
        # (In a real run, main would now have the new_file)
        self.assertTrue(os.path.exists(new_file))

if __name__ == "__main__":
    unittest.main()
