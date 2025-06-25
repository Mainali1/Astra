"""
Joke Generator Feature for Astra Voice Assistant
Provides mood-based jokes and humor using free APIs and offline databases
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import os
import random

# Feature information
FEATURE_INFO = {
    'name': 'jokes',
    'description': 'Generate mood-based jokes and humor using free APIs',
    'category': 'entertainment',
    'keywords': ['joke', 'funny', 'humor', 'laugh', 'comedy', 'pun', 'wit'],
    'examples': [
        'Tell me a joke',
        'Make me laugh',
        'Tell me a funny story',
        'I need some humor',
        'Tell me a dad joke',
        'Tell me a programming joke'
    ],
    'version': '1.0.0',
    'author': 'Astra Team'
}

class JokeGenerator:
    """Joke generator with multiple API integrations and offline support"""
    
    def __init__(self):
        self.joke_api_key = os.getenv('JOKE_API_KEY', '')
        self.cache_file = Path("data/jokes_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(hours=12)  # Cache for 12 hours
        
        # Offline joke database
        self.offline_jokes = {
            'general': [
                {
                    'setup': 'Why don\'t scientists trust atoms?',
                    'punchline': 'Because they make up everything!',
                    'category': 'science',
                    'rating': 4.5
                },
                {
                    'setup': 'Why did the scarecrow win an award?',
                    'punchline': 'Because he was outstanding in his field!',
                    'category': 'general',
                    'rating': 4.2
                },
                {
                    'setup': 'What do you call a fake noodle?',
                    'punchline': 'An impasta!',
                    'category': 'food',
                    'rating': 4.0
                },
                {
                    'setup': 'Why don\'t eggs tell jokes?',
                    'punchline': 'They\'d crack each other up!',
                    'category': 'food',
                    'rating': 3.8
                },
                {
                    'setup': 'What do you call a bear with no teeth?',
                    'punchline': 'A gummy bear!',
                    'category': 'animals',
                    'rating': 4.1
                }
            ],
            'programming': [
                {
                    'setup': 'Why do programmers prefer dark mode?',
                    'punchline': 'Because light attracts bugs!',
                    'category': 'programming',
                    'rating': 4.7
                },
                {
                    'setup': 'How many programmers does it take to change a light bulb?',
                    'punchline': 'None, that\'s a hardware problem!',
                    'category': 'programming',
                    'rating': 4.5
                },
                {
                    'setup': 'Why did the programmer quit his job?',
                    'punchline': 'Because he didn\'t get arrays!',
                    'category': 'programming',
                    'rating': 4.3
                },
                {
                    'setup': 'What do you call a programmer from Finland?',
                    'punchline': 'Nerdic!',
                    'category': 'programming',
                    'rating': 4.0
                },
                {
                    'setup': 'Why do Java developers wear glasses?',
                    'punchline': 'Because they can\'t C#!',
                    'category': 'programming',
                    'rating': 4.6
                }
            ],
            'dad_jokes': [
                {
                    'setup': 'What do you call a can opener that doesn\'t work?',
                    'punchline': 'A can\'t opener!',
                    'category': 'dad_jokes',
                    'rating': 4.8
                },
                {
                    'setup': 'Why did the math book look so sad?',
                    'punchline': 'Because it had too many problems!',
                    'category': 'education',
                    'rating': 4.4
                },
                {
                    'setup': 'What do you call a fish wearing a bowtie?',
                    'punchline': 'So-fish-ticated!',
                    'category': 'animals',
                    'rating': 4.2
                },
                {
                    'setup': 'Why don\'t skeletons fight each other?',
                    'punchline': 'They don\'t have the guts!',
                    'category': 'general',
                    'rating': 4.0
                },
                {
                    'setup': 'What do you call a bear with no teeth?',
                    'punchline': 'A gummy bear!',
                    'category': 'animals',
                    'rating': 4.1
                }
            ],
            'one_liners': [
                'I told my wife she was drawing her eyebrows too high. She looked surprised.',
                'Why don\'t scientists trust atoms? Because they make up everything!',
                'I\'m reading a book about anti-gravity. It\'s impossible to put down!',
                'Did you hear about the mathematician who\'s afraid of negative numbers? He\'ll stop at nothing to avoid them.',
                'Why did the scarecrow win an award? Because he was outstanding in his field!',
                'I used to be a baker, but I couldn\'t make enough dough.',
                'What do you call a fake noodle? An impasta!',
                'Why don\'t eggs tell jokes? They\'d crack each other up!',
                'I\'m on a seafood diet. I see food and I eat it.',
                'Why did the bicycle fall over? Because it was two-tired!'
            ]
        }
        
        # Mood-based joke categories
        self.mood_categories = {
            'happy': ['general', 'dad_jokes', 'one_liners'],
            'sad': ['dad_jokes', 'one_liners', 'general'],
            'stressed': ['programming', 'one_liners'],
            'tired': ['dad_jokes', 'one_liners'],
            'excited': ['general', 'programming'],
            'bored': ['programming', 'general', 'dad_jokes'],
            'angry': ['one_liners', 'dad_jokes'],
            'confused': ['dad_jokes', 'general']
        }
        
        # Load cache
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load jokes cache from file"""
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
        """Save jokes cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving jokes cache: {e}")
    
    def _get_cached_joke(self, category: str) -> Optional[Dict[str, Any]]:
        """Get joke from cache"""
        cache_key = f"joke_{category.lower()}"
        if cache_key in self.cache:
            data = self.cache[cache_key]
            if 'timestamp' in data:
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < self.cache_duration:
                    return data.get('joke')
        return None
    
    def _cache_joke(self, category: str, joke_data: Dict[str, Any]):
        """Cache joke data"""
        cache_key = f"joke_{category.lower()}"
        self.cache[cache_key] = {
            'joke': joke_data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def _get_joke_from_api(self, category: str = 'general') -> Dict[str, Any]:
        """Get joke from external API"""
        try:
            # Try multiple free joke APIs
            apis = [
                {
                    'url': 'https://official-joke-api.appspot.com/random_joke',
                    'params': {'category': category} if category != 'general' else {}
                },
                {
                    'url': 'https://api.chucknorris.io/jokes/random',
                    'params': {}
                },
                {
                    'url': 'https://v2.jokeapi.dev/joke/Any',
                    'params': {'safe-mode': 'on'}
                }
            ]
            
            for api in apis:
                try:
                    response = requests.get(api['url'], params=api['params'], timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Parse different API formats
                    if 'joke' in data:  # Chuck Norris API
                        return {
                            'success': True,
                            'setup': data['joke'],
                            'punchline': '',
                            'category': 'chuck_norris',
                            'source': 'api'
                        }
                    elif 'setup' in data and 'punchline' in data:  # JokeAPI
                        return {
                            'success': True,
                            'setup': data['setup'],
                            'punchline': data['punchline'],
                            'category': data.get('category', 'general'),
                            'source': 'api'
                        }
                    elif 'value' in data:  # Some APIs use 'value' field
                        return {
                            'success': True,
                            'setup': data['value'],
                            'punchline': '',
                            'category': 'general',
                            'source': 'api'
                        }
                        
                except requests.RequestException:
                    continue
            
            return {
                'success': False,
                'error': 'All joke APIs are currently unavailable'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"API error: {str(e)}"
            }
    
    def _get_offline_joke(self, category: str = 'general') -> Dict[str, Any]:
        """Get joke from offline database"""
        available_categories = list(self.offline_jokes.keys())
        
        if category not in available_categories:
            category = random.choice(available_categories)
        
        jokes = self.offline_jokes[category]
        joke = random.choice(jokes)
        
        return {
            'success': True,
            'setup': joke.get('setup', joke),
            'punchline': joke.get('punchline', ''),
            'category': joke.get('category', category),
            'source': 'offline',
            'rating': joke.get('rating', 4.0)
        }
    
    def _format_joke_response(self, joke_data: Dict[str, Any]) -> str:
        """Format joke into a readable response"""
        if not joke_data.get('success'):
            return f"Sorry, I couldn't find a joke right now. {joke_data.get('error', '')}"
        
        setup = joke_data.get('setup', '')
        punchline = joke_data.get('punchline', '')
        
        if punchline:
            return f"{setup}\n\n{punchline}"
        else:
            return setup
    
    def get_joke(self, category: str = 'general', mood: str = None) -> Dict[str, Any]:
        """Get a joke based on category and mood"""
        # Determine category based on mood
        if mood and mood in self.mood_categories:
            category = random.choice(self.mood_categories[mood])
        
        # Check cache first
        cached_joke = self._get_cached_joke(category)
        if cached_joke:
            return {
                'success': True,
                'data': cached_joke,
                'response': self._format_joke_response(cached_joke),
                'source': 'cache'
            }
        
        # Try API first
        joke_data = self._get_joke_from_api(category)
        
        if not joke_data.get('success'):
            # Fallback to offline jokes
            joke_data = self._get_offline_joke(category)
        
        if joke_data.get('success'):
            # Cache the result
            self._cache_joke(category, joke_data)
            
            # Format response
            formatted_response = self._format_joke_response(joke_data)
            
            return {
                'success': True,
                'data': joke_data,
                'response': formatted_response,
                'source': joke_data.get('source', 'unknown')
            }
        
        return joke_data
    
    def get_dad_joke(self) -> Dict[str, Any]:
        """Get a dad joke specifically"""
        return self.get_joke('dad_jokes')
    
    def get_programming_joke(self) -> Dict[str, Any]:
        """Get a programming joke specifically"""
        return self.get_joke('programming')
    
    def get_one_liner(self) -> Dict[str, Any]:
        """Get a one-liner joke"""
        return self.get_joke('one_liners')
    
    def get_mood_based_joke(self, mood: str) -> Dict[str, Any]:
        """Get a joke based on user's mood"""
        return self.get_joke(mood=mood)
    
    def get_joke_categories(self) -> Dict[str, Any]:
        """Get available joke categories"""
        return {
            'success': True,
            'categories': list(self.offline_jokes.keys()),
            'mood_categories': list(self.mood_categories.keys())
        }

