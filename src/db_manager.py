import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or 'database/outreach.db'
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        # Find schema path relative to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_path = os.path.join(base_dir, 'database', 'schema.sql')

        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
            else:
                print(f"Warning: schema.sql not found at {schema_path}")

    def add_venue(self, venue_data):
        query = """
        INSERT OR IGNORE INTO venues (id, name, city, website, google_rating, tags, raw_about_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        # Ensure we don't insert NULL for website if we want UNIQUE constraint to be effective
        # Note: SQLite treats multiple NULLs as unique, but we want to avoid duplicate names in the same city too.
        with self._get_connection() as conn:
            conn.execute(query, (
                venue_data['id'], venue_data['name'], venue_data['city'],
                venue_data.get('website'), venue_data.get('google_rating'),
                venue_data.get('tags'), venue_data.get('raw_about_text')
            ))

    def venue_exists_by_name(self, name, city):
        query = "SELECT id FROM venues WHERE name = ? AND city = ?"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (name, city))
            row = cursor.fetchone()
            return row[0] if row else None

    def add_contact(self, contact_data):
        query = """
        INSERT OR IGNORE INTO venue_contacts (venue_id, email, phone, instagram_handle, booking_page_url)
        VALUES (?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(query, (
                contact_data['venue_id'], contact_data.get('email'),
                contact_data.get('phone'), contact_data.get('instagram_handle'),
                contact_data.get('booking_page_url')
            ))

    def lead_exists(self, venue_id):
        query = "SELECT id FROM outreach_leads WHERE venue_id = ?"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (venue_id,))
            return cursor.fetchone() is not None

    def add_lead(self, lead_data):
        query = """
        INSERT OR IGNORE INTO outreach_leads (venue_id, vibe_score, qualification_justification, generated_pitch, pipeline_status)
        VALUES (?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(query, (
                lead_data['venue_id'], lead_data.get('vibe_score'),
                lead_data.get('qualification_justification'),
                lead_data.get('generated_pitch'),
                lead_data.get('pipeline_status', 'PENDING_QUALIFICATION')
            ))

    def update_lead_status(self, lead_id, status, pitch=None):
        if status == 'SENT':
            query = "UPDATE outreach_leads SET pipeline_status = ?, last_outreach_at = CURRENT_TIMESTAMP WHERE id = ?"
            params = (status, lead_id)
            if pitch:
                query = "UPDATE outreach_leads SET pipeline_status = ?, generated_pitch = ?, last_outreach_at = CURRENT_TIMESTAMP WHERE id = ?"
                params = (status, pitch, lead_id)
        elif pitch:
            query = "UPDATE outreach_leads SET pipeline_status = ?, generated_pitch = ? WHERE id = ?"
            params = (status, pitch, lead_id)
        else:
            query = "UPDATE outreach_leads SET pipeline_status = ? WHERE id = ?"
            params = (status, lead_id)

        with self._get_connection() as conn:
            conn.execute(query, params)

    def get_pending_leads(self):
        query = """
        SELECT l.id, v.name, v.city, l.vibe_score, l.qualification_justification, l.generated_pitch, l.pipeline_status,
               (SELECT email FROM venue_contacts WHERE venue_id = v.id LIMIT 1) as email,
               (SELECT instagram_handle FROM venue_contacts WHERE venue_id = v.id LIMIT 1) as instagram
        FROM outreach_leads l
        JOIN venues v ON l.venue_id = v.id
        WHERE l.pipeline_status = 'PENDING_REVIEW'
        ORDER BY l.vibe_score DESC
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_lead_history(self):
        query = """
        SELECT l.id, v.name, v.city, l.vibe_score, l.qualification_justification, l.generated_pitch, l.pipeline_status, l.follow_up_count, l.last_outreach_at
        FROM outreach_leads l
        JOIN venues v ON l.venue_id = v.id
        WHERE l.pipeline_status IN ('SENT', 'REJECTED')
        ORDER BY l.id DESC
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_venue(self, venue_id):
        query = "SELECT * FROM venues WHERE id = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (venue_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_leads_by_status(self, status):
        query = "SELECT * FROM outreach_leads WHERE pipeline_status = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (status,))
            return [dict(row) for row in cursor.fetchall()]

    def get_lead_by_venue_id(self, venue_id):
        query = "SELECT * FROM outreach_leads WHERE venue_id = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (venue_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_lead(self, lead_id):
        query = "SELECT * FROM outreach_leads WHERE id = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (lead_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_leads_eligible_for_follow_up(self, days_wait, max_follow_ups):
        # last_outreach_at is compared against CURRENT_TIMESTAMP - days_wait
        # EXCLUSION: Skip leads that have received a human reply (any reply in lead_replies)
        query = """
        SELECT * FROM outreach_leads
        WHERE pipeline_status = 'SENT'
        AND follow_up_count < ?
        AND last_outreach_at < datetime('now', '-' || ? || ' days')
        AND id NOT IN (SELECT DISTINCT lead_id FROM lead_replies)
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (max_follow_ups, days_wait))
            return [dict(row) for row in cursor.fetchall()]

    def record_follow_up(self, lead_id):
        query = """
        UPDATE outreach_leads
        SET follow_up_count = follow_up_count + 1,
            last_outreach_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        with self._get_connection() as conn:
            conn.execute(query, (lead_id,))

    def mark_city_processed(self, city, status='COMPLETED'):
        query = "INSERT OR REPLACE INTO city_processing_log (city, status, last_processed_at) VALUES (?, ?, CURRENT_TIMESTAMP)"
        with self._get_connection() as conn:
            conn.execute(query, (city, status))

    def is_city_processed(self, city):
        query = "SELECT status FROM city_processing_log WHERE city = ?"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (city,))
            row = cursor.fetchone()
            return row is not None and row[0] == 'COMPLETED'

    def add_reply(self, lead_id, content, sentiment='UNKNOWN'):
        query = "INSERT INTO lead_replies (lead_id, content, sentiment) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (lead_id, content, sentiment))

    def get_lead_replies(self, lead_id):
        query = "SELECT * FROM lead_replies WHERE lead_id = ? ORDER BY received_at DESC"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (lead_id,))
            return [dict(row) for row in cursor.fetchall()]

    def has_blocking_reply(self, lead_id):
        """Checks if a lead has received a reply that should pause automation."""
        query = "SELECT count(*) FROM lead_replies WHERE lead_id = ? AND sentiment IN ('INTERESTED', 'REJECTED')"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (lead_id,))
            return cursor.fetchone()[0] > 0

    def log_system_event(self, component, status, message=None):
        query = "INSERT INTO system_logs (component, status, message) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (component, status, message))

    def get_latest_system_logs(self, limit=5):
        query = "SELECT * FROM system_logs ORDER BY created_at DESC LIMIT ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]
