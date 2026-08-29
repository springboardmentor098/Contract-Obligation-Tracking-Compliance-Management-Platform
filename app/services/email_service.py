from app.core.config import settings
import smtplib
from email.mime.text import MIMEText


def send_notification_email(
    to_email: str,
    subject: str,
    message: str
):
    try:
        smtp_host = settings.smtp_host
        smtp_port = settings.smtp_port
        smtp_username = settings.smtp_username
        smtp_password = settings.smtp_password

        if not all([
            smtp_host,
            smtp_username,
            smtp_password
        ]):
            print(
                "SMTP configuration is missing. "
                "Email notification was not sent."
            )
            return False

        email_message = MIMEText(message)

        email_message["Subject"] = subject
        email_message["From"] = "noreply@example.com"
        email_message["To"] = to_email

        with smtplib.SMTP(
            smtp_host,
            smtp_port
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                smtp_username,
                smtp_password
            )

            server.send_message(
                email_message
            )

        print(
            f"Notification email sent to {to_email}"
        )

        return True

    except Exception as error:
        print(
            f"Failed to send notification email: {error}"
        )

        return False