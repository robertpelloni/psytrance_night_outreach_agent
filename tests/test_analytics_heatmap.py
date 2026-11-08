import pytest
import sqlite3
import os
from src.db_manager import DatabaseManager
from src.analytics import AnalyticsEngine
from src.dashboard.app import app

@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_heatmap.db"
    return str(db_file)

@pytest.fixture
def test_db(temp_db_path):
    db = DatabaseManager(temp_db_path)
    return db

def test_analytics_heatmap_empty_database(temp_db_path, test_db):
    """Verifies default behavior and structure when no outreach or replies have been logged."""
    ae = AnalyticsEngine(temp_db_path)
    data = ae.get_activity_heatmap()

    assert "days" in data
    assert len(data["days"]) == 7
    assert data["days"] == ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    assert "matrix" in data
    assert len(data["matrix"]) == 7
    assert len(data["matrix"][0]) == 24
    assert data["total_outreach_events"] == 0
    assert data["total_reply_events"] == 0
    assert "best_window" in data
    assert "description" in data["best_window"]

def test_analytics_heatmap_with_dispatches_and_replies(temp_db_path, test_db):
    """Verifies that last_outreach_at and reply timestamps populate the heatmap matrix correctly."""
    with test_db._get_connection() as conn:
        # Create venue
        conn.execute("""
            INSERT INTO venues (id, name, city) VALUES ('v1', 'City Club', 'Detroit')
        """)
        # Insert lead with Tuesday (dow=2) 14:00 (hour=14) outreach: e.g. 2026-11-10 14:30:00 (Tuesday)
        conn.execute("""
            INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status, last_outreach_at)
            VALUES ('v1', 8, 'SENT', '2026-11-10 14:30:00')
        """)
        lead_id = conn.execute("SELECT id FROM outreach_leads WHERE venue_id = 'v1'").fetchone()[0]

        # Insert reply on Wednesday (dow=3) 16:00 (hour=16): e.g. 2026-11-11 16:15:00 (Wednesday)
        conn.execute("""
            INSERT INTO lead_replies (lead_id, content, sentiment, received_at)
            VALUES (?, 'Sounds great, let us talk dates', 'INTERESTED', '2026-11-11 16:15:00')
        """, (lead_id,))
        conn.commit()

    ae = AnalyticsEngine(temp_db_path)
    heatmap = ae.get_activity_heatmap()

    # DOW 2 = Tue, Hour 14: outreach = 1
    assert heatmap["outreach_counts"][2][14] == 1
    assert heatmap["matrix"][2][14] >= 1

    # DOW 3 = Wed, Hour 16: reply = 1 (weighted x2)
    assert heatmap["reply_counts"][3][16] == 1
    assert heatmap["matrix"][3][16] >= 2

    assert heatmap["total_outreach_events"] == 1
    assert heatmap["total_reply_events"] == 1

def test_api_analytics_activity_heatmap_endpoint(monkeypatch, temp_db_path, test_db):
    """Verifies the REST API endpoint GET /api/analytics/activity_heatmap."""
    app.config["TESTING"] = True
    monkeypatch.setattr("src.dashboard.app.analytics", AnalyticsEngine(temp_db_path))

    with app.test_client() as client:
        resp = client.get("/api/analytics/activity_heatmap")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["status"] == "success"
        assert "heatmap" in payload
        assert "matrix" in payload["heatmap"]
        assert len(payload["heatmap"]["days"]) == 7

def test_dashboard_renders_activity_heatmap_ui(monkeypatch, temp_db_path, test_db):
    """Verifies that the dashboard index page renders the heatmap section without errors."""
    app.config["TESTING"] = True
    monkeypatch.setattr("src.dashboard.app.analytics", AnalyticsEngine(temp_db_path))
    monkeypatch.setattr("src.dashboard.app.db", test_db)

    with app.test_client() as client:
        resp = client.get("/?tab=analytics")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "Outreach Timing Matrix &amp; Response Velocity" in html or "Outreach Timing Matrix & Response Velocity" in html
        assert "Optimal Dispatch:" in html
        assert "Density Legend:" in html
