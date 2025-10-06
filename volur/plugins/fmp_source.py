"""Financial Modeling Prep data source implementation."""

import os

import requests

from ..caching import cached
from ..config import settings
from .base import Fundamentals, Quote


class FMPSource:
    """Financial Modeling Prep data source implementation."""

    name = "fmp"
    base_url = "https://financialmodelingprep.com/api/v3"

    def __init__(self):
        """Initialize FMP source with API key."""
        self.api_key = settings.fmp_api_key or os.getenv('FMP_API_KEY')
        if not self.api_key:
            raise ValueError("FMP_API_KEY environment variable is required for FMP data source")

    @cached(ttl=3600)  # Cache for 1 hour
    def get_quote(self, ticker: str) -> Quote:
        """Get current quote from Financial Modeling Prep."""
        try:
            url = f"{self.base_url}/quote/{ticker}"
            params = {'apikey': self.api_key}
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if not data:
                return Quote(ticker=ticker.upper(), price=None)

            quote_data = data[0]

            return Quote(
                ticker=ticker.upper(),
                price=quote_data.get('price'),
                currency='USD',  # FMP typically returns USD
                shares_outstanding=quote_data.get('sharesOutstanding')
            )

        except Exception:
            return Quote(ticker=ticker.upper(), price=None)

    @cached(ttl=3600)  # Cache for 1 hour
    def get_fundamentals(self, ticker: str) -> Fundamentals:
        """Get fundamental data from Financial Modeling Prep."""
        try:
            # Get key metrics
            url = f"{self.base_url}/key-metrics/{ticker}"
            params = {'apikey': self.api_key, 'limit': 1}
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            metrics_data = response.json()

            # Get financial ratios
            ratios_url = f"{self.base_url}/ratios/{ticker}"
            ratios_response = requests.get(ratios_url, params=params, timeout=30)
            ratios_data = ratios_response.json() if ratios_response.status_code == 200 else []

            # Get company profile
            profile_url = f"{self.base_url}/profile/{ticker}"
            profile_response = requests.get(profile_url, params={'apikey': self.api_key}, timeout=30)
            profile_data = profile_response.json() if profile_response.status_code == 200 else []

            # Extract data
            metrics = metrics_data[0] if metrics_data else {}
            ratios = ratios_data[0] if ratios_data else {}
            profile = profile_data[0] if profile_data else {}

            return Fundamentals(
                ticker=ticker.upper(),
                trailing_pe=ratios.get('priceEarningsRatio'),
                price_to_book=ratios.get('priceToBookRatio'),
                roe=ratios.get('returnOnEquity'),
                roa=ratios.get('returnOnAssets'),
                debt_to_equity=ratios.get('debtEquityRatio'),
                free_cash_flow=metrics.get('freeCashFlow'),
                revenue=metrics.get('revenue'),
                operating_margin=ratios.get('operatingMargin'),
                sector=profile.get('sector'),
                name=profile.get('companyName')
            )

        except Exception:
            return Fundamentals(
                ticker=ticker.upper(),
                trailing_pe=None,
                price_to_book=None,
                roe=None,
                roa=None,
                debt_to_equity=None,
                free_cash_flow=None
            )


# Register the source (only if API key is available)
try:
    from .base import register_source
    register_source(FMPSource())
except ValueError:
    # FMP source not available without API key
    pass
