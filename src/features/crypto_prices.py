import aiohttp
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CryptoPrices:
    """Cryptocurrency price tracking feature using CoinGecko API."""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.supported_coins: Dict[str, Dict] = {}
        self.last_update: Optional[datetime] = None
        self.cache_duration = timedelta(minutes=5)  # Cache prices for 5 minutes
        self.price_cache: Dict[str, Dict] = {}

    async def initialize(self):
        """Initialize by fetching supported cryptocurrencies."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/coins/list") as response:
                    if response.status == 200:
                        coins = await response.json()
                        self.supported_coins = {coin["id"]: coin for coin in coins}
                        logger.info(f"Loaded {len(self.supported_coins)} cryptocurrencies")
                    else:
                        logger.error(f"Failed to fetch cryptocurrencies: {response.status}")
        except Exception as e:
            logger.error(f"Error initializing crypto prices: {e}")

    async def get_price(self, coin_id: str, vs_currency: str = "usd") -> Optional[float]:
        """Get current price of a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin')
            vs_currency: Currency to get price in (default: 'usd')

        Returns:
            Current price or None if request fails
        """
        try:
            # Check cache first
            cache_key = f"{coin_id}_{vs_currency}"
            if cache_key in self.price_cache:
                cached_data = self.price_cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < self.cache_duration:
                    return cached_data["price"]

            # Validate coin ID
            if coin_id not in self.supported_coins:
                logger.error(f"Unsupported coin ID: {coin_id}")
                return None

            # Make API request
            async with aiohttp.ClientSession() as session:
                params = {"ids": coin_id, "vs_currencies": vs_currency}
                async with session.get(f"{self.base_url}/simple/price", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get(coin_id, {}).get(vs_currency)
                        if price is not None:
                            # Update cache
                            self.price_cache[cache_key] = {"price": price, "timestamp": datetime.now()}
                            logger.info(f"Got price for {coin_id}: {price} {vs_currency}")
                            return price
                    logger.error(f"Failed to fetch price: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching crypto price: {e}")
            return None

    async def get_market_data(self, coin_id: str) -> Optional[Dict]:
        """Get detailed market data for a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Dictionary with market data or None if request fails
        """
        try:
            if coin_id not in self.supported_coins:
                logger.error(f"Unsupported coin ID: {coin_id}")
                return None

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/coins/{coin_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = {
                            "current_price": data.get("market_data", {}).get("current_price", {}),
                            "market_cap": data.get("market_data", {}).get("market_cap", {}),
                            "total_volume": data.get("market_data", {}).get("total_volume", {}),
                            "high_24h": data.get("market_data", {}).get("high_24h", {}),
                            "low_24h": data.get("market_data", {}).get("low_24h", {}),
                            "price_change_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                            "last_updated": data.get("market_data", {}).get("last_updated"),
                        }
                        logger.info(f"Got market data for {coin_id}")
                        return market_data
                    logger.error(f"Failed to fetch market data: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None

    async def get_trending_coins(self) -> List[Dict]:
        """Get list of trending cryptocurrencies.

        Returns:
            List of trending coins or empty list if request fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/search/trending") as response:
                    if response.status == 200:
                        data = await response.json()
                        coins = data.get("coins", [])
                        logger.info(f"Got {len(coins)} trending coins")
                        return coins
                    logger.error(f"Failed to fetch trending coins: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return []

    def get_coin_id(self, symbol: str) -> Optional[str]:
        """Get CoinGecko coin ID from symbol.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')

        Returns:
            Coin ID or None if not found
        """
        symbol = symbol.lower()
        for coin_id, coin_data in self.supported_coins.items():
            if coin_data.get("symbol") == symbol:
                return coin_id
        return None

    def is_coin_supported(self, coin_id: str) -> bool:
        """Check if a coin is supported.

        Args:
            coin_id: CoinGecko coin ID to check

        Returns:
            True if coin is supported, False otherwise
        """
        return coin_id in self.supported_coins
