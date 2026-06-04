import unittest
import os
import shutil
import tempfile
import subprocess
import sqlite3
import json
from sync_repo import sync

class TestCrossBranchConsistency(unittest.TestCase):
    """
    Integration test to verify that the synchronization protocol maintains
    data structure consistency (schema and config) across multiple branches.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)

        # 1. Initialize Git Repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)

        # 2. Setup standard structure
        os.makedirs("database")
        os.makedirs("src")

        # Create a dummy VERSION.md
        with open("VERSION.md", "w") as f: f.write("1.1.3")

        # Create a basic schema.sql
        self.base_schema = "CREATE TABLE test (id TEXT PRIMARY KEY, val TEXT);"
        with open("database/schema.sql", "w") as f: f.write(self.base_schema)

        # Create a basic config.json
        self.base_config = {"key1": "val1"}
        with open("database/config.json", "w") as f: json.dump(self.base_config, f)

        # Commit initial state to main
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial Commit"], capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], capture_output=True)

    def tearDown(self):
        # Return to project root
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.rmtree(self.test_dir)

    def test_schema_and_config_merging_consistency(self):
        """
        Simulate Branch A (Schema change) and Branch B (Config change).
        Reconcile via Sync and verify main has both.
        """
        # 1. Create Branch A: Change Schema
        subprocess.run(["git", "checkout", "-b", "feature/schema-change"], capture_output=True)
        new_schema = self.base_schema + "\nALTER TABLE test ADD COLUMN branch_a TEXT;"
        with open("database/schema.sql", "w") as f: f.write(new_schema)
        subprocess.run(["git", "add", "database/schema.sql"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Branch A: Update Schema"], capture_output=True)
        subprocess.run(["git", "checkout", "main"], capture_output=True)

        # 2. Create Branch B: Change Config
        subprocess.run(["git", "checkout", "-b", "feature/config-change"], capture_output=True)
        new_config = self.base_config.copy()
        new_config["branch_b_key"] = "branch_b_val"
        with open("database/config.json", "w") as f: json.dump(new_config, f)
        subprocess.run(["git", "add", "database/config.json"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Branch B: Update Config"], capture_output=True)
        subprocess.run(["git", "checkout", "main"], capture_output=True)

        # 3. Run Sync Protocol (Mocking the remote/upstream parts)
        from src.db_manager import DatabaseManager
        test_db = DatabaseManager(db_path=os.path.join(self.test_dir, "database/outreach.db"))

        from unittest.mock import patch, MagicMock
        with patch('sync_repo.run_command') as mock_run:
            # We allow real git commands for local operations but intercept push/remote
            def side_effect(command, cwd=None):
                cmd_str = " ".join(command)
                if "push" in cmd_str or "fetch" in cmd_str or "remote" in cmd_str or "rev-parse origin" in cmd_str:
                    # Return local hash for remote to satisfy consistency check
                    if "rev-parse" in cmd_str:
                         lh = subprocess.run(["git", "rev-parse", "main"], capture_output=True, text=True).stdout.strip()
                         return MagicMock(returncode=0, stdout=lh)
                    return MagicMock(returncode=0, stdout="main")
                return subprocess.run(command, capture_output=True, text=True, cwd=cwd)

            mock_run.side_effect = side_effect

            # Since sync() discovers local branches, it should find both features
            # and merge them into main.
            with patch.dict(os.environ, {"GIT_SYNC_RUNNING": "0"}):
                with patch('sync_repo.validate_system', return_value=True):
                    with patch('sync_repo.db', test_db):
                        sync()

        # 4. Verify main has integrated both changes
        subprocess.run(["git", "checkout", "main"], capture_output=True)

        with open("database/schema.sql", "r") as f:
            integrated_schema = f.read()
            self.assertIn("branch_a", integrated_schema)

        with open("database/config.json", "r") as f:
            integrated_config = json.load(f)
            self.assertIn("branch_b_key", integrated_config)

        print("\n[CONSISTENCY TEST] Cross-branch data integrity verified.")

if __name__ == "__main__":
    unittest.main()
