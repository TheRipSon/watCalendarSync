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

def add_or_update_event(service, event_dict, calendarId):
    existing_events = service.events().list(calendarId=calendarId, q=event_dict['summary']).execute()
    events = existing_events.get('items', [])

    print(f"Event to insert/update: {event_dict}")  # Debug print

    # Ensure the start time is before the end time
    if event_dict['start']['dateTime'] >= event_dict['end']['dateTime']:
        print("Error: Start time must be before end time.")
        return  # Skip the event if times are incorrect

    if events:
        event = events[0]  # Get the first matching event

        # Update relevant fields from event_dict
        event['summary'] = event_dict['summary']
        event['description'] = event_dict['description']
        event['location'] = event_dict.get('location', event.get('location', ''))  # Update location if provided
        event['start'] = event_dict['start']
        event['end'] = event_dict['end']
        
        # Add or update additional fields as necessary
        # event['colorId'] = event_dict.get('colorId', event.get('colorId', ''))
        # Add any other fields you may want to update

        updated_event = service.events().update(calendarId=calendarId, eventId=event['id'], body=event).execute()
        print(f'Event updated: {updated_event.get("htmlLink")}')
    else:
        try:
            created_event = service.events().insert(calendarId=calendarId, body=event_dict).execute()
            print(f'Event created: {created_event.get("htmlLink")}')
        except Exception as e:
            print(f'Error creating event: {e}')

def fetch_existing_events(service, calendar_id, start_time, end_time):
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_time,
                                          timeMax=end_time, singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])
