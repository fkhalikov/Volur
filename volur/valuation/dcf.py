"""Discounted Cash Flow (DCF) valuation calculations."""

from typing import Optional, Tuple

from ..models.types import DCFParams
from ..plugins.base import Fundamentals, Quote


def calculate_dcf_value(
    quote: Quote,
    fundamentals: Fundamentals,
    params: DCFParams
) -> Tuple[Optional[float], Optional[float]]:
    """Calculate DCF intrinsic value.
    
    Args:
        quote: Stock quote data
        fundamentals: Company fundamental data
        params: DCF calculation parameters
        
    Returns:
        Tuple of (intrinsic_value_per_share, intrinsic_value_total)
        Returns None values if insufficient data
    """
    if not fundamentals.free_cash_flow:
        return None, None

    # Use terminal growth rate if provided, otherwise use long-term growth
    terminal_growth = params.terminal_growth or params.long_term_growth

    # Validate that terminal growth is less than discount rate
    if terminal_growth >= params.discount_rate:
        return None, None

    # Calculate present value of cash flows
    pv_cash_flows = _calculate_present_value_cash_flows(
        fundamentals.free_cash_flow,
        params.long_term_growth,
        params.discount_rate,
        params.years
    )

    # Calculate terminal value
    terminal_value = _calculate_terminal_value(
        fundamentals.free_cash_flow,
        params.long_term_growth,
        terminal_growth,
        params.discount_rate,
        params.years
    )

    # Total intrinsic value
    intrinsic_value_total = pv_cash_flows + terminal_value

    # Calculate per-share value if shares outstanding available
    intrinsic_value_per_share = None
    if quote.shares_outstanding and quote.shares_outstanding > 0:
        intrinsic_value_per_share = intrinsic_value_total / quote.shares_outstanding

    return intrinsic_value_per_share, intrinsic_value_total


def _calculate_present_value_cash_flows(
    initial_fcf: float,
    growth_rate: float,
    discount_rate: float,
    years: int
) -> float:
    """Calculate present value of projected cash flows."""
    pv_total = 0.0

    for year in range(1, years + 1):
        # Project FCF for this year
        projected_fcf = initial_fcf * ((1 + growth_rate) ** year)

        # Calculate present value
        pv = projected_fcf / ((1 + discount_rate) ** year)
        pv_total += pv

    return pv_total


def _calculate_terminal_value(
    initial_fcf: float,
    growth_rate: float,
    terminal_growth: float,
    discount_rate: float,
    years: int
) -> float:
    """Calculate terminal value using Gordon Growth Model."""
    # FCF in the terminal year
    terminal_fcf = initial_fcf * ((1 + growth_rate) ** years)

    # Terminal value = Terminal FCF * (1 + terminal_growth) / (discount_rate - terminal_growth)
    terminal_value = terminal_fcf * (1 + terminal_growth) / (discount_rate - terminal_growth)

    # Present value of terminal value
    pv_terminal_value = terminal_value / ((1 + discount_rate) ** years)

    return pv_terminal_value


def calculate_margin_of_safety(
    current_price: float,
    intrinsic_value_per_share: float
) -> Optional[float]:
    """Calculate margin of safety.
    
    Args:
        current_price: Current stock price
        intrinsic_value_per_share: Intrinsic value per share
        
    Returns:
        Margin of safety as a percentage, or None if invalid inputs
    """
    if not current_price or not intrinsic_value_per_share or intrinsic_value_per_share <= 0:
        return None

    margin_of_safety = (intrinsic_value_per_share - current_price) / intrinsic_value_per_share
    return margin_of_safety
