import aiohttp
from typing import List, Dict, Optional
import logging
from urllib.parse import quote_plus
import json

logger = logging.getLogger(__name__)

class WebSearch:
    """Web search feature using DuckDuckGo API."""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com"
        self.user_agent = "Astra/1.0"
        
    async def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search the web using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            List of search results, each containing title, link, and snippet
        """
        try:
            # URL encode the query
            encoded_query = quote_plus(query)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": self.user_agent}
                params = {
                    "q": encoded_query,
                    "format": "json",
                    "no_html": 1,
                    "no_redirect": 1
                }
                async with session.get(self.base_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        # Process instant answer if available
                        if data.get("AbstractText"):
                            results.append({
                                "title": data.get("Heading", "Instant Answer"),
                                "link": data.get("AbstractURL", ""),
                                "snippet": data.get("AbstractText", ""),
                                "source": "instant_answer"
                            })
                            
                        # Process related topics
                        for topic in data.get("RelatedTopics", [])[:max_results]:
                            if "Text" in topic and "FirstURL" in topic:
                                results.append({
                                    "title": topic.get("Text", "").split(" - ")[0],
                                    "link": topic.get("FirstURL", ""),
                                    "snippet": topic.get("Text", ""),
                                    "source": "related_topic"
                                })
                                
                        logger.info(f"Found {len(results)} results for query: {query}")
                        return results[:max_results]
                    else:
                        logger.error(f"Search request failed: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return []
            
    async def get_instant_answer(self, query: str) -> Optional[Dict]:
        """Get instant answer for a query.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary with instant answer data or None if not available
        """
        try:
            encoded_query = quote_plus(query)
            
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": self.user_agent}
                params = {
                    "q": encoded_query,
                    "format": "json",
                    "no_html": 1,
                    "no_redirect": 1,
                    "skip_disambig": 1
                }
                async with session.get(self.base_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if we have an instant answer
                        if data.get("AbstractText"):
                            answer = {
                                "heading": data.get("Heading", ""),
                                "text": data.get("AbstractText", ""),
                                "source": data.get("AbstractSource", ""),
                                "url": data.get("AbstractURL", ""),
                                "image": data.get("Image", "")
                            }
                            logger.info(f"Found instant answer for query: {query}")
                            return answer
                        else:
                            logger.info(f"No instant answer found for query: {query}")
                            return None
                    else:
                        logger.error(f"Instant answer request failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting instant answer: {e}")
            return None
            
    async def get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions for a query.
        
        Args:
            query: Partial search query
            
        Returns:
            List of search suggestions
        """
        try:
            encoded_query = quote_plus(query)
            
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": self.user_agent}
                params = {
                    "q": encoded_query,
                    "format": "json",
                    "no_html": 1,
                    "no_redirect": 1
                }
                async with session.get(f"{self.base_url}/ac/", params=params, headers=headers) as response:
                    if response.status == 200:
                        suggestions = await response.json()
                        results = [s.get("phrase") for s in suggestions if s.get("phrase")]
                        logger.info(f"Found {len(results)} suggestions for query: {query}")
                        return results
                    else:
                        logger.error(f"Suggestions request failed: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return [] 