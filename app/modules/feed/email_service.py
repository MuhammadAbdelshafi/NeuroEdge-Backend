import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        # In a real app, these would be in settings
        self.sender_email = "noreply@neurologyaggregator.com"
        # For now, we assume console mode if no real credentials are set
        self.console_mode = True 

    def send_email(self, to_email: str, subject: str, body_html: str):
        if self.console_mode:
            self._send_console(to_email, subject, body_html)
        else:
            self._send_smtp(to_email, subject, body_html)

    def _send_console(self, to_email: str, subject: str, body_html: str):
        logger.info("="*60)
        logger.info(f"EMAIL SIMULATION TO: {to_email}")
        logger.info(f"SUBJECT: {subject}")
        logger.info("BODY (Preview):")
        logger.info(body_html[:500] + "...")
        logger.info("="*60)

    def _send_smtp(self, to_email: str, subject: str, body_html: str):
        # Placeholder for actual SMTP implementation
        # implementing this blindly without credentials would fail
        pass

email_service = EmailService()
