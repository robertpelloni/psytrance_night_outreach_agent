import pytest
import os
from src.db_manager import DatabaseManager
from src.dashboard.app import app

TEST_DB_PATH = "database/test_notes.db"

@pytest.fixture
def test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = DatabaseManager(db_path=TEST_DB_PATH)
    db.add_venue({
        "id": "venue-123",
        "name": "Marble Bar",
        "city": "Detroit"
    })
    yield db
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_add_and_get_venue_notes(test_db):
    note_id = test_db.add_venue_note("venue-123", "Sound engineer prefers Allen & Heath Xone:96", author="Jules")
    assert note_id is not None

    notes = test_db.get_venue_notes("venue-123")
    assert len(notes) == 1
    assert notes[0]["note"] == "Sound engineer prefers Allen & Heath Xone:96"
    assert notes[0]["author"] == "Jules"
    assert notes[0]["created_at"] is not None

def test_venue_notes_api(test_db, monkeypatch):
    monkeypatch.setattr("src.dashboard.app.db", test_db)
    app.config["TESTING"] = True
    client = app.test_client()

    # Test POST JSON note
    post_res = client.post("/venue/venue-123/notes", json={
        "note": "Private backroom available for ambient second room",
        "author": "Resident DJ"
    })
    assert post_res.status_code == 200
    data = post_res.get_json()
    assert data["status"] == "success"
    assert data["author"] == "Resident DJ"

    # Test GET notes
    get_res = client.get("/venue/venue-123/notes")
    assert get_res.status_code == 200
    notes_data = get_res.get_json()
    assert len(notes_data["notes"]) == 1
    assert notes_data["notes"][0]["note"] == "Private backroom available for ambient second room"
