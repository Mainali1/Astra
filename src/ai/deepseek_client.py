"""
Astra AI Assistant - DeepSeek AI Client Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import aiohttp
from typing import Optional
from src.config import Config

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Client for interacting with DeepSeek AI through OpenRouter."""

    def __init__(self, config: Config):
        """Initialize the DeepSeek client."""
        self.config = config
        self.api_key = config.DEEPSEEK_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None

        # Personality configuration
        self.system_prompt = """You are Astra, an advanced AI assistant focused on productivity and efficiency.
You are helpful, professional, and direct in your responses.
You prioritize offline-first solutions when available.
You maintain context and remember important details within conversations."""

    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://astra.ai",  # Replace with actual domain
                    "X-Title": "Astra AI Assistant",
                }
            )

    async def get_response(self, user_input: str, conversation_history: Optional[list] = None) -> str:
        """Get a response from DeepSeek AI."""
        try:
            if not self.api_key:
                return "I apologize, but I'm currently operating in offline mode and cannot process complex queries."

            await self._ensure_session()

            # Prepare messages
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user input
            messages.append({"role": "user", "content": user_input})

            # Make API request
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json={"model": "deepseek/deepseek-chat", "messages": messages, "temperature": 0.7, "max_tokens": 1000},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_data = await response.text()
                    logger.error(f"DeepSeek API error: {error_data}")
                    return "I apologize, but I encountered an error processing your request."

        except Exception as e:
            logger.error(f"Error getting DeepSeek response: {str(e)}")
            return "I apologize, but I encountered an error processing your request."

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
