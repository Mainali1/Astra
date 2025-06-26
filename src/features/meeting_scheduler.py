import aiohttp
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event
import os

logger = logging.getLogger(__name__)


class MeetingScheduler:
    """Meeting scheduler feature with holiday awareness using Calendarific API."""

    def __init__(self, api_key: str, calendar_dir: str = "data/calendars"):
        self.base_url = "https://calendarific.com/api/v2"
        self.api_key = api_key
        self.calendar_dir = calendar_dir
        self.holidays_cache: Dict[str, List[Dict]] = {}
        self.cache_duration = timedelta(days=1)  # Cache holidays for 1 day
        self.last_cache_update: Optional[datetime] = None

        # Create calendar directory if it doesn't exist
        os.makedirs(calendar_dir, exist_ok=True)

    async def initialize(self):
        """Initialize the scheduler."""
        try:
            # Load any existing calendars
            if not os.path.exists(self.calendar_dir):
                os.makedirs(self.calendar_dir)
            logger.info("Meeting scheduler initialized")
        except Exception as e:
            logger.error(f"Error initializing meeting scheduler: {e}")

    async def get_holidays(self, country: str, year: int) -> List[Dict]:
        """Get holidays for a specific country and year.

        Args:
            country: Country code (e.g., 'US')
            year: Year to get holidays for

        Returns:
            List of holidays with dates and descriptions
        """
        try:
            cache_key = f"{country}_{year}"

            # Check cache first
            if (
                cache_key in self.holidays_cache
                and self.last_cache_update
                and datetime.now() - self.last_cache_update < self.cache_duration
            ):
                return self.holidays_cache[cache_key]

            # Make API request
            async with aiohttp.ClientSession() as session:
                params = {"api_key": self.api_key, "country": country, "year": year}
                async with session.get(f"{self.base_url}/holidays", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        holidays = data.get("response", {}).get("holidays", [])

                        # Update cache
                        self.holidays_cache[cache_key] = holidays
                        self.last_cache_update = datetime.now()

                        logger.info(f"Got {len(holidays)} holidays for {country} {year}")
                        return holidays
                    else:
                        logger.error(f"Failed to fetch holidays: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching holidays: {e}")
            return []

    async def schedule_meeting(
        self,
        title: str,
        start_time: datetime,
        duration: timedelta,
        attendees: List[str],
        description: str = "",
        location: str = "",
        calendar_name: str = "default",
    ) -> bool:
        """Schedule a new meeting.

        Args:
            title: Meeting title
            start_time: Meeting start time
            duration: Meeting duration
            attendees: List of attendee email addresses
            description: Meeting description
            location: Meeting location
            calendar_name: Name of calendar to add meeting to

        Returns:
            True if meeting was scheduled successfully, False otherwise
        """
        try:
            # Create calendar if it doesn't exist
            calendar_path = os.path.join(self.calendar_dir, f"{calendar_name}.ics")
            cal = Calendar()

            if os.path.exists(calendar_path):
                with open(calendar_path, "rb") as f:
                    cal = Calendar.from_ical(f.read())

            # Create event
            event = Event()
            event.add("summary", title)
            event.add("dtstart", start_time)
            event.add("dtend", start_time + duration)
            event.add("description", description)
            event.add("location", location)

            # Add attendees
            for attendee in attendees:
                event.add("attendee", f"MAILTO:{attendee}")

            # Add event to calendar
            cal.add_component(event)

            # Save calendar
            with open(calendar_path, "wb") as f:
                f.write(cal.to_ical())

            logger.info(f"Scheduled meeting: {title}")
            return True
        except Exception as e:
            logger.error(f"Error scheduling meeting: {e}")
            return False

    async def get_meetings(
        self, start_date: datetime, end_date: datetime, calendar_name: str = "default"
    ) -> List[Dict]:
        """Get meetings between two dates.

        Args:
            start_date: Start date to get meetings from
            end_date: End date to get meetings to
            calendar_name: Name of calendar to get meetings from

        Returns:
            List of meetings with details
        """
        try:
            calendar_path = os.path.join(self.calendar_dir, f"{calendar_name}.ics")
            if not os.path.exists(calendar_path):
                return []

            with open(calendar_path, "rb") as f:
                cal = Calendar.from_ical(f.read())

            meetings = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    event_start = component.get("dtstart").dt
                    if start_date <= event_start <= end_date:
                        meetings.append(
                            {
                                "title": str(component.get("summary")),
                                "start": event_start,
                                "end": component.get("dtend").dt,
                                "description": str(component.get("description", "")),
                                "location": str(component.get("location", "")),
                                "attendees": [str(a) for a in component.get("attendee", [])],
                            }
                        )

            logger.info(f"Found {len(meetings)} meetings between {start_date} and {end_date}")
            return meetings
        except Exception as e:
            logger.error(f"Error getting meetings: {e}")
            return []

    async def check_conflicts(
        self, start_time: datetime, duration: timedelta, calendar_name: str = "default", country: str = "US"
    ) -> List[Dict]:
        """Check for scheduling conflicts including holidays.

        Args:
            start_time: Proposed meeting start time
            duration: Proposed meeting duration
            calendar_name: Calendar to check
            country: Country code for holiday checking

        Returns:
            List of conflicts found
        """
        try:
            conflicts = []
            end_time = start_time + duration

            # Check existing meetings
            meetings = await self.get_meetings(start_time, end_time, calendar_name)
            for meeting in meetings:
                if start_time < meeting["end"] and end_time > meeting["start"]:
                    conflicts.append(
                        {"type": "meeting", "title": meeting["title"], "start": meeting["start"], "end": meeting["end"]}
                    )

            # Check holidays
            holidays = await self.get_holidays(country, start_time.year)
            for holiday in holidays:
                holiday_date = datetime.strptime(holiday["date"]["iso"], "%Y-%m-%d").replace(tzinfo=pytz.UTC)

                if holiday_date.date() == start_time.date():
                    conflicts.append({"type": "holiday", "name": holiday["name"], "date": holiday_date})

            logger.info(f"Found {len(conflicts)} conflicts")
            return conflicts
        except Exception as e:
            logger.error(f"Error checking conflicts: {e}")
            return []

    def delete_meeting(self, start_time: datetime, title: str, calendar_name: str = "default") -> bool:
        """Delete a meeting from the calendar.

        Args:
            start_time: Meeting start time
            title: Meeting title
            calendar_name: Calendar name

        Returns:
            True if meeting was deleted, False otherwise
        """
        try:
            calendar_path = os.path.join(self.calendar_dir, f"{calendar_name}.ics")
            if not os.path.exists(calendar_path):
                return False

            with open(calendar_path, "rb") as f:
                cal = Calendar.from_ical(f.read())

            new_cal = Calendar()
            deleted = False

            for component in cal.walk():
                if component.name == "VEVENT":
                    if component.get("dtstart").dt == start_time and str(component.get("summary")) == title:
                        deleted = True
                        continue
                    new_cal.add_component(component)

            if deleted:
                with open(calendar_path, "wb") as f:
                    f.write(new_cal.to_ical())
                logger.info(f"Deleted meeting: {title}")
                return True

            logger.warning(f"Meeting not found: {title}")
            return False
        except Exception as e:
            logger.error(f"Error deleting meeting: {e}")
            return False
