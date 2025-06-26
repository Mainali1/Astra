"""
Astra AI Assistant - Notes Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class Note:
    """Represents a single note."""

    def __init__(
        self, content: str, title: Optional[str] = None, note_id: Optional[str] = None, tags: Optional[List[str]] = None
    ):
        """Initialize a note."""
        self.id = note_id or str(int(datetime.now().timestamp()))
        self.title = title or f"Note {self.id}"
        self.content = content
        self.tags = tags or []
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        """Create note from dictionary."""
        note = cls(content=data["content"], title=data["title"], note_id=data["id"], tags=data["tags"])
        note.created_at = datetime.fromisoformat(data["created_at"])
        note.updated_at = datetime.fromisoformat(data["updated_at"])
        return note


class NotesFeature:
    """Notes feature for Astra."""

    def __init__(self, config: Config):
        """Initialize the notes feature."""
        self.config = config
        self.notes: List[Note] = []
        self.data_file = Path(config.DATA_DIR) / "notes.json"
        self._load_notes()

    def _load_notes(self):
        """Load notes from file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.notes = [Note.from_dict(n) for n in data]
                    logger.info(f"Loaded {len(self.notes)} notes")
        except Exception as e:
            logger.error(f"Error loading notes: {str(e)}")

    def _save_notes(self):
        """Save notes to file."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w") as f:
                json.dump([n.to_dict() for n in self.notes], f)
        except Exception as e:
            logger.error(f"Error saving notes: {str(e)}")

    def _find_note(self, identifier: str) -> Optional[Note]:
        """Find a note by ID or title."""
        for note in self.notes:
            if note.id == identifier or note.title.lower() == identifier.lower():
                return note
        return None

    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle note-related intents."""
        try:
            action = intent.get("action", "")
            params = intent.get("parameters", {})

            if action == "create_note":
                # Create new note
                content = params.get("content", "")
                title = params.get("title")
                tags = params.get("tags", "").split(",") if params.get("tags") else []

                if not content:
                    return "I need some content to create a note."

                note = Note(content=content, title=title, tags=tags)
                self.notes.append(note)
                self._save_notes()

                return f"Created note '{note.title}' with ID {note.id}"

            elif action == "read_note":
                # Read existing note
                identifier = params.get("identifier", "")
                if not identifier:
                    return "Which note would you like to read?"

                note = self._find_note(identifier)
                if note:
                    return f"Note '{note.title}':\n{note.content}"
                return f"I couldn't find a note matching '{identifier}'"

            elif action == "update_note":
                # Update existing note
                identifier = params.get("identifier", "")
                content = params.get("content", "")

                if not identifier or not content:
                    return "I need both the note identifier and new content to update a note."

                note = self._find_note(identifier)
                if note:
                    note.content = content
                    note.updated_at = datetime.now()
                    self._save_notes()
                    return f"Updated note '{note.title}'"
                return f"I couldn't find a note matching '{identifier}'"

            elif action == "delete_note":
                # Delete note
                identifier = params.get("identifier", "")
                if not identifier:
                    return "Which note would you like to delete?"

                note = self._find_note(identifier)
                if note:
                    self.notes.remove(note)
                    self._save_notes()
                    return f"Deleted note '{note.title}'"
                return f"I couldn't find a note matching '{identifier}'"

            elif action == "list_notes":
                # List all notes
                if not self.notes:
                    return "You don't have any notes."

                response = "Here are your notes:\n"
                for note in sorted(self.notes, key=lambda x: x.updated_at, reverse=True):
                    tags = f" [Tags: {', '.join(note.tags)}]" if note.tags else ""
                    response += f"- {note.title}{tags}\n"
                return response

            elif action == "search_notes":
                # Search notes
                query = params.get("query", "").lower()
                if not query:
                    return "What would you like to search for in your notes?"

                matches = []
                for note in self.notes:
                    if (
                        query in note.title.lower()
                        or query in note.content.lower()
                        or any(query in tag.lower() for tag in note.tags)
                    ):
                        matches.append(note)

                if not matches:
                    return f"No notes found matching '{query}'"

                response = f"Found {len(matches)} matching notes:\n"
                for note in matches:
                    response += f"- {note.title}\n"
                return response

            else:
                return "I'm not sure what you want to do with notes."

        except Exception as e:
            logger.error(f"Error handling notes request: {str(e)}")
            return "I'm sorry, but I encountered an error processing your notes request."

    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Notes feature is always available as it's offline

    async def cleanup(self):
        """Clean up resources."""
        self._save_notes()
