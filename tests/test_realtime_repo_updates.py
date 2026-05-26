import unittest
import os
import shutil
import tempfile
import subprocess
from sync_repo import sync
from unittest.mock import patch, MagicMock

class TestRealtimeRepoUpdates(unittest.TestCase):
    """
    Integration test to verify that the synchronization protocol correctly
    handles real-time updates from the remote repository.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.remote_dir = tempfile.mkdtemp()

        # 1. Initialize Bare Remote Repo
        subprocess.run(["git", "init", "--bare"], cwd=self.remote_dir, capture_output=True)

        # 2. Initialize Local Repo
        os.chdir(self.test_dir)
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", self.remote_dir], capture_output=True)

        # Initial commit to set up main
        os.makedirs("database")
        with open("VERSION.md", "w") as f: f.write("1.1.4")
        with open("database/schema.sql", "w") as f: f.write("CREATE TABLE test (id TEXT);")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], capture_output=True)
        # Use main as the default branch name
        subprocess.run(["git", "branch", "-M", "main"], capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True)

    def tearDown(self):
        # Return to project root
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.remote_dir)

    def test_realtime_upstream_sync(self):
        """
        Scenario:
        1. Remote main gets an update.
        2. Local feature branch has unique work.
        3. Local main runs sync.
        4. Verify local main has remote update AND feature is merged.
        """
        # 1. Simulate Remote Update
        temp_remote_clone = tempfile.mkdtemp()
        # Clone explicitly specifying main
        subprocess.run(["git", "clone", "-b", "main", self.remote_dir, temp_remote_clone], check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_remote_clone, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_remote_clone, check=True)

        with open(os.path.join(temp_remote_clone, "remote_update.txt"), "w") as f:
            f.write("Remote Change")
        subprocess.run(["git", "add", "."], cwd=temp_remote_clone, check=True)
        subprocess.run(["git", "commit", "-m", "Remote Update"], cwd=temp_remote_clone, check=True)
        # Push to the remote repo's main branch
        res = subprocess.run(["git", "push", "origin", "main"], cwd=temp_remote_clone, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Push to remote failed: {res.stderr}")
        shutil.rmtree(temp_remote_clone)

        # 2. Local Feature Update
        subprocess.run(["git", "checkout", "-b", "feature/local-work"], capture_output=True)
        with open("local_work.txt", "w") as f:
            f.write("Local Change")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Local Work"], capture_output=True)
        subprocess.run(["git", "checkout", "main"], capture_output=True)

        # 3. Run Sync Protocol
        # We need to ensure skip validation for the temp dir
        with patch.dict(os.environ, {"SKIP_SYNC_VALIDATION": "1"}):
            # Intercept consistency check to use our local 'origin'
            # The real sync script uses origin/main which exists in self.test_dir
            # because we did 'git fetch' (which is inside sync())
            from sync_repo import run_command
            # Ensure we are on main before sync
            subprocess.run(["git", "checkout", "main"], capture_output=True)
            sync()

        # 4. Verifications
        self.assertTrue(os.path.exists("remote_update.txt"), "Remote update was not pulled!")
        self.assertTrue(os.path.exists("local_work.txt"), "Local feature was not merged!")

        print("\n[REAL-TIME TEST] Protocol handled concurrent updates correctly.")

if __name__ == "__main__":
    unittest.main()
