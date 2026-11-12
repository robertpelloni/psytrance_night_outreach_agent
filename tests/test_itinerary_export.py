import pytest
import sqlite3
import json
from src.db_manager import DatabaseManager
from src.analytics import AnalyticsEngine
from src.dashboard.app import app

@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_export.db"
    return str(db_file)

@pytest.fixture
def test_db(temp_db_path):
    db = DatabaseManager(temp_db_path)
    return db

def test_export_leads_json_structured_data(temp_db_path, test_db):
    """Verifies that export_leads_json formats venue traits, coordinates, contacts, and warmth."""
    with test_db._get_connection() as conn:
        conn.execute("""
            INSERT INTO venues (id, name, city, address, phone, venue_type, capacity, neighborhood, extracted_traits, latitude, longitude, visual_vibe_score)
            VALUES ('v1', 'Tangent Gallery', 'Detroit', '715 E Milwaukee St', '313-873-2955', 'warehouse', 400, 'Milwaukee Junction',
                    '{"sound_system": "Void Acoustics", "subgenres": ["psytrance", "techno"]}', 42.3685, -83.0642, 9)
        """)
        conn.execute("""
            INSERT INTO venue_contacts (venue_id, email, instagram_handle)
            VALUES ('v1', 'booking@tangentgallery.com', '@tangentgallery')
        """)
        conn.execute("""
            INSERT INTO outreach_leads (venue_id, vibe_score, pipeline_status, qualified_genre, pitch_variant)
            VALUES ('v1', 9, 'SENT', 'psytrance', 'Underground')
        """)
        conn.commit()

    ae = AnalyticsEngine(temp_db_path)
    leads = ae.export_leads_json()

    assert len(leads) == 1
    lead = leads[0]
    assert lead["name"] == "Tangent Gallery"
    assert lead["city"] == "Detroit"
    assert lead["address"] == "715 E Milwaukee St"
    assert lead["capacity"] == 400
    assert lead["neighborhood"] == "Milwaukee Junction"
    assert lead["coordinates"]["latitude"] == 42.3685
    assert lead["extracted_traits"]["sound_system"] == "Void Acoustics"
    assert lead["email"] == "booking@tangentgallery.com"
    assert lead["instagram_handle"] == "@tangentgallery"
    assert lead["vibe_score"] == 9
    assert lead["visual_vibe_score"] == 9

def test_export_circuit_itinerary_json(temp_db_path, test_db):
    """Verifies that export_circuit_itinerary_json builds sequential stops and circuit logistics."""
    venues = [
        {"id": "v1", "name": "TV Lounge", "city": "Detroit", "latitude": 42.3364, "longitude": -83.0583, "vibe_score": 8, "pipeline_status": "SENT"},
        {"id": "v2", "name": "Smartbar", "city": "Chicago", "latitude": 41.9496, "longitude": -87.6588, "vibe_score": 9, "pipeline_status": "SENT"}
    ]

    ae = AnalyticsEngine(temp_db_path)
    itinerary = ae.export_circuit_itinerary_json(venues)

    assert "circuit_summary" in itinerary
    assert itinerary["circuit_summary"]["venue_count"] == 2
    assert itinerary["circuit_summary"]["total_transit_km"] > 350.0
    assert itinerary["circuit_summary"]["est_drive_hours"] > 3.0
    assert itinerary["circuit_summary"]["est_co2_footprint_kg"] > 50.0

    assert len(itinerary["tour_stops"]) == 2
    assert itinerary["tour_stops"][0]["sequence_order"] == 1
    assert itinerary["tour_stops"][0]["name"] == "TV Lounge"
    assert itinerary["tour_stops"][1]["sequence_order"] == 2
    assert itinerary["tour_stops"][1]["name"] == "Smartbar"

def test_export_leads_json_endpoint(monkeypatch, temp_db_path, test_db):
    """Verifies GET /export_leads_json REST endpoint."""
    app.config["TESTING"] = True
    monkeypatch.setattr("src.dashboard.app.analytics", AnalyticsEngine(temp_db_path))

    with app.test_client() as client:
        resp = client.get("/export_leads_json")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

def test_export_circuit_itinerary_endpoint(monkeypatch, temp_db_path, test_db):
    """Verifies POST /export_circuit_itinerary endpoint returns structured manifest."""
    app.config["TESTING"] = True
    monkeypatch.setattr("src.dashboard.app.analytics", AnalyticsEngine(temp_db_path))

    venues = [
        {"id": "v1", "name": "City Club", "city": "Detroit", "latitude": 42.336, "longitude": -83.056}
    ]
    with app.test_client() as client:
        resp = client.post("/export_circuit_itinerary", json={"venues": venues})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert "itinerary" in data
        assert data["itinerary"]["circuit_summary"]["venue_count"] == 1
