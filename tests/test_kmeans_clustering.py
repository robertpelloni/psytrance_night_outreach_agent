import os
import pytest
import sqlite3
from src.analytics import AnalyticsEngine
from src.tour_planner import TourPlanner
from src.ai_engine import AIEngine
from unittest.mock import MagicMock

@pytest.fixture
def test_db_kmeans():
    test_db = "database/test_kmeans.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    with open("database/schema.sql", "r") as f:
        cursor.executescript(f.read())

    # Insert diverse Midwest circuit venues
    venues = [
        ("v-det-1", "Leland City Club", "Detroit", 42.3355, -83.0560, "Industrial club"),
        ("v-det-2", "TV Lounge", "Detroit", 42.3360, -83.0610, "Underground club"),
        ("v-det-3", "Spot Lite Detroit", "Detroit", 42.3550, -83.0200, "Art space"),
        ("v-chi-1", "Smartbar", "Chicago", 41.9496, -87.6588, "Nightclub"),
        ("v-chi-2", "Radius Chicago", "Chicago", 41.8548, -87.6534, "Concert hall"),
        ("v-chi-3", "Spybar", "Chicago", 41.8950, -87.6350, "Basement venue"),
        ("v-cle-1", "The Foundry Concert Club", "Cleveland", 41.4850, -81.7920, "Live venue"),
        ("v-cle-2", "Crobar Lounge", "Cleveland", 41.4880, -81.7050, "Underground space"),
    ]

    for vid, name, city, lat, lon, traits in venues:
        cursor.execute("""
            INSERT INTO venues (id, name, city, latitude, longitude, extracted_traits)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (vid, name, city, lat, lon, traits))

        cursor.execute("""
            INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status, qualified_genre)
            VALUES (?, 8.0, 'APPROVED', 'Psytrance')
        """, (vid,))

    conn.commit()
    conn.close()

    yield test_db

    if os.path.exists(test_db):
        os.remove(test_db)

def test_kmeans_partitioning(test_db_kmeans):
    ae = AnalyticsEngine(db_path=test_db_kmeans)
    clusters = ae.get_venue_clusters(method='kmeans', min_vibe=6.0)

    assert len(clusters) >= 2
    for c in clusters:
        assert c["venue_count"] >= 2
        assert "center" in c
        assert "lat" in c["center"] and "lon" in c["center"]
        assert c["cluster_radius_km"] >= 0.0
        assert c["est_intercity_drive_hrs"] >= 0.0
        assert c["clustering_method"] == 'kmeans'

def test_kmeans_empty_database():
    empty_db = "database/test_empty_kmeans.db"
    if os.path.exists(empty_db):
        os.remove(empty_db)
    conn = sqlite3.connect(empty_db)
    with open("database/schema.sql", "r") as f:
        conn.cursor().executescript(f.read())
    conn.commit()
    conn.close()

    ae = AnalyticsEngine(db_path=empty_db)
    clusters = ae.get_venue_clusters(method='kmeans')
    assert clusters == []

    if os.path.exists(empty_db):
        os.remove(empty_db)

def test_tour_planner_kmeans_logistics(test_db_kmeans):
    ai = MagicMock(spec=AIEngine)
    ai._get_identity_context.return_value = {
        "artist_name": "Kinetic Psynapse",
        "epk_link": "https://press.kit/kinetic",
        "mix_link": "https://soundcloud.com/kinetic/tour-live"
    }

    tp = TourPlanner(db_path=test_db_kmeans, ai=ai)
    logistics = tp.compute_circuit_logistics(method='kmeans', min_vibe=6.5)

    assert "total_distance_km" in logistics
    assert "total_drive_hours" in logistics
    assert "paired_media" in logistics
    assert len(logistics["paired_media"]) >= 2

    # Check media tag attribution
    media_tags = [m.get("tag") for m in logistics["paired_media"]]
    assert "Core Press" in media_tags
    assert "Live Audio" in media_tags

def test_plan_circuit_endpoint_with_kmeans(test_db_kmeans):
    from src.dashboard.app import app
    app.config["TESTING"] = True
    app.config["DB_PATH"] = test_db_kmeans

    with app.test_client() as client:
        res = client.get("/plan_circuit?method=kmeans&min_vibe=7.0")
        assert res.status_code == 200
        data = res.get_json()
        assert "recommendation" in data
        assert "route" in data
        assert "logistics" in data
        assert data["logistics"]["total_distance_km"] >= 0.0

        # Also test /api/tour/simulate_circuit
        res2 = client.post("/api/tour/simulate_circuit", json={"method": "kmeans", "min_vibe": 7.0})
        assert res2.status_code == 200
        data2 = res2.get_json()
        assert data2["status"] == "success"
        assert data2["method"] == "kmeans"
