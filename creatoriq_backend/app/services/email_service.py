import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> bool:
    """
    Send a plain-text email using the configured SMTP server.

    Returns:
        True  - email sent successfully
        False - email sending failed
    """

    message = EmailMessage()

    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
        ) as smtp:

            smtp.starttls()

            smtp.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

            smtp.send_message(message)

        return True

    except Exception as exc:
        print(f"Email sending failed: {exc}")
        return False