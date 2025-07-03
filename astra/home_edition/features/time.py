from datetime import datetime
import pytz

def get_current_time(timezone: str = 'UTC') -> str:
    """
    Gets the current time in a specified timezone with robust error handling.

    Args:
        timezone: The timezone to get the current time in (e.g., 'America/New_York', 'Europe/London').

    Returns:
        The current time as a formatted string, or an error message.
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime('%Y-%m-%d %H:%M:%S %Z')
    except pytz.UnknownTimeZoneError:
        return f"Error: Unknown timezone '{timezone}'. Please use a valid IANA timezone."
    except Exception as e:
        # Log the exception here in a real application
        return f"An unexpected error occurred: {e}"

def list_timezones() -> list[str]:
    """
    Returns a list of all available IANA timezones.

    Returns:
        A list of timezone names.
    """
    return pytz.all_timezones