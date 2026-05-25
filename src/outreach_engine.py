import time
import os
from src.db_manager import DatabaseManager
from src.mailer import Mailer
from src.config_manager import ConfigManager

class OutreachEngine:
    def __init__(self, db_path=None):
        self.db = DatabaseManager(db_path=db_path)
        self.mailer = Mailer()
        self.config = ConfigManager()

    def process_approved_leads(self):
        """Dispatches emails for leads marked as APPROVED."""
        print("OutreachEngine: Checking for approved leads to dispatch...")
        leads = self.db.get_leads_by_status('APPROVED')

        for lead in leads:
            venue_id = lead['venue_id']
            # Fetch contact email
            query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
            with self.db._get_connection() as conn:
                cursor = conn.execute(query, (venue_id,))
                contact = cursor.fetchone()

            if contact and contact[0]:
                email = contact[0].split(',')[0].strip()
                if email:
                    print(f"Dispatching pitch to {email} for venue_id {venue_id}...")
                    subject = "Proposal for Psytrance Night Residency"
                    body = lead['generated_pitch']

                    if self.mailer.send_email(email, subject, body):
                        self.db.update_lead_status(lead['id'], 'SENT')
                        print(f"Lead {lead['id']} marked as SENT.")
                else:
                    print(f"No valid email found for lead {lead['id']}.")
            else:
                print(f"No contact info found for lead {lead['id']}.")

    def auto_approve_high_vibe_leads(self, threshold=9):
        """Automatically moves high-scoring leads to APPROVED status."""
        print(f"OutreachEngine: Auto-approving leads with vibe_score >= {threshold}...")
        query = "UPDATE outreach_leads SET pipeline_status = 'APPROVED' WHERE pipeline_status = 'PENDING_REVIEW' AND vibe_score >= ?"
        with self.db._get_connection() as conn:
            conn.execute(query, (threshold,))
            conn.commit()

    def run_outreach_cycle(self):
        """One-stop shop for running a full outreach cycle."""
        auto_threshold = self.config.get("auto_approve_threshold", 9)
        self.auto_approve_high_vibe_leads(threshold=auto_threshold)
        self.process_approved_leads()

if __name__ == "__main__":
    engine = OutreachEngine()
    while True:
        engine.run_outreach_cycle()
        # Sleep for 1 hour between cycles
        print("Outreach cycle complete. Sleeping for 1 hour...")
        time.sleep(3600)
