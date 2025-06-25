"""
Astra AI Assistant - Translation Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import aiohttp
from typing import Dict, Any, List, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class TranslationFeature:
    """Translation feature for Astra using LibreTranslate."""
    
    def __init__(self, config: Config):
        """Initialize the translation feature."""
        self.config = config
        self.base_url = "https://libretranslate.com/api"  # Default public instance
        self.session: Optional[aiohttp.ClientSession] = None
        self.supported_languages = {}
        self._initialize_languages()
    
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def _initialize_languages(self):
        """Initialize supported languages."""
        try:
            await self._ensure_session()
            async with self.session.get(f"{self.base_url}/languages") as response:
                if response.status == 200:
                    languages = await response.json()
                    self.supported_languages = {
                        lang['code']: lang['name']
                        for lang in languages
                    }
                    logger.info(f"Loaded {len(self.supported_languages)} supported languages")
        except Exception as e:
            logger.error(f"Error initializing languages: {str(e)}")
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate text between languages."""
        try:
            await self._ensure_session()
            
            # Validate languages
            if source_lang not in self.supported_languages:
                raise ValueError(f"Source language '{source_lang}' not supported")
            if target_lang not in self.supported_languages:
                raise ValueError(f"Target language '{target_lang}' not supported")
            
            # Make translation request
            async with self.session.post(
                f"{self.base_url}/translate",
                json={
                    "q": text,
                    "source": source_lang,
                    "target": target_lang
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('translatedText')
                else:
                    error_data = await response.text()
                    logger.error(f"Translation API error: {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return None
    
    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code."""
        return self.supported_languages.get(lang_code, lang_code)
    
    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle translation-related intents."""
        try:
            action = intent.get('action', '')
            params = intent.get('parameters', {})
            
            if action == 'translate':
                # Translate text
                text = params.get('text', '')
                source_lang = params.get('source_lang', 'auto')
                target_lang = params.get('target_lang', '')
                
                if not text:
                    return "What text would you like me to translate?"
                if not target_lang:
                    return "Which language should I translate to?"
                
                translated = await self.translate(text, source_lang, target_lang)
                if translated:
                    source_name = self.get_language_name(source_lang)
                    target_name = self.get_language_name(target_lang)
                    return f"Translation from {source_name} to {target_name}:\n{translated}"
                return "I'm sorry, but I couldn't translate that text."
                
            elif action == 'list_languages':
                # List supported languages
                response = "Supported languages:\n"
                for code, name in sorted(self.supported_languages.items()):
                    response += f"- {name} ({code})\n"
                return response
            
            else:
                return "I'm not sure what you want me to translate."
            
        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Error handling translation request: {str(e)}")
            return "I'm sorry, but I encountered an error with the translation."
    
    def is_available(self) -> bool:
        """Check if the feature is available."""
        return bool(self.supported_languages)
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None 