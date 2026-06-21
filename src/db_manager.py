import sqlite3
import os
import json

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.getenv("DB_PATH") or 'database/outreach.db'
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

        # Phase 43: Apply migrations for new columns (always run to catch existing DBs)
        # Re-opening connection to ensure transaction isolation if needed
        with self._get_connection() as conn:
            self._apply_migrations(conn)

    def _apply_migrations(self, conn):
        """Phase 43, 45 & 47: Add missing columns and tables for schema evolution."""
        # Phase 47: Artists Table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            bio TEXT,
            genres TEXT, -- Comma-separated
            epk_link TEXT,
            mix_link TEXT,
            rate_card TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        venue_cols = [
            ("address", "TEXT"),
            ("phone", "TEXT"),
            ("venue_type", "TEXT"),
            ("capacity", "INTEGER"),
            ("neighborhood", "TEXT"),
            ("source", "TEXT"),
            ("discovered_at", "TIMESTAMP")
        ]

        cursor = conn.execute("PRAGMA table_info(venues)")
        existing_venue_cols = [row[1] for row in cursor.fetchall()]

        for col_name, col_type in venue_cols:
            if col_name not in existing_venue_cols:
                try:
                    conn.execute(f"ALTER TABLE venues ADD COLUMN {col_name} {col_type}")
                    print(f"Migration: Added column '{col_name}' to 'venues' table.")
                except sqlite3.OperationalError as e:
                    print(f"Migration error on 'venues.{col_name}': {e}")

        # Phase 45 & 47: Negotiation Status and Artist ID for leads
        lead_cols = [
            ("negotiation_status", "TEXT DEFAULT 'INITIAL'"),
            ("artist_id", "INTEGER")
        ]
        cursor = conn.execute("PRAGMA table_info(outreach_leads)")
        existing_lead_cols = [row[1] for row in cursor.fetchall()]
        for col_name, col_type in lead_cols:
            if col_name not in existing_lead_cols:
                try:
                    conn.execute(f"ALTER TABLE outreach_leads ADD COLUMN {col_name} {col_type}")
                    print(f"Migration: Added column '{col_name}' to 'outreach_leads' table.")
                except sqlite3.OperationalError as e:
                    print(f"Migration error on 'outreach_leads.{col_name}': {e}")


        # Phase 49: Social Media Channels
        try:
            conn.execute("ALTER TABLE outreach_leads ADD COLUMN outreach_channel TEXT DEFAULT 'EMAIL'")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE lead_replies ADD COLUMN source_channel TEXT DEFAULT 'EMAIL'")
        except sqlite3.OperationalError:
            pass

        # Phase 48: AI Usage Tracking
        conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Phase 48: Unmatched Replies
        conn.execute("""
        CREATE TABLE IF NOT EXISTS unmatched_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            content TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            requires_attention BOOLEAN DEFAULT 1
        )
        """)

        # Add requires_attention column to existing lead_replies
        cursor = conn.execute("PRAGMA table_info(lead_replies)")
        existing_lead_replies_cols = [row[1] for row in cursor.fetchall()]
        if "requires_attention" not in existing_lead_replies_cols:
            try:
                conn.execute("ALTER TABLE lead_replies ADD COLUMN requires_attention BOOLEAN DEFAULT 1")
                print("Migration: Added column 'requires_attention' to 'lead_replies' table.")
            except sqlite3.OperationalError as e:
                print(f"Migration error on 'lead_replies.requires_attention': {e}")

        # Add requires_attention column to existing unmatched_replies
        cursor = conn.execute("PRAGMA table_info(unmatched_replies)")
        existing_unmatched_replies_cols = [row[1] for row in cursor.fetchall()]
        if "requires_attention" not in existing_unmatched_replies_cols:
            try:
                conn.execute("ALTER TABLE unmatched_replies ADD COLUMN requires_attention BOOLEAN DEFAULT 1")
                print("Migration: Added column 'requires_attention' to 'unmatched_replies' table.")
            except sqlite3.OperationalError as e:
                print(f"Migration error on 'unmatched_replies.requires_attention': {e}")

    def add_venue(self, venue_data):
        query = """
        INSERT OR IGNORE INTO venues (id, name, city, website, google_rating, tags, raw_about_text, extracted_traits, latitude, longitude, image_url, visual_description, address, phone, venue_type, capacity, neighborhood, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Ensure we don't insert NULL for website if we want UNIQUE constraint to be effective
        # Note: SQLite treats multiple NULLs as unique, but we want to avoid duplicate names in the same city too.
        with self._get_connection() as conn:
            conn.execute(query, (
                venue_data['id'], venue_data['name'], venue_data['city'],
                venue_data.get('website'), venue_data.get('google_rating'),
                venue_data.get('tags'), venue_data.get('raw_about_text'),
                venue_data.get('extracted_traits'),
                venue_data.get('latitude'),
                venue_data.get('longitude'),
                venue_data.get('image_url'),
                venue_data.get('visual_description'),
                venue_data.get('address'),
                venue_data.get('phone'),
                venue_data.get('venue_type'),
                venue_data.get('capacity'),
                venue_data.get('neighborhood'),
                venue_data.get('source')
            ))

    def update_venue_traits(self, venue_id, traits_json):
        query = "UPDATE venues SET extracted_traits = ? WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (traits_json, venue_id))

        # Phase 43: Update new columns from extracted traits if they exist
        try:
            traits = json.loads(traits_json)
            update_fields = []
            params = []

            field_map = {
                'venue_type': 'venue_type',
                'capacity': 'capacity',
                'neighborhood': 'neighborhood'
            }

            for trait_key, col_name in field_map.items():
                if trait_key in traits and traits[trait_key]:
                    update_fields.append(f"{col_name} = ?")
                    params.append(traits[trait_key])

            if update_fields:
                params.append(venue_id)
                update_query = f"UPDATE venues SET {', '.join(update_fields)} WHERE id = ?"
                with self._get_connection() as conn:
                    conn.execute(update_query, params)
        except Exception as e:
            print(f"Error updating extended venue fields from traits: {e}")

    def update_venue_location(self, venue_id, lat, lon):
        query = "UPDATE venues SET latitude = ?, longitude = ? WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (lat, lon, venue_id))

    def update_venue_visuals(self, venue_id, image_url, visual_description):
        query = "UPDATE venues SET image_url = ?, visual_description = ? WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (image_url, visual_description, venue_id))

    def get_venues_with_location(self):
        query = """
        SELECT v.*, l.vibe_score
        FROM venues v
        JOIN outreach_leads l ON v.id = l.venue_id
        WHERE v.latitude IS NOT NULL AND v.longitude IS NOT NULL
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

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
        INSERT OR IGNORE INTO outreach_leads (venue_id, vibe_score, qualification_justification, generated_pitch, pipeline_status, success_probability, qualified_genre, pitch_variant)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(query, (
                lead_data['venue_id'], lead_data.get('vibe_score'),
                lead_data.get('qualification_justification'),
                lead_data.get('generated_pitch'),
                lead_data.get('pipeline_status', 'PENDING_QUALIFICATION'),
                lead_data.get('success_probability'),
                lead_data.get('qualified_genre'),
                lead_data.get('pitch_variant')
            ))

    def update_lead_status(self, lead_id, status, pitch=None):
        query_parts = ["pipeline_status = ?"]
        params = [status]

        if status == 'SENT':
            query_parts.append("last_outreach_at = CURRENT_TIMESTAMP")

        if status in ['BOOKED', 'LOST', 'BOUNCED']:
             query_parts.append("negotiation_status = ?")
             params.append(status)

        if pitch:
            query_parts.append("generated_pitch = ?")
            params.append(pitch)

        params.append(lead_id)
        query = f"UPDATE outreach_leads SET {', '.join(query_parts)} WHERE id = ?"

        with self._get_connection() as conn:
            conn.execute(query, params)

    def update_negotiation_status(self, lead_id, status):
        query = "UPDATE outreach_leads SET negotiation_status = ? WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (status, lead_id))

    def get_pending_leads(self):
        query = """
        SELECT l.id, v.name, v.city, v.extracted_traits, v.image_url, v.visual_description, l.vibe_score, l.qualification_justification, l.generated_pitch, l.pipeline_status, l.success_probability, l.qualified_genre, l.pitch_variant,
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
        SELECT l.id, v.id as venue_id, v.name, v.city, v.image_url, v.visual_description, l.vibe_score, l.qualification_justification, l.generated_pitch, l.pipeline_status, l.follow_up_count, l.last_outreach_at, l.success_probability, l.qualified_genre, l.pitch_variant, l.negotiation_status
        FROM outreach_leads l
        JOIN venues v ON l.venue_id = v.id
        WHERE l.pipeline_status IN ('SENT', 'REJECTED', 'BOOKED', 'LOST')
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
        # EXCLUSION: Skip leads that have received a human reply (unless it is OOO)
        query = """
        SELECT * FROM outreach_leads
        WHERE pipeline_status = 'SENT'
        AND follow_up_count < ?
        AND last_outreach_at < datetime('now', '-' || ? || ' days')
        AND id NOT IN (SELECT DISTINCT lead_id FROM lead_replies WHERE sentiment NOT IN ('OOO', 'UNKNOWN'))
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

    def reset_city_cycle(self, city=None):
        """Resets the processing cycle for a specific city or all cities."""
        if city:
            query = "DELETE FROM city_processing_log WHERE city = ?"
            params = (city,)
        else:
            query = "DELETE FROM city_processing_log"
            params = ()
        with self._get_connection() as conn:
            conn.execute(query, params)

    def start_pipeline_run(self):
        query = "INSERT INTO pipeline_runs (status) VALUES ('RUNNING')"
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            return cursor.lastrowid

    def end_pipeline_run(self, run_id, status, city_count=0, venues_found=0, leads_generated=0, error=None):
        query = """
        UPDATE pipeline_runs
        SET status = ?, end_time = CURRENT_TIMESTAMP, city_count = ?, venues_found = ?, leads_generated = ?, error_message = ?
        WHERE id = ?
        """
        with self._get_connection() as conn:
            conn.execute(query, (status, city_count, venues_found, leads_generated, error, run_id))

    def get_pipeline_history(self, limit=10):
        query = "SELECT * FROM pipeline_runs ORDER BY start_time DESC LIMIT ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]


    def get_ai_usage_today(self):
        query = """
        SELECT SUM(total_tokens) as total
        FROM ai_usage
        WHERE date(timestamp) = date('now')
        """
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            row = cursor.fetchone()
            return row[0] if row and row[0] else 0

    def get_ai_usage_since(self, since_timestamp):
        query = """
        SELECT SUM(total_tokens) as total
        FROM ai_usage
        WHERE timestamp >= ?
        """
        with self._get_connection() as conn:
            cursor = conn.execute(query, (since_timestamp,))
            row = cursor.fetchone()
            return row[0] if row and row[0] else 0

    def log_ai_usage(self, model, prompt_tokens, completion_tokens, total_tokens):
        query = "INSERT INTO ai_usage (model, prompt_tokens, completion_tokens, total_tokens) VALUES (?, ?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (model, prompt_tokens, completion_tokens, total_tokens))

    def get_ai_usage_stats(self, days=7):
        query = """
        SELECT model, SUM(prompt_tokens) as prompt, SUM(completion_tokens) as completion, SUM(total_tokens) as total
        FROM ai_usage
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY model
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (days,))
            return [dict(row) for row in cursor.fetchall()]

    def add_unmatched_reply(self, sender, subject, content):
        query = "INSERT INTO unmatched_replies (sender, subject, content) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (sender, subject, content))

    def get_unmatched_replies(self):
        query = "SELECT * FROM unmatched_replies ORDER BY received_at DESC"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def delete_unmatched_reply(self, reply_id):
        query = "DELETE FROM unmatched_replies WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (reply_id,))

    def get_attention_required_count(self):
        query_lead = "SELECT COUNT(*) FROM lead_replies WHERE requires_attention = 1"
        query_unmatched = "SELECT COUNT(*) FROM unmatched_replies WHERE requires_attention = 1"
        with self._get_connection() as conn:
            lead_count = conn.execute(query_lead).fetchone()[0]
            unmatched_count = conn.execute(query_unmatched).fetchone()[0]
            return lead_count + unmatched_count

    def mark_reply_handled(self, reply_id, is_unmatched=False):
        table = "unmatched_replies" if is_unmatched else "lead_replies"
        query = f"UPDATE {table} SET requires_attention = 0 WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (reply_id,))

    # Phase 47: Artist Management Methods
    def add_artist(self, artist_data):
        query = """
        INSERT OR REPLACE INTO artists (name, bio, genres, epk_link, mix_link, rate_card)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            cursor = conn.execute(query, (
                artist_data['name'], artist_data.get('bio'),
                artist_data.get('genres'), artist_data.get('epk_link'),
                artist_data.get('mix_link'), artist_data.get('rate_card')
            ))
            return cursor.lastrowid

    def update_artist(self, artist_id, artist_data):
        query = """
        UPDATE artists
        SET name = ?, bio = ?, genres = ?, epk_link = ?, mix_link = ?, rate_card = ?
        WHERE id = ?
        """
        with self._get_connection() as conn:
            conn.execute(query, (
                artist_data['name'], artist_data.get('bio'),
                artist_data.get('genres'), artist_data.get('epk_link'),
                artist_data.get('mix_link'), artist_data.get('rate_card'),
                artist_id
            ))

    def get_artist(self, artist_id):
        query = "SELECT * FROM artists WHERE id = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (artist_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_artist_by_name(self, name):
        query = "SELECT * FROM artists WHERE name = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_artists(self):
        query = "SELECT * FROM artists ORDER BY name ASC"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def delete_artist(self, artist_id):
        query = "DELETE FROM artists WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (artist_id,))

    def add_reply(self, lead_id, content, sentiment='UNKNOWN', draft_response=None, source_channel='EMAIL'):
        query = "INSERT INTO lead_replies (lead_id, content, sentiment, draft_response, source_channel) VALUES (?, ?, ?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (lead_id, content, sentiment, draft_response, source_channel))

        # Update negotiation status on new reply
        if sentiment in ['INTERESTED', 'INQUIRY']:
            self.update_negotiation_status(lead_id, 'REPLIED')
        elif sentiment == 'REJECTED':
            self.update_negotiation_status(lead_id, 'LOST')

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


    def log_dm_sent(self, lead_id):
        query = "UPDATE outreach_leads SET pipeline_status = 'SENT', last_outreach_at = CURRENT_TIMESTAMP, outreach_channel = 'DM' WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (lead_id,))
        self.log_system_event('OUTREACH', 'SUCCESS', f"Manual DM sent to Lead {lead_id}")

    def update_lead_negotiation_from_dm(self, lead_id, sentiment):
        if sentiment in ['INTERESTED', 'INQUIRY']:
            query = "UPDATE outreach_leads SET negotiation_status = 'REPLIED' WHERE id = ?"
            with self._get_connection() as conn:
                conn.execute(query, (lead_id,))
        elif sentiment == 'REJECTED':
            query = "UPDATE outreach_leads SET negotiation_status = 'LOST' WHERE id = ?"
            with self._get_connection() as conn:
                conn.execute(query, (lead_id,))

    def log_system_event(self, component, status, message=None):
        query = "INSERT INTO system_logs (component, status, message) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (component, status, message))

    def get_latest_system_logs(self, limit=5):
        query = "SELECT * FROM system_logs ORDER BY id DESC LIMIT ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_version_audit_trail(self, limit=50):
        query = "SELECT * FROM version_audit_trail ORDER BY timestamp DESC LIMIT ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]
