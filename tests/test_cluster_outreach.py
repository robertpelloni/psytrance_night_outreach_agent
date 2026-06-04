import pytest
from unittest.mock import MagicMock, patch
from src.tour_planner import TourPlanner
from src.outreach_engine import OutreachEngine
import os

# Use a temporary file for the database path instead of :memory: to avoid FileNotFoundError in os.path.dirname
TEMP_DB = 'database/test_cluster.db'

@pytest.fixture
def planner():
    if not os.path.exists('database'): os.makedirs('database')
    return TourPlanner(db_path=TEMP_DB)

@pytest.fixture
def outreach_engine():
    if not os.path.exists('database'): os.makedirs('database')
    return OutreachEngine(db_path=TEMP_DB)

def test_generate_cluster_pitch_no_ai(planner):
    planner.ai.client = None
    assert planner.generate_cluster_pitch(0) is None

@patch('src.analytics.AnalyticsEngine.get_venue_clusters')
def test_generate_cluster_pitch_success(mock_clusters, planner):
    mock_clusters.return_value = [
        {'venues': [{'name': 'Venue A'}, {'name': 'Venue B'}]}
    ]
    planner.ai.client = MagicMock()
    planner.ai.client.chat.completions.create.return_value.choices[0].message.content = "Tour Pitch Content"

    pitch = planner.generate_cluster_pitch(0)
    assert pitch == "Tour Pitch Content"

def test_dispatch_cluster_pitch_empty(outreach_engine):
    results = outreach_engine.dispatch_cluster_pitch([], "Some Pitch")
    assert results['success'] == 0
    assert results['failure'] == 0

@patch('src.mailer.Mailer.send_email')
def test_dispatch_cluster_pitch_success(mock_send, outreach_engine):
    mock_send.return_value = True
    venues = [{'id': 'v1', 'name': 'Venue A'}]

    # Mock DB for contact info
    with patch.object(outreach_engine.db, '_get_connection') as mock_conn:
        mock_cursor = mock_conn.return_value.__enter__.return_value
        mock_cursor.execute.return_value.fetchone.return_value = ('test@example.com',)

        results = outreach_engine.dispatch_cluster_pitch(venues, "Cluster Pitch")
        assert results['success'] == 1
        assert mock_send.called

# Cleanup
def teardown_module(module):
    if os.path.exists(TEMP_DB):
        os.remove(TEMP_DB)
