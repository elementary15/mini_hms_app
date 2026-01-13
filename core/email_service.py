import requests


EMAIL_SERVICE_URL = "http://localhost:3000/send-email"


def send_email(email_type, to_email, data=None):
    payload = {
        "type": email_type,
        "to": to_email,
        "data": data or {}
    }

    try:
        requests.post(
            EMAIL_SERVICE_URL,
            json=payload,
            timeout=3
        )
    except Exception as e:
        # Email failure should NOT break main flow
        print("[Email Service Error]", e)
