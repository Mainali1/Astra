"""
Astra AI Assistant - Weather Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import aiohttp
from typing import Dict, Any, Optional
from src.config import Config
import os

logger = logging.getLogger(__name__)

class WeatherFeature:
    """Weather feature for Astra."""
    
    def __init__(self, config: Config):
        """Initialize the weather feature."""
        self.config = config
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle weather-related intents."""
        try:
            location = intent.get('parameters', {}).get('location', '')
            if not location:
                return "I need a location to check the weather for."
            
            if not self.api_key:
                return "I'm sorry, but I'm not configured to check the weather right now."
            
            await self._ensure_session()
            
            # Get weather data
            async with self.session.get(
                f"{self.base_url}/weather",
                params={
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data['main']['temp']
                    desc = data['weather'][0]['description']
                    return f"The weather in {location} is {desc} with a temperature of {temp}°C."
                else:
                    return f"I couldn't find weather information for {location}."
                    
        except Exception as e:
            logger.error(f"Error getting weather: {str(e)}")
            return "I'm sorry, but I encountered an error getting the weather information."
    
    def is_available(self) -> bool:
        """Check if the feature is available."""
        return bool(self.api_key)
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None 