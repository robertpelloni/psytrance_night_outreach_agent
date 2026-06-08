import unittest
import os
import shutil
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
from src.db_manager import DatabaseManager
from src.scraper_generator import ScraperGenerator
from sync_repo import sync
from main import main as run_pipeline

class TestAutonomousPipelineE2E(unittest.TestCase):
    """
    Master End-to-End test for the Autonomous Development Pipeline.
    Cycle: Code Gen -> Sync -> Execution -> Logging.
    """
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        self.scrapers_dir = os.path.join(self.test_dir, "src", "scrapers")
        os.makedirs(self.scrapers_dir)
        os.makedirs(os.path.join(self.test_dir, "database"))

        # Mock git env
        os.chdir(self.test_dir)
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)

        with open("VERSION.md", "w") as f: f.write("1.1.0")
        with open("database/schema.sql", "w") as f:
            f.write("""
CREATE TABLE IF NOT EXISTS venues (id TEXT PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL, website TEXT UNIQUE, google_rating REAL, tags TEXT, raw_about_text TEXT);
CREATE TABLE IF NOT EXISTS venue_contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, venue_id TEXT, email TEXT UNIQUE, phone TEXT, instagram_handle TEXT UNIQUE, booking_page_url TEXT, FOREIGN KEY(venue_id) REFERENCES venues(id));
CREATE TABLE IF NOT EXISTS outreach_leads (id INTEGER PRIMARY KEY AUTOINCREMENT, venue_id TEXT UNIQUE, vibe_score INTEGER, qualification_justification TEXT, generated_pitch TEXT, pipeline_status TEXT DEFAULT 'PENDING_QUALIFICATION', last_outreach_at TIMESTAMP, follow_up_count INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(venue_id) REFERENCES venues(id));
CREATE TABLE IF NOT EXISTS city_processing_log (city TEXT PRIMARY KEY, last_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status TEXT);
CREATE TABLE IF NOT EXISTS lead_replies (id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER, content TEXT NOT NULL, sentiment TEXT, received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(lead_id) REFERENCES outreach_leads(id));
CREATE TABLE IF NOT EXISTS system_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, component TEXT NOT NULL, status TEXT NOT NULL, message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            """)

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], capture_output=True)

    def tearDown(self):
        # Return to project root
        if hasattr(self, 'old_cwd'):
            os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    @patch('src.scraper_generator.OpenAI')
    @patch('src.ai_engine.OpenAI')
    @patch('src.mailer.smtplib.SMTP')
    @patch('src.config_manager.ConfigManager.load_config')
    def test_full_autonomous_cycle(self, mock_load_config, mock_smtp, mock_ai_openai, mock_gen_openai):
        # 1. Setup Config
        mock_load_config.return_value = {
            "cities": ["E2E City"],
            "vibe_threshold": 7,
            "auto_approve_threshold": 9
        }

        # 2. Simulate AI generating a new scraper
        mock_gen_client = MagicMock()
        mock_gen_openai.return_value = mock_gen_client
        mock_gen_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="""
import uuid
class E2EScraper:
    def search_venues(self, city):
        return [{
            'id': str(uuid.uuid4()),
            'name': 'E2E Venue',
            'city': city,
            'website': 'http://e2e.test',
            'raw_about_text': 'A test venue for E2E.'
        }]
"""))]
        )

        generator = ScraperGenerator(api_key="fake")
        # Fix path for generator in test context
        with patch('src.scraper_generator.open', unittest.mock.mock_open()) as mocked_file:
             filepath = generator.generate_scraper("http://e2e.test", "E2E Source")
             self.assertIn("e2e_source.py", filepath)

        # 3. Simulate code being "integrated" via Sync
        # We'll mock sync because we don't have a real remote
        from src.db_manager import DatabaseManager
        db_path_sync = os.path.join(self.test_dir, "database", "sync.db")
        db_sync = DatabaseManager(db_path=db_path_sync)

        with patch('sync_repo.run_command') as mock_sync_run:
            mock_sync_run.return_value = MagicMock(returncode=0, stdout="main")
            with patch('sync_repo.validate_system', return_value=True):
                with patch('sync_repo.db', db_sync):
                    sync()

        # 4. Run Main Pipeline (Simulated)
        # Mock AI vibe check for the venue found by our "generated" scraper
        mock_ai_client = MagicMock()
        mock_ai_openai.return_value = mock_ai_client
        mock_ai_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"vibe_score": 10, "justification": "E2E Match."}'))]
        )

        # Mock the scraper loading to find our "E2E" scraper
        with patch('main.load_scrapers') as mock_load:
            # Simulate what the generated scraper would return
            class MockScraper:
                def search_venues(self, city, query=None):
                    return [{
                        'id': 'e2e-id-123',
                        'name': 'E2E Venue',
                        'city': city,
                        'website': 'http://e2e.test',
                        'raw_about_text': 'A test venue for E2E.'
                    }]
            # Return as (query_scrapers, city_scrapers)
            mock_load.return_value = ([MockScraper()], [])

            # Run the pipeline with a temp DB
            db_path = os.path.join(self.test_dir, "database", "e2e.db")
            # We need to copy the real schema or just rely on DatabaseManager creating it
            # But DatabaseManager looks for 'database/schema.sql' relative to CWD
            with open("database/schema.sql", "w") as f:
                with open(os.path.join(os.path.dirname(__file__), "../database/schema.sql"), "r") as real_schema:
                    f.write(real_schema.read())

            with patch.dict(os.environ, {"OPENAI_API_KEY": "fake"}):
                with patch('src.db_manager.DatabaseManager.__init__', return_value=None) as mock_db_init:
                    # Manually setup the db instance to use our test path
                    with patch('src.db_manager.DatabaseManager._get_connection') as mock_conn:
                        import sqlite3
                        real_conn = sqlite3.connect(db_path)
                        mock_conn.side_effect = lambda: real_conn

                        # We need to ensure the schema is there
                        with open(os.path.join(os.path.dirname(__file__), "../database/schema.sql"), "r") as real_schema:
                            real_conn.executescript(real_schema.read())

                        # Re-patch the db manager in main.py to use our "real" mock
                        with patch('main.DatabaseManager') as mock_db_class:
                            # Create a real DatabaseManager but pointing to our db_path
                            from src.db_manager import DatabaseManager as RealDB
                            test_db = RealDB(db_path=db_path)
                            mock_db_class.return_value = test_db

                            # We also need to patch OutreachEngine, FollowUpEngine, OutreachPredictor, and AnalyticsEngine's DB
                            with patch('src.outreach_engine.DatabaseManager', return_value=test_db):
                                with patch('src.follow_up_engine.DatabaseManager', return_value=test_db):
                                    with patch('src.outreach_predictor.OutreachPredictor.__init__', autospec=True, return_value=None) as mock_pred_init:
                                        def pred_init_side_effect(self, db_path=None):
                                            self.db_path = db_path or 'database/outreach.db'
                                            from src.ai_engine import AIEngine
                                            self.ai = AIEngine()
                                        mock_pred_init.side_effect = pred_init_side_effect
                                        with patch('src.outreach_predictor.OutreachPredictor._get_connection', side_effect=lambda: sqlite3.connect(db_path)):
                                            with patch('src.analytics.AnalyticsEngine.__init__', autospec=True, return_value=None) as mock_anal_init:
                                                mock_anal_init.side_effect = lambda self, db_path=None: setattr(self, 'db_path', db_path or 'database/outreach.db')
                                                with patch('src.analytics.AnalyticsEngine._get_connection', side_effect=lambda: sqlite3.connect(db_path)):
                                                    run_pipeline()

        # 5. Verify results in DB and Logs
        db = DatabaseManager(db_path=db_path)
        self.assertTrue(db.venue_exists_by_name("E2E Venue", "E2E City"))

        logs = db.get_latest_system_logs()
        self.assertTrue(any(log['component'] == 'PIPELINE' and log['status'] == 'SUCCESS' for log in logs))

        print("\n[E2E] Autonomous Pipeline successfully integrated and verified.")

if __name__ == "__main__":
    unittest.main()
