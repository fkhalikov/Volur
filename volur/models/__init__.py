"""Domain models and types."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ValuationResult:
    """Result of a valuation calculation."""
    ticker: str
    intrinsic_value_per_share: Optional[float] = None
    intrinsic_value_total: Optional[float] = None
    margin_of_safety: Optional[float] = None
    value_score: Optional[float] = None
    fcf_yield: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None


@dataclass
class DCFParams:
    """Parameters for DCF calculation."""
    discount_rate: float = 0.10
    long_term_growth: float = 0.02
    years: int = 10
    terminal_growth: Optional[float] = None
