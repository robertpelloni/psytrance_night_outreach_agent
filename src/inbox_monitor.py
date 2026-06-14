import imaplib
import email
from email.header import decode_header
import os
from src.config_manager import ConfigManager
from src.db_manager import DatabaseManager
from src.sentiment_analyzer import SentimentAnalyzer

class InboxMonitor:
    def __init__(self, db_path=None):
        self.config = ConfigManager()
        self.db = DatabaseManager(db_path=db_path)
        self.analyzer = SentimentAnalyzer(db_path=db_path)

        self.imap_server = os.getenv("IMAP_SERVER") or self.config.get("imap_server")
        self.imap_user = os.getenv("IMAP_USER") or self.config.get("imap_user")
        self.imap_password = os.getenv("IMAP_PASSWORD") or self.config.get("imap_password")
        self.imap_port = int(os.getenv("IMAP_PORT") or self.config.get("imap_port") or 993)

    def _connect(self):
        """Establishes a connection to the IMAP server."""
        if not all([self.imap_server, self.imap_user, self.imap_password]):
            print("InboxMonitor: IMAP configuration incomplete. Skipping.")
            return None

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.imap_user, self.imap_password)
            return mail
        except Exception as e:
            print(f"InboxMonitor: Failed to connect to IMAP: {e}")
            return None

    def fetch_new_replies(self):
        """Polls the inbox for new unread messages and processes them."""
        mail = self._connect()
        if not mail:
            return 0

        new_replies_count = 0
        try:
            mail.select("INBOX")
            # Search for all messages (we'll filter by UID to avoid duplicates)
            status, messages = mail.uid('search', None, "ALL")
            if status != 'OK':
                return 0

            uids = messages[0].split()
            if not uids:
                return 0

            # Get the last processed UID from system logs or a dedicated setting
            # For now, we'll store it as a system event in logs to keep schema clean
            last_uid = self._get_last_processed_uid()

            for uid_bytes in uids:
                uid = int(uid_bytes)
                if uid <= last_uid:
                    continue

                # Fetch message
                status, msg_data = mail.uid('fetch', uid_bytes, '(RFC822)')
                if status != 'OK' or not msg_data or not msg_data[0]:
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Process the email
                if self._process_email(msg, uid):
                    new_replies_count += 1

                # Update last processed UID
                self._set_last_processed_uid(uid)

        except Exception as e:
            print(f"InboxMonitor: Error during polling: {e}")
        finally:
            mail.logout()

        return new_replies_count

    def _get_last_processed_uid(self):
        """Retrieves the last processed UID from system logs."""
        logs = self.db.get_latest_system_logs(limit=50)
        for log in logs:
            if log['component'] == 'INBOX' and log['status'] == 'UID_CHECK':
                try:
                    return int(log['message'])
                except:
                    continue
        return 0

    def _set_last_processed_uid(self, uid):
        """Persists the last processed UID."""
        self.db.log_system_event("INBOX", "UID_CHECK", str(uid))

    def _process_email(self, msg, uid):
        """Matches incoming email to a lead and routes to SentimentAnalyzer."""
        # Extract sender
        from_header = msg.get("From")
        sender_email = email.utils.parseaddr(from_header)[1]

        # Extract subject and body
        subject = self._decode_header_value(msg.get("Subject", ""))
        body = self._get_email_body(msg)

        print(f"InboxMonitor: Processing email from {sender_email} (UID: {uid})")

        # 1. Match by sender email in venue_contacts
        lead = self._match_lead_by_email(sender_email)

        # 2. Fallback: Match by venue name in subject or body
        if not lead:
            lead = self._match_lead_by_venue_name(subject, body)

        # 3. Bounce Detection
        if self._is_bounce(sender_email, subject, body):
            self._handle_bounce(subject, body, uid)
            return True

        if lead:
            print(f"  Matched to lead_id: {lead['id']} (Venue: {lead['name']})")
            # Route to SentimentAnalyzer
            self.analyzer.process_new_reply(lead['id'], f"Subject: {subject}\n\n{body}")
            self.db.log_system_event("INBOX", "MATCH_SUCCESS", f"UID {uid} matched to lead {lead['id']}")
            return True
        else:
            print(f"  Could not match email to any active lead. Storing as unmatched.")
            self.db.add_unmatched_reply(sender_email, subject, body)
            self.db.log_system_event("INBOX", "MATCH_FAILURE", f"UID {uid} from {sender_email} unmatched (Stored)")
            return False

    def _decode_header_value(self, value):
        decoded = decode_header(value)
        parts = []
        for content, charset in decoded:
            if isinstance(content, bytes):
                parts.append(content.decode(charset or 'utf-8', errors='ignore'))
            else:
                parts.append(content)
        return "".join(parts)

    def _get_email_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    return part.get_payload(decode=True).decode(errors='ignore')
        else:
            return msg.get_payload(decode=True).decode(errors='ignore')
        return ""

    def _match_lead_by_email(self, sender_email):
        """Finds a lead whose venue contact email matches the sender."""
        query = """
        SELECT l.*, v.name
        FROM outreach_leads l
        JOIN venues v ON l.venue_id = v.id
        JOIN venue_contacts vc ON v.id = vc.venue_id
        WHERE vc.email LIKE ?
        LIMIT 1
        """
        with self.db._get_connection() as conn:
            conn.row_factory = email_sqlite_row_factory
            cursor = conn.execute(query, (f"%{sender_email}%",))
            return cursor.fetchone()

    def _match_lead_by_venue_name(self, subject, body):
        """Attempts to match a lead by venue name mentioned in the email."""
        # Get all active leads
        query = """
        SELECT l.*, v.name
        FROM outreach_leads l
        JOIN venues v ON l.venue_id = v.id
        WHERE l.pipeline_status IN ('SENT', 'APPROVED', 'PENDING_REVIEW')
        """
        with self.db._get_connection() as conn:
            conn.row_factory = email_sqlite_row_factory
            cursor = conn.execute(query)
            leads = cursor.fetchall()

        combined_text = (subject + " " + body).lower()
        for lead in leads:
            if lead['name'].lower() in combined_text:
                return lead
        return None

    def _is_bounce(self, sender, subject, body):
        """Detects if an email is an SMTP bounce/delivery failure."""
        bounce_senders = ["mailer-daemon@", "postmaster@", "noreply@"]
        bounce_keywords = [
            "delivery status notification",
            "delivery failure",
            "undelivered mail",
            "returned mail",
            "message not delivered",
            "address not found",
            "mailbox unavailable"
        ]

        sender_lower = sender.lower()
        if any(b in sender_lower for b in bounce_senders):
            return True

        subject_lower = subject.lower()
        if any(k in subject_lower for k in bounce_keywords):
            return True

        return False

    def _handle_bounce(self, subject, body, uid):
        """Extracts the original recipient from a bounce and marks the lead."""
        import re
        # Try to find an email address in the body that matches an active lead
        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", body.lower())

        matched_lead = None
        for email_addr in emails:
            lead = self._match_lead_by_email(email_addr)
            if lead:
                matched_lead = lead
                break

        if matched_lead:
            print(f"  Bounce detected for lead {matched_lead['id']} ({email_addr})")
            self.db.update_lead_status(matched_lead['id'], 'BOUNCED')
            self.db.log_system_event("INBOX", "BOUNCE_DETECTED", f"UID {uid} marked lead {matched_lead['id']} as BOUNCED")
        else:
            print(f"  Bounce detected but could not identify lead.")
            self.db.log_system_event("INBOX", "BOUNCE_UNMATCHED", f"UID {uid} bounce from postmaster unmatched")

def email_sqlite_row_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
