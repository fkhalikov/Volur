"""Value scoring calculations."""

from typing import Optional

from ..config import settings
from ..plugins.base import Fundamentals, Quote


def calculate_value_score(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate a simple value score based on multiple metrics.
    
    The score combines:
    - P/E ratio (inverse - lower is better)
    - P/B ratio (inverse - lower is better) 
    - FCF yield (higher is better)
    - ROE (higher is better)
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        
    Returns:
        Value score (0-100, higher is better), or None if insufficient data
    """
    scores = []
    weights = []

    # P/E score (inverse - lower P/E is better)
    if fundamentals.trailing_pe and fundamentals.trailing_pe > 0:
        pe_score = min(100, max(0, 100 - fundamentals.trailing_pe * 2))  # Scale to 0-100
        scores.append(pe_score)
        weights.append(settings.pe_weight)

    # P/B score (inverse - lower P/B is better)
    if fundamentals.price_to_book and fundamentals.price_to_book > 0:
        pb_score = min(100, max(0, 100 - fundamentals.price_to_book * 20))  # Scale to 0-100
        scores.append(pb_score)
        weights.append(settings.pb_weight)

    # FCF yield score (higher is better)
    fcf_yield = _calculate_fcf_yield_for_scoring(quote, fundamentals)
    if fcf_yield is not None:
        fcf_score = min(100, max(0, fcf_yield * 1000))  # Scale to 0-100
        scores.append(fcf_score)
        weights.append(settings.fcf_yield_weight)

    # ROE score (higher is better)
    if fundamentals.roe is not None:
        roe_score = min(100, max(0, fundamentals.roe * 100))  # Scale to 0-100
        scores.append(roe_score)
        weights.append(settings.roe_weight)

    # Calculate weighted average
    if not scores or not weights:
        return None

    # Normalize weights
    total_weight = sum(weights)
    if total_weight == 0:
        return None

    normalized_weights = [w / total_weight for w in weights]

    # Calculate weighted score
    weighted_score = sum(score * weight for score, weight in zip(scores, normalized_weights))

    return round(weighted_score, 2)


def _calculate_fcf_yield_for_scoring(quote: Quote, fundamentals: Fundamentals) -> Optional[float]:
    """Calculate FCF yield for scoring purposes."""
    if not quote.price or not quote.shares_outstanding or not fundamentals.free_cash_flow:
        return None

    market_cap = quote.price * quote.shares_outstanding
    if market_cap <= 0:
        return None

    return fundamentals.free_cash_flow / market_cap


def get_value_score_interpretation(score: float) -> str:
    """Get interpretation of value score.
    
    Args:
        score: Value score (0-100)
        
    Returns:
        Interpretation string
    """
    if score >= 80:
        return "Excellent Value"
    elif score >= 60:
        return "Good Value"
    elif score >= 40:
        return "Fair Value"
    elif score >= 20:
        return "Poor Value"
    else:
        return "Very Poor Value"
