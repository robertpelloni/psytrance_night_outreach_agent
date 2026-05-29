import unittest
import os
import shutil
import tempfile
import subprocess
import json
from sync_repo import sync
from unittest.mock import patch, MagicMock

class TestMultiBranchStress(unittest.TestCase):
    """
    Stress test to verify that the synchronization protocol correctly
    handles complex unification scenarios with 5+ branches.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)

        # 1. Initialize Git Repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Stress Test"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "stress@example.com"], capture_output=True)

        # 2. Setup standard structure
        os.makedirs("database")
        os.makedirs("src")
        with open("VERSION.md", "w") as f: f.write("1.1.7")
        with open("database/schema.sql", "w") as f: f.write("CREATE TABLE stress (id TEXT PRIMARY KEY);")
        with open("database/config.json", "w") as f: json.dump({"base": True}, f)

        # 3. Initialize DB within test_dir to prevent system_logs errors
        from src.db_manager import DatabaseManager
        self.test_db = DatabaseManager(db_path=os.path.join(self.test_dir, "database/outreach.db"))

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial Stress Setup"], capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], capture_output=True)

    def tearDown(self):
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.rmtree(self.test_dir)

    @patch('sync_repo.ai.resolve_merge_conflict')
    def test_multi_branch_unification(self, mock_resolve):
        # AI always resolves to a combined state for the test
        mock_resolve.return_value = "RESOLVED_CONTENT"

        # 1. Create 5 Feature Branches with unique work
        branches = ["feature/a", "feature/b", "feature/c", "feature/d", "feature/e"]
        for i, branch in enumerate(branches):
            subprocess.run(["git", "checkout", "-b", branch], capture_output=True)
            with open(f"work_{i}.txt", "w") as f:
                f.write(f"Work from {branch}")
            subprocess.run(["git", "add", "."], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Commit {branch}"], capture_output=True)
            subprocess.run(["git", "checkout", "main"], capture_output=True)

        # 2. Run Sync Protocol (Mocking the remote/upstream parts)
        with patch('sync_repo.run_command') as mock_run:
            def side_effect(command, cwd=None):
                cmd_str = " ".join(command)
                if "push" in cmd_str or "fetch" in cmd_str or "remote" in cmd_str or "rev-parse origin" in cmd_str:
                    if "rev-parse" in cmd_str:
                         lh = subprocess.run(["git", "rev-parse", "main"], capture_output=True, text=True).stdout.strip()
                         return MagicMock(returncode=0, stdout=lh)
                    return MagicMock(returncode=0, stdout="main")
                return subprocess.run(command, capture_output=True, text=True, cwd=cwd)
            mock_run.side_effect = side_effect

            with patch('sync_repo.validate_system', return_value=True):
                with patch('sync_repo.db', self.test_db):
                    sync()

        # 3. Verify main has integrated all unique files
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        for i in range(5):
            self.assertTrue(os.path.exists(f"work_{i}.txt"), f"Work from feature {i} missing!")

        print("\n[STRESS TEST] Multi-branch unification verified.")

if __name__ == "__main__":
    unittest.main()
