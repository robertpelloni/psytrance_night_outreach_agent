import unittest
from unittest.mock import MagicMock, patch
from src.ai_engine import AIEngine

class TestAIEngine(unittest.TestCase):
    def setUp(self):
        self.ai = AIEngine(api_key="fake-key")

    @patch('src.ai_engine.OpenAI')
    def test_vibe_check(self, mock_openai):
        # Mocking the OpenAI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_ai = AIEngine(api_key="fake-key")

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"vibe_score": 9, "justification": "Great vibe"}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        result = mock_ai.vibe_check("Test Venue", "Dark basement with techno.")
        self.assertEqual(result['vibe_score'], 9)
        self.assertEqual(result['justification'], "Great vibe")

    def test_generate_pitch_no_client(self):
        # Test default behavior when client is not configured
        ai_no_key = AIEngine(api_key=None)
        pitch = ai_no_key.generate_pitch("Venue", "Justification")
        self.assertEqual(pitch, "Hey, we would love to play at your venue!")

if __name__ == "__main__":
    unittest.main()
