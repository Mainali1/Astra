"""
Dictionary Lookup Feature for Astra Voice Assistant
Provides word definitions, synonyms, and examples using free APIs
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

FEATURE_INFO = {
    'name': 'dictionary',
    'description': 'Look up word definitions, synonyms, and examples',
    'category': 'knowledge',
    'keywords': ['dictionary', 'define', 'definition', 'meaning', 'synonym', 'antonym', 'word'],
    'examples': [
        'Define the word "serendipity"',
        'What does "ephemeral" mean?',
        'Find synonyms for "happy"',
        'Look up "ubiquitous" in the dictionary'
    ],
    'version': '1.0.0',
    'author': 'Astra Team',
    'dependencies': ['requests'],
    'config': {
        'api_url': 'https://api.dictionaryapi.dev/api/v2/entries/en/',
        'fallback_api': 'https://api.datamuse.com/words',
        'max_results': 5
    }
}

class DictionaryFeature:
    """Dictionary lookup using free APIs"""
    
    def __init__(self):
        self.api_url = FEATURE_INFO['config']['api_url']
        self.fallback_api = FEATURE_INFO['config']['fallback_api']
        self.max_results = FEATURE_INFO['config']['max_results']
    
    def handle_dictionary_command(self, text: str) -> Dict[str, Any]:
        """Handle dictionary lookup commands"""
        try:
            # Extract word from command
            word = self._extract_word(text)
            if not word:
                return {
                    'success': False,
                    'response': 'Please specify a word to look up. For example: "Define the word serendipity"',
                    'error': 'No word specified'
                }
            
            # Get definition
            definition = self._get_definition(word)
            antonyms = self.get_antonyms_only(word)
            if definition:
                response = definition
                if antonyms and antonyms.get('success') and antonyms.get('data'):
                    response += f"\n\nAntonyms: {', '.join(antonyms['data'])}"
                return {
                    'success': True,
                    'response': response,
                    'word': word,
                    'data': definition
                }
            else:
                return {
                    'success': False,
                    'response': f"Sorry, I couldn't find a definition for '{word}'. Please check the spelling or try a different word.",
                    'error': 'Word not found'
                }
                
        except Exception as e:
            logger.error(f"Error in dictionary lookup: {e}")
            return {
                'success': False,
                'response': 'Sorry, I encountered an error while looking up the word. Please try again.',
                'error': str(e)
            }
    
    def _extract_word(self, text: str) -> Optional[str]:
        """Extract word from command text"""
        import re
        
        # Common patterns for dictionary commands
        patterns = [
            r'define\s+(?:the\s+)?word\s+"?([^"]+)"?',
            r'what\s+does\s+"?([^"]+)"?\s+mean',
            r'meaning\s+of\s+"?([^"]+)"?',
            r'dictionary\s+(?:for\s+)?"?([^"]+)"?',
            r'look\s+up\s+"?([^"]+)"?\s+in\s+the\s+dictionary',
            r'define\s+"?([^"]+)"?',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                word = match.group(1).strip()
                # Clean up the word
                word = re.sub(r'[^\w\s-]', '', word).strip()
                return word if word else None
        
        # Fallback: try to extract single word
        words = text.split()
        for word in words:
            if len(word) > 2 and word.isalpha():
                return word.lower()
        
        return None
    
    def _get_definition(self, word: str) -> str:
        """Get word definition from API"""
        try:
            # Try primary API
            response = requests.get(f"{self.api_url}{word}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                formatted = self._format_definition(data, word)
                return formatted if formatted else ""
            # Try fallback API for synonyms
            syn = self._get_synonyms(word)
            return syn if syn else ""
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            syn = self._get_synonyms(word)
            return syn if syn else ""
        except Exception as e:
            logger.error(f"Error getting definition: {e}")
            return ""
    
    def _format_definition(self, data: List[Dict], word: str) -> str:
        """Format definition data into readable response"""
        if not data:
            return ""
        result = f"**{word.title()}**\n\n"
        for entry in data[:2]:  # Limit to first 2 entries
            if 'meanings' in entry:
                for meaning in entry['meanings'][:3]:  # Limit to first 3 meanings
                    part_of_speech = meaning.get('partOfSpeech', '')
                    if part_of_speech:
                        result += f"*{part_of_speech}*\n"
                    for definition in meaning.get('definitions', [])[:2]:  # Limit to first 2 definitions
                        def_text = definition.get('definition', '')
                        if def_text:
                            result += f"\u2022 {def_text}\n"
                    examples = meaning.get('definitions', [])
                    for example in examples[:1]:  # Limit to first example
                        if 'example' in example:
                            result += f"  *Example: {example['example']}*\n"
                    result += "\n"
        if 'phonetic' in data[0]:
            result += f"Pronunciation: {data[0]['phonetic']}\n\n"
        if 'origin' in data[0]:
            result += f"Origin: {data[0]['origin']}\n\n"
        return result.strip() if result.strip() else ""
    
    def _get_synonyms(self, word: str) -> Optional[str]:
        """Get synonyms using fallback API"""
        try:
            # Get synonyms
            syn_response = requests.get(
                f"{self.fallback_api}?rel_syn={word}&max={self.max_results}",
                timeout=10
            )
            
            if syn_response.status_code == 200:
                synonyms = syn_response.json()
                if synonyms:
                    syn_list = [item['word'] for item in synonyms[:5]]
                    return f"**{word.title()}**\n\nSynonyms: {', '.join(syn_list)}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting synonyms: {e}")
            return None
    
    def get_word_info(self, word: str) -> Dict[str, Any]:
        """Get comprehensive word information"""
        try:
            response = requests.get(f"{self.api_url}{word}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'word': word,
                    'data': data,
                    'formatted': self._format_definition(data, word)
                }
            else:
                return {
                    'success': False,
                    'word': word,
                    'error': 'Word not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'word': word,
                'error': str(e)
            }
    
    def get_synonyms_only(self, word: str) -> Dict[str, Any]:
        """Get only synonyms for a word"""
        try:
            response = requests.get(
                f"{self.fallback_api}?rel_syn={word}&max={self.max_results}",
                timeout=10
            )
            
            if response.status_code == 200:
                synonyms = response.json()
                return {
                    'success': True,
                    'word': word,
                    'synonyms': [item['word'] for item in synonyms],
                    'response': f"Synonyms for '{word}': {', '.join([item['word'] for item in synonyms])}"
                }
            else:
                return {
                    'success': False,
                    'word': word,
                    'error': 'No synonyms found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'word': word,
                'error': str(e)
            }
    
    def get_antonyms_only(self, word: str) -> Dict[str, Any]:
        """Get only antonyms for a word"""
        try:
            response = requests.get(
                f"{self.fallback_api}?rel_ant={word}&max={self.max_results}",
                timeout=10
            )
            
            if response.status_code == 200:
                antonyms = response.json()
                return {
                    'success': True,
                    'word': word,
                    'antonyms': [item['word'] for item in antonyms],
                    'response': f"Antonyms for '{word}': {', '.join([item['word'] for item in antonyms])}"
                }
            else:
                return {
                    'success': False,
                    'word': word,
                    'error': 'No antonyms found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'word': word,
                'error': str(e)
            }

# Global instance
dictionary_feature = DictionaryFeature()

def handle_dictionary_command(text: str) -> Dict[str, Any]:
    """Handle dictionary lookup commands"""
    return dictionary_feature.handle_dictionary_command(text) 