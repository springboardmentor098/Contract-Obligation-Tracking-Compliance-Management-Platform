"""
Basic SMTP email sending (Sprint 12, section 15).

Credentials are read from environment variables via app.config.settings —
never hard-code them. A failure to send email is logged and swallowed so
that it never crashes the calling API request (section 22, Email Delivery
Failure handling).
"""

import logging
import smtplib
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("contractiq.email")


def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME:
        logger.warning("SMTP not configured; skipping email to %s: %s", to_email, subject)
        return False

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM
    message["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], message.as_string())
        return True
    except Exception:  # noqa: BLE001 - never let email failures break the request
        logger.exception("Failed to send email to %s", to_email)
        return False
