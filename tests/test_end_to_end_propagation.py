import unittest
import os
import shutil
import tempfile
import subprocess
from sync_repo import sync
from unittest.mock import patch

class TestEndToEndPropagation(unittest.TestCase):
    """
    Validates that features propagate from feature branches to main
    correctly using the full synchronization protocol.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.remote_dir = os.path.join(self.test_dir, "remote")
        self.local_dir = os.path.join(self.test_dir, "local")

        os.makedirs(self.remote_dir, exist_ok=True)
        os.makedirs(self.local_dir, exist_ok=True)

        # Setup Bare Remote
        subprocess.run(["git", "init", "--bare"], cwd=self.remote_dir, capture_output=True)

        # Setup Local
        subprocess.run(["git", "init"], cwd=self.local_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.local_dir)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.local_dir)
        subprocess.run(["git", "remote", "add", "origin", self.remote_dir], cwd=self.local_dir)

        # Initial Commit
        os.chdir(self.local_dir)
        os.makedirs("database")
        with open("VERSION.md", "w") as f: f.write("1.1.14")

        # Use real schema to satisfy DatabaseManager
        schema_src = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "database/schema.sql"))
        with open(schema_src, "r") as f:
            schema_content = f.read()
        with open("database/schema.sql", "w") as f:
            f.write(schema_content)

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True)

    def tearDown(self):
        # Return to real project root
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.rmtree(self.test_dir)

    def test_feature_propagation(self):
        # 1. Create Feature Branch
        subprocess.run(["git", "checkout", "-b", "feature/new-widget"], capture_output=True)
        with open("widget.py", "w") as f:
            f.write("print('Hello Widget')")
        subprocess.run(["git", "add", "widget.py"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add Widget"], capture_output=True)

        # 2. Back to main
        subprocess.run(["git", "checkout", "main"], capture_output=True)

        from src.db_manager import DatabaseManager
        test_db = DatabaseManager(db_path=os.path.join(self.local_dir, "database/outreach.db"))

        # 3. Trigger Sync
        with patch.dict(os.environ, {"SKIP_SYNC_VALIDATION": "1", "GIT_SYNC_RUNNING": "0"}):
            import sync_repo
            with patch('sync_repo.db', test_db):
                sync_repo.sync()

        # 4. Verify Widget propagated to main
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        self.assertTrue(os.path.exists("widget.py"), "Feature did not propagate to main!")

        # 5. Verify Feature branch is updated (reverse merge)
        subprocess.run(["git", "checkout", "feature/new-widget"], capture_output=True)
        # Add a dummy commit to main to test reverse merge
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        with open("main_update.txt", "w") as f: f.write("main")
        subprocess.run(["git", "add", "main_update.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Main update"], capture_output=True)

        with patch.dict(os.environ, {"SKIP_SYNC_VALIDATION": "1", "GIT_SYNC_RUNNING": "0"}):
            import sync_repo
            with patch('sync_repo.db', test_db):
                sync_repo.sync()

        subprocess.run(["git", "checkout", "feature/new-widget"], capture_output=True)
        self.assertTrue(os.path.exists("main_update.txt"), "Main updates did not propagate back to feature branch!")

if __name__ == "__main__":
    unittest.main()
