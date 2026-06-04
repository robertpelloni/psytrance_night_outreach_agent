import unittest
from unittest.mock import patch, MagicMock
from src.ai_engine import AIEngine

class TestGenreAdaptation(unittest.TestCase):
    def setUp(self):
        # Don't pass api_key here, we will patch OpenAI constructor
        self.ai = None

    @patch('src.ai_engine.OpenAI')
    def test_vibe_check_genre_inclusion(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"vibe_score": 8, "justification": "Fits the vibe."}'))]
        )

        ai = AIEngine(api_key="fake")
        genre = "dark techno"
        ai.vibe_check("Test Venue", "Dark industrial space.", genre=genre)

        # Verify genre is in the prompt
        self.assertTrue(mock_client.chat.completions.create.called)
        args, kwargs = mock_client.chat.completions.create.call_args
        prompt = kwargs['messages'][1]['content']
        self.assertIn(genre, prompt)

    @patch('src.ai_engine.OpenAI')
    def test_generate_pitch_genre_inclusion(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Mock Pitch"))]
        )

        ai = AIEngine(api_key="fake")
        genre = "ambient"
        ai.generate_pitch("Test Venue", "Good fit", genre=genre)

        self.assertTrue(mock_client.chat.completions.create.called)
        args, kwargs = mock_client.chat.completions.create.call_args
        prompt = kwargs['messages'][1]['content']
        self.assertIn(genre, prompt)

if __name__ == "__main__":
    unittest.main()
