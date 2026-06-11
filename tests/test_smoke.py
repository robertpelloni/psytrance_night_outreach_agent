import os
import sys
import unittest
import shutil
import tempfile
from src.db_manager import DatabaseManager
from src.ai_engine import AIEngine
from src.outreach_engine import OutreachEngine
from src.follow_up_engine import FollowUpEngine
from src.config_manager import ConfigManager
from unittest.mock import patch, MagicMock

class SmokeTest(unittest.TestCase):
    """
    A comprehensive smoke test to verify that all system components
    (DB, AI, Outreach, Follow-up) are functioning properly together.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "smoke_test.db")
        self.config_path = os.path.join(self.test_dir, "config.json")

        # Initialize Config
        with open(self.config_path, "w") as f:
            f.write('{"cities": ["Test City"], "vibe_threshold": 7, "auto_approve_threshold": 9}')

        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('src.ai_engine.OpenAI')
    @patch('src.mailer.smtplib.SMTP')
    @patch('src.config_manager.ConfigManager.load_config')
    @patch('src.outreach_engine.time.sleep')
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "fake-key",
        "SMTP_SERVER": "smtp.test",
        "SMTP_USER": "test",
        "SMTP_PASSWORD": "test",
        "SENDER_EMAIL": "test@test.com"
    })
    def test_full_system_flow(self, mock_sleep, mock_load_config, mock_smtp, mock_openai):
        mock_load_config.return_value = {
            "cities": ["Test City"],
            "vibe_threshold": 7,
            "auto_approve_threshold": 9,
            "follow_up_days": 7,
            "max_follow_ups": 2
        }

        # 1. Add Venue
        venue_data = {
            'id': 'test-venue-1',
            'name': 'The Smoke Club',
            'city': 'Test City',
            'website': 'http://smoke.test',
            'google_rating': 4.5,
            'tags': 'techno, underground',
            'raw_about_text': 'A dark underground club.'
        }
        self.db.add_venue(venue_data)

        # 2. Add Contact
        self.db.add_contact({
            'venue_id': 'test-venue-1',
            'email': 'booking@smoke.test',
            'instagram_handle': 'smoke_club'
        })

        # 3. AI Vibe Check & Lead Generation
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"vibe_score": 10, "justification": "Perfect fit."}'))]
        )

        ai = AIEngine()
        vibe = ai.vibe_check(venue_data['name'], venue_data['raw_about_text'])

        lead_data = {
            'venue_id': 'test-venue-1',
            'vibe_score': vibe['vibe_score'],
            'qualification_justification': vibe['justification'],
            'generated_pitch': 'Hey, we love your club!',
            'pipeline_status': 'PENDING_REVIEW'
        }
        self.db.add_lead(lead_data)

        # 4. Outreach Cycle
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        outreach = OutreachEngine(db_path=self.db_path)
        with patch.object(outreach.config, 'get', return_value=9):
            outreach.run_outreach_cycle()

        lead = self.db.get_lead_by_venue_id('test-venue-1')
        self.assertEqual(lead['pipeline_status'], 'SENT')

        # 5. Follow-up Cycle
        follow_up = FollowUpEngine(db_path=self.db_path)
        with patch.object(follow_up.db, 'get_leads_eligible_for_follow_up', return_value=[lead]):
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content='Just following up!'))]
            )
            follow_up.run_follow_up_cycle()

        lead = self.db.get_lead_by_venue_id('test-venue-1')
        self.assertEqual(lead['follow_up_count'], 1)

if __name__ == "__main__":
    unittest.main()
