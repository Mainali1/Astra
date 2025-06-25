"""
Astra AI Assistant - Time Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
from datetime import datetime
import pytz
from typing import Dict, Any, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class TimeFeature:
    """Time feature for Astra."""
    
    def __init__(self, config: Config):
        """Initialize the time feature."""
        self.config = config
        self._timezone = pytz.timezone('UTC')  # Default timezone
        self._format_24h = False  # 12-hour format by default
    
    def set_timezone(self, timezone_str: str) -> bool:
        """Set the timezone for time operations."""
        try:
            self._timezone = pytz.timezone(timezone_str)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False
    
    def set_24h_format(self, use_24h: bool):
        """Set whether to use 24-hour format."""
        self._format_24h = use_24h
    
    def _format_time(self, dt: datetime) -> str:
        """Format time according to settings."""
        if self._format_24h:
            return dt.strftime("%H:%M")
        return dt.strftime("%I:%M %p")
    
    def _get_current_time(self, timezone: Optional[str] = None) -> datetime:
        """Get current time in specified timezone."""
        now = datetime.now(pytz.UTC)
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                return now.astimezone(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                return now.astimezone(self._timezone)
        return now.astimezone(self._timezone)
    
    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle time-related intents."""
        try:
            action = intent.get('action', '')
            params = intent.get('parameters', {})
            
            if action == 'get_time':
                # Get current time
                now = self._get_current_time()
                date_str = now.strftime("%A, %B %d, %Y")
                time_str = self._format_time(now)
                return f"It's {time_str} on {date_str}"
                
            elif action == 'get_time_zone':
                # Get time in specific timezone
                location = params.get('location', '')
                if not location:
                    return "I need a location to check the time for."
                
                try:
                    # Try to find timezone for location
                    # This is a simplified version - in production you'd want
                    # to use a proper geocoding service to get the timezone
                    timezone = location.replace(' ', '_')
                    now = self._get_current_time(timezone)
                    time_str = self._format_time(now)
                    return f"The time in {location} is {time_str}"
                except Exception:
                    return f"I couldn't find the timezone for {location}"
            
            else:
                return "I'm not sure what time-related information you need."
            
        except Exception as e:
            logger.error(f"Error handling time request: {str(e)}")
            return "I'm sorry, but I encountered an error processing your time request."
    
    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Time feature is always available as it's offline
    
    async def cleanup(self):
        """Clean up resources."""
        pass  # No cleanup needed for time feature 