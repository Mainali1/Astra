"""
Astra AI Assistant - Timer Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re
from src.config import Config

logger = logging.getLogger(__name__)


class Timer:
    """Represents a single timer."""

    def __init__(self, duration: timedelta, name: Optional[str] = None, timer_id: Optional[str] = None):
        """Initialize a timer."""
        self.id = timer_id or str(int(datetime.now().timestamp()))
        self.name = name or f"Timer {self.id}"
        self.duration = duration
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.remaining: Optional[timedelta] = None
        self.is_running = False
        self.is_completed = False

    def start(self):
        """Start the timer."""
        if not self.is_running and not self.is_completed:
            self.start_time = datetime.now()
            self.end_time = self.start_time + self.duration
            self.is_running = True

    def pause(self):
        """Pause the timer."""
        if self.is_running:
            self.remaining = self.end_time - datetime.now()
            self.is_running = False

    def resume(self):
        """Resume the timer."""
        if not self.is_running and not self.is_completed and self.remaining:
            self.end_time = datetime.now() + self.remaining
            self.is_running = True

    def stop(self):
        """Stop the timer."""
        self.is_running = False
        self.is_completed = True

    def get_remaining(self) -> Optional[timedelta]:
        """Get remaining time."""
        if not self.is_running:
            return self.remaining
        if self.end_time:
            return max(timedelta(0), self.end_time - datetime.now())
        return None


class TimerFeature:
    """Timer feature for Astra."""

    def __init__(self, config: Config):
        """Initialize the timer feature."""
        self.config = config
        self.timers: Dict[str, Timer] = {}
        self._check_task = None
        self._callback = None

    def set_notification_callback(self, callback):
        """Set callback for timer notifications."""
        self._callback = callback

    def _parse_duration(self, duration_str: str) -> Optional[timedelta]:
        """Parse duration string into timedelta."""
        try:
            # Parse patterns like "1 hour 30 minutes" or "2h 15m"
            total_seconds = 0

            # Handle full words
            patterns = [
                (r"(\d+)\s*hours?", 3600),
                (r"(\d+)\s*minutes?", 60),
                (r"(\d+)\s*seconds?", 1),
                # Handle abbreviations
                (r"(\d+)\s*h", 3600),
                (r"(\d+)\s*m", 60),
                (r"(\d+)\s*s", 1),
            ]

            for pattern, multiplier in patterns:
                matches = re.finditer(pattern, duration_str, re.IGNORECASE)
                for match in matches:
                    total_seconds += int(match.group(1)) * multiplier

            if total_seconds == 0:
                # Try parsing as a single number of minutes
                try:
                    total_seconds = int(duration_str) * 60
                except ValueError:
                    return None

            return timedelta(seconds=total_seconds)

        except Exception as e:
            logger.error(f"Error parsing duration: {str(e)}")
            return None

    async def _check_timers(self):
        """Periodically check timers."""
        while True:
            now = datetime.now()
            completed = []

            for timer_id, timer in self.timers.items():
                if timer.is_running and not timer.is_completed:
                    if timer.end_time and timer.end_time <= now:
                        timer.stop()
                        completed.append(timer)

            # Notify about completed timers
            if completed and self._callback:
                for timer in completed:
                    await self._callback(timer)

            await asyncio.sleep(1)  # Check every second

    def start_checking(self):
        """Start checking timers."""
        if not self._check_task:
            self._check_task = asyncio.create_task(self._check_timers())

    def stop_checking(self):
        """Stop checking timers."""
        if self._check_task:
            self._check_task.cancel()
            self._check_task = None

    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle timer-related intents."""
        try:
            action = intent.get("action", "")
            params = intent.get("parameters", {})

            if action == "set_timer":
                # Create and start new timer
                duration_str = params.get("duration", "")
                name = params.get("name")

                if not duration_str:
                    return "I need a duration to set the timer."

                duration = self._parse_duration(duration_str)
                if not duration:
                    return f"I couldn't understand the duration '{duration_str}'."

                timer = Timer(duration=duration, name=name)
                self.timers[timer.id] = timer
                timer.start()

                return f"Started {timer.name} for {duration_str}"

            elif action == "pause_timer":
                # Pause running timer
                timer_id = params.get("timer_id")
                if timer_id and timer_id in self.timers:
                    timer = self.timers[timer_id]
                    timer.pause()
                    remaining = timer.get_remaining()
                    return f"Paused {timer.name} with {remaining.seconds // 60} minutes remaining"
                return "Which timer would you like to pause?"

            elif action == "resume_timer":
                # Resume paused timer
                timer_id = params.get("timer_id")
                if timer_id and timer_id in self.timers:
                    timer = self.timers[timer_id]
                    timer.resume()
                    return f"Resumed {timer.name}"
                return "Which timer would you like to resume?"

            elif action == "stop_timer":
                # Stop timer
                timer_id = params.get("timer_id")
                if timer_id and timer_id in self.timers:
                    timer = self.timers[timer_id]
                    timer.stop()
                    return f"Stopped {timer.name}"
                return "Which timer would you like to stop?"

            elif action == "list_timers":
                # List active timers
                active_timers = [t for t in self.timers.values() if t.is_running]
                if not active_timers:
                    return "No active timers."

                response = "Active timers:\n"
                for timer in active_timers:
                    remaining = timer.get_remaining()
                    if remaining:
                        minutes = remaining.seconds // 60
                        seconds = remaining.seconds % 60
                        response += f"- {timer.name}: {minutes}m {seconds}s remaining\n"
                return response

            else:
                return "I'm not sure what you want to do with timers."

        except Exception as e:
            logger.error(f"Error handling timer request: {str(e)}")
            return "I'm sorry, but I encountered an error processing your timer request."

    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Timer feature is always available as it's offline

    async def cleanup(self):
        """Clean up resources."""
        self.stop_checking()
        # Stop all active timers
        for timer in self.timers.values():
            if timer.is_running:
                timer.stop()
