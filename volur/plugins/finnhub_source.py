"""Finnhub data source implementation."""

import requests
from typing import Optional
from volur.plugins.base import DataSource, Quote, Fundamentals
from volur.caching import cached
from volur.config import settings


class FinnhubSource:
    """Finnhub data source implementation."""
    
    def __init__(self):
        """Initialize Finnhub source."""
        self.name = "finnhub"
        self.api_key = settings.finnhub_api_key
        if not self.api_key:
            raise ValueError("Finnhub API key not configured. Set FINNHUB_API_KEY environment variable.")
        
        self.base_url = "https://finnhub.io/api/v1"
        self.headers = {
            "X-Finnhub-Token": self.api_key,
            "User-Agent": "Volur/0.1.0"
        }
    
    def get_quote(self, ticker: str) -> Optional[Quote]:
        """Get current quote from Finnhub."""
        try:
            # Get quote data
            quote_url = f"{self.base_url}/quote"
            params = {"symbol": ticker}
            
            response = requests.get(quote_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            quote_data = response.json()
            
            # Debug logging
            print(f"Finnhub quote response for {ticker}: {quote_data}")
            
            # Check if we got valid data
            if not quote_data or quote_data.get('c') is None or quote_data.get('c') == 0:
                print(f"No valid quote data for {ticker}")
                return None
            
            # Get company profile for additional data
            profile_url = f"{self.base_url}/stock/profile2"
            profile_params = {"symbol": ticker}
            
            profile_response = requests.get(profile_url, params=profile_params, headers=self.headers, timeout=10)
            profile_data = profile_response.json() if profile_response.status_code == 200 else {}
            
            print(f"Finnhub profile response for {ticker}: {profile_data}")
            
            return Quote(
                ticker=ticker,
                price=quote_data.get('c', 0.0),  # current price
                currency=profile_data.get('currency', 'USD'),
                shares_outstanding=profile_data.get('shareOutstanding')
            )
            
        except Exception as e:
            print(f"Finnhub API error for {ticker}: {e}")
            return None
    
    def get_fundamentals(self, ticker: str) -> Optional[Fundamentals]:
        """Get fundamental data from Finnhub."""
        try:
            # Get company profile
            profile_url = f"{self.base_url}/stock/profile2"
            profile_params = {"symbol": ticker}
            
            profile_response = requests.get(profile_url, params=profile_params, headers=self.headers, timeout=10)
            profile_data = profile_response.json() if profile_response.status_code == 200 else {}
            
            # Get financial metrics
            metrics_url = f"{self.base_url}/stock/metric"
            metrics_params = {"symbol": ticker, "metric": "all"}
            
            metrics_response = requests.get(metrics_url, params=metrics_params, headers=self.headers, timeout=10)
            metrics_data = metrics_response.json() if metrics_response.status_code == 200 else {}
            
            # Get financial statements (basic)
            financials_url = f"{self.base_url}/stock/financials-reported"
            financials_params = {"symbol": ticker, "freq": "annual"}
            
            financials_response = requests.get(financials_url, params=financials_params, headers=self.headers, timeout=10)
            financials_data = financials_response.json() if financials_response.status_code == 200 else {}
            
            # Extract financial data
            current_metrics = metrics_data.get('metric', {})
            financials = financials_data.get('data', [])
            
            # Get latest financial data
            latest_financials = financials[0] if financials else {}
            report = latest_financials.get('report', {})
            
            return Fundamentals(
                ticker=ticker,
                name=profile_data.get('name', ticker),
                trailing_pe=current_metrics.get('peBasicExclExtraTTM'),
                forward_pe=current_metrics.get('peExclExtraTTM'),
                price_to_book=current_metrics.get('pbAnnual'),
                free_cash_flow=report.get('freeCashFlow'),
                revenue=report.get('revenues'),
                operating_margin=report.get('operatingIncome') / report.get('revenues') if report.get('revenues') and report.get('revenues') != 0 else None,
                roe=current_metrics.get('roeRfy'),
                roa=current_metrics.get('roaRfy'),
                debt_to_equity=current_metrics.get('totalDebt/totalEquityAnnual')
            )
            
        except Exception:
            return None


# Register the source
from volur.plugins import register_source
register_source(FinnhubSource())
