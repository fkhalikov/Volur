"""Tests for value scoring calculations."""

from volur.plugins.base import Fundamentals, Quote
from volur.valuation.scoring import (
    calculate_value_score,
    get_value_score_interpretation,
)


class TestValueScoring:
    """Test value scoring calculations."""

    def test_value_score_calculation(self):
        """Test value score calculation with all metrics."""
        quote = Quote(
            ticker="TEST",
            price=100.0,
            shares_outstanding=1000000
        )

        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=10.0,  # Low P/E = good
            price_to_book=1.0,  # Low P/B = good
            roe=0.20,  # High ROE = good
            roa=0.15,
            debt_to_equity=0.3,
            free_cash_flow=15000000  # High FCF yield = good
        )

        score = calculate_value_score(quote, fundamentals)

        assert score is not None
        assert 0 <= score <= 100
        assert score > 50  # Should be a good score with these metrics

    def test_value_score_missing_metrics(self):
        """Test value score calculation with missing metrics."""
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

        score = calculate_value_score(quote, fundamentals)
        assert score is None

    def test_value_score_partial_metrics(self):
        """Test value score calculation with partial metrics."""
        quote = Quote(
            ticker="TEST",
            price=100.0,
            shares_outstanding=1000000
        )

        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=15.0,  # Only P/E available
            price_to_book=None,
            roe=None,
            roa=None,
            debt_to_equity=None,
            free_cash_flow=None
        )

        score = calculate_value_score(quote, fundamentals)

        assert score is not None
        assert 0 <= score <= 100

    def test_value_score_poor_metrics(self):
        """Test value score calculation with poor metrics."""
        quote = Quote(
            ticker="TEST",
            price=100.0,
            shares_outstanding=1000000
        )

        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=50.0,  # High P/E = bad
            price_to_book=10.0,  # High P/B = bad
            roe=0.05,  # Low ROE = bad
            roa=0.03,
            debt_to_equity=2.0,
            free_cash_flow=1000000  # Low FCF yield = bad
        )

        score = calculate_value_score(quote, fundamentals)

        assert score is not None
        assert 0 <= score <= 100
        assert score < 50  # Should be a poor score with these metrics

    def test_value_score_extreme_values(self):
        """Test value score calculation with extreme values."""
        quote = Quote(
            ticker="TEST",
            price=100.0,
            shares_outstanding=1000000
        )

        fundamentals = Fundamentals(
            ticker="TEST",
            trailing_pe=0.1,  # Very low P/E
            price_to_book=0.1,  # Very low P/B
            roe=1.0,  # Very high ROE (100%)
            roa=0.5,
            debt_to_equity=0.1,
            free_cash_flow=100000000  # Very high FCF
        )

        score = calculate_value_score(quote, fundamentals)

        assert score is not None
        assert 0 <= score <= 100
        assert score > 80  # Should be excellent with these extreme good metrics

    def test_value_score_interpretation(self):
        """Test value score interpretation."""
        assert get_value_score_interpretation(90) == "Excellent Value"
        assert get_value_score_interpretation(70) == "Good Value"
        assert get_value_score_interpretation(50) == "Fair Value"
        assert get_value_score_interpretation(30) == "Poor Value"
        assert get_value_score_interpretation(10) == "Very Poor Value"

    def test_value_score_boundary_values(self):
        """Test value score interpretation at boundaries."""
        assert get_value_score_interpretation(80) == "Excellent Value"
        assert get_value_score_interpretation(79) == "Good Value"
        assert get_value_score_interpretation(60) == "Good Value"
        assert get_value_score_interpretation(59) == "Fair Value"
        assert get_value_score_interpretation(40) == "Fair Value"
        assert get_value_score_interpretation(39) == "Poor Value"
        assert get_value_score_interpretation(20) == "Poor Value"
        assert get_value_score_interpretation(19) == "Very Poor Value"
