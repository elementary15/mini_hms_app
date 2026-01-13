import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']


def load_credentials_for_user(user_id):
    """
    Load stored OAuth credentials for a given Django user.
    Returns None if the user has not connected Google Calendar.
    """
    token_path = f'google_tokens/user_{user_id}.json'

    if not os.path.exists(token_path):
        print(f"[Calendar] No token found for user {user_id}")
        return None

    return Credentials.from_authorized_user_file(token_path, SCOPES)


def create_calendar_event(creds, title, description, start_dt, end_dt):
    """
    Create an event in the user's primary Google Calendar.
    """
    try:
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }

        service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        print(f"[Calendar] Event created: {title}")

    except Exception as e:
        print("[Calendar ERROR]", e)
