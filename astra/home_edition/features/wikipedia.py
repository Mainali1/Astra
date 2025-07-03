import wikipedia
from typing import Optional, List

def search_wikipedia(query: str, sentences: int = 3) -> Optional[str]:
    """
    Searches Wikipedia for a given query and returns a summary.

    Args:
        query: The query to search for.
        sentences: The number of sentences to include in the summary.

    Returns:
        The summary of the Wikipedia page, or an error message.
    """
    try:
        # Set a user-agent to be a good citizen of the web
        wikipedia.set_user_agent("Astra/1.0 (https://github.com/your-repo/astra)")
        return wikipedia.summary(query, sentences=sentences)
    except wikipedia.exceptions.PageError:
        return f"Error: Could not find a Wikipedia page for '{query}'."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Error: Your query '{query}' is ambiguous. Please be more specific. Options: {e.options[:5]}"
    except Exception as e:
        # Log the exception here in a real application
        return f"An unexpected error occurred while searching Wikipedia: {e}"

def suggest_wikipedia(query: str) -> Optional[List[str]]:
    """
    Suggests Wikipedia articles for a given query.

    Args:
        query: The query to get suggestions for.

    Returns:
        A list of suggested article titles, or None if no suggestions are found.
    """
    try:
        return wikipedia.search(query)
    except Exception as e:
        # Log the exception here in a real application
        return None