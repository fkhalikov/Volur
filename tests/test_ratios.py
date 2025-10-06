"""Tests for financial ratio calculations."""

from volur.plugins.base import Fundamentals, Quote
from volur.valuation.ratios import (
    calculate_debt_to_equity,
    calculate_fcf_yield,
    calculate_price_to_book,
    calculate_price_to_earnings,
    calculate_return_on_assets,
    calculate_return_on_equity,
)


class TestRatioCalculations:
    """Test financial ratio calculations."""

    def test_fcf_yield_calculation(self):
        """Test FCF yield calculation."""
        quote = Quote(
            ticker="TEST",
            price=100.0,
            shares_outstanding=1000000
        )

        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000  # $10M FCF
        )

        fcf_yield = calculate_fcf_yield(quote, fundamentals)

        # Market cap = 100 * 1,000,000 = $100M
        # FCF yield = $10M / $100M = 0.10 (10%)
        assert fcf_yield == 0.10

    def test_fcf_yield_missing_data(self):
        """Test FCF yield calculation with missing data."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        fcf_yield = calculate_fcf_yield(quote, fundamentals)
        assert fcf_yield is None

    def test_fcf_yield_zero_market_cap(self):
        """Test FCF yield calculation with zero market cap."""
        quote = Quote(
            ticker="TEST",
            price=0.0,
            shares_outstanding=1000000
        )

        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        fcf_yield = calculate_fcf_yield(quote, fundamentals)
        assert fcf_yield is None

    def test_price_to_earnings(self):
        """Test P/E ratio calculation."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        pe = calculate_price_to_earnings(quote, fundamentals)
        assert pe == 15.0

    def test_price_to_book(self):
        """Test P/B ratio calculation."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        pb = calculate_price_to_book(quote, fundamentals)
        assert pb == 2.0

    def test_debt_to_equity(self):
        """Test D/E ratio calculation."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        de = calculate_debt_to_equity(quote, fundamentals)
        assert de == 0.5

    def test_return_on_equity(self):
        """Test ROE calculation."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        roe = calculate_return_on_equity(quote, fundamentals)
        assert roe == 0.15

    def test_return_on_assets(self):
        """Test ROA calculation."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        roa = calculate_return_on_assets(quote, fundamentals)
        assert roa == 0.10

    def test_ratios_with_none_values(self):
        """Test ratio calculations with None values."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=None,
            price_to_book=None,
            roe=None,
            roa=None,
            debt_to_equity=None,
            free_cash_flow=None
        )

        assert calculate_price_to_earnings(quote, fundamentals) is None
        assert calculate_price_to_book(quote, fundamentals) is None
        assert calculate_debt_to_equity(quote, fundamentals) is None
        assert calculate_return_on_equity(quote, fundamentals) is None
        assert calculate_return_on_assets(quote, fundamentals) is None
