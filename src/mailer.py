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

    def send_email(self, to_email, subject, body):
        if not all([self.smtp_server, self.smtp_user, self.smtp_password, self.sender_email]):
            print("SMTP configuration missing. Skipping email send.")
            return False

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

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
