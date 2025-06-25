"""
Notes feature for Astra Voice Assistant
Handles note-taking, searching, and management
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class NotesFeature:
    def __init__(self, data_dir: str = "data/notes"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.notes_file = self.data_dir / "notes.json"
        self.notes = self._load_notes()
        
    def _load_notes(self) -> List[Dict]:
        """Load notes from JSON file"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_notes(self):
        """Save notes to JSON file"""
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving notes: {e}")
    
    def create_note(self, title: str, content: str, tags: List[str] = None) -> Dict:
        """Create a new note"""
        note = {
            'id': len(self.notes) + 1,
            'title': title,
            'content': content,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.notes.append(note)
        self._save_notes()
        return note
    
    def update_note(self, note_id: int, title: str = None, content: str = None, tags: List[str] = None) -> Optional[Dict]:
        """Update an existing note"""
        for note in self.notes:
            if note['id'] == note_id:
                if title:
                    note['title'] = title
                if content:
                    note['content'] = content
                if tags is not None:
                    note['tags'] = tags
                note['updated_at'] = datetime.now().isoformat()
                self._save_notes()
                return note
        return None
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        for i, note in enumerate(self.notes):
            if note['id'] == note_id:
                del self.notes[i]
                self._save_notes()
                return True
        return False
    
    def get_note(self, note_id: int) -> Optional[Dict]:
        """Get a specific note"""
        for note in self.notes:
            if note['id'] == note_id:
                return note
        return None
    
    def list_notes(self, limit: int = 10) -> List[Dict]:
        """List recent notes"""
        return sorted(self.notes, key=lambda x: x['updated_at'], reverse=True)[:limit]
    
    def search_notes(self, query: str) -> List[Dict]:
        """Search notes by title, content, or tags"""
        query = query.lower()
        results = []
        
        for note in self.notes:
            if (query in note['title'].lower() or 
                query in note['content'].lower() or
                any(query in tag.lower() for tag in note['tags'])):
                results.append(note)
        
        return sorted(results, key=lambda x: x['updated_at'], reverse=True)
    
    def get_notes_by_tag(self, tag: str) -> List[Dict]:
        """Get notes by tag"""
        return [note for note in self.notes if tag.lower() in [t.lower() for t in note['tags']]]
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        tags = set()
        for note in self.notes:
            tags.update(note['tags'])
        return sorted(list(tags))

def handle_notes_command(text: str) -> Tuple[str, Dict]:
    """Handle notes-related voice commands"""
    text = text.lower()
    
    # Initialize notes feature
    notes = NotesFeature()
    
    # Create note
    if any(word in text for word in ['create note', 'new note', 'take note', 'write note']):
        # Extract title and content
        title_match = re.search(r'(?:create|new|take|write)\s+note\s+(?:titled\s+)?["\']?([^"\']+)["\']?', text)
        content_match = re.search(r'(?:content|saying|about)\s+["\']?([^"\']+)["\']?', text)
        
        title = title_match.group(1) if title_match else "Untitled Note"
        content = content_match.group(1) if content_match else "No content provided"
        
        # Extract tags
        tags = []
        tag_matches = re.findall(r'#(\w+)', text)
        tags.extend(tag_matches)
        
        note = notes.create_note(title, content, tags)
        
        response = f"I've created a note titled '{note['title']}' with {len(tags)} tags."
        return response, {'action': 'note_created', 'note': note}
    
    # Search notes
    elif any(word in text for word in ['find note', 'search note', 'look for note']):
        query_match = re.search(r'(?:find|search|look for)\s+note\s+(?:about\s+)?["\']?([^"\']+)["\']?', text)
        if query_match:
            query = query_match.group(1)
            results = notes.search_notes(query)
            
            if results:
                response = f"I found {len(results)} notes matching '{query}':\n"
                for i, note in enumerate(results[:5], 1):
                    response += f"{i}. {note['title']} (updated {note['updated_at'][:10]})\n"
            else:
                response = f"I couldn't find any notes matching '{query}'."
        else:
            response = "What would you like me to search for in your notes?"
        
        return response, {'action': 'notes_searched', 'query': query_match.group(1) if query_match else None}
    
    # List notes
    elif any(word in text for word in ['list notes', 'show notes', 'my notes', 'all notes']):
        all_notes = notes.list_notes(10)
        
        if all_notes:
            response = f"You have {len(all_notes)} recent notes:\n"
            for i, note in enumerate(all_notes, 1):
                response += f"{i}. {note['title']} (updated {note['updated_at'][:10]})\n"
        else:
            response = "You don't have any notes yet. Would you like me to create one for you?"
        
        return response, {'action': 'notes_listed', 'count': len(all_notes)}
    
    # Delete note
    elif any(word in text for word in ['delete note', 'remove note', 'erase note']):
        # Try to find note by title or ID
        title_match = re.search(r'(?:delete|remove|erase)\s+note\s+(?:titled\s+)?["\']?([^"\']+)["\']?', text)
        id_match = re.search(r'(?:delete|remove|erase)\s+note\s+(\d+)', text)
        
        if id_match:
            note_id = int(id_match.group(1))
            note = notes.get_note(note_id)
            if note and notes.delete_note(note_id):
                response = f"I've deleted the note '{note['title']}'."
            else:
                response = f"I couldn't find a note with ID {note_id}."
        elif title_match:
            title = title_match.group(1)
            # Find note by title
            for note in notes.notes:
                if title.lower() in note['title'].lower():
                    if notes.delete_note(note['id']):
                        response = f"I've deleted the note '{note['title']}'."
                        break
            else:
                response = f"I couldn't find a note titled '{title}'."
        else:
            response = "Which note would you like me to delete? Please specify the title or ID."
        
        return response, {'action': 'note_deleted'}
    
    # Show note content
    elif any(word in text for word in ['read note', 'show note', 'open note']):
        title_match = re.search(r'(?:read|show|open)\s+note\s+(?:titled\s+)?["\']?([^"\']+)["\']?', text)
        id_match = re.search(r'(?:read|show|open)\s+note\s+(\d+)', text)
        
        if id_match:
            note_id = int(id_match.group(1))
            note = notes.get_note(note_id)
            if note:
                response = f"Note: {note['title']}\n\n{note['content']}\n\nTags: {', '.join(note['tags']) if note['tags'] else 'None'}"
            else:
                response = f"I couldn't find a note with ID {note_id}."
        elif title_match:
            title = title_match.group(1)
            # Find note by title
            for note in notes.notes:
                if title.lower() in note['title'].lower():
                    response = f"Note: {note['title']}\n\n{note['content']}\n\nTags: {', '.join(note['tags']) if note['tags'] else 'None'}"
                    break
            else:
                response = f"I couldn't find a note titled '{title}'."
        else:
            response = "Which note would you like me to read? Please specify the title or ID."
        
        return response, {'action': 'note_read'}
    
    # List tags
    elif any(word in text for word in ['list tags', 'show tags', 'my tags']):
        tags = notes.get_all_tags()
        
        if tags:
            response = f"You have {len(tags)} tags:\n{', '.join(tags)}"
        else:
            response = "You don't have any tags yet."
        
        return response, {'action': 'tags_listed', 'tags': tags}
    
    # Notes by tag
    elif 'notes with tag' in text or 'notes tagged' in text:
        tag_match = re.search(r'(?:notes with tag|notes tagged)\s+["\']?([^"\']+)["\']?', text)
        if tag_match:
            tag = tag_match.group(1)
            tagged_notes = notes.get_notes_by_tag(tag)
            
            if tagged_notes:
                response = f"I found {len(tagged_notes)} notes with tag '{tag}':\n"
                for i, note in enumerate(tagged_notes, 1):
                    response += f"{i}. {note['title']} (updated {note['updated_at'][:10]})\n"
            else:
                response = f"I couldn't find any notes with tag '{tag}'."
        else:
            response = "Which tag would you like me to search for?"
        
        return response, {'action': 'notes_by_tag', 'tag': tag_match.group(1) if tag_match else None}
    
    # Default response
    else:
        response = """I can help you with notes! Here's what I can do:
- Create a new note: "Create note titled [title] about [content]"
- Search notes: "Find note about [topic]"
- List notes: "Show my notes"
- Read a note: "Read note [title or ID]"
- Delete a note: "Delete note [title or ID]"
- List tags: "Show my tags"
- Find notes by tag: "Show notes with tag [tag]"

What would you like to do with your notes?"""
        
        return response, {'action': 'notes_help'}

# Feature registration
FEATURE_INFO = {
    'name': 'notes',
    'description': 'Create, search, and manage text notes with tags',
    'keywords': ['note', 'notes', 'write', 'create', 'search', 'find', 'delete', 'tag', 'tags'],
    'examples': [
        'Create a note titled "Meeting Notes" about the project discussion',
        'Find notes about weather',
        'Show my notes',
        'Read note "Shopping List"',
        'Delete note 5',
        'Show notes with tag work'
    ]
} 