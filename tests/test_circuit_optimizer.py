import pytest
import sqlite3
import os
from unittest.mock import MagicMock
from src.tour_planner import TourPlanner
from src.analytics import AnalyticsEngine
from src.ai_engine import AIEngine
from src.config_manager import ConfigManager

TEST_CIRCUIT_DB = 'database/test_circuit.db'

@pytest.fixture
def circuit_db():
    if os.path.exists(TEST_CIRCUIT_DB):
        os.remove(TEST_CIRCUIT_DB)

    conn = sqlite3.connect(TEST_CIRCUIT_DB)
    conn.executescript("""
    CREATE TABLE venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        latitude REAL,
        longitude REAL
    );
    CREATE TABLE outreach_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venue_id INTEGER,
        vibe_score REAL,
        pipeline_status TEXT,
        pitch_variant TEXT
    );
    CREATE TABLE lead_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        sentiment TEXT
    );
    """)

    # Venues: Detroit hub (42.33, -83.04), Ann Arbor (42.28, -83.74), Chicago (41.87, -87.62), Toronto (43.65, -79.38)
    venues_data = [
        # Detroit cluster (high vibe >= 6.5)
        (1, 'Tangent Gallery', 'Detroit', 42.37, -83.05),
        (2, 'City Club', 'Detroit', 42.33, -83.05),
        # Ann Arbor cluster (high vibe >= 6.5)
        (3, 'Blind Pig', 'Ann Arbor', 42.28, -83.75),
        (4, 'Nectar', 'Ann Arbor', 42.28, -83.74),
        # Chicago cluster (high vibe >= 6.5)
        (5, 'Smartbar', 'Chicago', 41.94, -87.65),
        (6, 'Spybar', 'Chicago', 41.89, -87.63),
        # Toronto cluster (high vibe >= 6.5)
        (7, 'Coda', 'Toronto', 43.66, -79.41),
        (8, 'Vertigo', 'Toronto', 43.65, -79.39),
        # Low vibe venue (< 6.5)
        (9, 'Generic Bar', 'Detroit', 42.35, -83.06)
    ]

    for v in venues_data:
        conn.execute("INSERT INTO venues (id, name, city, latitude, longitude) VALUES (?, ?, ?, ?, ?)", v)

    leads_data = [
        (1, 1, 9.0, 'PENDING_REVIEW', 'A'),
        (2, 2, 8.5, 'PENDING_REVIEW', 'A'),
        (3, 3, 7.5, 'PENDING_REVIEW', 'B'),
        (4, 4, 7.0, 'PENDING_REVIEW', 'B'),
        (5, 5, 8.5, 'PENDING_REVIEW', 'A'),
        (6, 6, 8.0, 'PENDING_REVIEW', 'A'),
        (7, 7, 9.5, 'PENDING_REVIEW', 'B'),
        (8, 8, 9.0, 'PENDING_REVIEW', 'B'),
        (9, 9, 4.5, 'PENDING_QUALIFICATION', 'A') # Below 6.5 vibe threshold
    ]

    for l in leads_data:
        conn.execute("INSERT INTO outreach_leads (id, venue_id, vibe_score, pipeline_status, pitch_variant) VALUES (?, ?, ?, ?, ?)", l)

    conn.commit()
    conn.close()

    yield TEST_CIRCUIT_DB

    if os.path.exists(TEST_CIRCUIT_DB):
        os.remove(TEST_CIRCUIT_DB)

def test_vibe_scoring_threshold_and_prompt():
    ai = AIEngine()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"vibe_score": 7.5, "justification": "Authentic underground acoustics and Detroit warehouse aesthetic."}'
    mock_response.usage.prompt_tokens = 50
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 70
    mock_client.chat.completions.create.return_value = mock_response
    ai.client = mock_client

    result = ai.vibe_check(
        venue_name="Tangent Gallery",
        raw_text="Underground electronic arts venue with Void Acoustics and projection mapping.",
        genre="psytrance"
    )

    assert result["vibe_score"] == 7.5
    assert "acoustics" in result["justification"].lower() or "aesthetic" in result["justification"].lower()
    call_args = mock_client.chat.completions.create.call_args[1]
    prompt_sent = call_args["messages"][1]["content"]
    assert "6.5 vibe threshold" in prompt_sent
    assert "Detroit" in prompt_sent

def test_midwest_toronto_circuit_route(circuit_db):
    planner = TourPlanner(db_path=circuit_db)
    route = planner.get_circuit_route()

    assert len(route) >= 3
    # First cluster should be Detroit hub
    first_cluster_cities = [v['city'] for v in route[0]['venues']]
    assert 'Detroit' in first_cluster_cities

    # Check that Toronto is included in the circuit
    all_cities = [v['city'] for cluster in route for v in cluster['venues']]
    assert 'Toronto' in all_cities
    assert 'Chicago' in all_cities
    assert 'Ann Arbor' in all_cities

def test_tour_planner_with_artist_identity_and_threshold(circuit_db):
    mock_ai = MagicMock()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Optimal Tour Route: Detroit -> Ann Arbor -> Chicago -> Toronto."
    mock_client.chat.completions.create.return_value = mock_response
    mock_ai.client = mock_client
    mock_ai._get_identity_context.return_value = {
        "context": "Artist/DJ Name: Psylander | Collective: Detroit Mindstate | Home City: Detroit",
        "artist_name": "Psylander",
        "epk_link": "https://epk.test",
        "mix_link": "https://mix.test"
    }

    planner = TourPlanner(db_path=circuit_db, ai=mock_ai)
    result = planner.plan_optimized_tour(min_vibe=6.5)

    assert "Detroit" in result
    assert "Toronto" in result
    mock_client.chat.completions.create.assert_called_once()
    prompt = mock_client.chat.completions.create.call_args[1]["messages"][0]["content"]
    assert "Toronto" in prompt
    assert "Psylander" in prompt
    assert "cross-border" in prompt.lower() or "ambassador bridge" in prompt.lower()

def test_config_manager_float_vibe_threshold():
    cfg = ConfigManager()
    threshold = cfg.get("vibe_threshold")
    assert isinstance(threshold, (int, float))
    assert float(threshold) >= 6.0
