"""
Time Feature for Astra Voice Assistant
Provides current time, date, and timezone information
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pytz

# Feature information
FEATURE_INFO = {
    'name': 'time',
    'description': 'Get current time, date, and timezone information',
    'category': 'productivity',
    'keywords': ['time', 'date', 'clock', 'schedule', 'timezone', 'hour', 'minute'],
    'examples': [
        'What time is it?',
        'What\'s today\'s date?',
        'Time in New York',
        'What day is it?',
        'Current time in London'
    ],
    'version': '1.0.0',
    'author': 'Astra Team'
}

class TimeService:
    """Time and date service with timezone support"""
    
    def __init__(self):
        self.common_timezones = {
            'new york': 'America/New_York',
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'tokyo': 'Asia/Tokyo',
            'sydney': 'Australia/Sydney',
            'los angeles': 'America/Los_Angeles',
            'chicago': 'America/Chicago',
            'toronto': 'America/Toronto',
            'berlin': 'Europe/Berlin',
            'rome': 'Europe/Rome',
            'madrid': 'Europe/Madrid',
            'moscow': 'Europe/Moscow',
            'beijing': 'Asia/Shanghai',
            'seoul': 'Asia/Seoul',
            'singapore': 'Asia/Singapore',
            'dubai': 'Asia/Dubai',
            'mumbai': 'Asia/Kolkata',
            'cairo': 'Africa/Cairo',
            'johannesburg': 'Africa/Johannesburg',
            'sao paulo': 'America/Sao_Paulo',
            'mexico city': 'America/Mexico_City'
        }
    
    def get_current_time(self, timezone_name: str = None) -> Dict[str, Any]:
        """Get current time for specified timezone or local time"""
        try:
            if timezone_name:
                tz = pytz.timezone(timezone_name)
                current_time = datetime.now(tz)
            else:
                current_time = datetime.now()
            
            return {
                'time': current_time.strftime('%H:%M'),
                'time_12h': current_time.strftime('%I:%M %p'),
                'date': current_time.strftime('%Y-%m-%d'),
                'day_name': current_time.strftime('%A'),
                'month_name': current_time.strftime('%B'),
                'year': current_time.year,
                'timezone': str(current_time.tzinfo) if current_time.tzinfo else 'Local',
                'timestamp': current_time.isoformat()
            }
        except Exception as e:
            return {
                'error': f"Error getting time: {str(e)}"
            }
    
    def extract_timezone(self, text: str) -> Optional[str]:
        """Extract timezone from text"""
        text = text.lower()
        
        # Check for common timezone names
        for name, tz in self.common_timezones.items():
            if name in text:
                return tz
        
        # Check for timezone abbreviations
        tz_abbrevs = {
            'est': 'America/New_York',
            'pst': 'America/Los_Angeles',
            'gmt': 'Europe/London',
            'utc': 'UTC',
            'cet': 'Europe/Paris',
            'jst': 'Asia/Tokyo'
        }
        
        for abbrev, tz in tz_abbrevs.items():
            if abbrev in text:
                return tz
        
        return None
    
    def get_time_difference(self, timezone1: str, timezone2: str) -> Dict[str, Any]:
        """Get time difference between two timezones"""
        try:
            tz1 = pytz.timezone(timezone1)
            tz2 = pytz.timezone(timezone2)
            
            time1 = datetime.now(tz1)
            time2 = datetime.now(tz2)
            
            diff = time2 - time1.replace(tzinfo=None)
            hours = int(diff.total_seconds() / 3600)
            
            return {
                'timezone1': timezone1,
                'timezone2': timezone2,
                'difference_hours': hours,
                'time1': time1.strftime('%H:%M'),
                'time2': time2.strftime('%H:%M')
            }
        except Exception as e:
            return {
                'error': f"Error calculating time difference: {str(e)}"
            }
    
    def format_time_response(self, time_data: Dict[str, Any], timezone_name: str = None) -> str:
        """Format time data into a natural language response"""
        if 'error' in time_data:
            return f"Sorry, I couldn't get the time: {time_data['error']}"
        
        if timezone_name:
            response = f"Current time in {timezone_name} is {time_data['time_12h']} on {time_data['day_name']}, {time_data['month_name']} {time_data['date'].split('-')[2]}, {time_data['year']}"
        else:
            response = f"Current time is {time_data['time_12h']} on {time_data['day_name']}, {time_data['month_name']} {time_data['date'].split('-')[2]}, {time_data['year']}"
        
        return response

def handle_time_command(text: str) -> Dict[str, Any]:
    """Handle time and date commands"""
    time_service = TimeService()
    
    # Extract timezone from text
    timezone = time_service.extract_timezone(text)
    
    # Get current time
    time_data = time_service.get_current_time(timezone)
    
    if 'error' in time_data:
        return {
            'success': False,
            'error': time_data['error']
        }
    
    # Format response
    timezone_name = None
    if timezone:
        # Get friendly name for timezone
        for name, tz in time_service.common_timezones.items():
            if tz == timezone:
                timezone_name = name.title()
                break
        if not timezone_name:
            timezone_name = timezone.split('/')[-1].replace('_', ' ').title()
    
    response = time_service.format_time_response(time_data, timezone_name)
    
    return {
        'success': True,
        'response': response,
        'data': time_data,
        'type': 'time'
    } 