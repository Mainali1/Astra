"""
Home Edition Features

All the personal productivity tools and day-to-day life features for Home Edition.
No mock code, only real implementations and real API integrations.
"""

import asyncio
import json
import math
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import platform
import requests
import os

from astra.core.config import settings
from astra.core.logging import get_logger
from astra.core.security import security_manager
from .drm import verify_feature_access


class HomeFeatures:
    """Home Edition feature implementations (real code only)."""
    
    def __init__(self):
        self.logger = get_logger("astra.home.features")
        self.data_dir = settings.data_dir / "home_features"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _check_feature_access(self, feature_name: str) -> bool:
        """Check if user has access to specific feature."""
        return verify_feature_access(feature_name)
    
    # ==================== CALCULATOR ====================
    
    def calculator(self, expression: str) -> Dict[str, Any]:
        """Basic calculator with scientific functions."""
        if not self._check_feature_access("calculator"):
            return {"error": "Calculator feature not available"}
        
        try:
            # Sanitize input - only allow safe mathematical operations
            expression = re.sub(r'[^0-9+\-*/()., ]', '', expression)
            
            # Handle basic operations
            result = eval(expression)
            
            return {
                "expression": expression,
                "result": result,
                "type": "calculation"
            }
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}
    
    def scientific_calculator(self, function: str, value: float) -> Dict[str, Any]:
        """Scientific calculator functions."""
        if not self._check_feature_access("calculator"):
            return {"error": "Calculator feature not available"}
        
        try:
            import math
            
            functions = {
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log10,
                "ln": math.log,
                "sqrt": math.sqrt,
                "exp": math.exp,
                "abs": abs,
            }
            
            if function not in functions:
                return {"error": f"Unknown function: {function}"}
            
            result = functions[function](value)
            
            return {
                "function": function,
                "input": value,
                "result": result,
                "type": "scientific"
            }
        except Exception as e:
            return {"error": f"Scientific calculation error: {str(e)}"}
    
    # ==================== TIMER ====================
    
    def start_timer(self, duration_seconds: int, name: str = "Timer") -> Dict[str, Any]:
        """Start a timer."""
        if not self._check_feature_access("timer"):
            return {"error": "Timer feature not available"}
        
        try:
            timer_id = f"timer_{datetime.now().timestamp()}"
            end_time = datetime.now() + timedelta(seconds=duration_seconds)
            
            timer_data = {
                "id": timer_id,
                "name": name,
                "duration": duration_seconds,
                "start_time": datetime.now().isoformat(),
                "end_time": end_time.isoformat(),
                "status": "running"
            }
            
            # Save timer
            timer_file = self.data_dir / f"{timer_id}.json"
            with open(timer_file, 'w') as f:
                json.dump(timer_data, f)
            
            return {
                "timer_id": timer_id,
                "name": name,
                "duration": duration_seconds,
                "end_time": end_time.isoformat(),
                "status": "started"
            }
        except Exception as e:
            return {"error": f"Timer error: {str(e)}"}
    
    def check_timer(self, timer_id: str) -> Dict[str, Any]:
        """Check timer status."""
        if not self._check_feature_access("timer"):
            return {"error": "Timer feature not available"}
        
        try:
            timer_file = self.data_dir / f"{timer_id}.json"
            if not timer_file.exists():
                return {"error": "Timer not found"}
            
            with open(timer_file, 'r') as f:
                timer_data = json.load(f)
            
            end_time = datetime.fromisoformat(timer_data["end_time"])
            remaining = (end_time - datetime.now()).total_seconds()
            
            if remaining <= 0:
                timer_data["status"] = "completed"
                with open(timer_file, 'w') as f:
                    json.dump(timer_data, f)
                
                return {
                    "timer_id": timer_id,
                    "name": timer_data["name"],
                    "status": "completed",
                    "remaining": 0
                }
            
            return {
                "timer_id": timer_id,
                "name": timer_data["name"],
                "status": "running",
                "remaining": int(remaining)
            }
        except Exception as e:
            return {"error": f"Timer check error: {str(e)}"}
    
    # ==================== REMINDER ====================
    
    def create_reminder(self, title: str, message: str, due_time: str, 
                       priority: str = "medium") -> Dict[str, Any]:
        """Create a reminder."""
        if not self._check_feature_access("reminder"):
            return {"error": "Reminder feature not available"}
        
        try:
            reminder_id = f"reminder_{datetime.now().timestamp()}"
            due_datetime = datetime.fromisoformat(due_time)
            
            reminder_data = {
                "id": reminder_id,
                "title": title,
                "message": message,
                "due_time": due_time,
                "priority": priority,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Save reminder
            reminder_file = self.data_dir / f"{reminder_id}.json"
            with open(reminder_file, 'w') as f:
                json.dump(reminder_data, f)
            
            return {
                "reminder_id": reminder_id,
                "title": title,
                "due_time": due_time,
                "status": "created"
            }
        except Exception as e:
            return {"error": f"Reminder error: {str(e)}"}
    
    def get_reminders(self, status: str = "pending") -> Dict[str, Any]:
        """Get all reminders."""
        if not self._check_feature_access("reminder"):
            return {"error": "Reminder feature not available"}
        
        try:
            reminders = []
            for file in self.data_dir.glob("reminder_*.json"):
                with open(file, 'r') as f:
                    reminder_data = json.load(f)
                
                if reminder_data.get("status") == status:
                    reminders.append(reminder_data)
            
            return {
                "reminders": reminders,
                "count": len(reminders)
            }
        except Exception as e:
            return {"error": f"Get reminders error: {str(e)}"}
    
    # ==================== NOTES ====================
    
    def create_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a note."""
        if not self._check_feature_access("notes"):
            return {"error": "Notes feature not available"}
        
        try:
            note_id = f"note_{datetime.now().timestamp()}"
            
            note_data = {
                "id": note_id,
                "title": title,
                "content": content,
                "tags": tags or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save note
            note_file = self.data_dir / f"{note_id}.json"
            with open(note_file, 'w') as f:
                json.dump(note_data, f)
            
            return {
                "note_id": note_id,
                "title": title,
                "status": "created"
            }
        except Exception as e:
            return {"error": f"Note error: {str(e)}"}
    
    def get_notes(self, tag: Optional[str] = None) -> Dict[str, Any]:
        """Get all notes."""
        if not self._check_feature_access("notes"):
            return {"error": "Notes feature not available"}
        
        try:
            notes = []
            for file in self.data_dir.glob("note_*.json"):
                with open(file, 'r') as f:
                    note_data = json.load(f)
                
                if tag is None or tag in note_data.get("tags", []):
                    notes.append(note_data)
            
            return {
                "notes": notes,
                "count": len(notes)
            }
        except Exception as e:
            return {"error": f"Get notes error: {str(e)}"}
    
    # ==================== WEATHER (REAL API) ====================
    
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get weather information using WeatherAPI (free tier: 1M calls/month)."""
        if not self._check_feature_access("weather"):
            return {"error": "Weather feature not available"}
        
        try:
            # WeatherAPI requires an API key - get from settings or environment
            api_key = settings.openweather_api_key or os.getenv("WEATHERAPI_KEY")
            if not api_key:
                return {
                    "error": "Weather API key not configured", 
                    "setup_required": "Get free API key from https://www.weatherapi.com/",
                    "free_tier": "1 million calls/month"
                }
            
            url = f"https://api.weatherapi.com/v1/current.json"
            params = {
                "key": api_key,
                "q": location,
                "aqi": "no"  # Don't include air quality to save API calls
            }
            
            resp = requests.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "location": data["location"]["name"],
                    "region": data["location"]["region"],
                    "country": data["location"]["country"],
                    "temperature_c": data["current"]["temp_c"],
                    "temperature_f": data["current"]["temp_f"],
                    "condition": data["current"]["condition"]["text"],
                    "humidity": data["current"]["humidity"],
                    "wind_kph": data["current"]["wind_kph"],
                    "wind_mph": data["current"]["wind_mph"],
                    "icon": data["current"]["condition"]["icon"],
                    "feels_like_c": data["current"]["feelslike_c"],
                    "feels_like_f": data["current"]["feelslike_f"],
                    "source": "WeatherAPI",
                    "free_tier": "1 million calls/month"
                }
            elif resp.status_code == 401:
                return {"error": "Invalid WeatherAPI key - please check your API key"}
            elif resp.status_code == 429:
                return {"error": "WeatherAPI rate limit exceeded - free tier allows 1M calls/month"}
            else:
                return {"error": f"Weather API error: {resp.status_code} - {resp.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Weather API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Weather error: {str(e)}"}
    
    # ==================== CURRENCY CONVERTER (REAL API) ====================
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Convert currency using ExchangeRate.host (free tier: 100 requests/month)."""
        if not self._check_feature_access("currency_converter"):
            return {"error": "Currency Converter feature not available"}
        
        try:
            # ExchangeRate.host now requires an API key (free registration)
            api_key = os.getenv("EXCHANGERATE_API_KEY")
            if not api_key:
                return {
                    "error": "ExchangeRate API key not configured",
                    "setup_required": "Get free API key from https://exchangerate.host/",
                    "free_tier": "100 requests/month"
                }
            
            url = f"https://api.exchangerate.host/convert"
            params = {
                "access_key": api_key,
                "from": from_currency.upper(),
                "to": to_currency.upper(),
                "amount": amount
            }
            
            resp = requests.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return {
                        "amount": amount,
                        "from_currency": from_currency.upper(),
                        "to_currency": to_currency.upper(),
                        "rate": data["info"]["rate"],
                        "converted_amount": data["result"],
                        "date": data["date"],
                        "source": "exchangerate.host",
                        "free_tier": "100 requests/month"
                    }
                else:
                    return {"error": f"ExchangeRate API error: {data.get('error', {}).get('info', 'Unknown error')}"}
            elif resp.status_code == 401:
                return {"error": "Invalid ExchangeRate API key - please check your API key"}
            elif resp.status_code == 429:
                return {"error": "ExchangeRate API rate limit exceeded - free tier allows 100 requests/month"}
            else:
                return {"error": f"Currency API error: {resp.status_code} - {resp.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Currency API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Currency API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Currency conversion error: {str(e)}"}
    
    # ==================== WEB SEARCH (REAL API) ====================
    
    def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform web search using ContextualWeb Search API (free tier: 100 requests/day)."""
        if not self._check_feature_access("web_search"):
            return {"error": "Web Search feature not available"}
        
        try:
            # ContextualWeb Search API via RapidAPI requires an API key
            api_key = os.getenv("CONTEXTUALWEB_API_KEY")
            if not api_key:
                return {
                    "error": "ContextualWeb API key not configured",
                    "setup_required": "Get free API key from RapidAPI ContextualWeb Search",
                    "free_tier": "100 requests/day"
                }
            
            url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/WebSearchAPI"
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
            }
            params = {
                "q": query,
                "pageNumber": 1,
                "pageSize": max_results,
                "autoCorrect": True,
                "safeSearch": False
            }
            
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for r in data.get("value", []):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "description": r.get("description", ""),
                        "snippet": r.get("snippet", ""),
                        "date_published": r.get("datePublished", "")
                    })
                
                return {
                    "query": query,
                    "results": results,
                    "count": len(results),
                    "total_count": data.get("totalCount", 0),
                    "source": "ContextualWeb Search",
                    "free_tier": "100 requests/day"
                }
            elif resp.status_code == 401:
                return {"error": "Invalid ContextualWeb API key - please check your RapidAPI key"}
            elif resp.status_code == 429:
                return {"error": "ContextualWeb API rate limit exceeded - free tier allows 100 requests/day"}
            else:
                return {"error": f"Web search API error: {resp.status_code} - {resp.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Web search API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Web search API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Web search error: {str(e)}"}
    
    # ==================== DICTIONARY (REAL API) ====================
    
    def get_word_definition(self, word: str) -> Dict[str, Any]:
        """Get word definition using Free Dictionary API (always free, no API key required)."""
        if not self._check_feature_access("learning_assistant"):
            return {"error": "Learning Assistant feature not available"}
        
        try:
            # Free Dictionary API - no API key required
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
            
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    word_data = data[0]
                    meanings = []
                    
                    for meaning in word_data.get("meanings", []):
                        part_of_speech = meaning.get("partOfSpeech", "")
                        definitions = []
                        
                        for definition in meaning.get("definitions", []):
                            definitions.append({
                                "definition": definition.get("definition", ""),
                                "example": definition.get("example", "")
                            })
                        
                        meanings.append({
                            "part_of_speech": part_of_speech,
                            "definitions": definitions
                        })
                    
                    return {
                        "word": word,
                        "meanings": meanings,
                        "phonetic": word_data.get("phonetic", ""),
                        "origin": word_data.get("origin", ""),
                        "source": "dictionaryapi.dev",
                        "free_tier": "Always free, no limits"
                    }
                else:
                    return {"error": f"No definition found for '{word}'"}
            elif resp.status_code == 404:
                return {"error": f"Word '{word}' not found in dictionary"}
            else:
                return {"error": f"Dictionary API error: {resp.status_code} - {resp.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Dictionary API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Dictionary API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Definition error: {str(e)}"}
    
    # ==================== FILE MANAGER ====================
    
    def list_files(self, directory: str = ".") -> Dict[str, Any]:
        """List files in directory."""
        if not self._check_feature_access("file_manager"):
            return {"error": "File Manager feature not available"}
        
        try:
            path = Path(directory).resolve()
            if not path.exists():
                return {"error": "Directory not found"}
            
            files = []
            for item in path.iterdir():
                try:
                    stat = item.stat()
                    file_info = {
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    }
                    files.append(file_info)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
            
            return {
                "directory": str(path),
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": f"File listing error: {str(e)}"}
    
    # ==================== SYSTEM MONITOR ====================
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        if not self._check_feature_access("system_monitor"):
            return {"error": "System Monitor feature not available"}
        
        try:
            import psutil
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Get disk info
            disk = psutil.disk_usage('/')
            
            # Get boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": disk.percent,
                "uptime_days": uptime.days,
                "uptime_hours": uptime.seconds // 3600,
                "boot_time": boot_time.isoformat(),
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0]
            }
        except ImportError:
            return {"error": "psutil library not installed - run 'pip install psutil'"}
        except Exception as e:
            return {"error": f"System info error: {str(e)}"}
    
    # ==================== OCR (REAL API) ====================
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract text from image using OCR.Space API (free tier: 500 requests/day)."""
        if not self._check_feature_access("ocr"):
            return {"error": "OCR feature not available"}
        
        try:
            # OCR.Space requires an API key
            api_key = os.getenv("OCRSPACE_API_KEY")
            if not api_key:
                return {
                    "error": "OCR.Space API key not configured",
                    "setup_required": "Get free API key from https://ocr.space/",
                    "free_tier": "500 requests/day, 1MB file size limit"
                }
            
            # Check if file exists and is an image
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}"}
            
            # Check file size (free tier limit: 1MB)
            file_size = os.path.getsize(image_path)
            if file_size > 1024 * 1024:  # 1MB
                return {"error": "File size exceeds free tier limit (1MB)"}
            
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                data = {
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'filetype': 'png',
                    'detectOrientation': True
                }
                headers = {'apikey': api_key}
                
                resp = requests.post(
                    'https://api.ocr.space/parse/image',
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=30
                )
                
                if resp.status_code == 200:
                    result = resp.json()
                    
                    if result.get('IsErroredOnProcessing'):
                        return {"error": f"OCR processing error: {result.get('ErrorMessage', 'Unknown error')}"}
                    
                    parsed_results = result.get('ParsedResults', [])
                    if parsed_results:
                        parsed = parsed_results[0]
                        return {
                            "image_path": image_path,
                            "extracted_text": parsed.get('ParsedText', '').strip(),
                            "confidence": parsed.get('MeanConfidence', None),
                            "file_size_bytes": file_size,
                            "source": "ocr.space",
                            "free_tier": "500 requests/day, 1MB file size limit"
                        }
                    else:
                        return {"error": "No text found in image"}
                        
                elif resp.status_code == 401:
                    return {"error": "Invalid OCR.Space API key - please check your API key"}
                elif resp.status_code == 429:
                    return {"error": "OCR.Space API rate limit exceeded - free tier allows 500 requests/day"}
                else:
                    return {"error": f"OCR API error: {resp.status_code} - {resp.text}"}
                    
        except requests.exceptions.Timeout:
            return {"error": "OCR API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"OCR API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"OCR error: {str(e)}"} 