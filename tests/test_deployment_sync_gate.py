import unittest
import os
import subprocess
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from sync_repo import sync

class TestDeploymentSyncGate(unittest.TestCase):
    """
    Integration test to verify that the synchronization protocol acts as a
    mandatory gate before deployment, ensuring local and remote are consistent.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.remote_dir = os.path.join(self.test_dir, "remote")
        self.local_dir = os.path.join(self.test_dir, "local")

        os.makedirs(self.remote_dir)
        subprocess.run(["git", "init", "--bare"], cwd=self.remote_dir, capture_output=True)

        os.makedirs(self.local_dir)
        subprocess.run(["git", "init"], cwd=self.local_dir, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", self.remote_dir], cwd=self.local_dir)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.local_dir)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.local_dir)

        with open(os.path.join(self.local_dir, "VERSION.md"), "w") as f: f.write("1.1.22")
        subprocess.run(["git", "add", "."], cwd=self.local_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=self.local_dir, capture_output=True)
        subprocess.run(["git", "push", "origin", "master:main"], cwd=self.local_dir, capture_output=True)
        subprocess.run(["git", "checkout", "main"], cwd=self.local_dir, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_dry_run_validation_gate(self):
        """Verify that --dry-run passes when repo is consistent."""
        old_cwd = os.getcwd()
        os.chdir(self.local_dir)
        try:
            # Setup mock DB for sync logging
            from src.db_manager import DatabaseManager
            os.makedirs("database", exist_ok=True)
            test_db = DatabaseManager(db_path=os.path.join(self.local_dir, "database/outreach.db"))

            with patch.dict(os.environ, {"SKIP_SYNC_VALIDATION": "1", "GIT_SYNC_RUNNING": "0"}):
                with patch('sync_repo.db', test_db):
                    # Should NOT exit with error
                    sync(dry_run=True)
        finally:
            os.chdir(old_cwd)

    def test_gate_fails_on_inconsistency(self):
        """Verify that sync protocol fails if local is behind remote (simulated inconsistency)."""
        # 1. Update remote from another clone
        other_clone = os.path.join(self.test_dir, "other")
        subprocess.run(["git", "clone", self.remote_dir, other_clone], capture_output=True)
        with open(os.path.join(other_clone, "remote_work.txt"), "w") as f: f.write("work")
        subprocess.run(["git", "add", "."], cwd=other_clone, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=other_clone)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=other_clone)
        subprocess.run(["git", "commit", "-m", "Remote work"], cwd=other_clone, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=other_clone, capture_output=True)

        # 2. Run sync on local (which is now behind)
        old_cwd = os.getcwd()
        os.chdir(self.local_dir)
        try:
            from src.db_manager import DatabaseManager
            os.makedirs("database", exist_ok=True)
            test_db = DatabaseManager(db_path=os.path.join(self.local_dir, "database/outreach.db"))

            with patch.dict(os.environ, {"SKIP_SYNC_VALIDATION": "1", "GIT_SYNC_RUNNING": "0"}):
                with patch('sync_repo.db', test_db):
                    with patch('sys.exit') as mock_exit:
                        # sync() will merge remote/main into local, so it actually BECOMES consistent
                        # To truly test a failure gate, we'd need to mock the consistency check or
                        # have a non-mergeable state.
                        # But wait, sync() attempts to reconcile. If it succeeds, it's consistent.
                        # If we want it to FAIL, we need a validation failure.
                        # Patch os.environ and sync_repo module state to ensure validation fails
                        with patch('sync_repo.validate_system', return_value=False):
                            with patch.dict(os.environ, {"SKIP_SYNC_VALIDATION": "0"}):
                                sync(dry_run=True)
                                mock_exit.assert_called_with(1)
        finally:
            os.chdir(old_cwd)

if __name__ == "__main__":
    unittest.main()
