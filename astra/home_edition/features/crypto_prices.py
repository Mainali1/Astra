import requests
from typing import Optional, Dict

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

def get_crypto_price(crypto_id: str, vs_currency: str = 'usd') -> Optional[Dict[str, float]]:
    """
    Gets the price of a cryptocurrency from CoinGecko.

    Args:
        crypto_id: The CoinGecko ID of the cryptocurrency (e.g., 'bitcoin', 'ethereum').
        vs_currency: The currency to get the price in (e.g., 'usd', 'eur').

    Returns:
        A dictionary containing the price, or None if an error occurs.
    """
    try:
        response = requests.get(f"{COINGECKO_API_URL}/simple/price", params={
            'ids': crypto_id,
            'vs_currencies': vs_currency
        })
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data.get(crypto_id)
    except requests.exceptions.RequestException as e:
        # Log the exception here in a real application
        print(f"Error fetching crypto price: {e}")
        return None