# backend/utils/email_service.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables (ensure this is called if this file is imported directly)
load_dotenv()

# --- SMTP Email Service Configuration ---
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends an email using the configured SMTP server.
    Requires SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL
    to be set in environment variables.

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The plain text body of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL]):
        print("ERROR: SMTP credentials not fully configured. Skipping email sending.")
        return False

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['Tappointment_toolso'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"SUCCESS: Email sent to {to_email} with subject '{subject}'")
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email to {to_email}: {e}")
        return False

