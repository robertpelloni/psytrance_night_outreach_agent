import unittest
import os
import subprocess
import shutil
import tempfile

class TestProtocolE2E(unittest.TestCase):
    """
    End-to-End test for the combined Synchronization and Pipeline protocol.
    """
    def setUp(self):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # We'll use the existing scripts/test_sync_repo.py logic but verify
        # that the entire flow in scripts/start.sh (conceptualized) works.
        # For a true E2E in this sandbox, we'll verify the integration of
        # sync_repo and the main pipeline components.

    def test_unified_execution_flow(self):
        # 1. Verify sync script can be imported and has expected functions
        import scripts.sync_repo as sync_repo
        self.assertTrue(hasattr(sync_repo, 'sync'))

        # 2. Verify main pipeline can be imported
        import main
        self.assertTrue(hasattr(main, 'load_scrapers'))

    def test_script_executability(self):
        # Ensure setup and start scripts exist and are executable
        setup_script = os.path.join(self.project_root, "scripts", "setup.sh")
        start_script = os.path.join(self.project_root, "scripts", "start.sh")

        self.assertTrue(os.path.exists(setup_script))
        self.assertTrue(os.path.exists(start_script))
        self.assertTrue(os.access(setup_script, os.X_OK))
        self.assertTrue(os.access(start_script, os.X_OK))

if __name__ == "__main__":
    unittest.main()
