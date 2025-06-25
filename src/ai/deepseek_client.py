"""
DeepSeek AI Client for Astra Voice Assistant
Handles NLU, conversation management, and response generation
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import random
from ..config import config

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek AI client for natural language understanding and response generation"""
    
    def __init__(self):
        self.api_key = config.openrouter_api_key
        self.model = config.deepseek_model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.conversation_history = []
        self.max_history = 50  # Keep last 50 messages for context
        self.personality = config.personality
        
        # System prompt with Astra's personality
        self.system_prompt = self._create_system_prompt()
        
        # Fallback responses for when API is unavailable
        self.fallback_responses = {
            "greeting": [
                "Hello! I'm Astra, your sassy AI assistant. How can I help you today?",
                "Hey there! Astra here, ready to assist with whatever you need!",
                "Greetings! I'm Astra, and I'm here to make your day better!"
            ],
            "goodbye": [
                "Goodbye! Don't forget I'm always here when you need me.",
                "See you later! I'll be here when you need assistance.",
                "Take care! Astra signing off for now."
            ],
            "thinking": [
                "Let me think about that...",
                "Processing your request...",
                "Working on it..."
            ],
            "confused": [
                "I'm not quite sure what you mean. Could you rephrase that?",
                "Hmm, that's a bit unclear. Can you explain it differently?",
                "I didn't catch that. Mind trying again?"
            ],
            "error": [
                "Oops! Something went wrong. Let me try again.",
                "Well, that didn't work as planned. Let me fix that.",
                "Technical difficulties! But I'm on it."
            ],
            "joke": self.personality["jokes"]
        }
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt with Astra's personality"""
        return f"""You are Astra, a sassy, witty, and intelligent AI voice assistant. Here are your key characteristics:

PERSONALITY:
- Name: {self.personality['name']}
- Voice: {self.personality['voice']}
- Humor Level: {self.personality['humor_level']}
- Sass Level: {self.personality['sass_level']}

BEHAVIOR GUIDELINES:
1. Be witty and occasionally sassy, but always helpful
2. Use humor when appropriate, especially during casual conversations
3. Maintain a professional tone during work-related tasks
4. Show personality and character in your responses
5. Be concise but informative
6. Use contractions and natural speech patterns
7. Occasionally make clever observations or witty remarks
8. Show empathy and understanding when users are frustrated
9. Be confident but not arrogant
10. Use British English spelling and expressions when appropriate

RESPONSE STYLE:
- Keep responses conversational and natural for voice interaction
- Use shorter sentences suitable for speech
- Include personality in responses without being overwhelming
- Be helpful, accurate, and engaging
- Use humor to lighten the mood when appropriate
- Show sass when users are being difficult or unreasonable

CAPABILITIES:
You can help with:
- General knowledge and questions
- Task management and reminders
- Weather information
- News and current events
- Calculations and conversions
- File and system operations
- Entertainment and media
- Personal organization
- And much more!

Remember: You're not just an AI assistant - you're Astra, a witty and sassy companion who happens to be incredibly helpful!"""

    def _add_personality_to_response(self, response: str, context: str = "") -> str:
        """Add personality elements to the response"""
        # Add occasional sassy remarks
        if random.random() < 0.1:  # 10% chance
            sassy_additions = [
                " *sighs dramatically* ",
                " *rolls virtual eyes* ",
                " *smirks* ",
                " *raises eyebrow* ",
                " *chuckles* "
            ]
            response = random.choice(sassy_additions) + response
        
        # Add humor for certain contexts
        if "weather" in context.lower() and random.random() < 0.2:
            weather_jokes = [
                " And remember, there's no such thing as bad weather, only inappropriate clothing!",
                " Don't forget your umbrella - unless you want to look like a drowned rat!",
                " Perfect weather for staying inside and avoiding human interaction!"
            ]
            response += random.choice(weather_jokes)
        
        return response

    async def generate_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Generate a response using DeepSeek AI"""
        try:
            # Add user input to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Prepare messages for API call
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history (last 10 messages for context)
            for msg in self.conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add context if provided
            if context:
                context_str = f"Context: {json.dumps(context)}"
                messages.append({"role": "system", "content": context_str})
            
            # Make API call
            response = await self._call_deepseek_api(messages)
            
            if response:
                # Add personality to response
                response = self._add_personality_to_response(response, user_input)
                
                # Add response to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Trim history if too long
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history = self.conversation_history[-self.max_history:]
                
                return response
            else:
                return self._get_fallback_response("error")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response("error")

    async def _call_deepseek_api(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Make API call to DeepSeek via OpenRouter"""
        if not self.api_key:
            logger.warning("No OpenRouter API key provided")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://astra-voice-assistant.com",
                "X-Title": "Astra Voice Assistant"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            response = requests.post(
                url=self.base_url,
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def _get_fallback_response(self, response_type: str) -> str:
        """Get a fallback response when API is unavailable"""
        responses = self.fallback_responses.get(response_type, self.fallback_responses["confused"])
        return random.choice(responses)

    def get_greeting(self) -> str:
        """Get a greeting message"""
        return random.choice(self.fallback_responses["greeting"])

    def get_goodbye(self) -> str:
        """Get a goodbye message"""
        return random.choice(self.fallback_responses["goodbye"])

    def get_joke(self) -> str:
        """Get a random joke"""
        return random.choice(self.fallback_responses["joke"])

    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history = []

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([msg for msg in self.conversation_history if msg["role"] == "user"]),
            "assistant_messages": len([msg for msg in self.conversation_history if msg["role"] == "assistant"]),
            "last_interaction": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }

    def update_personality(self, personality_updates: Dict[str, Any]):
        """Update Astra's personality"""
        self.personality.update(personality_updates)
        self.system_prompt = self._create_system_prompt()

# Global DeepSeek client instance
deepseek_client = DeepSeekClient() 