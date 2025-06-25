"""
Enhanced Voice Assistant Core for Astra
Integrates with feature manager and provides personality-driven responses
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import json
from pathlib import Path

from ..config import config
from ..ai.deepseek_client import deepseek_client, DeepSeekClient
from ..speech.speech_recognition import speech_recognizer
from ..speech.text_to_speech import tts
from .feature_manager import get_feature_manager, FeatureManager
from .intent_recognizer import IntentRecognizer

logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Enhanced voice assistant with personality and feature integration"""
    
    def __init__(self):
        self.config = config
        self.is_running = False
        self.is_listening = False
        self.is_processing = False
        
        # Core components
        self.feature_manager = get_feature_manager()
        self.intent_recognizer = IntentRecognizer()
        self.deepseek_client = DeepSeekClient()
        
        # Personality traits
        self.personality = {
            'name': 'Astra',
            'tone': 'sassy',
            'humor_level': 'high',
            'professional_mode': False,
            'response_templates': {
                'greeting': [
                    "Hey there! What can I help you with today?",
                    "Well, well, well... look who decided to show up! What do you need?",
                    "Hello! Ready to make some magic happen?",
                    "Oh, you're back! I was starting to think you'd forgotten about me."
                ],
                'farewell': [
                    "See you later! Don't do anything I wouldn't do... which is basically nothing.",
                    "Bye! Try not to break anything while I'm gone.",
                    "Until next time! I'll be here, probably judging your life choices.",
                    "Take care! And remember, I'm always watching... just kidding. Maybe."
                ],
                'confusion': [
                    "I'm not sure I understood that. Could you try again, or maybe use smaller words?",
                    "Hmm, that went right over my head. Mind rephrasing that?",
                    "I think my circuits got confused. What exactly are you trying to say?",
                    "That's... not a thing I can do. Yet. Want to try something else?"
                ],
                'success': [
                    "There you go! Easy peasy.",
                    "Done and done! I'm basically a genius.",
                    "Mission accomplished! You're welcome.",
                    "Boom! Nailed it. What else you got?"
                ],
                'error': [
                    "Oops! Something went wrong. My bad, not yours.",
                    "Well, that didn't work. Let's pretend that never happened.",
                    "Error 404: Success not found. Want to try again?",
                    "I failed spectacularly. But hey, at least I tried!"
                ]
            }
        }
        
        # State management
        self.conversation_context = {}
        self.user_preferences = {}
        self.session_data = {
            "start_time": None,
            "interactions": 0,
            "features_used": set(),
            "last_interaction": None
        }
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_speech_recognized = None
        self.on_response_generated = None
        self.on_error = None
        self.on_status_changed = None
        
        # Conversation memory
        self.conversation_history = []
        self.max_history = 50
        
        # Initialize components
        self._setup_speech_callbacks()
        self._load_user_preferences()
        self._load_conversation_history()
    
    def _setup_speech_callbacks(self):
        """Setup speech recognition callbacks"""
        speech_recognizer.on_wake_word_detected = self._handle_wake_word
        speech_recognizer.on_speech_ended = self._handle_speech_recognized
        speech_recognizer.on_error = self._handle_speech_error
        
        tts.on_speech_started = self._handle_speech_started
        tts.on_speech_ended = self._handle_speech_ended
        tts.on_error = self._handle_tts_error
    
    def start(self):
        """Start the voice assistant"""
        if self.is_running:
            logger.warning("Voice assistant is already running")
            return
        
        try:
            logger.info("Starting Astra Voice Assistant...")
            
            # Initialize session
            self.session_data["start_time"] = datetime.now()
            self.session_data["interactions"] = 0
            self.session_data["features_used"].clear()
            
            # Start speech recognition
            speech_recognizer.start_listening()
            
            # Play greeting
            greeting = deepseek_client.get_greeting()
            tts.speak(greeting)
            
            self.is_running = True
            self.is_listening = True
            
            logger.info("Astra Voice Assistant started successfully")
            
            if self.on_status_changed:
                self.on_status_changed("started")
            
        except Exception as e:
            logger.error(f"Failed to start voice assistant: {e}")
            if self.on_error:
                self.on_error(str(e))
    
    def stop(self):
        """Stop the voice assistant"""
        if not self.is_running:
            return
        
        try:
            logger.info("Stopping Astra Voice Assistant...")
            
            # Stop speech recognition
            speech_recognizer.stop_listening()
            
            # Play goodbye message
            goodbye = deepseek_client.get_goodbye()
            tts.speak_immediate(goodbye)
            
            # Save session data
            self._save_session_data()
            
            self.is_running = False
            self.is_listening = False
            
            logger.info("Astra Voice Assistant stopped")
            
            if self.on_status_changed:
                self.on_status_changed("stopped")
            
        except Exception as e:
            logger.error(f"Error stopping voice assistant: {e}")
    
    def _handle_wake_word(self, text: str):
        """Handle wake word detection"""
        logger.info(f"Wake word detected: {text}")
        
        if self.on_wake_word_detected:
            self.on_wake_word_detected(text)
        
        # Play acknowledgment sound or message
        tts.speak("Yes?")
        
        # Start listening for command
        self.is_listening = True
    
    def _handle_speech_recognized(self, text: str, confidence: float):
        """Handle recognized speech"""
        if not self.is_listening or self.is_processing:
            return
        
        logger.info(f"Speech recognized: '{text}' (confidence: {confidence:.2f})")
        
        if self.on_speech_recognized:
            self.on_speech_recognized(text, confidence)
        
        # Process the command
        asyncio.create_task(self._process_command(text, confidence))
    
    def _handle_speech_error(self, error: str):
        """Handle speech recognition error"""
        logger.error(f"Speech recognition error: {error}")
        if self.on_error:
            self.on_error(error)
    
    def _handle_speech_started(self, text: str):
        """Handle TTS speech started"""
        logger.debug(f"Started speaking: '{text[:50]}...'")
    
    def _handle_speech_ended(self, text: str):
        """Handle TTS speech ended"""
        logger.debug(f"Finished speaking: '{text[:50]}...'")
        self.is_listening = True  # Resume listening
    
    def _handle_tts_error(self, error: str):
        """Handle TTS error"""
        logger.error(f"TTS error: {error}")
        if self.on_error:
            self.on_error(error)
    
    async def _process_command(self, text: str, confidence: float):
        """Process user command"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.is_listening = False
        
        try:
            # Update session data
            self.session_data["interactions"] += 1
            self.session_data["last_interaction"] = datetime.now()
            
            # Recognize intent
            intent = self.intent_recognizer.recognize_intent(text)
            logger.info(f"Intent recognized: {intent}")
            
            # Check if it's a feature command
            if intent['type'] == 'feature':
                response = await self._handle_feature_command(text, intent)
            elif intent['type'] == 'conversation':
                response = await self._handle_conversation(text, intent)
            elif intent['type'] == 'system':
                response = await self._handle_system_command(text, intent)
            else:
                # Use DeepSeek for general conversation
                response = await self._handle_general_conversation(text)
            
            # Speak response
            if response:
                tts.speak(response)
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            error_response = "Sorry, I encountered an error processing your request."
            tts.speak(error_response)
            
            if self.on_error:
                self.on_error(str(e))
        
        finally:
            self.is_processing = False
    
    async def _handle_feature_command(self, user_input: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle feature-specific commands"""
        feature_name = intent.get('feature')
        
        if not feature_name:
            response = self._get_personality_response('confusion')
            self._add_to_history(user_input, response, False)
            return {
                'success': False,
                'response': response,
                'type': 'confusion'
            }
        
        # Check if feature is enabled
        if not self.feature_manager.is_feature_enabled(feature_name):
            response = f"Sorry, the {feature_name} feature is currently disabled. You can enable it in the features settings."
            self._add_to_history(user_input, response, False)
            return {
                'success': False,
                'response': response,
                'type': 'feature_disabled'
            }
        
        # Get feature handler
        handler = self.feature_manager.get_feature(feature_name)
        if not handler:
            response = f"Sorry, I couldn't find the {feature_name} feature handler."
            self._add_to_history(user_input, response, False)
            return {
                'success': False,
                'response': response,
                'type': 'feature_not_found'
            }
        
        try:
            # Execute feature
            result = handler(user_input)
            
            if result.get('success', False):
                response = result.get('response', 'Feature executed successfully.')
                response = self._inject_personality(response, 'success')
            else:
                response = result.get('error', 'Feature execution failed.')
                response = self._inject_personality(response, 'error')
            
            self._add_to_history(user_input, response, result.get('success', False))
            
            return {
                'success': result.get('success', False),
                'response': response,
                'data': result.get('data'),
                'type': 'feature',
                'feature': feature_name
            }
            
        except Exception as e:
            response = f"Error executing {feature_name} feature: {str(e)}"
            response = self._inject_personality(response, 'error')
            self._add_to_history(user_input, response, False)
            return {
                'success': False,
                'response': response,
                'type': 'feature_error'
            }
    
    async def _handle_conversation(self, user_input: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general conversation"""
        # Use DeepSeek for conversation
        try:
            # Add personality context to the prompt
            personality_context = f"You are Astra, a sassy and witty AI assistant. Respond with humor and personality, but stay helpful. Previous conversation: {self._get_recent_context()}"
            
            response = await self.deepseek_client.chat(
                user_input, 
                system_prompt=personality_context
            )
            
            response = self._inject_personality(response)
            self._add_to_history(user_input, response, True)
            
            return {
                'success': True,
                'response': response,
                'type': 'conversation'
            }
            
        except Exception as e:
            response = f"Sorry, I'm having trouble with our conversation right now: {str(e)}"
            self._add_to_history(user_input, response, False)
            return {
                'success': False,
                'response': response,
                'type': 'conversation_error'
            }
    
    async def _handle_system_command(self, user_input: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system-level commands"""
        command = intent.get('command', '').lower()
        
        if command in ['hello', 'hi', 'hey']:
            response = self._get_personality_response('greeting')
        elif command in ['bye', 'goodbye', 'exit']:
            response = self._get_personality_response('farewell')
        elif command in ['help', 'features']:
            response = self._get_help_response()
        elif command in ['status', 'health']:
            response = self._get_status_response()
        else:
            response = self._get_personality_response('confusion')
        
        self._add_to_history(user_input, response, True)
        return {
            'success': True,
            'response': response,
            'type': 'system'
        }
    
    async def _handle_general_conversation(self, text: str) -> str:
        """Handle general conversation using DeepSeek"""
        try:
            # Prepare context
            context = {
                "session_data": self.session_data,
                "user_preferences": self.user_preferences,
                "available_features": list(self.feature_manager.get_available_features()),
                "conversation_context": self.conversation_context
            }
            
            # Generate response using DeepSeek
            response = await deepseek_client.generate_response(text, context)
            
            # Update conversation context
            self.conversation_context["last_query"] = text
            self.conversation_context["last_response"] = response
            self.conversation_context["timestamp"] = datetime.now().isoformat()
            
            return response
            
        except Exception as e:
            logger.error(f"Error in general conversation: {e}")
            return "Sorry, I'm having trouble understanding right now."
    
    def process_text_command(self, text: str) -> str:
        """Process text command (for non-voice input)"""
        try:
            # Create a simple event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Process command
            return loop.run_until_complete(self._process_command(text, 1.0))
            
        except Exception as e:
            logger.error(f"Error processing text command: {e}")
            return "Error processing command"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "is_running": self.is_running,
            "is_listening": self.is_listening,
            "is_processing": self.is_processing,
            "session_data": self.session_data,
            "speech_status": speech_recognizer.is_listening,
            "tts_status": tts.is_speaking,
            "available_features": list(self.feature_manager.get_available_features()),
            "enabled_features": list(self.feature_manager.get_enabled_features())
        }
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences"""
        self.user_preferences.update(preferences)
        self._save_user_preferences()
        logger.info("User preferences updated")
    
    def _load_user_preferences(self):
        """Load user preferences from file"""
        try:
            prefs_file = self.config.data_dir / "user_preferences.json"
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    self.user_preferences = json.load(f)
                logger.info("User preferences loaded")
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            self.user_preferences = {}
    
    def _save_user_preferences(self):
        """Save user preferences to file"""
        try:
            prefs_file = self.config.data_dir / "user_preferences.json"
            with open(prefs_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            logger.info("User preferences saved")
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
    
    def _save_session_data(self):
        """Save session data"""
        try:
            session_file = self.config.data_dir / "session_data.json"
            session_data = {
                "session": self.session_data,
                "conversation_summary": deepseek_client.get_conversation_summary(),
                "timestamp": datetime.now().isoformat()
            }
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            logger.info("Session data saved")
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.stop()
            
            # Cleanup components
            speech_recognizer.cleanup()
            tts.cleanup()
            
            logger.info("Voice assistant cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _load_conversation_history(self):
        """Load conversation history from file"""
        history_file = Path("data/conversation_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.conversation_history = []
    
    def _save_conversation_history(self):
        """Save conversation history to file"""
        history_file = Path("data/conversation_history.json")
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving conversation history: {e}")
    
    def _add_to_history(self, user_input: str, response: str, success: bool = True):
        """Add interaction to conversation history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': response,
            'success': success
        }
        
        self.conversation_history.append(entry)
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        self._save_conversation_history()
    
    def _get_personality_response(self, response_type: str) -> str:
        """Get a personality-driven response"""
        import random
        
        templates = self.personality['response_templates'].get(response_type, [])
        if templates:
            return random.choice(templates)
        return "I'm not sure how to respond to that."
    
    def _inject_personality(self, response: str, context: str = None) -> str:
        """Inject personality into response based on context"""
        if not self.personality['professional_mode']:
            # Add sassy comments for certain contexts
            if 'error' in response.lower() or 'sorry' in response.lower():
                response += f" {self._get_personality_response('error')}"
            elif 'success' in response.lower() or 'done' in response.lower():
                response += f" {self._get_personality_response('success')}"
        
        return response
    
    def _get_recent_context(self) -> str:
        """Get recent conversation context"""
        recent = self.conversation_history[-5:] if self.conversation_history else []
        context = []
        for entry in recent:
            context.append(f"User: {entry['user_input']}")
            context.append(f"Astra: {entry['assistant_response']}")
        return " | ".join(context)
    
    def _get_help_response(self) -> str:
        """Get help response with available features"""
        enabled_features = self.feature_manager.get_enabled_features()
        
        if enabled_features:
            feature_list = ", ".join(enabled_features)
            response = f"I can help you with: {feature_list}. You can also just chat with me about anything!"
        else:
            response = "I'm here to chat! Try asking me about the weather, time, or just have a conversation."
        
        return self._inject_personality(response)
    
    def _get_status_response(self) -> str:
        """Get system status response"""
        stats = self.feature_manager.get_feature_statistics()
        
        response = f"I'm running smoothly! I have {stats['enabled_features']} features enabled out of {stats['total_features']} total features."
        
        return self._inject_personality(response)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self._save_conversation_history()
    
    def set_personality_mode(self, professional: bool = False):
        """Set personality mode (professional or casual)"""
        self.personality['professional_mode'] = professional
    
    def get_feature_suggestions(self, user_input: str) -> List[str]:
        """Get feature suggestions based on user input"""
        return self.feature_manager.get_feature_suggestions(user_input)

# Global voice assistant instance
voice_assistant = VoiceAssistant() 