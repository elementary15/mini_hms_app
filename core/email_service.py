import requests


EMAIL_SERVICE_URL = "http://localhost:3000/send-email"


def _render_signup_welcome():
    return """
    <html>
      <body style="font-family: Arial, sans-serif; background:#f9fafb; padding:20px;">
        <div style="max-width:480px; background:#ffffff; padding:20px; border-radius:8px;">
          <h2 style="color:#111827;">Welcome to Mini HMS 👋</h2>
          <p>Your account has been successfully created.</p>
          <p>You can now log in and start using the system.</p>
          <p style="margin-top:24px; color:#6b7280; font-size:14px;">
            — Mini HMS Team
          </p>
        </div>
      </body>
    </html>
    """


def _render_booking_confirmation(data):
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background:#f9fafb; padding:20px;">
        <div style="max-width:480px; background:#ffffff; padding:20px; border-radius:8px;">
          <h2 style="color:#111827;">Appointment Confirmed ✅</h2>
          <p>Your appointment has been successfully booked.</p>

          <div style="margin-top:16px; padding:12px; background:#f3f4f6; border-radius:6px;">
            <p><strong>Doctor:</strong> {data.get("doctor")}</p>
            <p><strong>Date:</strong> {data.get("date")}</p>
            <p><strong>Time:</strong> {data.get("time")}</p>
          </div>

          <p style="margin-top:24px; color:#6b7280; font-size:14px;">
            — Mini HMS Team
          </p>
        </div>
      </body>
    </html>
    """


def send_email(email_type, to_email, data=None):
    data = data or {}

    html_body = None

    if email_type == "SIGNUP_WELCOME":
        html_body = _render_signup_welcome()

    elif email_type == "BOOKING_CONFIRMATION":
        html_body = _render_booking_confirmation(data)

    payload = {
        "type": email_type,
        "to": to_email,
        "data": data,
        "html": html_body
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
