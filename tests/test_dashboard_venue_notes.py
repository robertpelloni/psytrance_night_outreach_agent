import pytest
import sqlite3
from src.db_manager import DatabaseManager
from src.analytics import AnalyticsEngine
from src.dashboard.app import app

@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_notes.db"
    return str(db_file)

@pytest.fixture
def test_db(temp_db_path):
    db = DatabaseManager(temp_db_path)
    return db

def test_venue_notes_json_post_and_get(monkeypatch, temp_db_path, test_db):
    """Verifies that POST /venue/<id>/notes accepts JSON payloads and GET returns the note history."""
    app.config["TESTING"] = True
    monkeypatch.setattr("src.dashboard.app.db", test_db)

    # Seed venue
    test_db.add_venue({
        "id": "v_tangent",
        "name": "Tangent Gallery",
        "city": "Detroit"
    })

    with app.test_client() as client:
        # Post JSON note
        res = client.post("/venue/v_tangent/notes", json={
            "note": "Acoustic system: Void Incubus. Sound engineer prefers uncompressed WAV promos.",
            "author": "Sound Curator"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["author"] == "Sound Curator"
        assert "Void Incubus" in data["note"]

        # Fetch notes via GET
        get_res = client.get("/venue/v_tangent/notes")
        assert get_res.status_code == 200
        get_data = get_res.get_json()
        assert get_data["venue_id"] == "v_tangent"
        assert len(get_data["notes"]) == 1
        assert get_data["notes"][0]["author"] == "Sound Curator"

def test_venue_notes_validation_error_on_empty_note(monkeypatch, temp_db_path, test_db):
    """Verifies that submitting an empty note returns a 400 Bad Request."""
    app.config["TESTING"] = True
    monkeypatch.setattr("src.dashboard.app.db", test_db)

    with app.test_client() as client:
        res = client.post("/venue/v_tangent/notes", json={"note": ""})
        assert res.status_code == 400
        data = res.get_json()
        assert "error" in data

def test_index_renders_notes_modal_and_trigger_buttons(monkeypatch, temp_db_path, test_db):
    """Verifies that index.html renders #venueNotesModal and 'Notes' trigger buttons on leads."""
    app.config["TESTING"] = True
    monkeypatch.setattr("src.dashboard.app.db", test_db)
    monkeypatch.setattr("src.dashboard.app.analytics", AnalyticsEngine(temp_db_path))

    # Add a pending lead
    test_db.add_venue({
        "id": "v_cityclub",
        "name": "Leland City Club",
        "city": "Detroit"
    })
    test_db.add_lead({
        "venue_id": "v_cityclub",
        "vibe_score": 9,
        "qualification_justification": "Gothic industrial warehouse",
        "generated_pitch": "Let's bring dark psychedelic sounds.",
        "pipeline_status": "PENDING_REVIEW"
    })

    with app.test_client() as client:
        res = client.get("/?tab=pipeline&view=pending")
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert 'id="venueNotesModal"' in html
        assert "openVenueNotesModal('v_cityclub', 'Leland City Club')" in html
        assert "📝 Notes" in html
