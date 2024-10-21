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
    # Check if we already have token.json for previously authorized credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If credentials are invalid or do not exist, or are expired, refresh or get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("Token refreshed successfully.")
            except Exception as e:
                print(f"Error refreshing token: {e}. Re-authenticating...")
                creds = None  # Clear credentials to re-authenticate if refresh fails
        if not creds:
            # If there's no valid creds or refresh fails, prompt re-authentication
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("Authenticated and obtained new token.")
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def events_are_equal(event1, event2):
    """
    Helper function to check if two events are equal.
    We compare the summary, start time, end time, location, and description.
    """
    return (event1['summary'] == event2['summary'] and
            event1['start'] == event2['start'] and
            event1['end'] == event2['end'] and
            event1.get('location', '') == event2.get('location', '') and
            event1.get('description', '') == event2.get('description', ''))

def add_or_update_event(service, event_dict, calendarId):
    # Fetch existing events matching the summary (to minimize API calls)
    existing_events = service.events().list(calendarId=calendarId, q=event_dict['summary']).execute()
    events = existing_events.get('items', [])

    print(f"Event to insert/update: {event_dict}")  # Debug print

    # Ensure the start time is before the end time
    if event_dict['start']['dateTime'] >= event_dict['end']['dateTime']:
        print("Error: Start time must be before end time.")
        return  # Skip the event if times are incorrect

    if events:
        event = events[0]  # Get the first matching event

        # If the existing event is identical to the new one, skip the update
        if events_are_equal(event, event_dict):
            print(f'Skipping update for identical event: {event["summary"]}')
            return

        # Update relevant fields from event_dict if there's any difference
        event['summary'] = event_dict['summary']
        event['description'] = event_dict['description']
        event['location'] = event_dict.get('location', event.get('location', ''))
        event['start'] = event_dict['start']
        event['end'] = event_dict['end']
        
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