def handle_joke_command(text: str) -> Dict[str, Any]:
    """Handle joke-related voice commands"""
    generator = JokeGenerator()
    
    text_lower = text.lower()
    
    # Extract intent from text
    if any(word in text_lower for word in ['dad', 'father']):
        return generator.get_dad_joke()
    elif any(word in text_lower for word in ['programming', 'code', 'developer', 'software']):
        return generator.get_programming_joke()
    elif any(word in text_lower for word in ['one liner', 'one-liner', 'short']):
        return generator.get_one_liner()
    elif any(word in text_lower for word in ['sad', 'depressed', 'down']):
        return generator.get_mood_based_joke('sad')
    elif any(word in text_lower for word in ['stressed', 'anxious', 'worried']):
        return generator.get_mood_based_joke('stressed')
    elif any(word in text_lower for word in ['tired', 'exhausted', 'sleepy']):
        return generator.get_mood_based_joke('tired')
    elif any(word in text_lower for word in ['excited', 'happy', 'joyful']):
        return generator.get_mood_based_joke('happy')
    elif any(word in text_lower for word in ['bored', 'boring']):
        return generator.get_mood_based_joke('bored')
    elif any(word in text_lower for word in ['angry', 'mad', 'furious']):
        return generator.get_mood_based_joke('angry')
    elif any(word in text_lower for word in ['confused', 'puzzled']):
        return generator.get_mood_based_joke('confused')
    else:
        # Default to general joke
        return generator.get_joke()

# Export feature information
FEATURE_EXPORTS = {
    'handle_joke_command': handle_joke_command,
    'JokeGenerator': JokeGenerator,
    'FEATURE_INFO': FEATURE_INFO
} 