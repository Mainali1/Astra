import requests
from typing import Optional, List, Dict, Any

from astra.core.config import settings

CONTEXTUALWEB_SEARCH_API_URL = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/WebSearchAPI"

def web_search(query: str, page_number: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
    """
    Performs a web search using the ContextualWeb Search API.

    Args:
        query: The search query.
        page_number: The page number of results to retrieve.
        page_size: The number of results per page.

    Returns:
        A dictionary containing search results, or None if an error occurs.
    """
    api_key = settings.contextualweb_api_key # Assuming contextualweb_api_key is used for ContextualWeb Search
    if not api_key:
        return {"error": "ContextualWeb Search API key is not configured. Please set CONTEXTUALWEB_API_KEY in your .env file."}

    headers = {
        "x-rapidapi-host": "contextualwebsearch-websearch-v1.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }

    params = {
        "q": query,
        "pageNumber": page_number,
        "pageSize": page_size,
        "autoCorrect": True, # Auto-correct typos
        "safeSearch": True   # Enable safe search
    }

    try:
        response = requests.get(CONTEXTUALWEB_SEARCH_API_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        # Log the exception here in a real application
        print(f"Error during web search: {e}")
        return {"error": f"Failed to perform web search: {e}"}