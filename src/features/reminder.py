"""
Astra AI Assistant - Reminder Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import dateparser
from src.config import Config

logger = logging.getLogger(__name__)

class Reminder:
    """Represents a single reminder."""
    
    def __init__(self, task: str, time: datetime, reminder_id: Optional[str] = None):
        """Initialize a reminder."""
        self.id = reminder_id or str(int(datetime.now().timestamp()))
        self.task = task
        self.time = time
        self.completed = False
        self.notified = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reminder to dictionary."""
        return {
            'id': self.id,
            'task': self.task,
            'time': self.time.isoformat(),
            'completed': self.completed,
            'notified': self.notified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reminder':
        """Create reminder from dictionary."""
        return cls(
            task=data['task'],
            time=datetime.fromisoformat(data['time']),
            reminder_id=data['id']
        )

class ReminderFeature:
    """Reminder feature for Astra."""
    
    def __init__(self, config: Config):
        """Initialize the reminder feature."""
        self.config = config
        self.reminders: List[Reminder] = []
        self.data_file = Path(config.DATA_DIR) / 'reminders.json'
        self._load_reminders()
        self._check_task = None
        self._callback = None
    
    def _load_reminders(self):
        """Load reminders from file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.reminders = [Reminder.from_dict(r) for r in data]
                    logger.info(f"Loaded {len(self.reminders)} reminders")
        except Exception as e:
            logger.error(f"Error loading reminders: {str(e)}")
    
    def _save_reminders(self):
        """Save reminders to file."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump([r.to_dict() for r in self.reminders], f)
        except Exception as e:
            logger.error(f"Error saving reminders: {str(e)}")
    
    def set_notification_callback(self, callback):
        """Set callback for reminder notifications."""
        self._callback = callback
    
    async def _check_reminders(self):
        """Periodically check for due reminders."""
        while True:
            now = datetime.now()
            for reminder in self.reminders:
                if not reminder.notified and not reminder.completed:
                    if reminder.time <= now:
                        reminder.notified = True
                        if self._callback:
                            await self._callback(reminder)
            await asyncio.sleep(60)  # Check every minute
    
    def start_checking(self):
        """Start checking for reminders."""
        if not self._check_task:
            self._check_task = asyncio.create_task(self._check_reminders())
    
    def stop_checking(self):
        """Stop checking for reminders."""
        if self._check_task:
            self._check_task.cancel()
            self._check_task = None
    
    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle reminder-related intents."""
        try:
            action = intent.get('action', '')
            params = intent.get('parameters', {})
            
            if action == 'set_reminder':
                # Parse task and time
                task = params.get('task', '')
                time_str = params.get('time', '')
                
                if not task or not time_str:
                    return "I need both a task and a time to set a reminder."
                
                # Parse time string
                when = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})
                if not when:
                    return f"I couldn't understand when you want to be reminded about '{task}'."
                
                # Create reminder
                reminder = Reminder(task=task, time=when)
                self.reminders.append(reminder)
                self._save_reminders()
                
                # Format response
                time_str = when.strftime("%I:%M %p on %B %d, %Y")
                return f"I'll remind you about '{task}' at {time_str}"
                
            elif action == 'list_reminders':
                # List active reminders
                active = [r for r in self.reminders if not r.completed]
                if not active:
                    return "You don't have any active reminders."
                
                response = "Here are your active reminders:\n"
                for r in sorted(active, key=lambda x: x.time):
                    time_str = r.time.strftime("%I:%M %p on %B %d")
                    response += f"- {r.task} at {time_str}\n"
                return response
                
            elif action == 'complete_reminder':
                # Mark reminder as completed
                task = params.get('task', '')
                if not task:
                    return "Which reminder would you like to mark as completed?"
                
                for reminder in self.reminders:
                    if reminder.task.lower() == task.lower():
                        reminder.completed = True
                        self._save_reminders()
                        return f"Marked reminder '{task}' as completed."
                
                return f"I couldn't find a reminder for '{task}'."
            
            else:
                return "I'm not sure what you want to do with reminders."
            
        except Exception as e:
            logger.error(f"Error handling reminder request: {str(e)}")
            return "I'm sorry, but I encountered an error processing your reminder request."
    
    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Reminder feature is always available as it's offline
    
    async def cleanup(self):
        """Clean up resources."""
        self.stop_checking()
        self._save_reminders() 