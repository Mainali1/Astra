"""
Translation Feature for Astra Voice Assistant
Provides multi-language translation using free APIs and offline dictionaries
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import os
import hashlib

# Feature information
FEATURE_INFO = {
    'name': 'translation',
    'description': 'Translate text between 50+ languages using multiple free APIs',
    'category': 'communication',
    'keywords': ['translate', 'translation', 'language', 'interpret', 'convert'],
    'examples': [
        'Translate hello to Spanish',
        'What is bonjour in English?',
        'Translate this text to French',
        'How do you say thank you in German?',
        'Translate from English to Japanese'
    ],
    'version': '1.0.0',
    'author': 'Astra Team'
}

class TranslationService:
    """Translation service with multiple API integrations and offline support"""
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
        self.libre_api_key = os.getenv('LIBRE_TRANSLATE_API_KEY', '')
        self.cache_file = Path("data/translation_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(days=7)  # Cache for 7 days
        
        # Supported languages with codes
        self.languages = {
            'english': 'en',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'italian': 'it',
            'portuguese': 'pt',
            'russian': 'ru',
            'chinese': 'zh',
            'japanese': 'ja',
            'korean': 'ko',
            'arabic': 'ar',
            'hindi': 'hi',
            'bengali': 'bn',
            'urdu': 'ur',
            'turkish': 'tr',
            'dutch': 'nl',
            'swedish': 'sv',
            'norwegian': 'no',
            'danish': 'da',
            'finnish': 'fi',
            'polish': 'pl',
            'czech': 'cs',
            'hungarian': 'hu',
            'romanian': 'ro',
            'bulgarian': 'bg',
            'greek': 'el',
            'hebrew': 'he',
            'thai': 'th',
            'vietnamese': 'vi',
            'indonesian': 'id',
            'malay': 'ms',
            'filipino': 'tl',
            'swahili': 'sw',
            'yoruba': 'yo',
            'zulu': 'zu',
            'afrikaans': 'af',
            'albanian': 'sq',
            'armenian': 'hy',
            'azerbaijani': 'az',
            'basque': 'eu',
            'belarusian': 'be',
            'bosnian': 'bs',
            'catalan': 'ca',
            'croatian': 'hr',
            'estonian': 'et',
            'galician': 'gl',
            'georgian': 'ka',
            'icelandic': 'is',
            'irish': 'ga',
            'latvian': 'lv',
            'lithuanian': 'lt',
            'macedonian': 'mk',
            'maltese': 'mt',
            'mongolian': 'mn',
            'persian': 'fa',
            'serbian': 'sr',
            'slovak': 'sk',
            'slovenian': 'sl',
            'ukrainian': 'uk',
            'welsh': 'cy'
        }
        
        # Common phrases for offline translation
        self.common_phrases = {
            'hello': {
                'es': 'hola',
                'fr': 'bonjour',
                'de': 'hallo',
                'it': 'ciao',
                'pt': 'olá',
                'ru': 'привет',
                'zh': '你好',
                'ja': 'こんにちは',
                'ko': '안녕하세요',
                'ar': 'مرحبا'
            },
            'thank you': {
                'es': 'gracias',
                'fr': 'merci',
                'de': 'danke',
                'it': 'grazie',
                'pt': 'obrigado',
                'ru': 'спасибо',
                'zh': '谢谢',
                'ja': 'ありがとう',
                'ko': '감사합니다',
                'ar': 'شكرا'
            },
            'goodbye': {
                'es': 'adiós',
                'fr': 'au revoir',
                'de': 'auf wiedersehen',
                'it': 'arrivederci',
                'pt': 'adeus',
                'ru': 'до свидания',
                'zh': '再见',
                'ja': 'さようなら',
                'ko': '안녕히 가세요',
                'ar': 'وداعا'
            }
        }
        
        # Load cache
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load translation cache from file"""
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
        """Save translation cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving translation cache: {e}")
    
    def _get_cache_key(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """Generate cache key for translation"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{source_lang}_{target_lang}_{text_hash}"
    
    def _get_cached_translation(self, text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
        """Get translation from cache"""
        cache_key = self._get_cache_key(text, target_lang, source_lang)
        if cache_key in self.cache:
            data = self.cache[cache_key]
            if 'timestamp' in data:
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < self.cache_duration:
                    return data.get('translation')
        return None
    
    def _cache_translation(self, text: str, translation: str, target_lang: str, source_lang: str = 'auto'):
        """Cache translation"""
        cache_key = self._get_cache_key(text, target_lang, source_lang)
        self.cache[cache_key] = {
            'translation': translation,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        # Simple language detection based on character sets
        if re.search(r'[\u4e00-\u9fff]', text):  # Chinese characters
            return 'zh'
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):  # Japanese characters
            return 'ja'
        elif re.search(r'[\uac00-\ud7af]', text):  # Korean characters
            return 'ko'
        elif re.search(r'[\u0600-\u06ff]', text):  # Arabic characters
            return 'ar'
        elif re.search(r'[\u0400-\u04ff]', text):  # Cyrillic characters
            return 'ru'
        else:
            return 'en'  # Default to English
    
    def _get_language_code(self, language: str) -> str:
        """Get language code from language name"""
        language_lower = language.lower()
        return self.languages.get(language_lower, language_lower)
    
    def _get_offline_translation(self, text: str, target_lang: str) -> Optional[str]:
        """Get translation from offline common phrases"""
        text_lower = text.lower().strip()
        target_code = self._get_language_code(target_lang)
        
        if text_lower in self.common_phrases:
            return self.common_phrases[text_lower].get(target_code)
        
        return None
    
    def _translate_with_google(self, text: str, target_lang: str, source_lang: str = 'auto') -> Dict[str, Any]:
        """Translate using Google Translate API"""
        if not self.google_api_key:
            return {'success': False, 'error': 'Google Translate API key not configured'}
        
        try:
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': self.google_api_key,
                'q': text,
                'target': target_lang,
                'source': source_lang,
                'format': 'text'
            }
            
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'translations' in data['data']:
                translation = data['data']['translations'][0]['translatedText']
                detected_lang = data['data']['translations'][0].get('detectedSourceLanguage', source_lang)
                
                return {
                    'success': True,
                    'translation': translation,
                    'detected_language': detected_lang,
                    'source': 'google'
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid response from Google Translate API'
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Google Translate API error: {str(e)}"
            }
    
    def _translate_with_libre(self, text: str, target_lang: str, source_lang: str = 'auto') -> Dict[str, Any]:
        """Translate using LibreTranslate API"""
        try:
            url = "https://libretranslate.de/translate"
            data = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            if self.libre_api_key:
                data['api_key'] = self.libre_api_key
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if 'translatedText' in result:
                return {
                    'success': True,
                    'translation': result['translatedText'],
                    'detected_language': result.get('detectedLanguage', {}).get('confidence', 0),
                    'source': 'libre'
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid response from LibreTranslate API'
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"LibreTranslate API error: {str(e)}"
            }
    
    def _format_translation_response(self, text: str, translation: str, target_lang: str, source_lang: str = 'auto') -> str:
        """Format translation into a readable response"""
        target_name = next((name for name, code in self.languages.items() if code == target_lang), target_lang)
        source_name = next((name for name, code in self.languages.items() if code == source_lang), source_lang)
        
        if source_lang == 'auto':
            return f'"{text}" in {target_name} is: "{translation}"'
        else:
            return f'"{text}" ({source_name}) translated to {target_name}: "{translation}"'
    
    def translate(self, text: str, target_language: str, source_language: str = 'auto') -> Dict[str, Any]:
        """Translate text to target language"""
        if not text.strip():
            return {
                'success': False,
                'error': 'No text provided for translation'
            }
        
        target_lang = self._get_language_code(target_language)
        source_lang = self._get_language_code(source_language) if source_language != 'auto' else 'auto'
        
        # Check cache first
        cached_translation = self._get_cached_translation(text, target_lang, source_lang)
        if cached_translation:
            return {
                'success': True,
                'translation': cached_translation,
                'response': self._format_translation_response(text, cached_translation, target_lang, source_lang),
                'source': 'cache'
            }
        
        # Try offline translation first
        offline_translation = self._get_offline_translation(text, target_lang)
        if offline_translation:
            self._cache_translation(text, offline_translation, target_lang, source_lang)
            return {
                'success': True,
                'translation': offline_translation,
                'response': self._format_translation_response(text, offline_translation, target_lang, source_lang),
                'source': 'offline'
            }
        
        # Try Google Translate API
        if self.google_api_key:
            result = self._translate_with_google(text, target_lang, source_lang)
            if result.get('success'):
                translation = result['translation']
                self._cache_translation(text, translation, target_lang, source_lang)
                return {
                    'success': True,
                    'translation': translation,
                    'response': self._format_translation_response(text, translation, target_lang, source_lang),
                    'detected_language': result.get('detected_language'),
                    'source': 'google'
                }
        
        # Try LibreTranslate API
        result = self._translate_with_libre(text, target_lang, source_lang)
        if result.get('success'):
            translation = result['translation']
            self._cache_translation(text, translation, target_lang, source_lang)
            return {
                'success': True,
                'translation': translation,
                'response': self._format_translation_response(text, translation, target_lang, source_lang),
                'detected_language': result.get('detected_language'),
                'source': 'libre'
            }
        
        return {
            'success': False,
            'error': 'Translation failed. No available translation services.'
        }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages"""
        return {
            'success': True,
            'languages': self.languages,
            'count': len(self.languages)
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of given text"""
        detected = self._detect_language(text)
        language_name = next((name for name, code in self.languages.items() if code == detected), detected)
        
        return {
            'success': True,
            'language_code': detected,
            'language_name': language_name,
            'text': text
        }

