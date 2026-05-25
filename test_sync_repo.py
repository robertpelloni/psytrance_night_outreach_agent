import unittest
import os
import shutil
import subprocess
import tempfile
from sync_repo import run_command
from unittest.mock import patch, MagicMock

class TestSyncRepo(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for our git test environment
        self.test_dir = tempfile.mkdtemp()
        self.remote_dir = os.path.join(self.test_dir, "remote")
        self.local_dir = os.path.join(self.test_dir, "local")

        # Initialize remote repo
        os.makedirs(self.remote_dir)
        run_command(["git", "init", "--bare"], cwd=self.remote_dir)

        # Initialize local repo and push initial commit to remote
        os.makedirs(self.local_dir)
        run_command(["git", "init"], cwd=self.local_dir)
        run_command(["git", "remote", "add", "origin", self.remote_dir], cwd=self.local_dir)

        with open(os.path.join(self.local_dir, "README.md"), "w") as f:
            f.write("# Initial Commit")

        run_command(["git", "add", "README.md"], cwd=self.local_dir)
        run_command(["git", "config", "user.name", "Test User"], cwd=self.local_dir)
        run_command(["git", "config", "user.email", "test@example.com"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Initial commit"], cwd=self.local_dir)
        run_command(["git", "push", "origin", "master:main"], cwd=self.local_dir)
        run_command(["git", "checkout", "-b", "main"], cwd=self.local_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_run_command(self):
        result = run_command(["echo", "hello"], cwd=self.local_dir)
        self.assertEqual(result.stdout.strip(), "hello")
        self.assertEqual(result.returncode, 0)

    def test_sync_logic_forward_merge(self):
        # Create a feature branch with a unique commit
        run_command(["git", "checkout", "-b", "feature-1"], cwd=self.local_dir)
        with open(os.path.join(self.local_dir, "feature.txt"), "w") as f:
            f.write("Feature work")
        run_command(["git", "add", "feature.txt"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Feature commit"], cwd=self.local_dir)
        run_command(["git", "push", "origin", "feature-1"], cwd=self.local_dir)

        # Go back to main
        run_command(["git", "checkout", "main"], cwd=self.local_dir)

        # Import sync and run it in the local dir context
        import sync_repo
        # We need to monkeypatch or ensure it uses our local_dir
        # Since sync() uses os.getcwd(), we'll change dir
        old_cwd = os.getcwd()
        os.chdir(self.local_dir)
        try:
            sync_repo.sync()
        finally:
            os.chdir(old_cwd)

        # Verify main has the feature commit
        res = run_command(["git", "log", "main", "--format=%s"], cwd=self.local_dir)
        self.assertIn("Feature commit", res.stdout)

    def test_sync_logic_reverse_merge(self):
        # Create a feature branch
        run_command(["git", "checkout", "-b", "feature-2"], cwd=self.local_dir)
        run_command(["git", "push", "origin", "feature-2"], cwd=self.local_dir)

        # Add a commit to main
        run_command(["git", "checkout", "main"], cwd=self.local_dir)
        with open(os.path.join(self.local_dir, "main_update.txt"), "w") as f:
            f.write("Main update")
        run_command(["git", "add", "main_update.txt"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Main update commit"], cwd=self.local_dir)
        run_command(["git", "push", "origin", "main"], cwd=self.local_dir)

        # Run sync
        import sync_repo
        old_cwd = os.getcwd()
        os.chdir(self.local_dir)
        try:
            sync_repo.sync()
        finally:
            os.chdir(old_cwd)

        # Verify feature-2 has the main update commit
        res = run_command(["git", "log", "feature-2", "--format=%s"], cwd=self.local_dir)
        self.assertIn("Main update commit", res.stdout)

    def test_sync_logic_conflict_handling_no_ai(self):
        # 1. Create a feature branch and modify README
        run_command(["git", "checkout", "-b", "conflict-branch-no-ai"], cwd=self.local_dir)
        with open(os.path.join(self.local_dir, "README.md"), "w") as f:
            f.write("# Conflict work")
        run_command(["git", "add", "README.md"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Feature conflict commit"], cwd=self.local_dir)
        run_command(["git", "push", "origin", "conflict-branch-no-ai"], cwd=self.local_dir)

        # 2. Go back to main and modify README differently
        run_command(["git", "checkout", "main"], cwd=self.local_dir)
        with open(os.path.join(self.local_dir, "README.md"), "w") as f:
            f.write("# Main conflict work")
        run_command(["git", "add", "README.md"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Main conflict commit"], cwd=self.local_dir)
        run_command(["git", "push", "origin", "main"], cwd=self.local_dir)

        # 3. Run sync with AI disabled (mock client to None)
        import sync_repo
        with patch('sync_repo.ai.client', None):
            old_cwd = os.getcwd()
            os.chdir(self.local_dir)
            try:
                sync_repo.sync()
            finally:
                os.chdir(old_cwd)

        # 4. Verify that main's content is still 'Main conflict work' (since merge aborted)
        curr_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.local_dir).stdout.strip()
        self.assertEqual(curr_branch, "main")

        with open(os.path.join(self.local_dir, "README.md"), "r") as f:
            content = f.read().strip()
        self.assertEqual(content, "# Main conflict work")

    @patch('sync_repo.ai.resolve_merge_conflict')
    def test_sync_logic_ai_conflict_resolution(self, mock_resolve):
        # Mock AI resolution
        mock_resolve.return_value = "# Resolved Content"

        # 1. Create conflict
        run_command(["git", "checkout", "-b", "conflict-branch-ai"], cwd=self.local_dir)
        with open(os.path.join(self.local_dir, "README.md"), "w") as f:
            f.write("# Feature work")
        run_command(["git", "add", "README.md"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Feature commit"], cwd=self.local_dir)
        run_command(["git", "push", "origin", "conflict-branch-ai"], cwd=self.local_dir)

        run_command(["git", "checkout", "main"], cwd=self.local_dir)
        with open(os.path.join(self.local_dir, "README.md"), "w") as f:
            f.write("# Main work")
        run_command(["git", "add", "README.md"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Main commit"], cwd=self.local_dir)

        # 2. Run sync
        import sync_repo
        old_cwd = os.getcwd()
        os.chdir(self.local_dir)
        try:
            sync_repo.sync()
        finally:
            os.chdir(old_cwd)

        # 3. Verify resolution
        with open(os.path.join(self.local_dir, "README.md"), "r") as f:
            content = f.read().strip()
        self.assertEqual(content, "# Resolved Content")

        # Verify it's committed
        res = run_command(["git", "log", "-1", "--format=%s"], cwd=self.local_dir)
        self.assertEqual(res.stdout.strip(), "Resolve merge conflicts via AI")

    def test_sync_logic_consistency_verification(self):
        # 1. Add unique commit to local main
        with open(os.path.join(self.local_dir, "consistency.txt"), "w") as f:
            f.write("Consistency check")
        run_command(["git", "add", "consistency.txt"], cwd=self.local_dir)
        run_command(["git", "commit", "-m", "Local main update"], cwd=self.local_dir)

        # 2. Run sync
        import sync_repo
        old_cwd = os.getcwd()
        os.chdir(self.local_dir)
        try:
            sync_repo.sync()
        finally:
            os.chdir(old_cwd)

        # 3. Verify local hash matches remote hash
        local_hash = run_command(["git", "rev-parse", "main"], cwd=self.local_dir).stdout.strip()
        remote_hash = run_command(["git", "rev-parse", "origin/main"], cwd=self.local_dir).stdout.strip()
        self.assertEqual(local_hash, remote_hash)

if __name__ == "__main__":
    unittest.main()
