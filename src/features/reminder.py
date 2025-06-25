"""
Reminder feature for Astra Voice Assistant
Handles setting, managing, and checking reminders
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import threading
import time

class ReminderFeature:
    def __init__(self, data_dir: str = "data/reminders"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reminders_file = self.data_dir / "reminders.json"
        self.reminders = self._load_reminders()
        self.callback = None
        self.monitor_thread = None
        self.running = False
        
    def _load_reminders(self) -> List[Dict]:
        """Load reminders from JSON file"""
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_reminders(self):
        """Save reminders to JSON file"""
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving reminders: {e}")
    
    def set_callback(self, callback):
        """Set callback function for reminder notifications"""
        self.callback = callback
    
    def start_monitoring(self):
        """Start the reminder monitoring thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_reminders, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the reminder monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_reminders(self):
        """Monitor reminders in background thread"""
        while self.running:
            current_time = datetime.now()
            triggered_reminders = []
            
            for reminder in self.reminders:
                if reminder['status'] == 'active':
                    reminder_time = datetime.fromisoformat(reminder['datetime'])
                    if current_time >= reminder_time:
                        triggered_reminders.append(reminder)
                        reminder['status'] = 'triggered'
            
            # Trigger callbacks for due reminders
            for reminder in triggered_reminders:
                if self.callback:
                    self.callback(reminder)
            
            # Save updated reminders
            if triggered_reminders:
                self._save_reminders()
            
            # Check every 30 seconds
            time.sleep(30)
    
    def create_reminder(self, title: str, datetime_str: str, description: str = "") -> Dict:
        """Create a new reminder"""
        reminder = {
            'id': len(self.reminders) + 1,
            'title': title,
            'description': description,
            'datetime': datetime_str,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        self.reminders.append(reminder)
        self._save_reminders()
        return reminder
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder"""
        for i, reminder in enumerate(self.reminders):
            if reminder['id'] == reminder_id:
                del self.reminders[i]
                self._save_reminders()
                return True
        return False
    
    def get_reminder(self, reminder_id: int) -> Optional[Dict]:
        """Get a specific reminder"""
        for reminder in self.reminders:
            if reminder['id'] == reminder_id:
                return reminder
        return None
    
    def list_reminders(self, status: str = 'active', limit: int = 10) -> List[Dict]:
        """List reminders by status"""
        filtered_reminders = [r for r in self.reminders if r['status'] == status]
        return sorted(filtered_reminders, key=lambda x: x['datetime'])[:limit]
    
    def search_reminders(self, query: str) -> List[Dict]:
        """Search reminders by title or description"""
        query = query.lower()
        results = []
        
        for reminder in self.reminders:
            if (query in reminder['title'].lower() or 
                query in reminder['description'].lower()):
                results.append(reminder)
        
        return sorted(results, key=lambda x: x['datetime'])
    
    def _parse_time_expression(self, text: str) -> Optional[datetime]:
        """Parse natural language time expressions"""
        text = text.lower()
        now = datetime.now()
        
        # "in X minutes/hours/days"
        time_patterns = [
            (r'in (\d+) minutes?', lambda m: now + timedelta(minutes=int(m.group(1)))),
            (r'in (\d+) hours?', lambda m: now + timedelta(hours=int(m.group(1)))),
            (r'in (\d+) days?', lambda m: now + timedelta(days=int(m.group(1)))),
            (r'in (\d+) weeks?', lambda m: now + timedelta(weeks=int(m.group(1)))),
        ]
        
        for pattern, func in time_patterns:
            match = re.search(pattern, text)
            if match:
                return func(match)
        
        # "at X o'clock" or "at X AM/PM"
        clock_patterns = [
            (r'at (\d{1,2}):(\d{2})', lambda m: now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)),
            (r'at (\d{1,2}) o\'?clock', lambda m: now.replace(hour=int(m.group(1)), minute=0, second=0, microsecond=0)),
            (r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm)', lambda m: self._parse_12hour(m, now)),
        ]
        
        for pattern, func in clock_patterns:
            match = re.search(pattern, text)
            if match:
                return func(match)
        
        # "tomorrow at X"
        if 'tomorrow' in text:
            tomorrow = now + timedelta(days=1)
            # Remove "tomorrow" and try to parse the rest
            remaining_text = text.replace('tomorrow', '').strip()
            if remaining_text:
                time_result = self._parse_time_expression(remaining_text)
                if time_result:
                    return time_result.replace(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
        
        return None
    
    def _parse_12hour(self, match, base_time: datetime) -> datetime:
        """Parse 12-hour time format"""
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        ampm = match.group(3).lower()
        
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
        
        return base_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

def handle_reminder_command(text: str) -> Tuple[str, Dict]:
    """Handle reminder-related voice commands"""
    text = text.lower()
    
    # Initialize reminder feature
    reminders = ReminderFeature()
    
    # Set reminder
    if any(word in text for word in ['set reminder', 'create reminder', 'new reminder', 'remind me']):
        # Extract title and time
        title_match = re.search(r'(?:set|create|new)\s+reminder\s+(?:for\s+)?["\']?([^"\']+)["\']?', text)
        time_match = re.search(r'(?:at|in|on)\s+["\']?([^"\']+)["\']?', text)
        
        if title_match and time_match:
            title = title_match.group(1)
            time_expr = time_match.group(1)
            
            # Parse the time expression
            reminder_time = reminders._parse_time_expression(time_expr)
            
            if reminder_time:
                # Extract description if present
                description = ""
                desc_match = re.search(r'(?:about|regarding|for)\s+["\']?([^"\']+)["\']?', text)
                if desc_match:
                    description = desc_match.group(1)
                
                reminder = reminders.create_reminder(title, reminder_time.isoformat(), description)
                
                response = f"I've set a reminder for '{reminder['title']}' at {reminder_time.strftime('%I:%M %p on %B %d, %Y')}."
                return response, {'action': 'reminder_created', 'reminder': reminder}
            else:
                response = f"I couldn't understand the time '{time_expr}'. Please try again with a clearer time expression."
                return response, {'action': 'time_parse_error', 'time_expr': time_expr}
        else:
            response = "Please specify what to remind you about and when. For example: 'Set reminder for meeting at 3 PM'"
            return response, {'action': 'incomplete_reminder'}
    
    # List reminders
    elif any(word in text for word in ['list reminders', 'show reminders', 'my reminders', 'all reminders']):
        active_reminders = reminders.list_reminders('active')
        
        if active_reminders:
            response = f"You have {len(active_reminders)} active reminders:\n"
            for i, reminder in enumerate(active_reminders, 1):
                reminder_time = datetime.fromisoformat(reminder['datetime'])
                response += f"{i}. {reminder['title']} at {reminder_time.strftime('%I:%M %p on %B %d')}\n"
        else:
            response = "You don't have any active reminders."
        
        return response, {'action': 'reminders_listed', 'count': len(active_reminders)}
    
    # Delete reminder
    elif any(word in text for word in ['delete reminder', 'remove reminder', 'cancel reminder']):
        # Try to find reminder by title or ID
        title_match = re.search(r'(?:delete|remove|cancel)\s+reminder\s+(?:for\s+)?["\']?([^"\']+)["\']?', text)
        id_match = re.search(r'(?:delete|remove|cancel)\s+reminder\s+(\d+)', text)
        
        if id_match:
            reminder_id = int(id_match.group(1))
            reminder = reminders.get_reminder(reminder_id)
            if reminder and reminders.delete_reminder(reminder_id):
                response = f"I've deleted the reminder '{reminder['title']}'."
            else:
                response = f"I couldn't find a reminder with ID {reminder_id}."
        elif title_match:
            title = title_match.group(1)
            # Find reminder by title
            for reminder in reminders.reminders:
                if title.lower() in reminder['title'].lower():
                    if reminders.delete_reminder(reminder['id']):
                        response = f"I've deleted the reminder '{reminder['title']}'."
                        break
            else:
                response = f"I couldn't find a reminder for '{title}'."
        else:
            response = "Which reminder would you like me to delete? Please specify the title or ID."
        
        return response, {'action': 'reminder_deleted'}
    
    # Check reminders
    elif any(word in text for word in ['check reminders', 'any reminders', 'due reminders']):
        # Check for reminders due in the next hour
        now = datetime.now()
        due_soon = []
        
        for reminder in reminders.reminders:
            if reminder['status'] == 'active':
                reminder_time = datetime.fromisoformat(reminder['datetime'])
                if reminder_time <= now + timedelta(hours=1):
                    due_soon.append(reminder)
        
        if due_soon:
            response = f"You have {len(due_soon)} reminder(s) due soon:\n"
            for reminder in due_soon:
                reminder_time = datetime.fromisoformat(reminder['datetime'])
                response += f"- {reminder['title']} at {reminder_time.strftime('%I:%M %p')}\n"
        else:
            response = "You don't have any reminders due in the next hour."
        
        return response, {'action': 'reminders_checked', 'due_soon': len(due_soon)}
    
    # Search reminders
    elif any(word in text for word in ['find reminder', 'search reminder', 'look for reminder']):
        query_match = re.search(r'(?:find|search|look for)\s+reminder\s+(?:about\s+)?["\']?([^"\']+)["\']?', text)
        if query_match:
            query = query_match.group(1)
            results = reminders.search_reminders(query)
            
            if results:
                response = f"I found {len(results)} reminders matching '{query}':\n"
                for i, reminder in enumerate(results[:5], 1):
                    reminder_time = datetime.fromisoformat(reminder['datetime'])
                    response += f"{i}. {reminder['title']} at {reminder_time.strftime('%I:%M %p on %B %d')}\n"
            else:
                response = f"I couldn't find any reminders matching '{query}'."
        else:
            response = "What would you like me to search for in your reminders?"
        
        return response, {'action': 'reminders_searched', 'query': query_match.group(1) if query_match else None}
    
    # Default response
    else:
        response = """I can help you with reminders! Here's what I can do:
- Set a reminder: "Set reminder for meeting at 3 PM"
- List reminders: "Show my reminders"
- Delete reminder: "Delete reminder for meeting"
- Check due reminders: "Check reminders"
- Search reminders: "Find reminder about work"

Time formats I understand:
- "in 30 minutes"
- "in 2 hours"
- "at 3 PM"
- "at 2:30 PM"
- "tomorrow at 9 AM"

What would you like me to remind you about?"""
        
        return response, {'action': 'reminders_help'}

# Feature registration
FEATURE_INFO = {
    'name': 'reminder',
    'description': 'Set, manage, and check reminders with natural language time parsing',
    'keywords': ['reminder', 'remind', 'alarm', 'schedule', 'due', 'time'],
    'examples': [
        'Set reminder for meeting at 3 PM',
        'Remind me to call mom in 2 hours',
        'Show my reminders',
        'Delete reminder for dentist appointment',
        'Check if I have any reminders due'
    ]
} 