"""SEC data source implementation (skeleton with TODOs)."""

from typing import Any, Dict, Optional

import requests

from ..caching import cached
from ..config import settings
from .base import Fundamentals, Quote


class SECSource:
    """SEC EDGAR data source implementation."""

    name = "sec"
    base_url = "https://data.sec.gov/api/xbrl/companyfacts"

    def __init__(self):
        """Initialize SEC source with proper headers."""
        self.headers = {
            'User-Agent': settings.sec_user_agent,
            'Accept': 'application/json'
        }

    @cached(ttl=86400)  # Cache for 24 hours
    def get_quote(self, ticker: str) -> Quote:
        """Get current quote from SEC (placeholder - SEC doesn't provide real-time quotes)."""
        # TODO: SEC doesn't provide real-time quotes
        # This would need to be combined with another source for current prices
        return Quote(ticker=ticker.upper(), price=None)

    @cached(ttl=86400)  # Cache for 24 hours
    def get_fundamentals(self, ticker: str) -> Fundamentals:
        """Get fundamental data from SEC EDGAR."""
        try:
            # Convert ticker to CIK (Central Index Key)
            cik = self._get_cik_from_ticker(ticker)
            if not cik:
                return self._empty_fundamentals(ticker)

            # Fetch company facts
            url = f"{self.base_url}/CIK{cik.zfill(10)}.json"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            facts = data.get('facts', {})

            # Extract relevant metrics
            us_gaap = facts.get('us-gaap', {})
            dei = facts.get('dei', {})

            # Get latest values for key metrics
            trailing_pe = self._get_latest_value(us_gaap.get('EarningsPerShareBasic', {}))
            price_to_book = self._get_latest_value(us_gaap.get('BookValuePerShare', {}))
            roe = self._get_latest_value(us_gaap.get('ReturnOnEquity', {}))
            roa = self._get_latest_value(us_gaap.get('ReturnOnAssets', {}))
            debt_to_equity = self._get_latest_value(us_gaap.get('DebtToEquityRatio', {}))
            free_cash_flow = self._get_latest_value(us_gaap.get('NetCashProvidedByUsedInOperatingActivities', {}))
            revenue = self._get_latest_value(us_gaap.get('Revenues', {}))
            operating_margin = self._get_latest_value(us_gaap.get('OperatingIncomeLoss', {}))

            # Get company name
            name = self._get_latest_value(dei.get('EntityRegistrantName', {}))

            return Fundamentals(
                ticker=ticker.upper(),
                trailing_pe=trailing_pe,
                price_to_book=price_to_book,
                roe=roe,
                roa=roa,
                debt_to_equity=debt_to_equity,
                free_cash_flow=free_cash_flow,
                revenue=revenue,
                operating_margin=operating_margin,
                sector=None,  # TODO: Extract from SEC data
                name=name
            )

        except Exception:
            # TODO: Add proper error handling and logging
            return self._empty_fundamentals(ticker)

    def _get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Convert ticker symbol to CIK."""
        # TODO: Implement ticker to CIK mapping
        # This would typically involve querying SEC's ticker lookup API
        # For now, return None to indicate not implemented
        return None

    def _get_latest_value(self, metric_data: Dict[str, Any]) -> Optional[float]:
        """Extract the latest value from SEC metric data."""
        if not metric_data or 'units' not in metric_data:
            return None

        units = metric_data['units']
        # Look for USD values first, then other units
        for unit_type in ['USD', 'USD/shares', 'shares']:
            if unit_type in units:
                unit_data = units[unit_type]
                if unit_data:
                    # Get the most recent value
                    latest_entry = max(unit_data, key=lambda x: x['end'])
                    return latest_entry.get('val')

        return None

    def _empty_fundamentals(self, ticker: str) -> Fundamentals:
        """Return empty fundamentals for a ticker."""
        return Fundamentals(
            ticker=ticker.upper(),
            trailing_pe=None,
            price_to_book=None,
            roe=None,
            roa=None,
            debt_to_equity=None,
            free_cash_flow=None
        )


# Register the source
from .base import register_source

register_source(SECSource())
