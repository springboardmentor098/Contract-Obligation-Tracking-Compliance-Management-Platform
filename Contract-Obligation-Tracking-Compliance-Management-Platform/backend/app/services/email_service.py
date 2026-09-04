import os
import smtplib
from email.message import EmailMessage


def send_email(
    recipient_email: str,
    subject: str,
    body: str,
) -> bool:

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(
        os.getenv("SMTP_PORT", "587")
    )
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_host:
        raise RuntimeError(
            "SMTP_HOST is not configured"
        )

    if not smtp_username:
        raise RuntimeError(
            "SMTP_USERNAME is not configured"
        )

    if not smtp_password:
        raise RuntimeError(
            "SMTP_PASSWORD is not configured"
        )

    message = EmailMessage()

    message["From"] = smtp_username
    message["To"] = recipient_email
    message["Subject"] = subject

    message.set_content(body)

    try:
        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=20,
        ) as server:

            server.starttls()

            server.login(
                smtp_username,
                smtp_password,
            )

            server.send_message(message)

        return True

    except Exception as exc:
        print(
            f"Email delivery failed: {exc}"
        )
        return False