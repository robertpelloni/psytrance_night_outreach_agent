from src.ai_engine import AIEngine
from src.config_manager import ConfigManager
from src.db_manager import DatabaseManager

class CounterProposalGenerator:
    def __init__(self, ai=None, db_path=None):
        self.ai = ai or AIEngine()
        self.config = ConfigManager()
        self.db = DatabaseManager(db_path=db_path)

    def generate(self, lead_id, reply_content, constraints):
        """
        Takes negotiation objects + venue profile + artist EPK and produces
        a draft response for HITL review.
        """
        lead = self.db.get_lead(lead_id)
        if not lead:
            return "Error: Lead not found."

        venue = self.db.get_venue(lead['venue_id'])
        primary_genre = (self.config.get("target_genres") or ["psytrance"])[0]
        rate_card = self.config.get("rate_card")
        availability = self.config.get("availability_ranges")
        artist_id = self.config.get("artist_id")

        return self.ai.generate_reply_draft(
            venue['name'],
            reply_content,
            lead['generated_pitch'],
            genre=primary_genre,
            rate_card=rate_card,
            availability=availability,
            artist_id=artist_id,
            constraints=constraints
        )
