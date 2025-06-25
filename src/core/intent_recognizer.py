"""
Astra AI Assistant - Intent Recognizer Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import re
from typing import Dict, Optional, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Intent:
    """Represents a recognized intent."""
    feature: str
    action: str
    confidence: float
    parameters: Dict[str, Any]

class IntentRecognizer:
    """Handles natural language understanding and intent recognition."""
    
    def __init__(self):
        """Initialize the intent recognizer."""
        self.patterns: Dict[str, List[Dict[str, Any]]] = {
            'weather': [
                {'pattern': r'weather (?:in|at|for) (?P<location>.+)', 'action': 'get_weather'},
                {'pattern': r'(?:how is|what is) the weather (?:in|at|for) (?P<location>.+)', 'action': 'get_weather'},
            ],
            'time': [
                {'pattern': r'(?:what (?:time|date) is it|current time)', 'action': 'get_time'},
                {'pattern': r'time in (?P<location>.+)', 'action': 'get_time_zone'},
            ],
            'calculator': [
                {'pattern': r'calculate (?P<expression>.+)', 'action': 'calculate'},
                {'pattern': r'(?:what is|solve) (?P<expression>.+)', 'action': 'calculate'},
            ],
            'reminder': [
                {'pattern': r'remind me to (?P<task>.+) (?:in|at) (?P<time>.+)', 'action': 'set_reminder'},
                {'pattern': r'set (?:a|an) (?:reminder|alarm) (?:for|to) (?P<task>.+) (?:in|at) (?P<time>.+)', 'action': 'set_reminder'},
            ],
            'todo': [
                {'pattern': r'add (?:a )?task (?P<task>.+)', 'action': 'add_task'},
                {'pattern': r'mark task (?P<task>.+) as (?P<status>done|complete)', 'action': 'complete_task'},
            ],
            'timer': [
                {'pattern': r'set (?:a )?timer for (?P<duration>.+)', 'action': 'set_timer'},
                {'pattern': r'start (?:a )?timer for (?P<duration>.+)', 'action': 'set_timer'},
            ],
            'music': [
                {'pattern': r'play (?P<song>.+)', 'action': 'play_music'},
                {'pattern': r'stop music', 'action': 'stop_music'},
            ],
            'news': [
                {'pattern': r'(?:get|read) (?:the )?news', 'action': 'get_news'},
                {'pattern': r'news about (?P<topic>.+)', 'action': 'get_news_topic'},
            ],
        }
        
        # Compile all patterns
        for feature, patterns in self.patterns.items():
            for pattern in patterns:
                pattern['compiled'] = re.compile(pattern['pattern'], re.IGNORECASE)
    
    async def recognize(self, text: str) -> Optional[Intent]:
        """Recognize intent from text input."""
        try:
            # Check each feature's patterns
            for feature, patterns in self.patterns.items():
                for pattern in patterns:
                    match = pattern['compiled'].match(text)
                    if match:
                        # Extract parameters from the match
                        parameters = match.groupdict()
                        
                        return Intent(
                            feature=feature,
                            action=pattern['action'],
                            confidence=1.0,  # Simple pattern matching always returns 1.0
                            parameters=parameters
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error recognizing intent: {str(e)}")
            return None
    
    def add_pattern(self, feature: str, pattern: str, action: str):
        """Add a new pattern for intent recognition."""
        if feature not in self.patterns:
            self.patterns[feature] = []
            
        pattern_dict = {
            'pattern': pattern,
            'action': action,
            'compiled': re.compile(pattern, re.IGNORECASE)
        }
        
        self.patterns[feature].append(pattern_dict)
    
    def remove_pattern(self, feature: str, pattern: str):
        """Remove a pattern from intent recognition."""
        if feature in self.patterns:
            self.patterns[feature] = [
                p for p in self.patterns[feature]
                if p['pattern'] != pattern
            ] 