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
        primary_genre = (self.config.get("target_genres") or ["psytrance"])[0]

        print(f"FollowUpEngine: Checking for leads to follow up (after {days_wait} days, max_follow_ups={max_follow_ups})...")

        # We look for 'SENT' or 'FOLLOW_UP_APPROVED' leads that haven't been followed up in X days
        leads = self.db.get_leads_eligible_for_follow_up(days_wait, max_follow_ups)
        print(f"FollowUpEngine: Found {len(leads)} leads eligible for follow-up evaluation.")

        for lead in leads:
            # Re-check vibe score
            vibe_score = lead.get('vibe_score', 0)
            auto_approve_threshold = self.config.get("auto_approve_threshold") or 9

            if vibe_score < 6:
                print(f"Skipping follow-up for lead {lead['id']} due to low vibe score ({vibe_score}).")
                continue

            # HITL Gating Logic
            if lead['pipeline_status'] == 'SENT':
                if vibe_score >= auto_approve_threshold:
                    print(f"Auto-approving follow-up for high-vibe lead {lead['id']}...")
                    self.db.update_lead_status(lead['id'], 'FOLLOW_UP_APPROVED')
                else:
                    print(f"Lead {lead['id']} requires HITL approval for follow-up. Setting to PENDING_FOLLOW_UP.")
                    self.db.update_lead_status(lead['id'], 'PENDING_FOLLOW_UP')
                    continue
            elif lead['pipeline_status'] != 'FOLLOW_UP_APPROVED':
                continue

            print(f"Processing approved follow-up for lead_id {lead['id']}...")
            venue = self.db.get_venue(lead['venue_id'])
            # Fetch contact email and IG handle
            query = "SELECT email, instagram_handle FROM venue_contacts WHERE venue_id = ?"
            conn = self.db._get_connection()
            cursor = conn.execute(query, (lead['venue_id'],))
            contact = cursor.fetchone()

            if contact:
                email = contact[0].split(',')[0].strip() if contact[0] else None
                instagram = contact[1] if len(contact) > 1 else None

                vibe_threshold = self.config.get("vibe_threshold") or 6

                # Fetch variant from lead
                variant = lead.get('pitch_variant') or "Professional"

                if email:
                    print(f"Generating email follow-up for {venue['name']} ({email})...")
                    follow_up_pitch = self.ai.generate_follow_up(
                        venue['name'],
                        lead['generated_pitch'],
                        genre=primary_genre,
                        vibe_score=vibe_score,
                        threshold=vibe_threshold
                    )

                    subject = f"Re: Proposal for {primary_genre.capitalize()} Night Residency - {venue['name']}"
                    if self.mailer.send_email(email, subject, follow_up_pitch):
                        self.db.record_follow_up(lead['id'])
                        print(f"Follow-up sent to {email}. Count is now {lead.get('follow_up_count', 0) + 1}.")
                elif instagram:
                    print(f"Generating IG DM follow-up for {venue['name']} (@{instagram})...")
                    follow_up_pitch = self.ai.generate_follow_up(
                        venue['name'],
                        lead['generated_pitch'],
                        genre=primary_genre,
                        vibe_score=vibe_score,
                        threshold=vibe_threshold,
                        is_dm=True
                    )
                    self.db.record_follow_up(lead['id'])
                    self.db.log_system_event("FOLLOW_UP", "IG_DM_SENT", f"Simulated DM follow-up to @{instagram}: {follow_up_pitch[:100]}...")
                    print(f"Follow-up sent to IG @{instagram}. Count is now {lead.get('follow_up_count', 0) + 1}.")
                else:
                    print(f"No valid email or IG handle for follow-up on lead {lead['id']}.")
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
