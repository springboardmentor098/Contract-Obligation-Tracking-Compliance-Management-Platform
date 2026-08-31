import os
import smtplib
from email.message import EmailMessage


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")

    if not host or not username or not password:
        print("SMTP is not configured. Email skipped.")
        return False

    try:
        message = EmailMessage()
        message["From"] = username
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(message)

        return True

    except Exception as exc:
        print(f"Email delivery failed: {exc}")
        return False
