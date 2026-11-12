import pytest
import sqlite3
import os
from unittest.mock import patch, MagicMock
from src.db_manager import DatabaseManager
from src.mailer import Mailer

@pytest.fixture
def tracking_test_db(tmp_path):
    db_file = str(tmp_path / "test_email_tracking.db")
    db = DatabaseManager(db_path=db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Seed venue and lead
    cursor.execute("""
        INSERT INTO venues (id, name, city)
        VALUES ('v1', 'Tracked Venue', 'Detroit')
    """)
    cursor.execute("""
        INSERT INTO outreach_leads (id, venue_id, pipeline_status, vibe_score, generated_pitch)
        VALUES (101, 'v1', 'SENT', 8, 'Hey team, here is our mix https://soundcloud.com/test')
    """)
    cursor.execute("""
        INSERT INTO outreach_leads (id, venue_id, pipeline_status, vibe_score, generated_pitch)
        VALUES (102, 'v2', 'SENT', 7, 'Second pitch')
    """)
    conn.commit()
    conn.close()
    return db

def test_db_tracking_events_lifecycle(tracking_test_db):
    db = tracking_test_db

    # 1. Record open event
    db.record_tracking_event(101, 'OPEN', ip_address='192.168.1.1', user_agent='TestMailer/1.0')
    db.record_tracking_event(101, 'OPEN', ip_address='192.168.1.2', user_agent='TestMailer/1.0')

    # 2. Record click event
    db.record_tracking_event(101, 'CLICK', target_url='https://soundcloud.com/test', ip_address='192.168.1.1', user_agent='TestBrowser/1.0')

    # 3. Retrieve events
    events = db.get_lead_tracking_events(101)
    assert len(events) == 3
    assert any(e['event_type'] == 'CLICK' and e['target_url'] == 'https://soundcloud.com/test' for e in events)

    # 4. Check summary
    summary = db.get_lead_tracking_summary(101)
    assert summary['opens'] == 2
    assert summary['clicks'] == 1
    assert summary['last_engagement'] is not None

    # 5. Check overall stats
    stats = db.get_overall_engagement_stats()
    assert stats['total_sent'] == 2
    assert stats['unique_opened'] == 1
    assert stats['open_rate'] == 50.0
    assert stats['unique_clicked'] == 1
    assert stats['ctr'] == 50.0

def test_mailer_tracked_html_generation():
    mailer = Mailer()
    body = "Check out our EPK at https://epk.example.com and Soundcloud https://soundcloud.com/psy"
    html = mailer._build_tracked_html_body(body, 101, "http://localhost:5000")

    assert '<img src="http://localhost:5000/track/open/101.gif"' in html
    assert 'href="http://localhost:5000/track/click/101?url=https%3A%2F%2Fepk.example.com"' in html
    assert 'href="http://localhost:5000/track/click/101?url=https%3A%2F%2Fsoundcloud.com%2Fpsy"' in html

def test_flask_tracking_routes(monkeypatch, tracking_test_db):
    from src.dashboard.app import app
    monkeypatch.setattr("src.dashboard.app.db", tracking_test_db)
    app.config["TESTING"] = True
    client = app.test_client()

    # Test open tracking pixel
    res_open = client.get("/track/open/101.gif", headers={"User-Agent": "Gmail/1.0"})
    assert res_open.status_code == 200
    assert res_open.mimetype == "image/gif"
    assert res_open.headers.get("Cache-Control") == "no-cache, no-store, must-revalidate, max-age=0"

    # Test click tracking redirect
    res_click = client.get("/track/click/101?url=https://epk.example.com/artist")
    assert res_click.status_code == 302
    assert res_click.headers.get("Location") == "https://epk.example.com/artist"

    # Verify recorded in DB
    events = tracking_test_db.get_lead_tracking_events(101)
    assert len(events) == 2
    assert any(e['event_type'] == 'OPEN' for e in events)
    assert any(e['event_type'] == 'CLICK' and e['target_url'] == 'https://epk.example.com/artist' for e in events)
