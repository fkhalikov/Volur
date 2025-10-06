"""Tests for DCF valuation calculations."""

from volur.models.types import DCFParams
from volur.plugins.base import Fundamentals, Quote
from volur.valuation.dcf import calculate_dcf_value, calculate_margin_of_safety


class TestDCFCalculation:
    """Test DCF valuation calculations."""

    def test_dcf_basic_calculation(self):
        """Test basic DCF calculation with valid inputs."""
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

        params = DCFParams(
            discount_rate=0.10,
            long_term_growth=0.05,
            years=10
        )

        iv_per_share, iv_total = calculate_dcf_value(quote, fundamentals, params)

        assert iv_per_share is not None
        assert iv_total is not None
        assert iv_per_share > 0
        assert iv_total > 0
        assert iv_per_share == iv_total / quote.shares_outstanding

    def test_dcf_no_fcf_returns_none(self):
        """Test DCF calculation returns None when FCF is missing."""
        quote = Quote(ticker="TEST", price=100.0)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=None
        )

        params = DCFParams()
        iv_per_share, iv_total = calculate_dcf_value(quote, fundamentals, params)

        assert iv_per_share is None
        assert iv_total is None

    def test_dcf_terminal_growth_validation(self):
        """Test DCF calculation validates terminal growth < discount rate."""
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

        params = DCFParams(
            discount_rate=0.10,
            long_term_growth=0.05,
            terminal_growth=0.12  # Invalid: > discount rate
        )

        iv_per_share, iv_total = calculate_dcf_value(quote, fundamentals, params)

        assert iv_per_share is None
        assert iv_total is None

    def test_margin_of_safety_calculation(self):
        """Test margin of safety calculation."""
        # Positive margin of safety
        mos = calculate_margin_of_safety(80.0, 100.0)
        assert mos == 0.20  # 20%

        # Negative margin of safety
        mos = calculate_margin_of_safety(120.0, 100.0)
        assert mos == -0.20  # -20%

        # Zero margin of safety
        mos = calculate_margin_of_safety(100.0, 100.0)
        assert mos == 0.0

    def test_margin_of_safety_invalid_inputs(self):
        """Test margin of safety with invalid inputs."""
        # None values
        assert calculate_margin_of_safety(None, 100.0) is None
        assert calculate_margin_of_safety(80.0, None) is None

        # Zero intrinsic value
        assert calculate_margin_of_safety(80.0, 0.0) is None

        # Negative intrinsic value
        assert calculate_margin_of_safety(80.0, -100.0) is None

    def test_dcf_with_different_parameters(self):
        """Test DCF calculation with different parameter sets."""
        quote = Quote(ticker="TEST", price=100.0, shares_outstanding=1000000)
        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

        # Higher discount rate should result in lower intrinsic value
        params_high_discount = DCFParams(discount_rate=0.15, long_term_growth=0.05)
        params_low_discount = DCFParams(discount_rate=0.08, long_term_growth=0.05)

        iv_high, _ = calculate_dcf_value(quote, fundamentals, params_high_discount)
        iv_low, _ = calculate_dcf_value(quote, fundamentals, params_low_discount)

        assert iv_high is not None
        assert iv_low is not None
        assert iv_low > iv_high
