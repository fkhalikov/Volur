"""Plugin base interfaces and registry for data sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class Quote:
    """Stock quote data."""
    ticker: str
    price: Optional[float]
    currency: Optional[str] = None
    shares_outstanding: Optional[float] = None


@dataclass
class Fundamentals:
    """Company fundamental data."""
    ticker: str
    trailing_pe: Optional[float]
    price_to_book: Optional[float]
    roe: Optional[float]
    roa: Optional[float]
    debt_to_equity: Optional[float]
    free_cash_flow: Optional[float]   # equity FCF preferred
    revenue: Optional[float] = None
    operating_margin: Optional[float] = None
    sector: Optional[str] = None
    name: Optional[str] = None


class DataSource(Protocol):
    """Protocol for data source implementations."""
    name: str

    def get_quote(self, ticker: str) -> Quote:
        """Get current quote for a ticker."""
        ...

    def get_fundamentals(self, ticker: str) -> Fundamentals:
        """Get fundamental data for a ticker."""
        ...


# Simple registry for runtime selection
_REGISTRY: Dict[str, DataSource] = {}


def register_source(source: DataSource) -> None:
    """Register a data source in the global registry."""
    _REGISTRY[source.name] = source


def get_source(name: str) -> DataSource:
    """Get a registered data source by name."""
    if name not in _REGISTRY:
        raise KeyError(f"Unknown data source: {name}")
    return _REGISTRY[name]


def list_sources() -> List[str]:
    """List all registered data source names."""
    return sorted(_REGISTRY.keys())
