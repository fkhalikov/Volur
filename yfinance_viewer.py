"""Yahoo Finance Data Viewer - Simple UI to view raw yfinance data."""

import streamlit as st
import pandas as pd
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


def display_quote_data(quote: Quote):
    """Display quote data in a formatted layout."""
    st.subheader("📈 Quote Data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ticker", quote.ticker)
        st.metric("Price", format_currency(quote.price))
    
    with col2:
        st.metric("Currency", quote.currency or "N/A")
        st.metric("Shares Outstanding", format_large_number(quote.shares_outstanding))
    
    with col3:
        if quote.price and quote.shares_outstanding:
            market_cap = quote.price * quote.shares_outstanding
            st.metric("Market Cap", format_large_number(market_cap))
        else:
            st.metric("Market Cap", "N/A")
    
    with col4:
        st.metric("Data Source", "Yahoo Finance")


def display_fundamentals_data(fundamentals: Fundamentals):
    """Display fundamentals data in a formatted layout."""
    st.subheader("📊 Fundamentals Data")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("P/E Ratio", format_number(fundamentals.trailing_pe))
        st.metric("P/B Ratio", format_number(fundamentals.price_to_book))
    
    with col2:
        st.metric("ROE", format_percentage(fundamentals.roe))
        st.metric("ROA", format_percentage(fundamentals.roa))
    
    with col3:
        st.metric("Debt-to-Equity", format_number(fundamentals.debt_to_equity))
        st.metric("Operating Margin", format_percentage(fundamentals.operating_margin))
    
    with col4:
        st.metric("Free Cash Flow", format_large_number(fundamentals.free_cash_flow))
        st.metric("Revenue", format_large_number(fundamentals.revenue))
    
    # Company info
    st.subheader("🏢 Company Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Company Name", fundamentals.name or "N/A")
    
    with col2:
        st.metric("Sector", fundamentals.sector or "N/A")


def display_raw_data_table(quote: Quote, fundamentals: Fundamentals):
    """Display raw data in a table format."""
    st.subheader("📋 Raw Data Table")
    
    # Quote data table
    st.write("**Quote Data:**")
    quote_data = {
        "Field": ["Ticker", "Price", "Currency", "Shares Outstanding"],
        "Value": [
            quote.ticker,
            format_currency(quote.price),
            quote.currency or "N/A",
            format_large_number(quote.shares_outstanding)
        ]
    }
    quote_df = pd.DataFrame(quote_data)
    st.dataframe(quote_df, use_container_width=True, hide_index=True)
    
    # Fundamentals data table
    st.write("**Fundamentals Data:**")
    fundamentals_data = {
        "Field": [
            "Ticker", "P/E Ratio", "P/B Ratio", "ROE", "ROA", 
            "Debt-to-Equity", "Free Cash Flow", "Revenue", 
            "Operating Margin", "Sector", "Company Name"
        ],
        "Value": [
            fundamentals.ticker,
            format_number(fundamentals.trailing_pe),
            format_number(fundamentals.price_to_book),
            format_percentage(fundamentals.roe),
            format_percentage(fundamentals.roa),
            format_number(fundamentals.debt_to_equity),
            format_large_number(fundamentals.free_cash_flow),
            format_large_number(fundamentals.revenue),
            format_percentage(fundamentals.operating_margin),
            fundamentals.sector or "N/A",
            fundamentals.name or "N/A"
        ]
    }
    fundamentals_df = pd.DataFrame(fundamentals_data)
    st.dataframe(fundamentals_df, use_container_width=True, hide_index=True)


def main():
    """Main Streamlit application for Yahoo Finance data viewer."""
    st.set_page_config(
        page_title="Yahoo Finance Data Viewer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Yahoo Finance Data Viewer")
    st.markdown("View raw data from Yahoo Finance for any stock ticker.")
    
    # Sidebar for ticker input
    st.sidebar.header("Configuration")
    
    ticker = st.sidebar.text_input(
        "Enter Stock Ticker",
        value="AAPL",
        help="Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
    ).upper().strip()
    
    # Display options
    st.sidebar.subheader("Display Options")
    show_metrics = st.sidebar.checkbox("Show Metrics Cards", value=True)
    show_table = st.sidebar.checkbox("Show Raw Data Table", value=True)
    
    if ticker:
        # Analyze button
        if st.sidebar.button("Fetch Data", type="primary"):
            try:
                # Create Yahoo Finance source
                source = yf_source.YahooFinanceSource()
                
                # Show loading spinner
                with st.spinner(f"Fetching data for {ticker} from Yahoo Finance..."):
                    quote = source.get_quote(ticker)
                    fundamentals = source.get_fundamentals(ticker)
                
                # Display results
                st.success(f"Data fetched successfully for {ticker}")
                
                if show_metrics:
                    display_quote_data(quote)
                    st.markdown("---")
                    display_fundamentals_data(fundamentals)
                
                if show_table:
                    st.markdown("---")
                    display_raw_data_table(quote, fundamentals)
                
                # Data quality indicators
                st.subheader("🔍 Data Quality")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    quote_completeness = sum([
                        quote.price is not None,
                        quote.currency is not None,
                        quote.shares_outstanding is not None
                    ]) / 3 * 100
                    st.metric("Quote Data Completeness", f"{quote_completeness:.0f}%")
                
                with col2:
                    fundamentals_completeness = sum([
                        fundamentals.trailing_pe is not None,
                        fundamentals.price_to_book is not None,
                        fundamentals.roe is not None,
                        fundamentals.roa is not None,
                        fundamentals.debt_to_equity is not None,
                        fundamentals.free_cash_flow is not None,
                        fundamentals.revenue is not None,
                        fundamentals.operating_margin is not None,
                        fundamentals.sector is not None,
                        fundamentals.name is not None
                    ]) / 10 * 100
                    st.metric("Fundamentals Data Completeness", f"{fundamentals_completeness:.0f}%")
                
                with col3:
                    overall_completeness = (quote_completeness + fundamentals_completeness) / 2
                    st.metric("Overall Data Completeness", f"{overall_completeness:.0f}%")
                
            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {str(e)}")
                st.info("Please check that the ticker symbol is valid and try again.")
    
    # Instructions
    st.markdown("---")
    st.subheader("📖 Instructions")
    st.markdown("""
    1. **Enter a ticker symbol** in the sidebar (e.g., AAPL, MSFT, GOOGL)
    2. **Click "Fetch Data"** to retrieve data from Yahoo Finance
    3. **View the data** in metrics cards and/or raw data table
    4. **Check data quality** indicators to see completeness
    
    **Note**: This tool fetches real-time data from Yahoo Finance. Some data may be missing 
    for certain tickers or may take a moment to load.
    """)


if __name__ == "__main__":
    main()
