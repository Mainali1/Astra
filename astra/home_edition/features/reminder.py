from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from astra.core.database import database_manager, Base, Column, Integer, String, DateTime, Boolean

class Reminder(Base):
    """
    Reminder model for storing user reminders.
    """
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    message = Column(String(255), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def add_reminder(user_id: int, message: str, remind_at: datetime) -> Reminder:
    """
    Adds a new reminder for a specific user.

    Args:
        user_id: The ID of the user.
        message: The reminder message.
        remind_at: The datetime when the reminder should trigger.

    Returns:
        The created Reminder object.
    """
    with database_manager.get_session() as session:
        reminder = Reminder(
            user_id=user_id,
            message=message,
            remind_at=remind_at
        )
        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        return reminder

def get_active_reminders(user_id: int) -> List[Reminder]:
    """
    Gets all active reminders for a specific user.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of active Reminder objects.
    """
    with database_manager.get_session() as session:
        return session.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.is_active == True,
            Reminder.remind_at > datetime.utcnow()
        ).all()

def deactivate_reminder(user_id: int, reminder_id: int) -> bool:
    """
    Deactivates a reminder for a specific user.

    Args:
        user_id: The ID of the user.
        reminder_id: The ID of the reminder to deactivate.

    Returns:
        True if the reminder was deactivated, False otherwise.
    """
    with database_manager.get_session() as session:
        reminder = session.query(Reminder).filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        ).first()
        if reminder:
            reminder.is_active = False
            session.commit()
            return True
        return False