"""
Astra AI Assistant - News Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import aiohttp
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class NewsArticle:
    """Represents a single news article."""

    def __init__(self, title: str, description: str, url: str, source: str, published_at: datetime):
        """Initialize a news article."""
        self.title = title
        self.description = description
        self.url = url
        self.source = source
        self.published_at = published_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NewsArticle":
        """Create article from dictionary."""
        return cls(
            title=data["title"],
            description=data["description"],
            url=data["url"],
            source=data["source"],
            published_at=datetime.fromisoformat(data["published_at"]),
        )


class NewsFeature:
    """News feature for Astra."""

    def __init__(self, config: Config):
        """Initialize the news feature."""
        self.config = config
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, List[NewsArticle]] = {}
        self.cache_time: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=30)

    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers={"X-Api-Key": self.api_key})

    async def _fetch_news(self, query: Optional[str] = None) -> List[NewsArticle]:
        """Fetch news from the API."""
        try:
            if not self.api_key:
                raise ValueError("News API key not configured")

            await self._ensure_session()

            # Check cache
            cache_key = query or "top"
            if (
                cache_key in self.cache
                and cache_key in self.cache_time
                and datetime.now() - self.cache_time[cache_key] < self.cache_duration
            ):
                return self.cache[cache_key]

            # Prepare API endpoint and parameters
            if query:
                endpoint = f"{self.base_url}/everything"
                params = {"q": query, "sortBy": "relevancy"}
            else:
                endpoint = f"{self.base_url}/top-headlines"
                params = {"country": "us"}  # Default to US news

            # Make API request
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = []

                    for article in data.get("articles", []):
                        try:
                            articles.append(
                                NewsArticle(
                                    title=article["title"],
                                    description=article.get("description", ""),
                                    url=article["url"],
                                    source=article["source"]["name"],
                                    published_at=datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00")),
                                )
                            )
                        except Exception as e:
                            logger.warning(f"Error parsing article: {str(e)}")

                    # Update cache
                    self.cache[cache_key] = articles
                    self.cache_time[cache_key] = datetime.now()

                    return articles
                else:
                    error_data = await response.text()
                    logger.error(f"News API error: {error_data}")
                    raise ValueError(f"News API error: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            raise

    def _format_articles(self, articles: List[NewsArticle], limit: int = 5) -> str:
        """Format articles for display."""
        if not articles:
            return "No news articles found."

        response = "Here are the latest news articles:\n\n"
        for i, article in enumerate(articles[:limit], 1):
            response += f"{i}. {article.title}\n"
            if article.description:
                response += f"   {article.description}\n"
            response += f"   Source: {article.source}\n"
            response += f"   Read more: {article.url}\n\n"

        return response

    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle news-related intents."""
        try:
            action = intent.get("action", "")
            params = intent.get("parameters", {})

            if action == "get_news":
                # Get top headlines
                articles = await self._fetch_news()
                return self._format_articles(articles)

            elif action == "get_news_topic":
                # Get news about specific topic
                topic = params.get("topic", "")
                if not topic:
                    return "What topic would you like to read news about?"

                articles = await self._fetch_news(query=topic)
                return self._format_articles(articles)

            else:
                return "I'm not sure what kind of news you're looking for."

        except ValueError as e:
            return f"I couldn't fetch the news: {str(e)}"
        except Exception as e:
            logger.error(f"Error handling news request: {str(e)}")
            return "I'm sorry, but I encountered an error getting the news."

    def is_available(self) -> bool:
        """Check if the feature is available."""
        return bool(self.api_key)

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
