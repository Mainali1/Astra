"""
Astra AI Assistant - Wikipedia Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import aiohttp
from typing import Dict, Any, List, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class WikipediaFeature:
    """Wikipedia feature for Astra."""

    def __init__(self, config: Config):
        """Initialize the Wikipedia feature."""
        self.config = config
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Dict[str, Any]] = {}

    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Search Wikipedia articles."""
        try:
            await self._ensure_session()

            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "srprop": "snippet",
            }

            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("query", {}).get("search", [])
                return []

        except Exception as e:
            logger.error(f"Error searching Wikipedia: {str(e)}")
            return []

    async def get_article(self, title: str) -> Optional[Dict[str, Any]]:
        """Get Wikipedia article content."""
        try:
            # Check cache first
            if title in self.cache:
                return self.cache[title]

            await self._ensure_session()

            params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts|info",
                "exintro": True,
                "explaintext": True,
                "inprop": "url",
            }

            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get("query", {}).get("pages", {})
                    if pages:
                        # Get the first (and only) page
                        page = next(iter(pages.values()))
                        if "missing" not in page:
                            # Cache the result
                            self.cache[title] = page
                            return page
                return None

        except Exception as e:
            logger.error(f"Error getting Wikipedia article: {str(e)}")
            return None

    def _format_search_results(self, results: List[Dict[str, str]]) -> str:
        """Format search results for display."""
        if not results:
            return "No Wikipedia articles found."

        response = "Here are the most relevant Wikipedia articles:\n\n"
        for i, result in enumerate(results, 1):
            title = result["title"]
            snippet = result.get("snippet", "").replace('<span class="searchmatch">', "").replace("</span>", "")
            response += f"{i}. {title}\n   {snippet}\n\n"
        return response

    def _format_article(self, article: Dict[str, Any]) -> str:
        """Format article for display."""
        title = article.get("title", "Unknown")
        extract = article.get("extract", "No content available.")
        url = article.get("fullurl", "")

        response = f"Wikipedia article: {title}\n\n"
        response += extract[:1000] + "...\n\n" if len(extract) > 1000 else extract + "\n\n"
        if url:
            response += f"Read more: {url}"
        return response

    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle Wikipedia-related intents."""
        try:
            action = intent.get("action", "")
            params = intent.get("parameters", {})

            if action == "search_wikipedia":
                # Search for articles
                query = params.get("query", "")
                if not query:
                    return "What would you like to search for on Wikipedia?"

                results = await self.search(query)
                return self._format_search_results(results)

            elif action == "get_article":
                # Get specific article
                title = params.get("title", "")
                if not title:
                    return "Which Wikipedia article would you like to read?"

                article = await self.get_article(title)
                if article:
                    return self._format_article(article)
                return f"I couldn't find a Wikipedia article about '{title}'."

            else:
                return "I'm not sure what you want to look up on Wikipedia."

        except Exception as e:
            logger.error(f"Error handling Wikipedia request: {str(e)}")
            return "I'm sorry, but I encountered an error with the Wikipedia lookup."

    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Wikipedia API is always available

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
