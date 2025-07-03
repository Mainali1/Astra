from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from astra.core.database import database_manager, Note

def create_note(user_id: int, title: str, content: Optional[str] = None) -> Note:
    """
    Creates a new note for a specific user.

    Args:
        user_id: The ID of the user.
        title: The title of the note.
        content: The content of the note.

    Returns:
        The created Note object.
    """
    with database_manager.get_session() as session:
        note = Note(
            user_id=user_id,
            title=title,
            content=content
        )
        session.add(note)
        session.commit()
        session.refresh(note)
        return note

def get_note(user_id: int, note_id: int) -> Optional[Note]:
    """
    Gets a specific note for a user.

    Args:
        user_id: The ID of the user.
        note_id: The ID of the note.

    Returns:
        The Note object if found, None otherwise.
    """
    with database_manager.get_session() as session:
        return session.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id
        ).first()

def get_all_notes(user_id: int) -> List[Note]:
    """
    Gets all notes for a specific user.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of Note objects.
    """
    with database_manager.get_session() as session:
        return session.query(Note).filter(Note.user_id == user_id).all()

def update_note(user_id: int, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Note]:
    """
    Updates an existing note for a specific user.

    Args:
        user_id: The ID of the user.
        note_id: The ID of the note to update.
        title: The new title for the note (optional).
        content: The new content for the note (optional).

    Returns:
        The updated Note object if found, None otherwise.
    """
    with database_manager.get_session() as session:
        note = session.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id
        ).first()
        if note:
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            session.commit()
            session.refresh(note)
            return note
        return None

def delete_note(user_id: int, note_id: int) -> bool:
    """
    Deletes a note for a specific user.

    Args:
        user_id: The ID of the user.
        note_id: The ID of the note to delete.

    Returns:
        True if the note was deleted, False otherwise.
    """
    with database_manager.get_session() as session:
        note = session.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id
        ).first()
        if note:
            session.delete(note)
            session.commit()
            return True
        return False