import pytest
import sqlite3
import os
from unittest.mock import MagicMock
from src.analytics import AnalyticsEngine
from src.tour_planner import TourPlanner
from src.dashboard.app import app

TEST_DB = 'database/test_tour_enhanced.db'

@pytest.fixture(autouse=True)
def setup_tour_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    os.makedirs('database', exist_ok=True)

    with sqlite3.connect(TEST_DB) as conn:
        conn.execute("""
            CREATE TABLE venues (
                id TEXT PRIMARY KEY,
                name TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL
            )
        """)
        conn.execute("""
            CREATE TABLE outreach_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venue_id TEXT,
                vibe_score REAL,
                pipeline_status TEXT,
                pitch_variant TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE lead_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                sentiment TEXT
            )
        """)

        # Add Detroit venues (Cluster 1)
        conn.execute("INSERT INTO venues VALUES ('v1', 'Tangent Gallery', 'Detroit', 42.3732, -83.0645)")
        conn.execute("INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status) VALUES ('v1', 8.5, 'PENDING_REVIEW')")
        conn.execute("INSERT INTO venues VALUES ('v2', 'Russell Industrial', 'Detroit', 42.3770, -83.0560)")
        conn.execute("INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status) VALUES ('v2', 9.0, 'PENDING_REVIEW')")

        # Add Ann Arbor venue nearby Detroit (Cluster 1 or transit link)
        conn.execute("INSERT INTO venues VALUES ('v3', 'Nectarine Ballroom', 'Ann Arbor', 42.2808, -83.7430)")
        conn.execute("INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status) VALUES ('v3', 7.5, 'PENDING_REVIEW')")

        # Add Chicago venues (Cluster 2) ~380 km away
        conn.execute("INSERT INTO venues VALUES ('v4', 'Smartbar', 'Chicago', 41.9496, -87.6587)")
        conn.execute("INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status) VALUES ('v4', 9.0, 'PENDING_REVIEW')")
        conn.execute("INSERT INTO venues VALUES ('v5', 'Radius', 'Chicago', 41.8540, -87.6534)")
        conn.execute("INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status) VALUES ('v5', 8.0, 'PENDING_REVIEW')")

        # Add Toronto venue (Cluster 3) ~370 km east of Detroit
        conn.execute("INSERT INTO venues VALUES ('v6', 'Coda', 'Toronto', 43.6654, -79.4103)")
        conn.execute("INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status) VALUES ('v6', 8.8, 'PENDING_REVIEW')")
        conn.execute("INSERT INTO venues VALUES ('v7', 'Vertigo', 'Toronto', 43.6550, -79.3850)")
        conn.execute("INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status) VALUES ('v7', 7.5, 'PENDING_REVIEW')")

    yield

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_hierarchical_clustering_algorithm():
    """Verify hierarchical agglomerative clustering groups venues correctly."""
    analytics = AnalyticsEngine(db_path=TEST_DB)
    clusters_hier = analytics.get_venue_clusters(radius_km=70, min_vibe=7.0, method='hierarchical')
    assert len(clusters_hier) >= 2
    for c in clusters_hier:
        assert c['venue_count'] >= 2
        assert c['clustering_method'] == 'hierarchical'
        assert 'cluster_radius_km' in c
        assert 'est_intercity_drive_hrs' in c

def test_circuit_logistics_calculation():
    """Verify compute_circuit_logistics computes transit distance, rest days, and CO2."""
    mock_ai = MagicMock()
    mock_ai._get_identity_context.return_value = {
        "artist_name": "Kinetic Psy",
        "epk_link": "https://epk.test.com",
        "mix_link": "https://soundcloud.com/test-mix"
    }

    planner = TourPlanner(db_path=TEST_DB, ai=mock_ai)
    logistics = planner.compute_circuit_logistics(method='hierarchical', min_vibe=7.0)

    assert logistics['total_distance_km'] > 100.0
    assert logistics['total_drive_hours'] > 1.0
    assert logistics['recommended_rest_days'] >= 1
    assert logistics['est_carbon_kg'] > 10.0
    assert len(logistics['leg_details']) >= 1
    assert len(logistics['paired_media']) == 2
    assert any(m['title'] == 'Electronic Press Kit (EPK)' for m in logistics['paired_media'])

def test_plan_circuit_endpoint_with_logistics():
    """Test /plan_circuit returns recommendation, route, and enriched logistics."""
    client = app.test_client()
    app.config['TESTING'] = True

    resp = client.get('/plan_circuit?method=hierarchical&min_vibe=7.0')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'route' in data
    assert 'logistics' in data
    assert 'total_distance_km' in data['logistics']

def test_simulate_circuit_api_endpoint():
    """Test POST /api/tour/simulate_circuit handles custom parameters."""
    client = app.test_client()
    app.config['TESTING'] = True

    payload = {
        "method": "hierarchical",
        "min_vibe": 7.0
    }
    resp = client.post('/api/tour/simulate_circuit', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    assert data['method'] == 'hierarchical'
    assert 'route' in data
    assert 'logistics' in data
