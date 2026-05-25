import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path='database/outreach.db'):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        schema_path = 'database/schema.sql'
        if not os.path.exists('database'):
            os.makedirs('database')

        with self._get_connection() as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())

    def add_venue(self, venue_data):
        query = """
        INSERT OR IGNORE INTO venues (id, name, city, website, google_rating, tags, raw_about_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(query, (
                venue_data['id'], venue_data['name'], venue_data['city'],
                venue_data.get('website'), venue_data.get('google_rating'),
                venue_data.get('tags'), venue_data.get('raw_about_text')
            ))

    def add_contact(self, contact_data):
        query = """
        INSERT INTO venue_contacts (venue_id, email, phone, instagram_handle, booking_page_url)
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
        if self.lead_exists(lead_data['venue_id']):
            return
        query = """
        INSERT INTO outreach_leads (venue_id, vibe_score, qualification_justification, generated_pitch, pipeline_status)
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
        if pitch:
            query = "UPDATE outreach_leads SET pipeline_status = ?, generated_pitch = ? WHERE id = ?"
            params = (status, pitch, lead_id)
        else:
            query = "UPDATE outreach_leads SET pipeline_status = ? WHERE id = ?"
            params = (status, lead_id)

        with self._get_connection() as conn:
            conn.execute(query, params)

    def get_pending_leads(self):
        query = """
        SELECT l.id, v.name, v.city, l.vibe_score, l.qualification_justification, l.generated_pitch, l.pipeline_status
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
        SELECT l.id, v.name, v.city, l.vibe_score, l.qualification_justification, l.generated_pitch, l.pipeline_status
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

    def get_lead(self, lead_id):
        query = "SELECT * FROM outreach_leads WHERE id = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (lead_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
