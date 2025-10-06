"""Yahoo Finance data source implementation."""


import yfinance as yf

from ..caching import cached
from .base import Fundamentals, Quote


class YahooFinanceSource:
    """Yahoo Finance data source implementation."""

    name = "yfinance"

    @cached(ttl=3600)  # Cache for 1 hour
    def get_quote(self, ticker: str) -> Quote:
        """Get current quote from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return Quote(
                ticker=ticker.upper(),
                price=info.get('currentPrice') or info.get('regularMarketPrice'),
                currency=info.get('currency'),
                shares_outstanding=info.get('sharesOutstanding')
            )
        except Exception:
            return Quote(ticker=ticker.upper(), price=None)

    @cached(ttl=3600)  # Cache for 1 hour
    def get_fundamentals(self, ticker: str) -> Fundamentals:
        """Get fundamental data from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get financials for more detailed data
            financials = stock.financials
            balance_sheet = stock.balance_sheet

            # Calculate ROE and ROA if possible
            roe = None
            roa = None
            if financials is not None and not financials.empty:
                try:
                    net_income = financials.iloc[0].get('Net Income', 0)
                    if balance_sheet is not None and not balance_sheet.empty:
                        total_equity = balance_sheet.iloc[0].get('Total Stockholder Equity', 0)
                        total_assets = balance_sheet.iloc[0].get('Total Assets', 0)

                        if total_equity and total_equity != 0:
                            roe = net_income / total_equity
                        if total_assets and total_assets != 0:
                            roa = net_income / total_assets
                except (IndexError, KeyError, ZeroDivisionError):
                    pass

            return Fundamentals(
                ticker=ticker.upper(),
                trailing_pe=info.get('trailingPE'),
                price_to_book=info.get('priceToBook'),
                roe=roe,
                roa=roa,
                debt_to_equity=info.get('debtToEquity'),
                free_cash_flow=info.get('freeCashflow'),
                revenue=info.get('totalRevenue'),
                operating_margin=info.get('operatingMargins'),
                sector=info.get('sector'),
                name=info.get('longName')
            )
        except Exception:
            return Fundamentals(ticker=ticker.upper(), trailing_pe=None, price_to_book=None,
                               roe=None, roa=None, debt_to_equity=None, free_cash_flow=None)


# Register the source
from .base import register_source

register_source(YahooFinanceSource())
