import unittest
import os
from src.db_manager import DatabaseManager

class TestDatabaseIsolation(unittest.TestCase):
    def test_db_path_env_respect(self):
        custom_path = "database/custom_test.db"
        os.environ["DB_PATH"] = custom_path

        try:
            db = DatabaseManager()
            self.assertEqual(db.db_path, custom_path)

            # Verify explicit path overrides env
            explicit_path = "database/explicit.db"
            db_explicit = DatabaseManager(db_path=explicit_path)
            self.assertEqual(db_explicit.db_path, explicit_path)
        finally:
            if "DB_PATH" in os.environ:
                del os.environ["DB_PATH"]
            if os.path.exists(custom_path):
                os.remove(custom_path)
            if os.path.exists("database/explicit.db"):
                os.remove("database/explicit.db")

if __name__ == "__main__":
    unittest.main()
