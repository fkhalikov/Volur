"""Simple Yahoo Finance Data Viewer - Direct API approach without yfinance dependency."""

import streamlit as st
import pandas as pd
import requests
import json
from typing import Optional, Dict, Any


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


def fetch_yahoo_finance_data(ticker: str) -> Dict[str, Any]:
    """Fetch data from Yahoo Finance using direct API calls."""
    try:
        # Yahoo Finance API endpoint
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            return {
                'ticker': ticker.upper(),
                'price': meta.get('regularMarketPrice'),
                'currency': meta.get('currency'),
                'shares_outstanding': meta.get('sharesOutstanding'),
                'market_cap': meta.get('marketCap'),
                'pe_ratio': meta.get('trailingPE'),
                'pb_ratio': meta.get('priceToBook'),
                'dividend_yield': meta.get('dividendYield'),
                'beta': meta.get('beta'),
                'volume': meta.get('regularMarketVolume'),
                'avg_volume': meta.get('averageVolume'),
                'day_high': meta.get('regularMarketDayHigh'),
                'day_low': meta.get('regularMarketDayLow'),
                'previous_close': meta.get('previousClose'),
                'fifty_two_week_high': meta.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': meta.get('fiftyTwoWeekLow'),
                'company_name': meta.get('longName'),
                'exchange': meta.get('exchangeName'),
                'sector': meta.get('sector'),
                'industry': meta.get('industry')
            }
        else:
            return {'error': 'No data found for ticker'}
            
    except Exception as e:
        return {'error': str(e)}


def display_stock_data(data: Dict[str, Any]):
    """Display stock data in a formatted layout."""
    if 'error' in data:
        st.error(f"Error: {data['error']}")
        return
    
    st.subheader(f"📈 {data['ticker']} - {data.get('company_name', 'N/A')}")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Price", format_currency(data.get('price')))
        st.metric("Previous Close", format_currency(data.get('previous_close')))
        st.metric("Day High", format_currency(data.get('day_high')))
        st.metric("Day Low", format_currency(data.get('day_low')))
    
    with col2:
        st.metric("52 Week High", format_currency(data.get('fifty_two_week_high')))
        st.metric("52 Week Low", format_currency(data.get('fifty_two_week_low')))
        st.metric("Volume", format_large_number(data.get('volume')))
        st.metric("Avg Volume", format_large_number(data.get('avg_volume')))
    
    with col3:
        st.metric("Market Cap", format_large_number(data.get('market_cap')))
        st.metric("P/E Ratio", format_number(data.get('pe_ratio')))
        st.metric("P/B Ratio", format_number(data.get('pb_ratio')))
        st.metric("Beta", format_number(data.get('beta')))
    
    with col4:
        st.metric("Dividend Yield", format_percentage(data.get('dividend_yield')))
        st.metric("Currency", data.get('currency', 'N/A'))
        st.metric("Exchange", data.get('exchange', 'N/A'))
        st.metric("Shares Outstanding", format_large_number(data.get('shares_outstanding')))


def display_company_info(data: Dict[str, Any]):
    """Display company information."""
    st.subheader("🏢 Company Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Company Name:** {data.get('company_name', 'N/A')}")
        st.write(f"**Ticker:** {data.get('ticker', 'N/A')}")
        st.write(f"**Exchange:** {data.get('exchange', 'N/A')}")
        st.write(f"**Currency:** {data.get('currency', 'N/A')}")
    
    with col2:
        st.write(f"**Sector:** {data.get('sector', 'N/A')}")
        st.write(f"**Industry:** {data.get('industry', 'N/A')}")
        st.write(f"**Shares Outstanding:** {format_large_number(data.get('shares_outstanding'))}")


def display_raw_data_table(data: Dict[str, Any]):
    """Display raw data in a table format."""
    st.subheader("📋 Raw Data Table")
    
    # Convert to DataFrame for better display
    df_data = []
    for key, value in data.items():
        if key != 'error':
            if isinstance(value, (int, float)):
                if key in ['price', 'market_cap', 'volume', 'avg_volume', 'shares_outstanding']:
                    formatted_value = format_large_number(value)
                elif key in ['pe_ratio', 'pb_ratio', 'beta']:
                    formatted_value = format_number(value)
                elif key in ['dividend_yield']:
                    formatted_value = format_percentage(value)
                else:
                    formatted_value = format_number(value)
            else:
                formatted_value = str(value) if value is not None else 'N/A'
            
            df_data.append({
                'Field': key.replace('_', ' ').title(),
                'Value': formatted_value
            })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Simple Yahoo Finance Data Viewer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Simple Yahoo Finance Data Viewer")
    st.markdown("View real-time stock data from Yahoo Finance (no yfinance dependency required).")
    
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
    show_company = st.sidebar.checkbox("Show Company Info", value=True)
    show_table = st.sidebar.checkbox("Show Raw Data Table", value=False)
    
    if ticker:
        # Fetch button
        if st.sidebar.button("Fetch Data", type="primary"):
            try:
                # Show loading spinner
                with st.spinner(f"Fetching data for {ticker} from Yahoo Finance..."):
                    data = fetch_yahoo_finance_data(ticker)
                
                if 'error' not in data:
                    st.success(f"Data fetched successfully for {ticker}")
                    
                    if show_metrics:
                        display_stock_data(data)
                        st.markdown("---")
                    
                    if show_company:
                        display_company_info(data)
                        st.markdown("---")
                    
                    if show_table:
                        display_raw_data_table(data)
                else:
                    st.error(f"Error fetching data: {data['error']}")
                
            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {str(e)}")
                st.info("Please check that the ticker symbol is valid and try again.")
    
    # Instructions
    st.markdown("---")
    st.subheader("📖 Instructions")
    st.markdown("""
    1. **Enter a ticker symbol** in the sidebar (e.g., AAPL, MSFT, GOOGL)
    2. **Click "Fetch Data"** to retrieve real-time data from Yahoo Finance
    3. **View the data** in metrics cards, company info, and/or raw data table
    
    **Features:**
    - Real-time stock prices and metrics
    - Company information
    - Market data (volume, 52-week highs/lows)
    - Financial ratios (P/E, P/B, Beta)
    - No external dependencies required
    
    **Note**: This tool fetches data directly from Yahoo Finance API. 
    Some data may be missing for certain tickers.
    """)


if __name__ == "__main__":
    main()
