import json
import smtplib
from email.message import EmailMessage
import os


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(to_email, subject, body):
    print("SMTP_USER:", os.environ.get("SMTP_USER"))
    print("SMTP_PASS exists:", "SMTP_PASS" in os.environ)

    msg = EmailMessage()
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    print("Connecting to SMTP...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        server.set_debuglevel(1)
        server.starttls()
        print("Logging in...")
        server.login(
            os.environ["SMTP_USER"],
            os.environ["SMTP_PASS"]
        )
        print("Sending email...")
        server.send_message(msg)

def handler(event, context):
    try:
        body = json.loads(event["body"])

        email_type = body["type"]
        to_email = body["to"]
        data = body.get("data", {})

        if email_type == "SIGNUP_WELCOME":
            subject = "Welcome to Mini HMS"
            content = f"""
Hi,

Welcome to Mini Hospital Management System.
Your account has been successfully created.

Regards,
Mini HMS Team
"""

        elif email_type == "BOOKING_CONFIRMATION":
            subject = "Appointment Confirmed"
            content = f"""
Hi,

Your appointment has been confirmed.

Doctor: {data.get("doctor")}
Date: {data.get("date")}
Time: {data.get("time")}

Regards,
Mini HMS Team
"""

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid email type"})
            }

        send_email(to_email, subject, content)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email sent"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
