"""Command-line Yahoo Finance data viewer."""

import argparse
import sys
from typing import Optional
import volur.plugins.yf_source as yf_source
from volur.plugins.base import Quote, Fundamentals


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


def format_large_number(value: Optional[float]) -> str:
    """Format large numbers with appropriate units."""
    if value is None:
        return "N/A"
    
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"


def print_quote_data(quote: Quote) -> None:
    """Print quote data in a formatted table."""
    print(f"\n{'='*60}")
    print(f"QUOTE DATA - {quote.ticker}")
    print(f"{'='*60}")
    
    print(f"{'Field':<20} {'Value':<30}")
    print("-" * 50)
    print(f"{'Ticker':<20} {quote.ticker:<30}")
    print(f"{'Price':<20} {format_currency(quote.price):<30}")
    print(f"{'Currency':<20} {quote.currency or 'N/A':<30}")
    print(f"{'Shares Outstanding':<20} {format_large_number(quote.shares_outstanding):<30}")
    
    if quote.price and quote.shares_outstanding:
        market_cap = quote.price * quote.shares_outstanding
        print(f"{'Market Cap':<20} {format_large_number(market_cap):<30}")


def print_fundamentals_data(fundamentals: Fundamentals) -> None:
    """Print fundamentals data in a formatted table."""
    print(f"\n{'='*60}")
    print(f"FUNDAMENTALS DATA - {fundamentals.ticker}")
    print(f"{'='*60}")
    
    print(f"{'Field':<20} {'Value':<30}")
    print("-" * 50)
    print(f"{'Ticker':<20} {fundamentals.ticker:<30}")
    print(f"{'P/E Ratio':<20} {format_number(fundamentals.trailing_pe):<30}")
    print(f"{'P/B Ratio':<20} {format_number(fundamentals.price_to_book):<30}")
    print(f"{'ROE':<20} {format_percentage(fundamentals.roe):<30}")
    print(f"{'ROA':<20} {format_percentage(fundamentals.roa):<30}")
    print(f"{'Debt-to-Equity':<20} {format_number(fundamentals.debt_to_equity):<30}")
    print(f"{'Free Cash Flow':<20} {format_large_number(fundamentals.free_cash_flow):<30}")
    print(f"{'Revenue':<20} {format_large_number(fundamentals.revenue):<30}")
    print(f"{'Operating Margin':<20} {format_percentage(fundamentals.operating_margin):<30}")
    print(f"{'Sector':<20} {fundamentals.sector or 'N/A':<30}")
    print(f"{'Company Name':<20} {fundamentals.name or 'N/A':<30}")


def print_data_quality(quote: Quote, fundamentals: Fundamentals) -> None:
    """Print data quality indicators."""
    print(f"\n{'='*60}")
    print("DATA QUALITY INDICATORS")
    print(f"{'='*60}")
    
    # Quote data completeness
    quote_fields = [quote.price, quote.currency, quote.shares_outstanding]
    quote_completeness = sum(1 for field in quote_fields if field is not None) / len(quote_fields) * 100
    
    # Fundamentals data completeness
    fundamentals_fields = [
        fundamentals.trailing_pe, fundamentals.price_to_book, fundamentals.roe,
        fundamentals.roa, fundamentals.debt_to_equity, fundamentals.free_cash_flow,
        fundamentals.revenue, fundamentals.operating_margin, fundamentals.sector,
        fundamentals.name
    ]
    fundamentals_completeness = sum(1 for field in fundamentals_fields if field is not None) / len(fundamentals_fields) * 100
    
    overall_completeness = (quote_completeness + fundamentals_completeness) / 2
    
    print(f"{'Quote Data Completeness':<30} {quote_completeness:.0f}%")
    print(f"{'Fundamentals Data Completeness':<30} {fundamentals_completeness:.0f}%")
    print(f"{'Overall Data Completeness':<30} {overall_completeness:.0f}%")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Yahoo Finance Data Viewer - View raw yfinance data from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yfinance_cli_viewer.py AAPL
  python yfinance_cli_viewer.py MSFT --quote-only
  python yfinance_cli_viewer.py GOOGL --fundamentals-only
        """
    )
    
    parser.add_argument(
        "ticker",
        help="Stock ticker symbol to analyze"
    )
    
    parser.add_argument(
        "--quote-only",
        action="store_true",
        help="Show only quote data"
    )
    
    parser.add_argument(
        "--fundamentals-only",
        action="store_true",
        help="Show only fundamentals data"
    )
    
    parser.add_argument(
        "--no-quality",
        action="store_true",
        help="Don't show data quality indicators"
    )
    
    args = parser.parse_args()
    
    ticker = args.ticker.upper().strip()
    
    try:
        # Create Yahoo Finance source
        source = yf_source.YahooFinanceSource()
        
        print(f"Fetching data for {ticker} from Yahoo Finance...")
        
        # Get data
        quote = source.get_quote(ticker)
        fundamentals = source.get_fundamentals(ticker)
        
        print(f"Data fetched successfully for {ticker}")
        
        # Display data based on options
        if args.quote_only:
            print_quote_data(quote)
        elif args.fundamentals_only:
            print_fundamentals_data(fundamentals)
        else:
            print_quote_data(quote)
            print_fundamentals_data(fundamentals)
        
        if not args.no_quality:
            print_data_quality(quote, fundamentals)
        
        print(f"\n{'='*60}")
        print("Data source: Yahoo Finance")
        print(f"{'='*60}\n")
        
        return 0
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}", file=sys.stderr)
        print("Please check that the ticker symbol is valid and try again.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
