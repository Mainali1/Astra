"""
News Feature for Astra Voice Assistant
Provides news aggregation using multiple free APIs with intelligent categorization
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import os
import feedparser
from urllib.parse import urlparse

# Feature information
FEATURE_INFO = {
    'name': 'news',
    'description': 'Get latest news from multiple sources with intelligent categorization',
    'category': 'knowledge',
    'keywords': ['news', 'headlines', 'current events', 'latest', 'breaking', 'top stories'],
    'examples': [
        'What\'s the latest news?',
        'Show me breaking news',
        'News about technology',
        'Top headlines today',
        'Business news',
        'Sports news'
    ],
    'version': '1.0.0',
    'author': 'Astra Team'
}

class NewsService:
    """News service with multiple API integrations and intelligent categorization"""
    
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.cache_file = Path("data/news_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
        
        # News sources and categories
        self.categories = {
            'general': ['general', 'world', 'international'],
            'technology': ['technology', 'tech', 'ai', 'artificial intelligence', 'software'],
            'business': ['business', 'economy', 'finance', 'market', 'stock'],
            'sports': ['sports', 'football', 'basketball', 'tennis', 'olympics'],
            'entertainment': ['entertainment', 'movies', 'music', 'celebrity', 'hollywood'],
            'science': ['science', 'health', 'medical', 'research', 'discovery'],
            'politics': ['politics', 'government', 'election', 'policy'],
            'environment': ['environment', 'climate', 'weather', 'nature']
        }
        
        # RSS feeds for backup
        self.rss_feeds = {
            'general': [
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://rss.cnn.com/rss/edition.rss',
                'https://feeds.reuters.com/Reuters/worldNews'
            ],
            'technology': [
                'https://feeds.feedburner.com/TechCrunch/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index'
            ],
            'business': [
                'https://feeds.reuters.com/reuters/businessNews',
                'https://feeds.bloomberg.com/markets/news.rss',
                'https://www.ft.com/rss/home'
            ]
        }
        
        # Load cache
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load news cache from file"""
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
        """Save news cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving news cache: {e}")
    
    def _get_cached_news(self, category: str) -> Optional[Dict[str, Any]]:
        """Get news from cache"""
        cache_key = f"news_{category.lower()}"
        if cache_key in self.cache:
            data = self.cache[cache_key]
            if 'timestamp' in data:
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < self.cache_duration:
                    return data.get('news')
        return None
    
    def _cache_news(self, category: str, news_data: Dict[str, Any]):
        """Cache news data"""
        cache_key = f"news_{category.lower()}"
        self.cache[cache_key] = {
            'news': news_data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def _categorize_query(self, query: str) -> str:
        """Categorize news query into predefined categories"""
        query_lower = query.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return category
        
        return 'general'
    
    def _get_news_from_api(self, category: str = 'general', query: str = '') -> Dict[str, Any]:
        """Get news from NewsAPI"""
        if not self.news_api_key:
            return self._get_news_from_rss(category)
        
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': self.news_api_key,
                'language': 'en',
                'pageSize': 10
            }
            
            if query:
                params['q'] = query
                url = "https://newsapi.org/v2/everything"
            else:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                return {
                    'success': False,
                    'error': f"API Error: {data.get('message', 'Unknown error')}"
                }
            
            articles = data.get('articles', [])
            formatted_articles = []
            
            for article in articles:
                formatted_articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'image_url': article.get('urlToImage', '')
                })
            
            return {
                'success': True,
                'articles': formatted_articles,
                'total_results': data.get('totalResults', 0),
                'category': category,
                'query': query
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
    
    def _get_news_from_rss(self, category: str = 'general') -> Dict[str, Any]:
        """Get news from RSS feeds as fallback"""
        try:
            feeds = self.rss_feeds.get(category, self.rss_feeds['general'])
            all_articles = []
            
            for feed_url in feeds[:3]:  # Limit to 3 feeds
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:  # Limit to 5 articles per feed
                        article = {
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'url': entry.get('link', ''),
                            'source': feed.feed.get('title', urlparse(feed_url).netloc),
                            'published_at': entry.get('published', ''),
                            'image_url': ''
                        }
                        all_articles.append(article)
                except Exception as e:
                    print(f"Error parsing RSS feed {feed_url}: {e}")
                    continue
            
            # Sort by publication date (newest first)
            all_articles.sort(key=lambda x: x['published_at'], reverse=True)
            
            return {
                'success': True,
                'articles': all_articles[:10],  # Limit to 10 articles
                'total_results': len(all_articles),
                'category': category,
                'source': 'rss'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"RSS parsing error: {str(e)}"
            }
    
    def _format_news_response(self, news_data: Dict[str, Any]) -> str:
        """Format news data into a readable response"""
        if not news_data.get('success'):
            return f"Sorry, I couldn't fetch the news right now. {news_data.get('error', '')}"
        
        articles = news_data.get('articles', [])
        if not articles:
            return "No news articles found for that category."
        
        category = news_data.get('category', 'general').title()
        response = f"Here are the top {len(articles)} {category} news headlines:\n\n"
        
        for i, article in enumerate(articles[:5], 1):  # Limit to 5 in response
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown source')
            response += f"{i}. {title} (via {source})\n"
        
        response += f"\nTotal articles found: {news_data.get('total_results', len(articles))}"
        return response
    
    def get_news(self, query: str = '') -> Dict[str, Any]:
        """Get news based on query or category"""
        # Check cache first
        category = self._categorize_query(query) if query else 'general'
        cached_news = self._get_cached_news(category)
        
        if cached_news:
            return {
                'success': True,
                'data': cached_news,
                'source': 'cache'
            }
        
        # Get fresh news
        news_data = self._get_news_from_api(category, query)
        
        if news_data.get('success'):
            # Cache the result
            self._cache_news(category, news_data)
            
            # Format response
            formatted_response = self._format_news_response(news_data)
            
            return {
                'success': True,
                'data': news_data,
                'response': formatted_response,
                'source': 'api'
            }
        
        return news_data
    
    def get_breaking_news(self) -> Dict[str, Any]:
        """Get breaking news headlines"""
        return self.get_news("breaking news")
    
    def get_category_news(self, category: str) -> Dict[str, Any]:
        """Get news for a specific category"""
        return self.get_news(category)
    
    def search_news(self, query: str) -> Dict[str, Any]:
        """Search for specific news topics"""
        return self.get_news(query)

def handle_news_command(text: str) -> Dict[str, Any]:
    """Handle news-related voice commands"""
    service = NewsService()
    
    # Extract intent from text
    text_lower = text.lower()
    
    if 'breaking' in text_lower or 'latest' in text_lower:
        return service.get_breaking_news()
    elif any(cat in text_lower for cat in ['tech', 'technology', 'ai', 'artificial intelligence']):
        return service.get_category_news('technology')
    elif any(cat in text_lower for cat in ['business', 'economy', 'finance']):
        return service.get_category_news('business')
    elif any(cat in text_lower for cat in ['sports', 'football', 'basketball']):
        return service.get_category_news('sports')
    elif any(cat in text_lower for cat in ['entertainment', 'movies', 'music']):
        return service.get_category_news('entertainment')
    elif any(cat in text_lower for cat in ['science', 'health', 'medical']):
        return service.get_category_news('science')
    elif any(cat in text_lower for cat in ['politics', 'government']):
        return service.get_category_news('politics')
    elif any(cat in text_lower for cat in ['environment', 'climate']):
        return service.get_category_news('environment')
    else:
        # General news request
        return service.get_news()

# Export feature information
FEATURE_EXPORTS = {
    'handle_news_command': handle_news_command,
    'NewsService': NewsService,
    'FEATURE_INFO': FEATURE_INFO
} 