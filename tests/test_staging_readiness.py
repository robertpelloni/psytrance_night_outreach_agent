import unittest
import os
import sqlite3
from src.db_manager import DatabaseManager

class TestStagingReadiness(unittest.TestCase):
    def test_environment_files(self):
        # Verify core execution scripts exist and are executable
        scripts = ['start.sh', 'setup.sh', 'sync_repo.py', 'deploy_staging.sh']
        for script in scripts:
            self.assertTrue(os.path.exists(script), f"Missing core script: {script}")
            if script.endswith('.sh'):
                self.assertTrue(os.access(script, os.X_OK), f"Script not executable: {script}")

    def test_database_connectivity(self):
        # Verify we can initialize a staging database
        db_path = 'database/staging_readiness.db'
        if os.path.exists(db_path): os.remove(db_path)

        db = DatabaseManager(db_path=db_path)
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_logs'")
            self.assertIsNotNone(cursor.fetchone(), "Database schema not initialized correctly")

        os.remove(db_path)

    def test_config_integrity(self):
        # Verify config exists and has required keys
        config_path = 'database/config.json'
        self.assertTrue(os.path.exists(config_path))
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.assertIn('cities', config)
            self.assertIn('vibe_threshold', config)

if __name__ == "__main__":
    unittest.main()
