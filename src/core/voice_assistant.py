"""
Astra AI Assistant - Core Voice Assistant Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from src.config import Config
from src.core.feature_manager import FeatureManager
from src.core.intent_recognizer import IntentRecognizer
from src.speech.speech_recognition import SpeechRecognizer
from src.speech.text_to_speech import TextToSpeech
from src.ai.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Core voice assistant class managing all interactions."""

    def __init__(self, config: Config):
        """Initialize the voice assistant with configuration."""
        self.config = config
        self.feature_manager = FeatureManager(config)
        self.intent_recognizer = IntentRecognizer()
        self.speech_recognizer = SpeechRecognizer(config)
        self.text_to_speech = TextToSpeech(config)
        self.ai_client = DeepSeekClient(config)

        # State management
        self._listening = False
        self._current_conversation: Dict[str, Any] = {}

    async def start_listening(self):
        """Start listening for voice input."""
        if self._listening:
            return

        self._listening = True
        logger.info("Started listening for voice input")

        try:
            while self._listening:
                # Process audio input
                audio_input = await self.speech_recognizer.listen()
                if audio_input:
                    await self.process_input(audio_input)
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in listening loop: {str(e)}", exc_info=True)
            self._listening = False

    async def stop_listening(self):
        """Stop listening for voice input."""
        self._listening = False
        logger.info("Stopped listening for voice input")

    async def process_input(self, input_text: str) -> Optional[str]:
        """Process text input and return response."""
        try:
            # Recognize intent
            intent = await self.intent_recognizer.recognize(input_text)

            if not intent:
                # No specific intent found, use AI fallback
                response = await self.ai_client.get_response(input_text)
            else:
                # Handle intent with appropriate feature
                feature = self.feature_manager.get_feature(intent["feature"])
                if feature:
                    response = await feature.handle(intent)
                else:
                    response = "I'm sorry, that feature is not available."

            # Convert response to speech if needed
            if response:
                await self.text_to_speech.speak(response)

            return response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}", exc_info=True)
            return "I'm sorry, I encountered an error processing your request."

    async def cleanup(self):
        """Clean up resources."""
        await self.stop_listening()
        await self.speech_recognizer.cleanup()
        await self.text_to_speech.cleanup()
        await self.ai_client.cleanup()
