import os
import json
import sqlite3
import pytest
from unittest.mock import MagicMock
from src.db_manager import DatabaseManager
from src.recommendation_engine import RecommendationEngine
from src.dashboard.app import app

@pytest.fixture
def contingency_db(tmp_path):
    db_file = str(tmp_path / "test_contingency.db")
    db = DatabaseManager(db_path=db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Target venue
    cursor.execute("""
        INSERT INTO venues (id, name, city, latitude, longitude, extracted_traits, tags, venue_type, capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "detroit_hub", "Tangent Gallery", "Detroit", 42.3732, -83.0645,
        json.dumps(["void acoustics", "warehouse", "art gallery"]),
        "underground, electronic", "Nightclub", 400
    ))

    # Alternate venue with shared acoustic system
    cursor.execute("""
        INSERT INTO venues (id, name, city, latitude, longitude, extracted_traits, tags, venue_type, capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "ferndale_alt", "Magic Stick Lounge", "Ferndale", 42.4606, -83.1346,
        json.dumps(["void acoustics", "psytrance night", "led panels"]),
        "electronic", "Nightclub", 350
    ))

    # Add lead for alternate venue
    cursor.execute("""
        INSERT INTO outreach_leads (venue_id, pipeline_status, vibe_score, qualification_justification)
        VALUES ('ferndale_alt', 'PENDING_REVIEW', 8.5, 'Underground sound matching')
    """)

    conn.commit()
    conn.close()
    return db

def test_acoustic_bonus_in_recommendations(contingency_db):
    """Verify that shared premium sound systems receive acoustic bonus."""
    rec_engine = RecommendationEngine(db_manager=contingency_db)
    recs = rec_engine.get_recommendations("detroit_hub", limit=3)
    assert len(recs) >= 1
    top_match = recs[0]
    assert top_match["venue_id"] == "ferndale_alt"
    assert top_match["match_score"] > 0.45
    assert "void acoustics" in [t.lower() for t in top_match["shared_traits"]]

def test_generate_contingency_pitch_fallback(contingency_db):
    """Verify contingency pitch template generation when AI client is None."""
    rec_engine = RecommendationEngine(db_manager=contingency_db)
    result = rec_engine.generate_contingency_pitch("detroit_hub", "ferndale_alt", ai_engine=None)
    assert result["status"] == "success"
    assert "Tangent Gallery" in result["target_venue"]
    assert "Magic Stick Lounge" in result["alt_venue"]
    assert "Magic Stick Lounge" in result["subject"]
    assert "trial residency" in result["pitch"]

def test_generate_contingency_pitch_with_mock_ai(contingency_db):
    """Verify AI-generated structured contingency pitch."""
    mock_ai = MagicMock()
    mock_ai._get_identity_context.return_value = {
        "artist_name": "Kinetic Psy",
        "epk_link": "https://epk.test.com",
        "mix_link": "https://mix.test.com"
    }
    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "subject": "Psytrance Tour Contingency - Magic Stick Lounge",
            "body": "Hi Magic Stick team, we are routing our Midwest circuit..."
        })))
    ]
    mock_ai.client.chat.completions.create.return_value = mock_resp

    rec_engine = RecommendationEngine(db_manager=contingency_db)
    result = rec_engine.generate_contingency_pitch("detroit_hub", "ferndale_alt", ai_engine=mock_ai)
    assert result["status"] == "success"
    assert result["subject"] == "Psytrance Tour Contingency - Magic Stick Lounge"
    assert "Midwest circuit" in result["pitch"]

def test_api_recommendations_pitch_endpoint(monkeypatch, contingency_db):
    """Test POST /api/recommendations/pitch/<target_id>/<alt_id> endpoint."""
    monkeypatch.setattr("src.dashboard.app.db", contingency_db)
    app.config["TESTING"] = True
    client = app.test_client()

    resp = client.post("/api/recommendations/pitch/detroit_hub/ferndale_alt", json={})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "Magic Stick Lounge" in data["alt_venue"]
    assert "subject" in data
    assert "pitch" in data
