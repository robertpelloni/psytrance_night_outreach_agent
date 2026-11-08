import os
import json
import sqlite3
import pytest
from src.db_manager import DatabaseManager
from src.recommendation_engine import RecommendationEngine

@pytest.fixture
def test_db_setup(tmp_path):
    db_file = str(tmp_path / "test_rec.db")
    db = DatabaseManager(db_path=db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Seed test venues
    # Venue A: Detroit underground club with Void Acoustics and psytrance
    cursor.execute("""
        INSERT INTO venues (id, name, city, latitude, longitude, extracted_traits, tags, venue_type, capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "venue_a", "Subterranean Detroit", "Detroit", 42.3314, -83.0458,
        json.dumps(["void acoustics", "dark warehouse", "psytrance", "laser lighting"]),
        "electronic, underground, warehouse", "Nightclub", 400
    ))

    # Venue B: Ferndale venue with Void sound and techno/psytrance (Close proximity: ~15km)
    cursor.execute("""
        INSERT INTO venues (id, name, city, latitude, longitude, extracted_traits, tags, venue_type, capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "venue_b", "The Magic Stick / Sound Lounge", "Ferndale", 42.4606, -83.1346,
        json.dumps(["void acoustics", "psytrance", "custom visuals"]),
        "underground, electronic", "Nightclub", 350
    ))

    # Venue C: Chicago warehouse with Funktion-One (Corridor: ~450km)
    cursor.execute("""
        INSERT INTO venues (id, name, city, latitude, longitude, extracted_traits, tags, venue_type, capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "venue_c", "Primary Chicago", "Chicago", 41.8781, -87.6298,
        json.dumps(["funktion-one", "underground", "techno"]),
        "warehouse, club", "Nightclub", 450
    ))

    # Venue D: Commercial cocktail lounge (mismatched traits and rejected)
    cursor.execute("""
        INSERT INTO venues (id, name, city, latitude, longitude, extracted_traits, tags, venue_type, capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "venue_d", "Luxe VIP Lounge", "Detroit", 42.3350, -83.0490,
        json.dumps(["bottle service", "vip booths", "top 40"]),
        "lounge, cocktail", "Lounge", 150
    ))

    # Seed leads for these venues
    cursor.execute("""
        INSERT INTO outreach_leads (venue_id, pipeline_status, vibe_score, qualification_justification)
        VALUES ('venue_a', 'REJECTED', 7, 'Target rejected due to date conflict')
    """)
    cursor.execute("""
        INSERT INTO outreach_leads (venue_id, pipeline_status, vibe_score, qualification_justification)
        VALUES ('venue_b', 'PENDING_REVIEW', 9, 'High-affinity underground fit')
    """)
    cursor.execute("""
        INSERT INTO outreach_leads (venue_id, pipeline_status, vibe_score, qualification_justification)
        VALUES ('venue_c', 'APPROVED', 8, 'Regional hub')
    """)
    cursor.execute("""
        INSERT INTO outreach_leads (venue_id, pipeline_status, vibe_score, qualification_justification)
        VALUES ('venue_d', 'REJECTED', 2, 'Unsuitable commercial vibe')
    """)

    conn.commit()
    conn.close()
    return db

def test_trait_extraction():
    v = {
        "extracted_traits": json.dumps(["funktion-one", "hazer"]),
        "tags": "psytrance, techno",
        "venue_type": "Nightclub"
    }
    traits = RecommendationEngine._extract_trait_set(v)
    assert "funktion-one" in traits
    assert "hazer" in traits
    assert "psytrance" in traits
    assert "techno" in traits
    assert "nightclub" in traits

def test_recommend_alternatives_scoring(test_db_setup):
    rec_engine = RecommendationEngine(db_manager=test_db_setup)

    # Recommend alternatives when venue_a is rejected
    recs = rec_engine.get_recommendations("venue_a", limit=5, min_score=0.1, exclude_rejected=True)

    assert len(recs) >= 1
    # Venue B should rank higher than Venue C because of closer proximity and shared Void sound
    top_rec = recs[0]
    assert top_rec["venue_id"] == "venue_b"
    assert top_rec["match_score"] > 0.4
    assert "void acoustics" in [t.lower() for t in top_rec["shared_traits"]]
    assert top_rec["distance_km"] is not None
    assert top_rec["distance_km"] < 25.0 # Ferndale to Detroit is ~15-20km

    # Target venue A and rejected venue D should be excluded
    rec_ids = [r["venue_id"] for r in recs]
    assert "venue_a" not in rec_ids
    assert "venue_d" not in rec_ids

def test_recommend_venues_api_endpoint(monkeypatch, test_db_setup):
    from src.dashboard.app import app
    monkeypatch.setattr("src.dashboard.app.db", test_db_setup)
    app.config["TESTING"] = True
    client = app.test_client()

    res = client.get("/recommend_venues/venue_a?limit=3")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["target_venue_id"] == "venue_a"
    assert len(data["recommendations"]) >= 1
    assert data["recommendations"][0]["venue_id"] == "venue_b"
