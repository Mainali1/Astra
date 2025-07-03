import requests
from typing import Optional, Dict, Any

from astra.core.config import settings

WEATHERAPI_BASE_URL = "http://api.weatherapi.com/v1"

def get_current_weather(location: str) -> Optional[Dict[str, Any]]:
    """
    Gets current weather conditions for a given location.

    Args:
        location: The city name, zip code, or IP address.

    Returns:
        A dictionary containing current weather data, or None if an error occurs.
    """
    api_key = settings.openweather_api_key # Assuming openweather_api_key is used for WeatherAPI
    if not api_key:
        return {"error": "WeatherAPI key is not configured. Please set OPENWEATHER_API_KEY in your .env file."}

    try:
        response = requests.get(f"{WEATHERAPI_BASE_URL}/current.json", params={
            'key': api_key,
            'q': location
        })
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        # Log the exception here in a real application
        print(f"Error fetching current weather: {e}")
        return {"error": f"Failed to retrieve weather data: {e}"}

def get_forecast_weather(location: str, days: int = 3) -> Optional[Dict[str, Any]]:
    """
    Gets weather forecast for a given location for a specified number of days.

    Args:
        location: The city name, zip code, or IP address.
        days: Number of days to get the forecast for (1-10).

    Returns:
        A dictionary containing forecast weather data, or None if an error occurs.
    """
    api_key = settings.openweather_api_key
    if not api_key:
        return {"error": "WeatherAPI key is not configured. Please set OPENWEATHER_API_KEY in your .env file."}

    if not 1 <= days <= 10:
        return {"error": "Forecast days must be between 1 and 10."}

    try:
        response = requests.get(f"{WEATHERAPI_BASE_URL}/forecast.json", params={
            'key': api_key,
            'q': location,
            'days': days
        })
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        # Log the exception here in a real application
        print(f"Error fetching forecast weather: {e}")
        return {"error": f"Failed to retrieve forecast data: {e}"}