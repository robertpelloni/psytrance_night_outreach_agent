import pytest
from unittest.mock import MagicMock, patch
from src.outreach_predictor import OutreachPredictor
import json

@pytest.fixture
def predictor():
    return OutreachPredictor(db_path=':memory:')

def test_predict_success_probability_no_lead(predictor):
    with patch.object(predictor, '_get_connection') as mock_conn:
        mock_cursor = mock_conn.return_value.__enter__.return_value
        mock_cursor.execute.return_value.fetchone.return_value = None

        prob = predictor.predict_success_probability(999)
        assert prob == 0

@patch('src.outreach_predictor.AIEngine')
def test_predict_success_probability_basic(mock_ai, predictor):
    with patch.object(predictor, '_get_connection') as mock_conn:
        mock_cursor = mock_conn.return_value.__enter__.return_value

        # Mock lead data
        # Now we need to mock the cache check too
        mock_cursor.execute.return_value.fetchone.side_effect = [
            None, # cache
            {'vibe_score': 8, 'extracted_traits': None, 'city': 'Berlin'}, # lead
            {'interested': 2, 'total': 10} # city stats
        ]

        prob = predictor.predict_success_probability(1)
        # Base: 8 * 8 = 64
        # City rate: 20%
        # Blended: 64 * 0.7 + 20 * 0.3 = 44.8 + 6 = 50.8
        assert prob == 50.8

def test_predict_success_probability_with_ai(predictor):
    predictor.ai.client = MagicMock()
    predictor.ai.client.chat.completions.create.return_value.choices[0].message.content = "10"

    with patch.object(predictor, '_get_connection') as mock_conn:
        mock_cursor = mock_conn.return_value.__enter__.return_value

        # Mock lead data
        traits = json.dumps({"sound_system": "Funktion-One"})
        mock_cursor.execute.return_value.fetchone.side_effect = [
            None, # cache
            {'vibe_score': 10, 'extracted_traits': traits, 'city': 'Goa'}, # lead
            None # no city stats
        ]

        prob = predictor.predict_success_probability(1)
        # Base: 10 * 8 = 80
        # No city stats
        # AI Adjustment: +10
        # Total: 90
        assert prob == 90

def test_predict_success_probability_cached(predictor):
    with patch.object(predictor, '_get_connection') as mock_conn:
        mock_cursor = mock_conn.return_value.__enter__.return_value
        mock_cursor.execute.return_value.fetchone.return_value = {'success_probability': 75.0}

        prob = predictor.predict_success_probability(1)
        assert prob == 75.0
