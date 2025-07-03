"""
News Feature

News headlines and articles using NewsAPI (free tier: 100 requests/day).
"""

import os
import requests
from typing import Dict, Any, List, Optional
from astra.core.logging import get_logger
from astra.home_edition.drm import verify_feature_access


class NewsFeature:
    """News feature using NewsAPI."""
    
    def __init__(self):
        self.logger = get_logger("astra.home.news")
        
    def _check_feature_access(self) -> bool:
        """Check if user has access to news feature."""
        return verify_feature_access("news")
    
    def get_top_headlines(self, country: str = "us", category: Optional[str] = None) -> Dict[str, Any]:
        """Get top headlines by country and category."""
        if not self._check_feature_access():
            return {"error": "News feature not available"}
        
        try:
            api_key = os.getenv("NEWSAPI_KEY")
            if not api_key:
                return {
                    "error": "NewsAPI key not configured",
                    "setup_required": "Get free API key from https://newsapi.org/",
                    "free_tier": "100 requests/day"
                }
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": api_key,
                "country": country.lower(),
                "pageSize": 20
            }
            
            if category:
                params["category"] = category.lower()
            
            resp = requests.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    articles = []
                    for article in data.get("articles", []):
                        articles.append({
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "url": article.get("url", ""),
                            "image_url": article.get("urlToImage", ""),
                            "published_at": article.get("publishedAt", ""),
                            "source": article.get("source", {}).get("name", ""),
                            "author": article.get("author", "")
                        })
                    
                    return {
                        "country": country,
                        "category": category,
                        "articles": articles,
                        "total_results": data.get("totalResults", 0),
                        "source": "NewsAPI",
                        "free_tier": "100 requests/day"
                    }
                else:
                    return {"error": f"NewsAPI error: {data.get('message', 'Unknown error')}"}
            elif resp.status_code == 401:
                return {"error": "Invalid NewsAPI key - please check your API key"}
            elif resp.status_code == 429:
                return {"error": "NewsAPI rate limit exceeded - free tier allows 100 requests/day"}
            else:
                return {"error": f"News API error: {resp.status_code} - {resp.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "News API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"News API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"News error: {str(e)}"}
    
    def search_news(self, query: str, language: str = "en", sort_by: str = "publishedAt") -> Dict[str, Any]:
        """Search for news articles."""
        if not self._check_feature_access():
            return {"error": "News feature not available"}
        
        try:
            api_key = os.getenv("NEWSAPI_KEY")
            if not api_key:
                return {
                    "error": "NewsAPI key not configured",
                    "setup_required": "Get free API key from https://newsapi.org/",
                    "free_tier": "100 requests/day"
                }
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "apiKey": api_key,
                "q": query,
                "language": language,
                "sortBy": sort_by,
                "pageSize": 20
            }
            
            resp = requests.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    articles = []
                    for article in data.get("articles", []):
                        articles.append({
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "url": article.get("url", ""),
                            "image_url": article.get("urlToImage", ""),
                            "published_at": article.get("publishedAt", ""),
                            "source": article.get("source", {}).get("name", ""),
                            "author": article.get("author", ""),
                            "content": article.get("content", "")
                        })
                    
                    return {
                        "query": query,
                        "language": language,
                        "sort_by": sort_by,
                        "articles": articles,
                        "total_results": data.get("totalResults", 0),
                        "source": "NewsAPI",
                        "free_tier": "100 requests/day"
                    }
                else:
                    return {"error": f"NewsAPI error: {data.get('message', 'Unknown error')}"}
            elif resp.status_code == 401:
                return {"error": "Invalid NewsAPI key - please check your API key"}
            elif resp.status_code == 429:
                return {"error": "NewsAPI rate limit exceeded - free tier allows 100 requests/day"}
            else:
                return {"error": f"News search API error: {resp.status_code} - {resp.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "News search API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"News search API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"News search error: {str(e)}"}
    
    def get_sources(self, category: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        """Get available news sources."""
        if not self._check_feature_access():
            return {"error": "News feature not available"}
        
        try:
            api_key = os.getenv("NEWSAPI_KEY")
            if not api_key:
                return {
                    "error": "NewsAPI key not configured",
                    "setup_required": "Get free API key from https://newsapi.org/",
                    "free_tier": "100 requests/day"
                }
            
            url = "https://newsapi.org/v2/sources"
            params = {
                "apiKey": api_key,
                "language": language
            }
            
            if category:
                params["category"] = category.lower()
            
            resp = requests.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    sources = []
                    for source in data.get("sources", []):
                        sources.append({
                            "id": source.get("id", ""),
                            "name": source.get("name", ""),
                            "description": source.get("description", ""),
                            "url": source.get("url", ""),
                            "category": source.get("category", ""),
                            "language": source.get("language", ""),
                            "country": source.get("country", "")
                        })
                    
                    return {
                        "category": category,
                        "language": language,
                        "sources": sources,
                        "count": len(sources),
                        "source": "NewsAPI",
                        "free_tier": "100 requests/day"
                    }
                else:
                    return {"error": f"NewsAPI error: {data.get('message', 'Unknown error')}"}
            elif resp.status_code == 401:
                return {"error": "Invalid NewsAPI key - please check your API key"}
            elif resp.status_code == 429:
                return {"error": "NewsAPI rate limit exceeded - free tier allows 100 requests/day"}
            else:
                return {"error": f"News sources API error: {resp.status_code} - {resp.text}"}
                
        except requests.exceptions.Timeout:
            return {"error": "News sources API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"News sources API connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"News sources error: {str(e)}"} 