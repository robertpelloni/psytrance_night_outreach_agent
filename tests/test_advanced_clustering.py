import pytest
import os
from src.db_manager import DatabaseManager
from src.analytics import AnalyticsEngine

TEST_DB_PATH = "database/test_clustering.db"

@pytest.fixture
def clustering_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = DatabaseManager(db_path=TEST_DB_PATH)

    # Detroit cluster venues
    db.add_venue({
        "id": "v1",
        "name": "Marble Bar",
        "city": "Detroit",
        "latitude": 42.3734,
        "longitude": -83.0827
    })
    db.add_venue({
        "id": "v2",
        "name": "Tangent Gallery",
        "city": "Detroit",
        "latitude": 42.3730,
        "longitude": -83.0600
    })

    # Add mock leads
    with db._get_connection() as conn:
        conn.execute("INSERT INTO outreach_leads (id, venue_id, vibe_score, pipeline_status) VALUES (1, 'v1', 9.0, 'APPROVED')")
        conn.execute("INSERT INTO outreach_leads (id, venue_id, vibe_score, pipeline_status) VALUES (2, 'v2', 8.5, 'SENT')")

    yield db

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_cluster_metrics_calculation(clustering_db):
    analytics = AnalyticsEngine(db_path=TEST_DB_PATH)
    clusters = analytics.get_venue_clusters(radius_km=30, min_vibe=7.0)

    assert len(clusters) == 1
    c = clusters[0]
    assert c["venue_count"] == 2
    assert c["avg_vibe"] == 8.8
    assert "cluster_radius_km" in c
    assert "est_intercity_drive_hrs" in c
    assert c["cluster_radius_km"] > 0
    assert c["est_intercity_drive_hrs"] >= 0
