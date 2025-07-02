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
            # Sanitize input
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
        """Get weather information."""
        if not self._check_feature_access("weather"):
            return {"error": "Weather feature not available"}
        
        try:
            # Use WeatherAPI (https://www.weatherapi.com/) as a free API example
            api_key = settings.openweather_api_key or os.getenv("WEATHERAPI_KEY")
            if not api_key:
                return {"error": "No weather API key configured"}
            url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "location": data["location"]["name"],
                    "region": data["location"]["region"],
                    "country": data["location"]["country"],
                    "temperature_c": data["current"]["temp_c"],
                    "condition": data["current"]["condition"]["text"],
                    "humidity": data["current"]["humidity"],
                    "wind_kph": data["current"]["wind_kph"],
                    "icon": data["current"]["condition"]["icon"],
                    "source": "WeatherAPI"
                }
            return {"error": f"Weather API error: {resp.text}"}
        except Exception as e:
            return {"error": f"Weather error: {str(e)}"}
    
    # ==================== CURRENCY CONVERTER (REAL API) ====================
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Convert currency."""
        if not self._check_feature_access("currency_converter"):
            return {"error": "Currency Converter feature not available"}
        
        try:
            # Use exchangerate.host (https://exchangerate.host/) as a free API
            url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "rate": data["info"]["rate"],
                    "converted_amount": data["result"],
                    "source": "exchangerate.host"
                }
            return {"error": f"Currency API error: {resp.text}"}
        except Exception as e:
            return {"error": f"Currency conversion error: {str(e)}"}
    
    # ==================== WEB SEARCH (REAL API) ====================
    
    def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform web search."""
        if not self._check_feature_access("web_search"):
            return {"error": "Web Search feature not available"}
        
        try:
            # Use ContextualWeb Search API (https://contextualwebsearch.com/) as a free API
            api_key = os.getenv("CONTEXTUALWEB_API_KEY")
            if not api_key:
                return {"error": "No web search API key configured"}
            url = f"https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/WebSearchAPI"
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
            }
            params = {"q": query, "pageNumber": 1, "pageSize": max_results, "autoCorrect": True}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = [
                    {
                        "title": r["title"],
                        "url": r["url"],
                        "description": r["description"]
                    } for r in data.get("value", [])
                ]
                return {
                    "query": query,
                    "results": results,
                    "count": len(results),
                    "source": "ContextualWeb"
                }
            return {"error": f"Web search API error: {resp.text}"}
        except Exception as e:
            return {"error": f"Web search error: {str(e)}"}
    
    # ==================== DICTIONARY (REAL API) ====================
    
    def get_word_definition(self, word: str) -> Dict[str, Any]:
        """Get word definition."""
        if not self._check_feature_access("learning_assistant"):
            return {"error": "Learning Assistant feature not available"}
        
        try:
            # Use Free Dictionary API (https://dictionaryapi.dev/)
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                meanings = data[0].get("meanings", [])
                definitions = []
                for m in meanings:
                    for d in m.get("definitions", []):
                        definitions.append(d.get("definition"))
                return {
                    "word": word,
                    "definitions": definitions,
                    "source": "dictionaryapi.dev"
                }
            return {"error": f"Dictionary API error: {resp.text}"}
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
                file_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                files.append(file_info)
            
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
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "uptime": psutil.boot_time(),
                "platform": platform.system(),
                "python_version": platform.python_version()
            }
        except Exception as e:
            return {"error": f"System info error: {str(e)}"}
    
    # ==================== OCR (REAL API) ====================
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract text from image using OCR."""
        if not self._check_feature_access("ocr"):
            return {"error": "OCR feature not available"}
        
        try:
            # Use OCR.Space API (https://ocr.space/OCRAPI) as a free API
            api_key = os.getenv("OCRSPACE_API_KEY")
            if not api_key:
                return {"error": "No OCR API key configured"}
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                data = {'language': 'eng', 'isOverlayRequired': False}
                headers = {'apikey': api_key}
                resp = requests.post('https://api.ocr.space/parse/image', files=files, data=data, headers=headers, timeout=30)
                if resp.status_code == 200:
                    result = resp.json()
                    parsed = result.get('ParsedResults', [{}])[0]
                    return {
                        "image_path": image_path,
                        "extracted_text": parsed.get('ParsedText', ''),
                        "confidence": parsed.get('MeanConfidence', None),
                        "source": "ocr.space"
                    }
                return {"error": f"OCR API error: {resp.text}"}
        except Exception as e:
            return {"error": f"OCR error: {str(e)}"} 