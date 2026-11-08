import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class Mailer:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        port = os.getenv("SMTP_PORT")
        self.smtp_port = int(port) if port and port.strip() else 587
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")


    def send_email(self, to_email, subject, body, lead_id=None, base_url=None):
        if not all([self.smtp_server, self.smtp_user, self.smtp_password, self.sender_email]):
            print("SMTP configuration missing. Skipping email send (Simulated Success).")
            return True  # Force true for testing without real credentials

        message = MIMEMultipart("alternative")
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = subject

        # Plain text version
        message.attach(MIMEText(body, "plain"))

        # HTML version with tracking pixel and wrapped hyperlinks if lead_id is provided
        if lead_id is not None:
            host_url = base_url or os.getenv("APP_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
            html_body = self._build_tracked_html_body(body, lead_id, host_url)
            message.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    @staticmethod
    def _build_tracked_html_body(plain_text: str, lead_id: int, base_url: str) -> str:
        """Converts plain text pitch into HTML with tracking pixel and link wrappers."""
        import html
        import re
        import urllib.parse

        # Escape raw text
        escaped_text = html.escape(plain_text)

        # Wrap URLs with click tracking redirect: {base_url}/track/click/{lead_id}?url={encoded_url}
        def wrap_url(match):
            raw_url = match.group(0)
            encoded = urllib.parse.quote(raw_url, safe="")
            tracked = f"{base_url}/track/click/{lead_id}?url={encoded}"
            return f'<a href="{tracked}" target="_blank" style="color: #00d2ff; text-decoration: underline;">{raw_url}</a>'

        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        linked_text = url_pattern.sub(wrap_url, escaped_text)

        # Convert line breaks
        formatted_content = linked_text.replace("\n", "<br/>")

        # Transparent 1x1 GIF tracking pixel
        pixel_url = f"{base_url}/track/open/{lead_id}.gif"
        tracking_pixel = f'<img src="{pixel_url}" width="1" height="1" alt="" style="display:none;width:1px;height:1px;border:0;" />'

        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.6; color: #222;">
    <div>
        {formatted_content}
    </div>
    {tracking_pixel}
</body>
</html>"""
        return html_template
