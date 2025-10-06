"""Command-line interface for Volur."""

import argparse
import sys
from typing import List, Optional

from .config import settings
from .models.types import DCFParams
from .plugins.base import get_source, list_sources
from .valuation.engine import analyze_stock


def format_currency(value: Optional[float]) -> str:
    """Format currency value for display."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_percentage(value: Optional[float]) -> str:
    """Format percentage value for display."""
    if value is None:
        return "N/A"
    return f"{value:.2%}"


def format_number(value: Optional[float]) -> str:
    """Format number for display."""
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def print_valuation_table(results: List, source_name: str) -> None:
    """Print valuation results in a formatted table."""
    print(f"\n{'='*80}")
    print(f"VALUATION RESULTS - Data Source: {source_name.upper()}")
    print(f"{'='*80}")

    # Table header
    print(f"{'Ticker':<8} {'Price':<10} {'IV/Share':<12} {'MoS':<8} {'Score':<8} {'P/E':<8} {'P/B':<8} {'ROE':<8} {'FCF Yield':<10}")
    print("-" * 80)

    # Table rows
    for result in results:
        print(f"{result.ticker:<8} "
              f"{format_currency(result.intrinsic_value_per_share):<12} "
              f"{format_percentage(result.margin_of_safety):<8} "
              f"{format_number(result.value_score):<8} "
              f"{format_number(result.pe_ratio):<8} "
              f"{format_number(result.pb_ratio):<8} "
              f"{format_percentage(result.roe):<8} "
              f"{format_percentage(result.fcf_yield):<10}")

    print(f"{'='*80}\n")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Volur - A pluggable valuation platform for value investing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  volur --source yfinance --ticker AAPL MSFT
  volur --source fmp --ticker AAPL --growth 0.05 --discount 0.12
  volur --source sec --ticker AAPL --years 15 --terminal 0.03
        """
    )

    # Required arguments
    parser.add_argument(
        "--source",
        choices=list_sources(),
        default="yfinance",
        help="Data source to use (default: yfinance)"
    )
    parser.add_argument(
        "--ticker",
        nargs="+",
        required=True,
        help="Stock ticker symbol(s) to analyze"
    )

    # DCF parameters
    parser.add_argument(
        "--growth",
        type=float,
        default=settings.long_term_growth,
        help=f"Long-term growth rate (default: {settings.long_term_growth})"
    )
    parser.add_argument(
        "--discount",
        type=float,
        default=settings.discount_rate,
        help=f"Discount rate (default: {settings.discount_rate})"
    )
    parser.add_argument(
        "--years",
        type=int,
        default=settings.years,
        help=f"Number of years for DCF (default: {settings.years})"
    )
    parser.add_argument(
        "--terminal",
        type=float,
        help="Terminal growth rate (defaults to growth rate)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.growth < 0 or args.growth > 1:
        print("Error: Growth rate must be between 0 and 1", file=sys.stderr)
        return 1

    if args.discount <= 0 or args.discount > 1:
        print("Error: Discount rate must be between 0 and 1", file=sys.stderr)
        return 1

    if args.years <= 0:
        print("Error: Years must be positive", file=sys.stderr)
        return 1

    if args.terminal is not None and (args.terminal < 0 or args.terminal >= args.discount):
        print("Error: Terminal growth must be non-negative and less than discount rate", file=sys.stderr)
        return 1

    # Create DCF parameters
    dcf_params = DCFParams(
        discount_rate=args.discount,
        long_term_growth=args.growth,
        years=args.years,
        terminal_growth=args.terminal
    )

    # Get data source
    try:
        data_source = get_source(args.source)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Analyze each ticker
    results = []
    errors = []

    print(f"Analyzing {len(args.ticker)} ticker(s) using {args.source} data source...")

    for ticker in args.ticker:
        try:
            result = analyze_stock(data_source, ticker.upper(), dcf_params)
            results.append(result)
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}", file=sys.stderr)
            errors.append(ticker)

    # Print results
    if results:
        print_valuation_table(results, args.source)

        # Print summary
        print("SUMMARY:")
        print(f"  Successfully analyzed: {len(results)} ticker(s)")
        if errors:
            print(f"  Failed to analyze: {len(errors)} ticker(s): {', '.join(errors)}")

    # Return error code if any tickers failed
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
