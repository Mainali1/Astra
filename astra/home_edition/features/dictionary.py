import requests
from typing import Optional, List, Dict, Any

DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

def get_word_definition(word: str) -> Optional[List[Dict[str, Any]]]:
    """
    Gets the definition of a word from the Free Dictionary API.

    Args:
        word: The word to get the definition for.

    Returns:
        A list of dictionaries containing word definitions, or None if an error occurs.
    """
    try:
        response = requests.get(f"{DICTIONARY_API_URL}/{word}")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        # Log the exception here in a real application
        print(f"Error fetching word definition: {e}")
        return None