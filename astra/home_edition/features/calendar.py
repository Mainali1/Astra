from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from astra.core.database import database_manager, CalendarEvent

def add_event(user_id: int, title: str, start_time: datetime, end_time: datetime, description: Optional[str] = None) -> CalendarEvent:
    """
    Adds an event to the calendar for a specific user.

    :param user_id: The ID of the user.
    :param title: The title of the event.
    :param start_time: The start time of the event.
    :param end_time: The end time of the event.
    :param description: The description of the event.
    :return: The created event.
    """
    with database_manager.get_session() as session:
        event = CalendarEvent(
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return event

def get_events(user_id: int, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
    """
    Gets all events for a user within a given date range.

    :param user_id: The ID of the user.
    :param start_date: The start of the date range.
    :param end_date: The end of the date range.
    :return: A list of events.
    """
    with database_manager.get_session() as session:
        return session.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= start_date,
            CalendarEvent.end_time <= end_date
        ).all()

def delete_event(user_id: int, event_id: int) -> bool:
    """
    Deletes an event for a specific user.

    :param user_id: The ID of the user.
    :param event_id: The ID of the event to delete.
    :return: True if the event was deleted, False otherwise.
    """
    with database_manager.get_session() as session:
        event = session.query(CalendarEvent).filter(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == user_id
        ).first()
        if event:
            session.delete(event)
            session.commit()
            return True
        return False