def handle_translation_command(text: str) -> Dict[str, Any]:
    """Handle translation-related voice commands"""
    service = TranslationService()
    
    # Extract translation intent from text
    text_lower = text.lower()
    
    # Patterns for translation commands
    patterns = [
        r'translate\s+(.+?)\s+(?:to|in)\s+(\w+)',
        r'what\s+is\s+(.+?)\s+in\s+(\w+)',
        r'how\s+do\s+you\s+say\s+(.+?)\s+in\s+(\w+)',
        r'(.+?)\s+in\s+(\w+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            if len(match.groups()) == 2:
                text_to_translate = match.group(1).strip()
                target_language = match.group(2).strip()
                
                if text_to_translate and target_language:
                    return service.translate(text_to_translate, target_language)
    
    # If no pattern matches, try to extract language and text
    words = text_lower.split()
    if len(words) >= 3:
        # Look for language keywords
        for i, word in enumerate(words):
            if word in service.languages or word in service.languages.values():
                # Try to extract text before or after the language
                if i > 0:
                    text_to_translate = ' '.join(words[:i])
                    target_language = word
                    return service.translate(text_to_translate, target_language)
                elif i < len(words) - 1:
                    text_to_translate = ' '.join(words[i+1:])
                    target_language = word
                    return service.translate(text_to_translate, target_language)
    
    return {
        'success': False,
        'error': 'Please specify what text to translate and to which language. For example: "Translate hello to Spanish"'
    }

# Export feature information
FEATURE_EXPORTS = {
    'handle_translation_command': handle_translation_command,
    'TranslationService': TranslationService,
    'FEATURE_INFO': FEATURE_INFO
} 