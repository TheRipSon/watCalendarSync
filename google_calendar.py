# google_calendar.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def add_or_update_event(service, event_dict):
    existing_events = service.events().list(calendarId='primary', q=event_dict['summary']).execute()
    events = existing_events.get('items', [])

    if events:
        event = events[0]
        event['start'] = event_dict['start']
        event['end'] = event_dict['end']
        updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
        print(f'Event updated: {updated_event.get("htmlLink")}')
    else:
        created_event = service.events().insert(calendarId='primary', body=event_dict).execute()
        print(f'Event created: {created_event.get("htmlLink")}')
