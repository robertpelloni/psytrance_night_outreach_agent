import pytest
from unittest.mock import MagicMock
from src.ai_engine import AIEngine

def test_generate_pitch_includes_venue_notes():
    ai = AIEngine()
    mock_client = MagicMock()
    ai.client = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content="Mocked Pitch Response"))
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    notes = [
        {"author": "Curator Alex", "note": "Sound engineer prefers Void Acoustics and low sub bass frequencies."},
        {"author": "Resident DJ", "note": "Strict midnight noise ordinance for outdoor courtyard."}
    ]

    pitch = ai.generate_pitch(
        venue_name="Russell Industrial Center",
        justification="Iconic Detroit underground warehouse complex",
        notes=notes
    )

    assert pitch == "Mocked Pitch Response"
    assert mock_client.chat.completions.create.called

    # Verify the generated prompt in call args
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    prompt_content = messages[1]["content"]

    assert "Curator Confidential Intelligence & Field Notes" in prompt_content
    assert "Sound engineer prefers Void Acoustics" in prompt_content
    assert "Strict midnight noise ordinance" in prompt_content

def test_vibe_check_includes_venue_notes():
    ai = AIEngine()
    mock_client = MagicMock()
    ai.client = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content='{"vibe_score": 8.5, "justification": "Underground warehouse vibe confirmed."}'))
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    notes = [
        {"author": "Curator", "note": "Venue recently installed Danley Sound Labs subwoofers"}
    ]

    res = ai.vibe_check(
        venue_name="Tangent Gallery",
        raw_text="Eclectic Detroit art space and gallery",
        notes=notes
    )

    assert res["vibe_score"] == 8.5
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    prompt_content = call_kwargs["messages"][1]["content"]

    assert "Curator Confidential Intelligence & Field Notes" in prompt_content
    assert "Venue recently installed Danley Sound Labs subwoofers" in prompt_content
