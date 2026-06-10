import unittest
import sqlite3
import os
import tempfile
from src.analytics import AnalyticsEngine

class TestAnalyticsReporting(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE venues (
                id INTEGER PRIMARY KEY,
                name TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL
            )
        """)
        self.conn.execute("""
            CREATE TABLE outreach_leads (
                id INTEGER PRIMARY KEY,
                venue_id INTEGER,
                vibe_score REAL,
                pipeline_status TEXT,
                pitch_variant TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE lead_replies (
                id INTEGER PRIMARY KEY,
                lead_id INTEGER,
                sentiment TEXT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.engine = AnalyticsEngine(db_path=self.db_path)

    def tearDown(self):
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_get_conversion_funnel(self):
        # Setup data
        self.conn.execute("INSERT INTO venues (id, name, city) VALUES (1, 'Venue 1', 'Detroit')")
        self.conn.execute("INSERT INTO venues (id, name, city) VALUES (2, 'Venue 2', 'Detroit')")

        # Lead 1: Qualified, Pitched, Replied, Booked
        self.conn.execute("INSERT INTO outreach_leads (id, venue_id, vibe_score, pipeline_status) VALUES (1, 1, 8.5, 'BOOKED')")
        self.conn.execute("INSERT INTO lead_replies (id, lead_id, sentiment) VALUES (1, 1, 'INTERESTED')")

        # Lead 2: Qualified, Pitched (SENT)
        self.conn.execute("INSERT INTO outreach_leads (id, venue_id, vibe_score, pipeline_status) VALUES (2, 2, 7.0, 'SENT')")
        self.conn.commit()

        funnel = self.engine.get_conversion_funnel()

        self.assertEqual(funnel['discovered'], 2)
        self.assertEqual(funnel['qualified'], 2)
        self.assertEqual(funnel['pitched'], 2)
        self.assertEqual(funnel['replied'], 1)
        self.assertEqual(funnel['booked'], 1)

    def test_get_scene_health(self):
        # Setup data
        self.conn.execute("INSERT INTO outreach_leads (id, venue_id, pipeline_status) VALUES (1, 1, 'BOOKED')")
        self.conn.execute("INSERT INTO outreach_leads (id, venue_id, pipeline_status) VALUES (2, 2, 'SENT')")
        self.conn.execute("INSERT INTO outreach_leads (id, venue_id, pipeline_status) VALUES (3, 3, 'SENT')")

        # 2 replies
        self.conn.execute("INSERT INTO lead_replies (id, lead_id, sentiment) VALUES (1, 1, 'INTERESTED')")
        self.conn.execute("INSERT INTO lead_replies (id, lead_id, sentiment) VALUES (2, 2, 'INQUIRY')")
        self.conn.commit()

        health = self.engine.get_scene_health()

        # Response Rate: 2/3 = 66.7%
        self.assertEqual(health['response_rate'], 66.7)
        # Booking Rate: 1/2 = 50.0%
        self.assertEqual(health['booking_rate'], 50.0)
        # Interested Rate: 1/3 = 33.3%
        self.assertEqual(health['interested_rate'], 33.3)

    def test_get_venue_warmth(self):
        self.conn.execute("INSERT INTO outreach_leads (id, venue_id, pipeline_status) VALUES (1, 100, 'SENT')")
        self.conn.commit()

        # No replies yet
        warmth = self.engine.get_venue_warmth(100)
        self.assertEqual(warmth, 20)

        # Interested reply
        import datetime
        now = datetime.datetime.now()
        early_str = (now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("INSERT INTO lead_replies (id, lead_id, sentiment, received_at) VALUES (1, 1, 'INTERESTED', ?)", (early_str,))
        self.conn.commit()

        warmth = self.engine.get_venue_warmth(100)
        # Base(40) + Interested(40) + Recent(20) = 100
        self.assertEqual(warmth, 100)

        # Rejected reply
        late_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("INSERT INTO lead_replies (id, lead_id, sentiment, received_at) VALUES (2, 1, 'REJECTED', ?)", (late_str,))
        self.conn.commit()
        warmth = self.engine.get_venue_warmth(100)
        self.assertEqual(warmth, 5)

if __name__ == '__main__':
    unittest.main()
