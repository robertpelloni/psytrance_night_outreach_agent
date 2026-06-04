import unittest
import os
import shutil
import tempfile
import subprocess
from sync_repo import sync
from unittest.mock import patch, MagicMock

class TestDistributedSync(unittest.TestCase):
    """
    Integration test simulating two independent autonomous actors
    modifying the same repository concurrently.
    """
    def setUp(self):
        self.test_root = tempfile.mkdtemp()
        self.remote_dir = os.path.join(self.test_root, "remote")
        self.agent_a_dir = os.path.join(self.test_root, "agent_a")
        self.agent_b_dir = os.path.join(self.test_root, "agent_b")

        # 1. Initialize Central Remote
        os.makedirs(self.remote_dir, exist_ok=True)
        subprocess.run(["git", "init", "--bare"], cwd=self.remote_dir, capture_output=True)

        # 2. Setup Agent A
        os.makedirs(self.agent_a_dir, exist_ok=True)
        subprocess.run(["git", "init"], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Agent A"], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "a@test.com"], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", self.remote_dir], cwd=self.agent_a_dir, capture_output=True)

        os.makedirs(os.path.join(self.agent_a_dir, "database"), exist_ok=True)
        with open(os.path.join(self.agent_a_dir, "VERSION.md"), "w") as f: f.write("1.1.10")
        subprocess.run(["git", "add", "."], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=self.agent_a_dir, capture_output=True)

        # 3. Setup Agent B
        subprocess.run(["git", "clone", self.remote_dir, self.agent_b_dir], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Agent B"], cwd=self.agent_b_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "b@test.com"], cwd=self.agent_b_dir, capture_output=True)

    def tearDown(self):
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.rmtree(self.test_root)

    @patch('sync_repo.ai.resolve_merge_conflict')
    def test_distributed_reconciliation(self, mock_resolve):
        """
        Scenario:
        1. Agent A pushes a new feature file.
        2. Agent B (local) creates a different file on a feature branch.
        3. Agent B runs sync.
        4. Verify Agent B reconciles A's changes AND merges local feature.
        """
        mock_resolve.return_value = "RESOLVED_CONTENT"

        # 1. Agent A pushes change
        with open(os.path.join(self.agent_a_dir, "agent_a_work.txt"), "w") as f:
            f.write("A's contribution")
        subprocess.run(["git", "add", "."], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Work from A"], cwd=self.agent_a_dir, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=self.agent_a_dir, capture_output=True)

        # 2. Agent B works locally on feature branch
        os.chdir(self.agent_b_dir)
        subprocess.run(["git", "checkout", "-b", "feature/agent-b-task"], capture_output=True)
        with open("agent_b_work.txt", "w") as f:
            f.write("B's contribution")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Work from B"], capture_output=True)
        subprocess.run(["git", "checkout", "main"], capture_output=True)

        # 3. Agent B runs Sync Protocol
        # Setup mock DB for sync logging
        from src.db_manager import DatabaseManager
        os.makedirs("database", exist_ok=True)
        test_db = DatabaseManager(db_path=os.path.join(self.agent_b_dir, "database/outreach.db"))

        with patch.dict(os.environ, {"SKIP_SYNC_VALIDATION": "1", "GIT_SYNC_RUNNING": "0"}):
            with patch('sync_repo.db', test_db):
                sync()

        # 4. Verifications
        self.assertTrue(os.path.exists("agent_a_work.txt"), "B failed to pull A's changes!")
        self.assertTrue(os.path.exists("agent_b_work.txt"), "B failed to merge local feature!")

        # Verify remote main was updated by B's sync
        subprocess.run(["git", "fetch", "origin"], capture_output=True)
        remote_ls = subprocess.run(["git", "ls-tree", "-r", "origin/main", "--name-only"], capture_output=True, text=True).stdout
        self.assertIn("agent_b_work.txt", remote_ls)

        print("\n[DISTRIBUTED SYNC TEST] Multi-agent reconciliation verified.")

if __name__ == "__main__":
    unittest.main()
