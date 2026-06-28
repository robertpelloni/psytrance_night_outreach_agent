import unittest
from src.ai_engine import AIEngine
from unittest.mock import MagicMock, patch
import json

class TestContextualOutreach(unittest.TestCase):
    def test_media_library_selection(self):
        """Verify that AI can pick the best media based on tags."""
        ai = AIEngine(api_key="fake")
        mock_client = MagicMock()
        ai.client = mock_client

        # Setup mock response to return the 'Dark Psy' URL
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="https://soundcloud.com/dark-psy"))]
        )

        media_library = [
            {"name": "Dark Psy", "url": "https://soundcloud.com/dark-psy", "tags": ["dark", "underground"]},
            {"name": "Prog", "url": "https://soundcloud.com/prog", "tags": ["outdoor", "morning"]}
        ]

        traits = '{"atmosphere": "industrial underground", "sound_system": "loud"}'
        selected = ai.select_contextual_media(traits, media_library)

        self.assertEqual(selected, "https://soundcloud.com/dark-psy")
        self.assertTrue(mock_client.chat.completions.create.called)

    def test_pitch_generation_with_library(self):
        """Verify that pitch generation uses the contextual media."""
        ai = AIEngine(api_key="fake")
        mock_client = MagicMock()
        ai.client = mock_client

        # 1. First call to select_contextual_media
        # 2. Second call to generate_pitch
        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content="https://selected.test"))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Pitch including https://selected.test"))])
        ]

        media_library = [{"url": "https://selected.test", "tags": ["test"]}]
        pitch = ai.generate_pitch("Venue", "Justification", traits='{"test": "val"}', media_library=media_library)

        self.assertIn("https://selected.test", pitch['body'])

if __name__ == "__main__":
    unittest.main()
