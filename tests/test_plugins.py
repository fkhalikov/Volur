"""Tests for plugin system and data sources."""

from unittest.mock import Mock

import pytest

from volur.plugins.base import (
    _REGISTRY,
    DataSource,
    Fundamentals,
    Quote,
    get_source,
    list_sources,
    register_source,
)
from volur.plugins.sec_source import SECSource
from volur.plugins.yf_source import YahooFinanceSource


class TestPluginRegistry:
    """Test the plugin registry system."""

    def setup_method(self):
        """Clear registry before each test."""
        _REGISTRY.clear()

    def test_register_and_get_source(self):
        """Test registering and retrieving a data source."""
        mock_source = Mock(spec=DataSource)
        mock_source.name = "test_source"

        register_source(mock_source)

        retrieved_source = get_source("test_source")
        assert retrieved_source is mock_source

    def test_get_nonexistent_source_raises_error(self):
        """Test that getting a nonexistent source raises KeyError."""
        with pytest.raises(KeyError, match="Unknown data source: nonexistent"):
            get_source("nonexistent")

    def test_list_sources(self):
        """Test listing all registered sources."""
        mock_source1 = Mock(spec=DataSource)
        mock_source1.name = "source_a"

        mock_source2 = Mock(spec=DataSource)
        mock_source2.name = "source_b"

        register_source(mock_source1)
        register_source(mock_source2)

        sources = list_sources()
        assert set(sources) == {"source_a", "source_b"}
        assert sources == sorted(sources)  # Should be sorted

    def test_register_multiple_sources_same_name(self):
        """Test that registering multiple sources with same name overwrites."""
        mock_source1 = Mock(spec=DataSource)
        mock_source1.name = "test_source"

        mock_source2 = Mock(spec=DataSource)
        mock_source2.name = "test_source"

        register_source(mock_source1)
        register_source(mock_source2)

        retrieved_source = get_source("test_source")
        assert retrieved_source is mock_source2  # Last registered wins


class TestYahooFinanceSource:
    """Test Yahoo Finance data source."""

    def setup_method(self):
        """Clear registry before each test."""
        _REGISTRY.clear()

    @pytest.mark.network
    def test_yahoo_finance_source_registration(self):
        """Test that Yahoo Finance source is registered."""
        # Import the module to trigger registration

        sources = list_sources()
        assert "yfinance" in sources

    @pytest.mark.network
    def test_yahoo_finance_get_quote(self):
        """Test getting quote from Yahoo Finance."""
        source = YahooFinanceSource()

        # Test with a real ticker (requires network)
        quote = source.get_quote("AAPL")

        assert quote.ticker == "AAPL"
        assert quote.price is not None
        assert quote.price > 0

    @pytest.mark.network
    def test_yahoo_finance_get_fundamentals(self):
        """Test getting fundamentals from Yahoo Finance."""
        source = YahooFinanceSource()

        # Test with a real ticker (requires network)
        fundamentals = source.get_fundamentals("AAPL")

        assert fundamentals.ticker == "AAPL"
        # At least some fields should be populated
        assert any([
            fundamentals.trailing_pe,
            fundamentals.price_to_book,
            fundamentals.roe,
            fundamentals.roa,
            fundamentals.debt_to_equity,
            fundamentals.free_cash_flow
        ])

    def test_yahoo_finance_invalid_ticker(self):
        """Test Yahoo Finance with invalid ticker."""
        source = YahooFinanceSource()

        quote = source.get_quote("INVALID_TICKER_XYZ")
        assert quote.ticker == "INVALID_TICKER_XYZ"
        assert quote.price is None

        fundamentals = source.get_fundamentals("INVALID_TICKER_XYZ")
        assert fundamentals.ticker == "INVALID_TICKER_XYZ"
        assert fundamentals.trailing_pe is None


class TestSECSource:
    """Test SEC data source."""

    def setup_method(self):
        """Clear registry before each test."""
        _REGISTRY.clear()

    def test_sec_source_registration(self):
        """Test that SEC source is registered."""
        # Import the module to trigger registration

        sources = list_sources()
        assert "sec" in sources

    def test_sec_source_get_quote(self):
        """Test getting quote from SEC (should return None)."""
        source = SECSource()

        quote = source.get_quote("AAPL")

        assert quote.ticker == "AAPL"
        assert quote.price is None  # SEC doesn't provide real-time quotes

    def test_sec_source_get_fundamentals_no_cik(self):
        """Test getting fundamentals from SEC without CIK mapping."""
        source = SECSource()

        fundamentals = source.get_fundamentals("AAPL")

        assert fundamentals.ticker == "AAPL"
        # Should return empty fundamentals since CIK mapping is not implemented
        assert fundamentals.trailing_pe is None
        assert fundamentals.price_to_book is None


class TestDataModels:
    """Test data model classes."""

    def test_quote_creation(self):
        """Test Quote dataclass creation."""
        quote = Quote(
            ticker="AAPL",
            price=150.0,
            currency="USD",
            shares_outstanding=1000000000
        )

        assert quote.ticker == "AAPL"
        assert quote.price == 150.0
        assert quote.currency == "USD"
        assert quote.shares_outstanding == 1000000000

    def test_fundamentals_creation(self):
        """Test Fundamentals dataclass creation."""
        fundamentals = Fundamentals(
            ticker="AAPL",
            trailing_pe=25.0,
            price_to_book=5.0,
            roe=0.20,
            roa=0.15,
            debt_to_equity=0.3,
            free_cash_flow=50000000000,
            revenue=300000000000,
            operating_margin=0.25,
            sector="Technology",
            name="Apple Inc."
        )

        assert fundamentals.ticker == "AAPL"
        assert fundamentals.trailing_pe == 25.0
        assert fundamentals.price_to_book == 5.0
        assert fundamentals.roe == 0.20
        assert fundamentals.roa == 0.15
        assert fundamentals.debt_to_equity == 0.3
        assert fundamentals.free_cash_flow == 50000000000
        assert fundamentals.revenue == 300000000000
        assert fundamentals.operating_margin == 0.25
        assert fundamentals.sector == "Technology"
        assert fundamentals.name == "Apple Inc."
