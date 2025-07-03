import requests
from typing import Optional, Dict, Any

EXCHANGERATE_API_URL = "https://api.exchangerate.host/latest"

def convert_currency(amount: float, from_currency: str, to_currency: str) -> Optional[Dict[str, Any]]:
    """
    Converts an amount from one currency to another using ExchangeRate.host.

    Args:
        amount: The amount to convert.
        from_currency: The currency to convert from (e.g., 'USD', 'EUR').
        to_currency: The currency to convert to (e.g., 'GBP', 'JPY').

    Returns:
        A dictionary containing the conversion result, or None if an error occurs.
    """
    try:
        response = requests.get(EXCHANGERATE_API_URL, params={
            'base': from_currency.upper(),
            'symbols': to_currency.upper()
        })
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        if data.get("success"):
            rate = data["rates"][to_currency.upper()]
            converted_amount = amount * rate
            return {
                "amount": amount,
                "from_currency": from_currency.upper(),
                "to_currency": to_currency.upper(),
                "rate": rate,
                "converted_amount": converted_amount,
                "date": data["date"]
            }
        else:
            return {"error": data.get("error", {}).get("info", "Unknown error from API.")}

    except requests.exceptions.RequestException as e:
        # Log the exception here in a real application
        print(f"Error during currency conversion: {e}")
        return {"error": f"Failed to retrieve exchange rates: {e}"}