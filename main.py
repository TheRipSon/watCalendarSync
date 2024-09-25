# main.py

from google_calendar import authenticate_google_calendar, add_or_update_event
from schedule_fetcher import fetch_schedule

def main():
    # URL of the schedule page
    url = 'https://planzajec.wcy.wat.edu.pl/pl/rozklad?date=1727647200&grupa_id=WCY23KA1S4'
    
    # Fetch the schedule
    lessons_for_calendar = fetch_schedule(url)

    # Authenticate and create a service instance
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    # Loop through each lesson and add/update in Google Calendar
    for lesson in lessons_for_calendar:
        add_or_update_event(service, lesson)

if __name__ == "__main__":
    main()
