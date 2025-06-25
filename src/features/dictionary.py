"""
Astra AI Assistant - Dictionary Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import aiohttp
from typing import Dict, Any, List, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class DictionaryEntry:
    """Represents a dictionary entry."""
    
    def __init__(self, word: str, phonetic: Optional[str] = None):
        """Initialize a dictionary entry."""
        self.word = word
        self.phonetic = phonetic
        self.meanings: List[Dict[str, Any]] = []
    
    def add_meaning(self, part_of_speech: str, definitions: List[str],
                   synonyms: Optional[List[str]] = None,
                   antonyms: Optional[List[str]] = None):
        """Add a meaning to the entry."""
        self.meanings.append({
            'part_of_speech': part_of_speech,
            'definitions': definitions,
            'synonyms': synonyms or [],
            'antonyms': antonyms or []
        })
    
    def format_entry(self) -> str:
        """Format the entry for display."""
        result = f"{self.word}"
        if self.phonetic:
            result += f" /{self.phonetic}/"
        result += "\n\n"
        
        for meaning in self.meanings:
            result += f"[{meaning['part_of_speech']}]\n"
            for i, definition in enumerate(meaning['definitions'], 1):
                result += f"{i}. {definition}\n"
            
            if meaning['synonyms']:
                result += f"\nSynonyms: {', '.join(meaning['synonyms'][:5])}\n"
            if meaning['antonyms']:
                result += f"Antonyms: {', '.join(meaning['antonyms'][:5])}\n"
            result += "\n"
        
        return result.strip()

class DictionaryFeature:
    """Dictionary feature for Astra."""
    
    def __init__(self, config: Config):
        """Initialize the dictionary feature."""
        self.config = config
        self.base_url = "https://api.dictionaryapi.dev/api/v2/entries/en"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, DictionaryEntry] = {}
    
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def _lookup_word(self, word: str) -> Optional[DictionaryEntry]:
        """Look up a word in the dictionary."""
        try:
            # Check cache first
            if word.lower() in self.cache:
                return self.cache[word.lower()]
            
            await self._ensure_session()
            
            # Make API request
            async with self.session.get(f"{self.base_url}/{word}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        # Parse first result
                        result = data[0]
                        entry = DictionaryEntry(
                            word=result['word'],
                            phonetic=result.get('phonetic')
                        )
                        
                        # Add meanings
                        for meaning in result.get('meanings', []):
                            definitions = [
                                d['definition']
                                for d in meaning.get('definitions', [])
                            ]
                            entry.add_meaning(
                                part_of_speech=meaning['partOfSpeech'],
                                definitions=definitions,
                                synonyms=meaning.get('synonyms', []),
                                antonyms=meaning.get('antonyms', [])
                            )
                        
                        # Cache the result
                        self.cache[word.lower()] = entry
                        return entry
                    
                return None
                
        except Exception as e:
            logger.error(f"Error looking up word: {str(e)}")
            return None
    
    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle dictionary-related intents."""
        try:
            action = intent.get('action', '')
            params = intent.get('parameters', {})
            
            if action == 'define_word':
                # Look up word definition
                word = params.get('word', '')
                if not word:
                    return "What word would you like me to define?"
                
                entry = await self._lookup_word(word)
                if entry:
                    return entry.format_entry()
                return f"I couldn't find a definition for '{word}'."
                
            elif action == 'get_synonyms':
                # Get synonyms for a word
                word = params.get('word', '')
                if not word:
                    return "What word would you like synonyms for?"
                
                entry = await self._lookup_word(word)
                if entry:
                    synonyms = set()
                    for meaning in entry.meanings:
                        synonyms.update(meaning['synonyms'])
                    
                    if synonyms:
                        return f"Synonyms for '{word}': {', '.join(sorted(synonyms)[:10])}"
                    return f"I couldn't find any synonyms for '{word}'."
                return f"I couldn't find '{word}' in the dictionary."
                
            elif action == 'get_antonyms':
                # Get antonyms for a word
                word = params.get('word', '')
                if not word:
                    return "What word would you like antonyms for?"
                
                entry = await self._lookup_word(word)
                if entry:
                    antonyms = set()
                    for meaning in entry.meanings:
                        antonyms.update(meaning['antonyms'])
                    
                    if antonyms:
                        return f"Antonyms for '{word}': {', '.join(sorted(antonyms)[:10])}"
                    return f"I couldn't find any antonyms for '{word}'."
                return f"I couldn't find '{word}' in the dictionary."
            
            else:
                return "I'm not sure what you want to look up in the dictionary."
            
        except Exception as e:
            logger.error(f"Error handling dictionary request: {str(e)}")
            return "I'm sorry, but I encountered an error with the dictionary lookup."
    
    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Dictionary API is free and doesn't require authentication
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None 