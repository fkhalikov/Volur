"""Financial ratio calculations."""

from typing import Optional

from ..plugins.base import Fundamentals, Quote


def calculate_fcf_yield(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate Free Cash Flow yield.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        
    Returns:
        FCF yield as a percentage, or None if insufficient data
    """
    if not quote.price or not quote.shares_outstanding or not fundamentals.free_cash_flow:
        return None

    # Calculate market cap
    market_cap = quote.price * quote.shares_outstanding

    if market_cap <= 0:
        return None

    # FCF yield = Free Cash Flow / Market Cap
    fcf_yield = fundamentals.free_cash_flow / market_cap
    return fcf_yield


def calculate_price_to_earnings(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate Price-to-Earnings ratio.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        
    Returns:
        P/E ratio, or None if insufficient data
    """
    return fundamentals.trailing_pe


def calculate_price_to_book(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate Price-to-Book ratio.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        
    Returns:
        P/B ratio, or None if insufficient data
    """
    return fundamentals.price_to_book


def calculate_debt_to_equity(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate Debt-to-Equity ratio.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        
    Returns:
        D/E ratio, or None if insufficient data
    """
    return fundamentals.debt_to_equity


def calculate_return_on_equity(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate Return on Equity.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        
    Returns:
        ROE as a percentage, or None if insufficient data
    """
    return fundamentals.roe


def calculate_return_on_assets(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate Return on Assets.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        
    Returns:
        ROA as a percentage, or None if insufficient data
    """
    return fundamentals.roa
