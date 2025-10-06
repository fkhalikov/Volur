"""Volur: A pluggable valuation platform for value investing."""

__version__ = "0.1.0"
__author__ = "Volur Team"
__description__ = "A pluggable valuation platform with multiple data sources"

from .plugins.base import (
    DataSource,
    Fundamentals,
    Quote,
    get_source,
    list_sources,
    register_source,
)

__all__ = [
    "DataSource",
    "Quote",
    "Fundamentals",
    "register_source",
    "get_source",
    "list_sources",
]
