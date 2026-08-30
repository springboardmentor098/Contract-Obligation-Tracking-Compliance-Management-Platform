import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_email(
    to_email: str,
    subject: str,
    message: str
):
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_host or not smtp_username or not smtp_password:
            print("SMTP configuration is missing")
            return False

        email = EmailMessage()

        email["From"] = smtp_username
        email["To"] = to_email
        email["Subject"] = subject

        email.set_content(message)

        with smtplib.SMTP(smtp_host, smtp_port) as server:

            server.starttls()

            server.login(
                smtp_username,
                smtp_password
            )

            server.send_message(email)

        print(f"Email sent successfully to {to_email}")

        return True

    except Exception as e:
        print(f"Email sending failed: {e}")

        return False