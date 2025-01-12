import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_calendar_service():
    """Gets Google Calendar service using access token from .env."""
    try:
        access_token = os.getenv('GCAL_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("GCAL_ACCESS_TOKEN not found in .env")

        creds = Credentials(
            token=access_token,
            scopes=['https://www.googleapis.com/auth/calendar']
        )

        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def create_calendar_event(summary, description, start_time, end_time, attendees=None, location=None):
    """
    Create a Google Calendar event.
    
    Args:
        summary (str): Title of the event
        description (str): Description of the event
        start_time (datetime): Start time of the event
        end_time (datetime): End time of the event
        attendees (list, optional): List of attendee email addresses
        location (str, optional): Location of the event
    
    Returns:
        dict: Created event object if successful, None otherwise
    """
    try:
        service = get_calendar_service()
        if not service:
            return None

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
        return event

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_calendar_availability(days=14, start_hour=9, end_hour=21):
    """
    Get calendar availability for the specified number of days.
    Returns events in a structured format for easy parsing.
    
    Args:
        days (int): Number of days to look ahead
        start_hour (int): Start of business hours (24h format, default 9 AM)
        end_hour (int): End of business hours (24h format, default 9 PM)
    """
    try:
        service = get_calendar_service()
        if not service:
            return None

        # Calculate time range
        now = datetime.now()
        time_min = now.replace(hour=0, minute=0, second=0, microsecond=0)
        time_max = (now + timedelta(days=days)).replace(hour=23, minute=59, second=59)

        # Get events from calendar
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min.isoformat() + 'Z',
            timeMax=time_max.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        # Format events in a structured way and filter by business hours
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Convert to datetime objects
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            # Only include events that overlap with business hours
            if start_dt.hour >= start_hour or end_dt.hour <= end_hour:
                formatted_events.append({
                    'date': start_dt.strftime('%Y-%m-%d'),
                    'start_time': start_dt.strftime('%I:%M %p'),
                    'end_time': end_dt.strftime('%I:%M %p'),
                    'summary': event['summary']
                })

        # Group events by date
        events_by_date = {}
        current_date = time_min
        while current_date <= time_max:
            date_str = current_date.strftime('%Y-%m-%d')
            events_by_date[date_str] = [
                event for event in formatted_events 
                if event['date'] == date_str
            ]
            current_date += timedelta(days=1)

        return events_by_date

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

if __name__ == "__main__":
    # Create a meeting for tomorrow at 1 PM
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=13, minute=0, second=0, microsecond=0)
    end_time = tomorrow.replace(hour=13, minute=15, second=0, microsecond=0)

    meeting = create_calendar_event(
        summary="Meeting to Sell iPad",
        description="Meeting to discuss and complete iPad sale",
        start_time=start_time,
        end_time=end_time,
        attendees=['example@email.com'],
        location=None
    )

    # Get and print availability
    availability = get_calendar_availability()
    if availability:
        print("\nCalendar Availability for Next 2 Weeks:")
        print("=====================================")
        for date, events in availability.items():
            print(f"\nDate: {date}")
            if events:
                print("Busy times:")
                for event in events:
                    print(f"  - {event['start_time']} to {event['end_time']}: {event['summary']}")
            else:
                print("  No events scheduled")