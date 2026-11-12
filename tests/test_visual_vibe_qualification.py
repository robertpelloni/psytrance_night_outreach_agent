import pytest
import os
import json
from unittest.mock import MagicMock, patch
from src.db_manager import DatabaseManager
from src.ai_engine import AIEngine

TEST_DB_PATH = "database/test_visual_vibe.db"

@pytest.fixture
def test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = DatabaseManager(db_path=TEST_DB_PATH)
    yield db
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_db_update_venue_visuals_with_score(test_db):
    venue_id = "detroit_warehouse_01"
    test_db.add_venue({
        "id": venue_id,
        "name": "Russell Industrial Center",
        "city": "Detroit"
    })

    test_db.update_venue_visuals(
        venue_id,
        image_url="https://images.unsplash.com/underground_warehouse.jpg",
        visual_description="High ceiling warehouse with lasers and UV decor",
        visual_vibe_score=9
    )

    venue = test_db.get_venue(venue_id)
    assert venue is not None
    assert venue["image_url"] == "https://images.unsplash.com/underground_warehouse.jpg"
    assert venue["visual_description"] == "High ceiling warehouse with lasers and UV decor"
    assert venue["visual_vibe_score"] == 9

def test_ai_engine_analyze_visual_vibe_mock():
    with patch("src.ai_engine.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "visual_vibe_score": 8,
                "visual_description": "Raw concrete bunker with industrial aesthetic and Funktion-One sound booth"
            })))
        ]
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 30
        mock_response.usage.total_tokens = 80
        mock_client.chat.completions.create.return_value = mock_response

        ai = AIEngine(api_key="test_key")
        result = ai.analyze_visual_vibe("https://example.com/venue.jpg", genre="psytrance")

        assert result["visual_vibe_score"] == 8
        assert "Raw concrete" in result["visual_description"]

def test_dashboard_analyze_venue_visuals_endpoint(monkeypatch, test_db):
    from src.dashboard.app import app
    app.config["TESTING"] = True

    venue_id = "hamtramck_diy_01"
    test_db.add_venue({
        "id": venue_id,
        "name": "Hamtramck Underground Loft",
        "city": "Hamtramck",
        "image_url": "https://example.com/loft.jpg"
    })

    client = app.test_client()
    monkeypatch.setattr("src.dashboard.app.db", test_db)

    with patch("src.dashboard.app.ai.analyze_visual_vibe") as mock_analyze:
        mock_analyze.return_value = {
            "visual_vibe_score": 9,
            "visual_description": "Perfect underground warehouse environment"
        }

        res = client.post(f"/analyze_venue_visuals/{venue_id}", json={})
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["visual_vibe_score"] == 9
        assert "Perfect underground" in data["visual_description"]

        # Confirm persisted in DB
        v = test_db.get_venue(venue_id)
        assert v["visual_vibe_score"] == 9
        assert v["visual_description"] == "Perfect underground warehouse environment"

def test_dashboard_analyze_venue_visuals_missing_image(monkeypatch, test_db):
    from src.dashboard.app import app
    app.config["TESTING"] = True

    venue_id = "no_img_venue"
    test_db.add_venue({
        "id": venue_id,
        "name": "No Image Space",
        "city": "Detroit"
    })

    client = app.test_client()
    monkeypatch.setattr("src.dashboard.app.db", test_db)

    res = client.post(f"/analyze_venue_visuals/{venue_id}", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "No image URL" in data["message"]
