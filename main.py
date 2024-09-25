# main.py
import os
from google_calendar import authenticate_google_calendar, add_or_update_event, fetch_existing_events
from schedule_fetcher import fetch_schedule, fetch_update_time
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta

def main():
    url = 'https://planzajec.wcy.wat.edu.pl/pl/rozklad?date=1727647200&grupa_id=WCY23KA1S4'
    
    # Fetch update time from the webpage
    update_time = fetch_update_time(url)

    lessons_for_calendar = fetch_schedule(url)
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    # Load environment variables from .env file
    load_dotenv()
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")

    # Define the time range to fetch existing events
    now = datetime.now()
    start_time = now.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time = (now + timedelta(days=30)).isoformat() + 'Z'  # Fetch for the next 30 days

    existing_events = fetch_existing_events(service, calendar_id, start_time, end_time)

    # Create a set of existing event summaries for quick lookup
    existing_event_summaries = {event['summary'] for event in existing_events}

    for lesson in lessons_for_calendar:
        # Append update time to the description
        if update_time:
            lesson['description'] += f"\n\nData aktualizacji: {update_time}"
        if lesson['summary'] in existing_event_summaries:
            # Update the existing event
            print(f'Updating existing event: {lesson["summary"]}')
            add_or_update_event(service, lesson, calendar_id)
        else:
            # Create a new event
            print(f'Creating new event: {lesson["summary"]}')
            add_or_update_event(service, lesson, calendar_id)

    # Optionally, handle deletions for events not in fetched lessons
    for event in existing_events:
        if event['summary'] not in {lesson['summary'] for lesson in lessons_for_calendar}:
            print(f'Deleting event: {event["summary"]}')
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()


if __name__ == "__main__":
    main()