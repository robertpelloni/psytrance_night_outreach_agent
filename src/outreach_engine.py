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
        """Dispatches emails for leads marked as APPROVED with safety throttles."""
        print("OutreachEngine: Checking for approved leads to dispatch...")
        leads = self.db.get_leads_by_status('APPROVED')

        max_daily = self.config.get("daily_outreach_limit") or 10
        delay_min = self.config.get("outreach_delay_min") or 5

        # Count how many sent today
        sent_today_query = "SELECT COUNT(*) FROM outreach_leads WHERE pipeline_status = 'SENT' AND last_outreach_at >= date('now')"
        with self.db._get_connection() as conn:
            sent_today = conn.execute(sent_today_query).fetchone()[0]

        if sent_today >= max_daily:
            print(f"OutreachEngine: Daily limit reached ({sent_today}/{max_daily}). Skipping dispatch.")
            return

        for lead in leads:
            if sent_today >= max_daily:
                print(f"OutreachEngine: Daily limit reached during loop. Stopping.")
                break

            venue_id = lead['venue_id']
            # Fetch contact email
            query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
            with self.db._get_connection() as conn:
                cursor = conn.execute(query, (venue_id,))
                contact = cursor.fetchone()

            if contact:
                email = contact[0].split(',')[0].strip() if contact[0] else None
                if email:
                    print(f"Dispatching pitch to {email} for venue_id {venue_id}...")
                    subject = "Proposal for Psytrance Night Residency"
                    body = lead['generated_pitch']

                    if self.mailer.send_email(email, subject, body):
                        self.db.update_lead_status(lead['id'], 'SENT')
                        print(f"Lead {lead['id']} marked as SENT.")
                        sent_today += 1

                        # Guardrail: Delay between emails
                        if sent_today < max_daily:
                            print(f"OutreachEngine: Sleeping for {delay_min} minutes before next dispatch...")
                            time.sleep(delay_min * 60)
                else:
                    # Check for IG DM fallback
                    ig_query = "SELECT instagram_handle FROM venue_contacts WHERE venue_id = ?"
                    with self.db._get_connection() as conn:
                        ig_cursor = conn.execute(ig_query, (venue_id,))
                        ig_contact = ig_cursor.fetchone()

                    if ig_contact and ig_contact[0]:
                        print(f"Dispatching IG DM pitch to {ig_contact[0]} for venue_id {venue_id}...")
                        self.db.update_lead_status(lead['id'], 'SENT')
                        self.db.log_system_event("OUTREACH", "IG_DM_SENT", f"Simulated DM to @{ig_contact[0]}: {lead['generated_pitch'][:100]}...")
                        print(f"Lead {lead['id']} marked as SENT via IG DM.")
                        sent_today += 1

                        if sent_today < max_daily:
                            time.sleep(delay_min * 60)
                    else:
                        print(f"No valid email or IG handle found for lead {lead['id']}.")
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
        auto_threshold = self.config.get("auto_approve_threshold") or 9
        self.auto_approve_high_vibe_leads(threshold=auto_threshold)
        self.process_approved_leads()

    def dispatch_cluster_pitch(self, venues_list, cluster_pitch):
        """Sends a unified tour pitch to a list of venues."""
        print(f"OutreachEngine: Dispatching cluster pitch to {len(venues_list)} venues...")
        results = {"success": 0, "failure": 0}

        for venue in venues_list:
            venue_id = venue['id']
            # Fetch contact email
            query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
            with self.db._get_connection() as conn:
                cursor = conn.execute(query, (venue_id,))
                contact = cursor.fetchone()

            if contact and contact[0]:
                email = contact[0].split(',')[0].strip()
                if email:
                    print(f"Dispatching tour pitch to {email}...")
                    subject = "Proposal for Regional Psytrance Residency Tour"

                    if self.mailer.send_email(email, subject, cluster_pitch):
                        # Update any existing lead for this venue to SENT
                        # Note: This uses venue_id to find the lead
                        lead_query = "SELECT id FROM outreach_leads WHERE venue_id = ?"
                        with self.db._get_connection() as conn:
                            lead = conn.execute(lead_query, (venue_id,)).fetchone()
                            if lead:
                                self.db.update_lead_status(lead[0], 'SENT', pitch=cluster_pitch)

                        results['success'] += 1
                    else:
                        results['failure'] += 1

        return results

if __name__ == "__main__":
    engine = OutreachEngine()
    while True:
        engine.run_outreach_cycle()
        # Sleep for 1 hour between cycles
        print("Outreach cycle complete. Sleeping for 1 hour...")
        time.sleep(3600)
