"""
Weather Feature for Astra Voice Assistant
Provides weather information using OpenWeatherMap API with offline fallback
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import os

# Feature information
FEATURE_INFO = {
    'name': 'weather',
    'description': 'Get current weather conditions and forecasts for any location',
    'category': 'knowledge',
    'keywords': ['weather', 'temperature', 'forecast', 'climate', 'rain', 'sunny', 'cloudy'],
    'examples': [
        'What\'s the weather like?',
        'Weather forecast for tomorrow',
        'Temperature in New York',
        'Is it going to rain today?',
        'Weather in London'
    ],
    'version': '1.0.0',
    'author': 'Astra Team'
}

class WeatherService:
    """Weather service with API integration and caching"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.cache_file = Path("data/weather_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
        # Weather condition mappings
        self.weather_conditions = {
            '01d': 'clear sky',
            '01n': 'clear sky',
            '02d': 'few clouds',
            '02n': 'few clouds',
            '03d': 'scattered clouds',
            '03n': 'scattered clouds',
            '04d': 'broken clouds',
            '04n': 'broken clouds',
            '09d': 'shower rain',
            '09n': 'shower rain',
            '10d': 'rain',
            '10n': 'rain',
            '11d': 'thunderstorm',
            '11n': 'thunderstorm',
            '13d': 'snow',
            '13n': 'snow',
            '50d': 'mist',
            '50n': 'mist'
        }
        
        # Load cache
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load weather cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    # Remove expired entries
                    current_time = datetime.now()
                    expired_keys = []
                    for key, data in cache.items():
                        if 'timestamp' in data:
                            cache_time = datetime.fromisoformat(data['timestamp'])
                            if current_time - cache_time > self.cache_duration:
                                expired_keys.append(key)
                    
                    for key in expired_keys:
                        del cache[key]
                    
                    return cache
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_cache(self):
        """Save weather cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving weather cache: {e}")
    
    def _get_cached_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get weather from cache"""
        cache_key = location.lower().replace(' ', '_')
        if cache_key in self.cache:
            data = self.cache[cache_key]
            if 'timestamp' in data:
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < self.cache_duration:
                    return data.get('weather')
        return None
    
    def _cache_weather(self, location: str, weather_data: Dict[str, Any]):
        """Cache weather data"""
        cache_key = location.lower().replace(' ', '_')
        self.cache[cache_key] = {
            'weather': weather_data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def _get_weather_icon_description(self, icon_code: str) -> str:
        """Get human-readable weather description from icon code"""
        return self.weather_conditions.get(icon_code, 'unknown')
    
    def _format_temperature(self, temp_kelvin: float, unit: str = 'celsius') -> str:
        """Format temperature in specified unit"""
        if unit == 'celsius':
            temp = temp_kelvin - 273.15
            return f"{temp:.1f}°C"
        elif unit == 'fahrenheit':
            temp = (temp_kelvin - 273.15) * 9/5 + 32
            return f"{temp:.1f}°F"
        else:
            return f"{temp_kelvin:.1f}K"
    
    def _format_wind_speed(self, speed_ms: float) -> str:
        """Format wind speed in km/h"""
        speed_kmh = speed_ms * 3.6
        return f"{speed_kmh:.1f} km/h"
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location"""
        # Check cache first
        cached_weather = self._get_cached_weather(location)
        if cached_weather:
            return {
                'success': True,
                'data': cached_weather,
                'source': 'cache'
            }
        
        # If no API key, return offline response
        if not self.api_key:
            return self._get_offline_weather(location)
        
        try:
            # Get coordinates first
            geocode_url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(geocode_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') != 200:
                return {
                    'success': False,
                    'error': f"Location not found: {location}"
                }
            
            # Extract weather information
            weather_info = {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': self._format_temperature(data['main']['temp']),
                'feels_like': self._format_temperature(data['main']['feels_like']),
                'humidity': f"{data['main']['humidity']}%",
                'pressure': f"{data['main']['pressure']} hPa",
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': self._format_wind_speed(data['wind']['speed']),
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': f"{data.get('visibility', 0) / 1000:.1f} km",
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self._cache_weather(location, weather_info)
            
            return {
                'success': True,
                'data': weather_info,
                'source': 'api'
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Weather service error: {str(e)}"
            }
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'Weather API not configured'
            }
        
        try:
            forecast_url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') != '200':
                return {
                    'success': False,
                    'error': f"Location not found: {location}"
                }
            
            # Process forecast data
            forecasts = []
            for item in data['list']:
                forecast = {
                    'datetime': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M'),
                    'date': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d'),
                    'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                    'temperature': self._format_temperature(item['main']['temp']),
                    'description': item['weather'][0]['description'].title(),
                    'humidity': f"{item['main']['humidity']}%",
                    'wind_speed': self._format_wind_speed(item['wind']['speed']),
                    'icon': item['weather'][0]['icon']
                }
                forecasts.append(forecast)
            
            return {
                'success': True,
                'data': {
                    'location': data['city']['name'],
                    'country': data['city']['country'],
                    'forecasts': forecasts
                }
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Forecast service error: {str(e)}"
            }
    
    def _get_offline_weather(self, location: str) -> Dict[str, Any]:
        """Get offline weather response when API is unavailable"""
        # Simple offline weather simulation
        import random
        
        conditions = ['sunny', 'cloudy', 'rainy', 'partly cloudy', 'overcast']
        temperatures = range(15, 30)  # 15-30°C
        
        return {
            'success': True,
            'data': {
                'location': location,
                'country': 'Unknown',
                'temperature': f"{random.choice(temperatures)}°C",
                'feels_like': f"{random.choice(temperatures)}°C",
                'humidity': f"{random.randint(40, 80)}%",
                'pressure': f"{random.randint(1000, 1020)} hPa",
                'description': random.choice(conditions).title(),
                'icon': '01d',
                'wind_speed': f"{random.randint(5, 25)} km/h",
                'wind_direction': random.randint(0, 360),
                'visibility': f"{random.randint(8, 12)} km",
                'sunrise': '06:30',
                'sunset': '18:30',
                'timestamp': datetime.now().isoformat(),
                'note': 'Offline mode - data may not be accurate'
            },
            'source': 'offline'
        }
    
    def extract_location(self, text: str) -> str:
        """Extract location from user input"""
        # Common location patterns
        patterns = [
            r'in\s+([A-Za-z\s,]+?)(?:\?|$|\s+(?:today|tomorrow|now))',
            r'weather\s+(?:in\s+)?([A-Za-z\s,]+?)(?:\?|$|\s+(?:today|tomorrow|now))',
            r'temperature\s+(?:in\s+)?([A-Za-z\s,]+?)(?:\?|$|\s+(?:today|tomorrow|now))',
            r'forecast\s+(?:for\s+)?([A-Za-z\s,]+?)(?:\?|$|\s+(?:today|tomorrow|now))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up location
                location = re.sub(r'\s+', ' ', location)
                location = location.rstrip(',')
                return location
        
        # Default location if none found
        return "current location"

def handle_weather_command(text: str) -> Dict[str, Any]:
    """Handle weather commands"""
    weather_service = WeatherService()
    
    # Extract location from text
    location = weather_service.extract_location(text)
    
    # Check if user is asking for forecast
    if any(word in text.lower() for word in ['forecast', 'tomorrow', 'week', 'days']):
        # Get forecast
        result = weather_service.get_forecast(location)
        if result['success']:
            data = result['data']
            response = f"Weather forecast for {data['location']}, {data['country']}: "
            
            # Group forecasts by day
            daily_forecasts = {}
            for forecast in data['forecasts']:
                date = forecast['date']
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(forecast)
            
            # Create summary
            for i, (date, forecasts) in enumerate(list(daily_forecasts.items())[:3]):  # Show next 3 days
                if i > 0:
                    response += ". "
                
                # Get average temperature
                temps = [float(f['temperature'].replace('°C', '')) for f in forecasts]
                avg_temp = sum(temps) / len(temps)
                
                # Get most common condition
                conditions = [f['description'] for f in forecasts]
                most_common = max(set(conditions), key=conditions.count)
                
                day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                response += f"{day_name}: {most_common}, {avg_temp:.1f}°C"
            
            return {
                'success': True,
                'response': response,
                'data': result['data'],
                'type': 'forecast'
            }
        else:
            return result
    else:
        # Get current weather
        result = weather_service.get_current_weather(location)
        if result['success']:
            data = result['data']
            response = f"Current weather in {data['location']}, {data['country']}: {data['description']}, {data['temperature']} (feels like {data['feels_like']}). Humidity: {data['humidity']}, Wind: {data['wind_speed']}"
            
            if result['source'] == 'offline':
                response += " (Offline mode)"
            
            return {
                'success': True,
                'response': response,
                'data': data,
                'type': 'current'
            }
        else:
            return result 