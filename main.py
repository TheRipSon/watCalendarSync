# main.py

import os
from google_calendar import authenticate_google_calendar, add_or_update_event, fetch_existing_events
from schedule_fetcher import fetch_schedule, fetch_update_time
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta

def get_calendar_id(lesson_info):
    """
    Determine the appropriate calendar based on the lesson type.
    """
    if "Laboratorium" in lesson_info:
        return os.getenv("LABORATORIUM_CALENDAR_ID")
    elif "Wykład" in lesson_info:
        return os.getenv("WYKLAD_CALENDAR_ID")
    elif "Ćwiczenia" in lesson_info:
        return os.getenv("CWICZENIA_CALENDAR_ID")
    elif "Projekt" in lesson_info:
        return os.getenv("PROJEKT_CALENDAR_ID")
    else:
        # Default to the 'Wykład' calendar for unknown types
        return os.getenv("WYKLAD_CALENDAR_ID")

def main():
    url = 'https://planzajec.wcy.wat.edu.pl/pl/rozklad?date=1727647200&grupa_id=WCY23KA1S4'
    
    # Fetch update time from the webpage
    update_time = fetch_update_time(url)

    lessons_for_calendar = fetch_schedule(url)
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    # Load environment variables from .env file
    load_dotenv()

    # Define the time range to fetch existing events
    now = datetime.now()
    start_time = now.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time = (now + timedelta(days=30)).isoformat() + 'Z'  # Fetch for the next 30 days

    # Process each lesson and assign to the appropriate calendar
    for lesson in lessons_for_calendar:
        # Append update time to the description
        if update_time:
            lesson['description'] += f"\n\nData aktualizacji: {update_time}"
        
        # Get the appropriate calendar ID based on the lesson type
        calendar_id = get_calendar_id(lesson['description'])

        # Add or update the event in the calendar
        add_or_update_event(service, lesson, calendar_id)

    # Now, check each calendar for events that should be deleted
    all_calendar_ids = [
        os.getenv("LABORATORIUM_CALENDAR_ID"),
        os.getenv("WYKLAD_CALENDAR_ID"),
        os.getenv("CWICZENIA_CALENDAR_ID"),
        os.getenv("PROJEKT_CALENDAR_ID")
    ]

    # Get the summaries of all lessons that should be in the calendarhttps://calendar.google.com/calendar/ical/6c418b350014271b934e76cdd1483673b796183c6ae6c445237e36c99443b2fc%40group.calendar.google.com/public/basic.icshttps://calendar.google.com/calendar/ical/6c418b350014271b934e76cdd1483673b796183c6ae6c445237e36c99443b2fc%40group.calendar.google.com/public/basic.ics
    fetched_lesson_summaries = {lesson['summary'] for lesson in lessons_for_calendar}

    for calendar_id in all_calendar_ids:
        # Fetch existing events in this calendar
        existing_events = fetch_existing_events(service, calendar_id, start_time, end_time)
        
        for event in existing_events:
            # If the event is not in the current schedule, delete it
            if event['summary'] not in fetched_lesson_summaries:
                print(f'Deleting event from {calendar_id}: {event["summary"]}')
                service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()

if __name__ == "__main__":
    main()

