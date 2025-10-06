"""Main valuation engine that orchestrates all calculations."""

from ..models.types import DCFParams, ValuationResult
from ..plugins.base import DataSource, Fundamentals, Quote
from .dcf import calculate_dcf_value, calculate_margin_of_safety
from .ratios import calculate_fcf_yield
from .scoring import calculate_value_score


def calculate_comprehensive_valuation(
    quote: Quote,
    fundamentals: Fundamentals,
    params: DCFParams
) -> ValuationResult:
    """Calculate comprehensive valuation for a stock.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        params: DCF calculation parameters
        
    Returns:
        Comprehensive valuation result
    """
    # Calculate DCF intrinsic value
    intrinsic_value_per_share, intrinsic_value_total = calculate_dcf_value(
        quote, fundamentals, params
    )

    # Calculate margin of safety
    margin_of_safety = None
    if quote.price and intrinsic_value_per_share:
        margin_of_safety = calculate_margin_of_safety(quote.price, intrinsic_value_per_share)

    # Calculate FCF yield
    fcf_yield = calculate_fcf_yield(quote, fundamentals)

    # Calculate value score
    value_score = calculate_value_score(quote, fundamentals)

    return ValuationResult(
        ticker=quote.ticker,
        intrinsic_value_per_share=intrinsic_value_per_share,
        intrinsic_value_total=intrinsic_value_total,
        margin_of_safety=margin_of_safety,
        value_score=value_score,
        fcf_yield=fcf_yield,
        pe_ratio=fundamentals.trailing_pe,
        pb_ratio=fundamentals.price_to_book,
        roe=fundamentals.roe,
        debt_to_equity=fundamentals.debt_to_equity
    )


def analyze_stock(
    data_source: DataSource,
    ticker: str,
    params: DCFParams
) -> ValuationResult:
    """Analyze a stock using the specified data source.
    
    Args:
        data_source: Data source to use
        ticker: Stock ticker symbol
        params: DCF calculation parameters
        
    Returns:
        Comprehensive valuation result
    """
    # Get data from source
    quote = data_source.get_quote(ticker)
    fundamentals = data_source.get_fundamentals(ticker)

    # Calculate comprehensive valuation
    return calculate_comprehensive_valuation(quote, fundamentals, params)
