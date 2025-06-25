import aiohttp
import asyncio
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """Currency converter feature using exchangerate.host API."""
    
    def __init__(self):
        self.base_url = "https://api.exchangerate.host"
        self.supported_currencies: Dict[str, str] = {}
        self.last_update: Optional[Dict] = None
    
    async def initialize(self):
        """Initialize the currency converter by fetching supported currencies."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/symbols") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.supported_currencies = data.get("symbols", {})
                        logger.info(f"Loaded {len(self.supported_currencies)} currencies")
                    else:
                        logger.error(f"Failed to fetch currencies: {response.status}")
        except Exception as e:
            logger.error(f"Error initializing currency converter: {e}")
            
    async def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert an amount from one currency to another.
        
        Args:
            amount: The amount to convert
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')
            
        Returns:
            Converted amount or None if conversion fails
        """
        try:
            # Normalize currency codes
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # Validate currencies
            if from_currency not in self.supported_currencies:
                logger.error(f"Unsupported source currency: {from_currency}")
                return None
            if to_currency not in self.supported_currencies:
                logger.error(f"Unsupported target currency: {to_currency}")
                return None
                
            # Make API request
            async with aiohttp.ClientSession() as session:
                params = {
                    "from": from_currency,
                    "to": to_currency,
                    "amount": amount
                }
                async with session.get(f"{self.base_url}/convert", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result")
                        if result is not None:
                            logger.info(f"Converted {amount} {from_currency} to {result} {to_currency}")
                            return result
                    logger.error(f"Conversion failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error during currency conversion: {e}")
            return None
            
    async def get_latest_rates(self, base_currency: str = "USD") -> Optional[Dict[str, float]]:
        """Get latest exchange rates for a base currency.
        
        Args:
            base_currency: Base currency code (default: 'USD')
            
        Returns:
            Dictionary of currency rates or None if request fails
        """
        try:
            base_currency = base_currency.upper()
            if base_currency not in self.supported_currencies:
                logger.error(f"Unsupported base currency: {base_currency}")
                return None
                
            async with aiohttp.ClientSession() as session:
                params = {"base": base_currency}
                async with session.get(f"{self.base_url}/latest", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        rates = data.get("rates")
                        if rates:
                            self.last_update = data
                            logger.info(f"Updated rates for {base_currency}")
                            return rates
                    logger.error(f"Failed to fetch rates: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching latest rates: {e}")
            return None
            
    def get_currency_name(self, currency_code: str) -> Optional[str]:
        """Get the full name of a currency from its code.
        
        Args:
            currency_code: Currency code (e.g., 'USD')
            
        Returns:
            Currency name or None if not found
        """
        currency_code = currency_code.upper()
        currency_info = self.supported_currencies.get(currency_code)
        if isinstance(currency_info, dict):
            return currency_info.get("description")
        return None

    def is_currency_supported(self, currency_code: str) -> bool:
        """Check if a currency is supported.
        
        Args:
            currency_code: Currency code to check
            
        Returns:
            True if currency is supported, False otherwise
        """
        return currency_code.upper() in self.supported_currencies 