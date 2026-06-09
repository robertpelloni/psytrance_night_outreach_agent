from src.db_manager import DatabaseManager
from src.ai_engine import AIEngine

class SentimentAnalyzer:
    def __init__(self, db_path=None):
        self.db = DatabaseManager(db_path=db_path)
        self.ai = AIEngine()

    def process_new_reply(self, lead_id, content):
        """Analyzes a new reply and stores it with sentiment and drafted response."""
        # Ensure lead_id is an integer if passed as a mock or other type in tests
        try:
            lead_id = int(lead_id)
        except (ValueError, TypeError):
            pass

        sentiment = self.ai.analyze_sentiment(content)
        print(f"SentimentAnalyzer: Detected {sentiment} for lead_id {lead_id}.")

        draft = None
        if sentiment in ['INTERESTED', 'INQUIRY']:
            from src.config_manager import ConfigManager
            config = ConfigManager()
            primary_genre = (config.get("target_genres") or ["psytrance"])[0]
            rate_card = config.get("rate_card")
            availability = config.get("availability_ranges")

            lead = self.db.get_lead(lead_id)
            venue = self.db.get_venue(lead['venue_id'])
            draft = self.ai.generate_reply_draft(
                venue['name'],
                content,
                lead['generated_pitch'],
                genre=primary_genre,
                rate_card=rate_card,
                availability=availability
            )
        elif sentiment == 'OOO':
            # Phase 45: Queue re-attempt by bumping last_outreach_at forward
            # so the FollowUpEngine picks it up later
            print(f"SentimentAnalyzer: OOO detected for lead_id {lead_id}. Queuing re-attempt.")
            # For simplicity, we just reset the outreach timestamp to 10 days ago
            # (or some future-dated logic if we had a proper task queue)
            # Actually, the follow-up engine waits N days. If we want it to re-try in N days,
            # we should update last_outreach_at to NOW.
            with self.db._get_connection() as conn:
                conn.execute("UPDATE outreach_leads SET last_outreach_at = CURRENT_TIMESTAMP WHERE id = ?", (lead_id,))

        self.db.add_reply(lead_id, content, sentiment, draft_response=draft)
        return sentiment

if __name__ == "__main__":
    # Example usage / manual test
    analyzer = SentimentAnalyzer()
    test_content = "We are interested in hosting a psytrance night. What are your dates?"
    analyzer.process_new_reply(1, test_content)
