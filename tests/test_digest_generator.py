import pytest
import sqlite3
import os
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from src.digest_generator import DigestGenerator
from src.dashboard.app import app

TEST_DB_PATH = 'database/test_digest.db'

@pytest.fixture
def test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    conn = sqlite3.connect(TEST_DB_PATH)
    conn.executescript("""
    CREATE TABLE venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        website TEXT,
        google_rating REAL
    );
    CREATE TABLE outreach_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venue_id INTEGER,
        vibe_score REAL,
        pipeline_status TEXT,
        last_outreach_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE lead_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        content TEXT,
        sentiment TEXT,
        requires_attention INTEGER DEFAULT 0,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE ai_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        total_tokens INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE unmatched_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        subject TEXT,
        body TEXT
    );
    """)

    # Populate dummy historical and recent data
    now_str = datetime.now().isoformat()
    old_str = (datetime.now() - timedelta(days=15)).isoformat()

    conn.execute("INSERT INTO venues (id, name, city) VALUES (1, 'V1', 'Detroit'), (2, 'V2', 'Chicago')")
    conn.execute(
        "INSERT INTO outreach_leads (id, venue_id, vibe_score, pipeline_status, last_outreach_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 1, 9, 'SENT', now_str, now_str)
    )
    conn.execute(
        "INSERT INTO outreach_leads (id, venue_id, vibe_score, pipeline_status, last_outreach_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (2, 2, 8, 'BOOKED', now_str, old_str)
    )
    conn.execute(
        "INSERT INTO lead_replies (id, lead_id, content, sentiment, requires_attention, received_at) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 1, 'Interested in booking psytrance!', 'INTERESTED', 1, now_str)
    )
    conn.execute(
        "INSERT INTO ai_usage (model, prompt_tokens, completion_tokens, total_tokens, timestamp) VALUES (?, ?, ?, ?, ?)",
        ('gpt-4o', 100, 25, 125, now_str)
    )
    conn.execute(
        "INSERT INTO unmatched_replies (sender, subject, body) VALUES ('anon@psy.org', 'Hello', 'Mysterious note')"
    )
    conn.commit()
    conn.close()

    yield TEST_DB_PATH

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_digest_metric_aggregation(test_db):
    generator = DigestGenerator(db_path=test_db)
    metrics = generator.collect_metrics(days=7)

    assert metrics['period_days'] == 7
    assert metrics['total_venues'] == 2
    assert metrics['leads_qualified'] == 1  # lead 1 created recently, lead 2 15 days ago
    assert metrics['pitches_sent'] == 2     # leads with status SENT/BOOKED and last_outreach_at within cutoff
    assert metrics['total_booked'] == 1
    assert metrics['replies_received'] == 1
    assert metrics['replies_by_sentiment'].get('INTERESTED') == 1
    assert metrics['tokens_consumed'] == 125
    assert metrics['attention_required'] == 1
    assert metrics['unmatched_replies'] == 1
    assert len(metrics['recent_replies']) == 1

def test_digest_rendering_text_and_html(test_db):
    generator = DigestGenerator(db_path=test_db)
    metrics = generator.collect_metrics(days=7)

    text = generator.render_text_digest(metrics)
    assert 'Psytrance Night Outreach Pipeline Digest (Past 7 Days)' in text
    assert 'New Leads Qualified: 1' in text
    assert 'Total Booked Venues: 1' in text

    html = generator.render_html_digest(metrics)
    assert '<!DOCTYPE html>' in html
    assert '🌌 Psytrance Outreach Pipeline Digest' in html
    assert 'INTERESTED:' in html
    assert 'V1' in html

def test_digest_dispatch_via_mailer(test_db):
    mock_mailer = MagicMock()
    mock_mailer.send_email.return_value = True

    generator = DigestGenerator(db_path=test_db, mailer=mock_mailer)
    res = generator.dispatch_digest(recipient_email='booking@psycollective.org', days=7)

    assert res['success'] is True
    assert res['recipient'] == 'booking@psycollective.org'
    assert 'Pipeline Digest' in res['subject']
    mock_mailer.send_email.assert_called_once()
    args, kwargs = mock_mailer.send_email.call_args
    assert kwargs.get('to_email') == 'booking@psycollective.org' or args[0] == 'booking@psycollective.org'

def test_dashboard_digest_routes():
    client = app.test_client()

    # GET /preview_digest
    res_preview = client.get('/preview_digest?days=7')
    assert res_preview.status_code == 200
    assert b'Pipeline Digest' in res_preview.data

    # POST /send_digest
    res_send = client.post('/send_digest', json={'days': 7, 'recipient_email': 'test_admin@psy.org'})
    assert res_send.status_code == 200
    data = res_send.get_json()
    assert data['success'] is True
    assert data['recipient'] == 'test_admin@psy.org'
