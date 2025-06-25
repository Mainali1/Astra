"""
Intent Recognition for Astra Voice Assistant
Maps user speech to specific features and intents
"""

import re
import logging
from typing import Dict, Any, Optional, List
import json
from pathlib import Path

from ..config import config

logger = logging.getLogger(__name__)

class IntentRecognizer:
    """Recognizes user intents and maps them to features"""
    
    def __init__(self):
        self.config = config
        self.intent_patterns = self._load_intent_patterns()
        self.feature_keywords = self._load_feature_keywords()
        
    def _load_intent_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load intent recognition patterns"""
        patterns = {
            "weather": [
                {"pattern": r"weather|temperature|forecast|climate", "feature": "weather"},
                {"pattern": r"what's the weather|how's the weather|weather today", "feature": "weather"},
                {"pattern": r"temperature outside|is it raining|will it rain", "feature": "weather"}
            ],
            "time": [
                {"pattern": r"what time|current time|time now", "feature": "time"},
                {"pattern": r"tell me the time|what's the time", "feature": "time"}
            ],
            "date": [
                {"pattern": r"what date|today's date|current date", "feature": "date"},
                {"pattern": r"what day|what day is it", "feature": "date"}
            ],
            "calculator": [
                {"pattern": r"calculate|math|compute|add|subtract|multiply|divide", "feature": "calculator"},
                {"pattern": r"what is (\d+[\+\-\*\/]\d+)", "feature": "calculator"}
            ],
            "timer": [
                {"pattern": r"set timer|start timer|timer for", "feature": "timer"},
                {"pattern": r"countdown|alarm|remind me in", "feature": "timer"}
            ],
            "stopwatch": [
                {"pattern": r"stopwatch|start stopwatch|lap time", "feature": "stopwatch"}
            ],
            "notes": [
                {"pattern": r"take note|write down|remember that", "feature": "notes"},
                {"pattern": r"note|memo|jot down", "feature": "notes"}
            ],
            "tasks": [
                {"pattern": r"add task|new task|todo|to do", "feature": "tasks"},
                {"pattern": r"task list|my tasks|show tasks", "feature": "tasks"}
            ],
            "music": [
                {"pattern": r"play music|start music|music player", "feature": "music"},
                {"pattern": r"pause|stop|next|previous", "feature": "music"}
            ],
            "joke": [
                {"pattern": r"tell joke|make me laugh|funny", "feature": "joke"},
                {"pattern": r"joke|humor|comedy", "feature": "joke"}
            ],
            "search": [
                {"pattern": r"search for|find|look up", "feature": "search"},
                {"pattern": r"google|web search|internet search", "feature": "search"}
            ],
            "news": [
                {"pattern": r"news|headlines|current events", "feature": "news"},
                {"pattern": r"what's happening|latest news", "feature": "news"}
            ],
            "calendar": [
                {"pattern": r"calendar|schedule|appointment", "feature": "calendar"},
                {"pattern": r"add event|meeting|reminder", "feature": "calendar"}
            ],
            "email": [
                {"pattern": r"email|mail|send email", "feature": "email"},
                {"pattern": r"compose|draft|write email", "feature": "email"}
            ],
            "file_manager": [
                {"pattern": r"file|folder|directory", "feature": "file_manager"},
                {"pattern": r"open file|create folder|delete", "feature": "file_manager"}
            ],
            "system_control": [
                {"pattern": r"volume|brightness|system", "feature": "system_control"},
                {"pattern": r"shutdown|restart|sleep", "feature": "system_control"}
            ],
            "translator": [
                {"pattern": r"translate|translation|language", "feature": "translator"},
                {"pattern": r"how do you say|in spanish|in french", "feature": "translator"}
            ],
            "dictionary": [
                {"pattern": r"define|definition|meaning of", "feature": "dictionary"},
                {"pattern": r"what does|dictionary|word meaning", "feature": "dictionary"},
                {"pattern": r"define the word|look up|synonym|antonym", "feature": "dictionary"}
            ],
            "converter": [
                {"pattern": r"convert|conversion|units", "feature": "converter"},
                {"pattern": r"miles to km|pounds to kg|fahrenheit to celsius", "feature": "converter"},
                {"pattern": r"how many|what is.*in.*", "feature": "converter"}
            ],
            "pomodoro": [
                {"pattern": r"pomodoro|focus timer|work session", "feature": "pomodoro"},
                {"pattern": r"start pomodoro|break time", "feature": "pomodoro"}
            ],
            "wiki": [
                {"pattern": r"wikipedia|wiki|information about", "feature": "wiki"},
                {"pattern": r"who is|what is|tell me about", "feature": "wiki"}
            ],
            "quote": [
                {"pattern": r"quote|inspiration|motivation", "feature": "quote"},
                {"pattern": r"inspirational quote|famous quote", "feature": "quote"}
            ],
            "mood": [
                {"pattern": r"mood|how are you feeling|emotion", "feature": "mood"},
                {"pattern": r"track mood|mood tracker", "feature": "mood"}
            ],
            "habit": [
                {"pattern": r"habit|routine|track habit", "feature": "habit"},
                {"pattern": r"daily habit|habit tracker", "feature": "habit"}
            ],
            "project_management": [
                {"pattern": r"plan project|create project plan", "feature": "project_manager"},
                {"pattern": r"brainstorm|generate ideas", "feature": "project_manager"},
                {"pattern": r"optimize schedule|task schedule", "feature": "project_manager"},
                {"pattern": r"analyze risks|project risks", "feature": "project_manager"}
            ],
            "email_management": [
                {"pattern": r"summarize emails|email summary", "feature": "email_manager"},
                {"pattern": r"generate email response|reply to email", "feature": "email_manager"},
                {"pattern": r"prioritize emails|email priority", "feature": "email_manager"},
                {"pattern": r"check important emails|urgent emails", "feature": "email_manager"}
            ],
            "document_management": [
                {"pattern": r"summarize document|document summary", "feature": "summarizer"},
                {"pattern": r"analyze (text|document|pdf|file)", "feature": "summarizer"},
                {"pattern": r"extract key points|main points", "feature": "summarizer"},
                {"pattern": r"document analysis|text analysis", "feature": "summarizer"}
            ],
            "automation": [
                {"pattern": r"create (macro|automation|routine)", "feature": "automation_manager"},
                {"pattern": r"start (my )?(routine|automation|macro)", "feature": "automation_manager"},
                {"pattern": r"run (automation|macro|script)", "feature": "automation_manager"},
                {"pattern": r"show (my )?(automations|macros|workflows)", "feature": "automation_manager"},
                {"pattern": r"enable automation", "feature": "automation_manager"},
                {"pattern": r"disable automation", "feature": "automation_manager"}
            ],
            "workflow": [
                {"pattern": r"create workflow", "feature": "workflow_manager"},
                {"pattern": r"run workflow", "feature": "workflow_manager"},
                {"pattern": r"show workflows", "feature": "workflow_manager"},
                {"pattern": r"workflow status", "feature": "workflow_manager"},
                {"pattern": r"enable workflow", "feature": "workflow_manager"},
                {"pattern": r"disable workflow", "feature": "workflow_manager"}
            ],
            "script": [
                {"pattern": r"create script", "feature": "script_manager"},
                {"pattern": r"run script", "feature": "script_manager"},
                {"pattern": r"show scripts", "feature": "script_manager"},
                {"pattern": r"script status", "feature": "script_manager"},
                {"pattern": r"enable script", "feature": "script_manager"},
                {"pattern": r"disable script", "feature": "script_manager"}
            ]
        }
        
        return patterns
    
    def _load_feature_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for each feature"""
        keywords = {
            "weather": ["weather", "temperature", "forecast", "climate", "rain", "sunny", "cold", "hot"],
            "time": ["time", "clock", "hour", "minute", "current time"],
            "date": ["date", "day", "month", "year", "today", "tomorrow"],
            "calculator": ["calculate", "math", "compute", "add", "subtract", "multiply", "divide", "equation"],
            "timer": ["timer", "countdown", "alarm", "reminder", "set timer"],
            "stopwatch": ["stopwatch", "lap", "timing", "race"],
            "notes": ["note", "memo", "write", "remember", "jot down"],
            "tasks": ["task", "todo", "to do", "checklist", "assignment"],
            "music": ["music", "song", "play", "pause", "stop", "next", "previous"],
            "joke": ["joke", "funny", "humor", "laugh", "comedy"],
            "search": ["search", "find", "look up", "google", "web search"],
            "news": ["news", "headlines", "current events", "latest"],
            "calendar": ["calendar", "schedule", "appointment", "event", "meeting"],
            "email": ["email", "mail", "send", "compose", "draft"],
            "file_manager": ["file", "folder", "directory", "open", "create", "delete"],
            "system_control": ["volume", "brightness", "system", "shutdown", "restart"],
            "translator": ["translate", "translation", "language", "spanish", "french"],
            "dictionary": ["define", "definition", "meaning", "word", "dictionary"],
            "converter": ["convert", "conversion", "miles", "kilometers", "pounds", "kilograms"],
            "pomodoro": ["pomodoro", "focus", "work", "break", "session"],
            "wiki": ["wikipedia", "wiki", "information", "who is", "what is"],
            "quote": ["quote", "inspiration", "motivation", "famous"],
            "mood": ["mood", "feeling", "emotion", "how are you"],
            "habit": ["habit", "routine", "track", "daily"],
            "project_manager": [
                "project", "plan", "brainstorm", "ideas", "schedule", 
                "tasks", "risks", "analysis", "optimize", "planning"
            ],
            "email_manager": [
                "email", "mail", "inbox", "summarize", "prioritize",
                "response", "reply", "urgent", "important"
            ],
            "summarizer": [
                "summarize", "summary", "document", "text", "analyze",
                "extract", "key points", "main points", "pdf", "file"
            ],
            "automation_manager": [
                "automation", "macro", "routine", "workflow", "script",
                "automate", "create", "run", "start", "stop", "enable",
                "disable", "show", "list", "status", "morning", "evening",
                "work", "home", "schedule", "trigger"
            ],
            "workflow_manager": [
                "workflow", "process", "steps", "sequence", "automation",
                "create", "run", "start", "stop", "enable", "disable",
                "show", "list", "status", "condition", "action", "trigger"
            ],
            "script_manager": [
                "script", "command", "system", "automate", "run",
                "create", "execute", "start", "stop", "enable", "disable",
                "show", "list", "status", "backup", "cleanup", "schedule"
            ]
        }
        
        return keywords
    
    def recognize_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """Recognize intent from user text"""
        text_lower = text.lower().strip()
        
        # Check for exact matches first
        for intent_type, patterns in self.intent_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                feature = pattern_info["feature"]
                
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Extract parameters based on feature type
                    parameters = self._extract_parameters(feature, text_lower)
                    
                    return {
                        "intent": intent_type,
                        "feature": feature,
                        "confidence": 0.9,
                        "parameters": parameters,
                        "original_text": text
                    }
        
        # Check for keyword matches
        best_match = None
        best_score = 0
        
        for feature, keywords in self.feature_keywords.items():
            score = self._calculate_keyword_score(text_lower, keywords)
            if score > best_score and score > 0.3:  # Minimum threshold
                best_score = score
                best_match = {
                    "intent": "general",
                    "feature": feature,
                    "confidence": score,
                    "parameters": {},
                    "original_text": text
                }
        
        return best_match
    
    def _extract_parameters(self, feature: str, text: str) -> Dict[str, Any]:
        """Extract parameters from text based on feature type"""
        parameters = {}
        
        if feature == "weather":
            # Extract location
            location_match = re.search(r"(?:in|at|for)\s+([a-zA-Z\s]+)", text)
            if location_match:
                parameters["location"] = location_match.group(1).strip()
            
            # Extract time
            if "tomorrow" in text:
                parameters["time"] = "tomorrow"
            elif "weekend" in text:
                parameters["time"] = "weekend"
        
        elif feature == "calculator":
            # Extract mathematical expression
            math_match = re.search(r"(\d+[\+\-\*\/]\d+)", text)
            if math_match:
                parameters["expression"] = math_match.group(1)
        
        elif feature == "timer":
            # Extract time duration
            time_match = re.search(r"(\d+)\s*(minute|hour|second)", text)
            if time_match:
                parameters["duration"] = int(time_match.group(1))
                parameters["unit"] = time_match.group(2)
        
        elif feature == "notes":
            # Extract note content
            note_match = re.search(r"(?:note|remember|write down)\s+(.+)", text)
            if note_match:
                parameters["content"] = note_match.group(1).strip()
        
        elif feature == "tasks":
            # Extract task description
            task_match = re.search(r"(?:task|todo|to do)\s+(.+)", text)
            if task_match:
                parameters["description"] = task_match.group(1).strip()
        
        elif feature == "search":
            # Extract search query
            search_match = re.search(r"(?:search|find|look up)\s+(.+)", text)
            if search_match:
                parameters["query"] = search_match.group(1).strip()
        
        elif feature == "email":
            # Extract email details
            to_match = re.search(r"to\s+([a-zA-Z\s]+)", text)
            if to_match:
                parameters["to"] = to_match.group(1).strip()
            
            subject_match = re.search(r"about\s+(.+)", text)
            if subject_match:
                parameters["subject"] = subject_match.group(1).strip()
        
        elif feature == "translator":
            # Extract language and text
            lang_match = re.search(r"(?:in|to)\s+([a-zA-Z]+)", text)
            if lang_match:
                parameters["target_language"] = lang_match.group(1).strip()
            
            text_match = re.search(r"(?:translate|say)\s+(.+)", text)
            if text_match:
                parameters["text"] = text_match.group(1).strip()
        
        elif feature == "dictionary":
            # Extract word to define
            word_match = re.search(r"(?:define|meaning of|what does)\s+([a-zA-Z]+)", text)
            if word_match:
                parameters["word"] = word_match.group(1).strip()
        
        elif feature == "converter":
            # Extract conversion details
            convert_match = re.search(r"(\d+)\s*([a-zA-Z]+)\s+to\s+([a-zA-Z]+)", text)
            if convert_match:
                parameters["value"] = float(convert_match.group(1))
                parameters["from_unit"] = convert_match.group(2).strip()
                parameters["to_unit"] = convert_match.group(3).strip()
        
        elif feature == "pomodoro":
            # Extract duration
            duration_match = re.search(r"(\d+)\s*minute", text)
            if duration_match:
                parameters["duration"] = int(duration_match.group(1))
        
        elif feature == "automation_manager":
            # Extract automation name and type
            name_match = re.search(r"(create|run|start|stop|enable|disable)\s+(\w+)\s+(routine|macro|automation)", text)
            if name_match:
                parameters["action"] = name_match.group(1)
                parameters["name"] = name_match.group(2)
                parameters["type"] = name_match.group(3)

        elif feature == "workflow_manager":
            # Extract workflow name and action
            workflow_match = re.search(r"(create|run|start|stop|enable|disable)\s+(\w+)\s+workflow", text)
            if workflow_match:
                parameters["action"] = workflow_match.group(1)
                parameters["name"] = workflow_match.group(2)

        elif feature == "script_manager":
            # Extract script name and action
            script_match = re.search(r"(create|run|start|stop|enable|disable)\s+(\w+)\s+script", text)
            if script_match:
                parameters["action"] = script_match.group(1)
                parameters["name"] = script_match.group(2)
        
        return parameters
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate similarity score based on keywords"""
        if not keywords:
            return 0.0
        
        matches = 0
        for keyword in keywords:
            if keyword in text:
                matches += 1
        
        return matches / len(keywords)
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents"""
        return list(self.intent_patterns.keys())
    
    def get_feature_keywords(self, feature: str) -> List[str]:
        """Get keywords for a specific feature"""
        return self.feature_keywords.get(feature, [])
    
    def add_custom_pattern(self, intent: str, pattern: str, feature: str):
        """Add a custom intent pattern"""
        if intent not in self.intent_patterns:
            self.intent_patterns[intent] = []
        
        self.intent_patterns[intent].append({
            "pattern": pattern,
            "feature": feature
        })
        
        logger.info(f"Added custom pattern: {pattern} -> {feature}")
    
    def remove_pattern(self, intent: str, pattern: str):
        """Remove an intent pattern"""
        if intent in self.intent_patterns:
            self.intent_patterns[intent] = [
                p for p in self.intent_patterns[intent] 
                if p["pattern"] != pattern
            ]
            logger.info(f"Removed pattern: {pattern}")
    
    def save_patterns(self):
        """Save patterns to file"""
        try:
            patterns_file = self.config.data_dir / "intent_patterns.json"
            with open(patterns_file, 'w') as f:
                json.dump(self.intent_patterns, f, indent=2)
            logger.info("Intent patterns saved")
        except Exception as e:
            logger.error(f"Error saving intent patterns: {e}")
    
    def load_patterns(self):
        """Load patterns from file"""
        try:
            patterns_file = self.config.data_dir / "intent_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    self.intent_patterns = json.load(f)
                logger.info("Intent patterns loaded")
        except Exception as e:
            logger.error(f"Error loading intent patterns: {e}") 