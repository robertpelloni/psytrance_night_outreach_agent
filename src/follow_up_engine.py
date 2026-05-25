import time
from datetime import datetime, timedelta
from src.db_manager import DatabaseManager
from src.ai_engine import AIEngine
from src.mailer import Mailer
from src.config_manager import ConfigManager

class FollowUpEngine:
    def __init__(self, db_path=None):
        self.db = DatabaseManager(db_path=db_path)
        self.ai = AIEngine()
        self.mailer = Mailer()
        self.config = ConfigManager()

    def process_follow_ups(self):
        """Identifies leads eligible for a follow-up and dispatches them."""
        days_wait = self.config.get("follow_up_days") or 7
        max_follow_ups = self.config.get("max_follow_ups") or 2

        print(f"FollowUpEngine: Checking for leads to follow up (after {days_wait} days, max_follow_ups={max_follow_ups})...")

        # We look for 'SENT' leads that haven't been followed up in X days
        leads = self.db.get_leads_eligible_for_follow_up(days_wait, max_follow_ups)
        print(f"FollowUpEngine: Found {len(leads)} leads eligible for follow-up.")

        for lead in leads:
            print(f"Processing follow-up for lead_id {lead['id']}...")
            venue = self.db.get_venue(lead['venue_id'])
            # Fetch contact email
            query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
            with self.db._get_connection() as conn:
                cursor = conn.execute(query, (lead['venue_id'],))
                contact = cursor.fetchone()

            if contact and contact[0]:
                email = contact[0].split(',')[0].strip()
                if email:
                    print(f"Generating follow-up for {venue['name']} ({email})...")
                    follow_up_pitch = self.ai.generate_follow_up(venue['name'], lead['generated_pitch'])

                    subject = f"Re: Proposal for Psytrance Night Residency - {venue['name']}"
                    if self.mailer.send_email(email, subject, follow_up_pitch):
                        self.db.record_follow_up(lead['id'])
                        print(f"Follow-up sent to {email}. Count is now {lead['follow_up_count'] + 1}.")
                else:
                    print(f"No valid email for follow-up on lead {lead['id']}.")
            else:
                print(f"No contact info for follow-up on lead {lead['id']}.")

    def run_follow_up_cycle(self):
        """Executes a full follow-up cycle."""
        self.process_follow_ups()

if __name__ == "__main__":
    engine = FollowUpEngine()
    while True:
        engine.run_follow_up_cycle()
        print("Follow-up cycle complete. Sleeping for 24 hours...")
        time.sleep(86400)
