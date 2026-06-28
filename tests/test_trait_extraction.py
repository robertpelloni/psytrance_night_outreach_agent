import pytest
from src.ai_engine import AIEngine
from unittest.mock import MagicMock, patch
import json

def test_extract_venue_traits_success():
    ai = AIEngine(api_key="fake_key")

    # Mock OpenAI response
    mock_response = MagicMock()
    mock_traits = {
        "sound_system": "Funktion-One",
        "lighting": "Lasers and Projection Mapping",
        "atmosphere": "Underground Industrial",
        "music_policy": "Psytrance, Techno"
    }
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(mock_traits)))
    ]

    with patch.object(ai.client.chat.completions, 'create', return_value=mock_response):
        traits_json = ai.extract_venue_traits("Sonic Temple has a Funktion-One rig and lasers.")
        traits = json.loads(traits_json)

        assert traits["sound_system"] == "Funktion-One"
        assert "Lasers" in traits["lighting"]
        assert traits["atmosphere"] == "Underground Industrial"

def test_extract_venue_traits_error_handling():
    ai = AIEngine(api_key="fake_key")

    with patch.object(ai.client.chat.completions, 'create', side_effect=Exception("API Error")):
        traits_json = ai.extract_venue_traits("Some text")
        assert traits_json == "{}"

def test_generate_pitch_with_traits():
    ai = AIEngine(api_key="fake_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Hey Sonic Temple, we love your Funktion-One sound system!"))
    ]

    traits = json.dumps({"sound_system": "Funktion-One"})

    with patch.object(ai.client.chat.completions, 'create', return_value=mock_response):
        pitch = ai.generate_pitch("Sonic Temple", "Great vibe", traits=traits)
        assert "Funktion-One" in pitch['body']
