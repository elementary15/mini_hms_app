from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Ensure credentials.json is in the same folder as this script
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    SCOPES
)

# Force localhost and 8080 to match your Google Console exactly
creds = flow.run_local_server(
    host='localhost',
    port=8080, 
    authorization_prompt_message='Please visit this URL: {url}',
    success_message='Success! You can close this tab.'
)

print("Authentication successful!")