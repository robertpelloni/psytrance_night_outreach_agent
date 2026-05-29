import unittest
import os
import shutil
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

class TestSyncSafetyGates(unittest.TestCase):
    """
    Verifies that the synchronization protocol protects the main branch
    by aborting the push if system validation fails.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.remote_dir = os.path.join(self.test_dir, "remote")
        self.local_dir = os.path.join(self.test_dir, "local")

        os.makedirs(self.remote_dir, exist_ok=True)
        os.makedirs(self.local_dir, exist_ok=True)

        subprocess.run(["git", "init", "--bare"], cwd=self.remote_dir, capture_output=True)
        subprocess.run(["git", "init"], cwd=self.local_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.local_dir)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.local_dir)
        subprocess.run(["git", "remote", "add", "origin", self.remote_dir], cwd=self.local_dir)

        os.chdir(self.local_dir)
        with open("VERSION.md", "w") as f: f.write("1.1.20")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True)

    def tearDown(self):
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.rmtree(self.test_dir)

    @patch('sync_repo.validate_system')
    def test_sync_aborts_on_validation_failure(self, mock_validate):
        from src.db_manager import DatabaseManager
        test_db = DatabaseManager(db_path=os.path.join(self.local_dir, "database/outreach.db"))

        # 1. Setup: Validation will fail
        mock_validate.return_value = False

        # 2. Add some local work
        with open("new_work.txt", "w") as f: f.write("work")
        subprocess.run(["git", "add", "new_work.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "New local work"], capture_output=True)

        # 3. Run Sync (Expected to exit with 1 due to validation failure)
        import sync_repo
        # We patch sys.exit to avoid stopping the test runner
        # We also clear SKIP_SYNC_VALIDATION to ensure the gate is active
        with patch('sys.exit') as mock_exit:
            with patch.dict(os.environ, {"GIT_SYNC_RUNNING": "0", "SKIP_SYNC_VALIDATION": "0"}):
                with patch('sync_repo.db', test_db):
                    sync_repo.sync()
                    mock_exit.assert_called_with(1)

        # 4. Verify: Remote main should NOT have the new work
        remote_res = subprocess.run(["git", "ls-tree", "-r", "main", "--name-only"], cwd=self.remote_dir, capture_output=True, text=True)
        self.assertNotIn("new_work.txt", remote_res.stdout, "Safety gate failed! Pushed invalid code to remote.")

if __name__ == "__main__":
    unittest.main()
