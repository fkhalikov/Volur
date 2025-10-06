"""Advanced Yahoo Finance Data Viewer - Shows comprehensive yfinance data."""

import streamlit as st
import pandas as pd
import yfinance as yf
from typing import Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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


def display_stock_info(ticker_obj):
    """Display comprehensive stock information."""
    st.subheader("📈 Stock Information")
    
    info = ticker_obj.info
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Price", format_currency(info.get('currentPrice')))
        st.metric("Previous Close", format_currency(info.get('previousClose')))
        st.metric("Open", format_currency(info.get('open')))
        st.metric("Day High", format_currency(info.get('dayHigh')))
        st.metric("Day Low", format_currency(info.get('dayLow')))
    
    with col2:
        st.metric("52 Week High", format_currency(info.get('fiftyTwoWeekHigh')))
        st.metric("52 Week Low", format_currency(info.get('fiftyTwoWeekLow')))
        st.metric("Volume", format_large_number(info.get('volume')))
        st.metric("Avg Volume", format_large_number(info.get('averageVolume')))
        st.metric("Market Cap", format_large_number(info.get('marketCap')))
    
    with col3:
        st.metric("P/E Ratio", format_number(info.get('trailingPE')))
        st.metric("Forward P/E", format_number(info.get('forwardPE')))
        st.metric("P/B Ratio", format_number(info.get('priceToBook')))
        st.metric("PEG Ratio", format_number(info.get('pegRatio')))
        st.metric("EPS", format_currency(info.get('trailingEps')))
    
    with col4:
        st.metric("Dividend Yield", format_percentage(info.get('dividendYield')))
        st.metric("Beta", format_number(info.get('beta')))
        st.metric("ROE", format_percentage(info.get('returnOnEquity')))
        st.metric("ROA", format_percentage(info.get('returnOnAssets')))
        st.metric("Debt-to-Equity", format_number(info.get('debtToEquity')))


def display_company_info(ticker_obj):
    """Display company information."""
    st.subheader("🏢 Company Information")
    
    info = ticker_obj.info
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Company Name:** {info.get('longName', 'N/A')}")
        st.write(f"**Short Name:** {info.get('shortName', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Exchange:** {info.get('exchange', 'N/A')}")
        st.write(f"**Currency:** {info.get('currency', 'N/A')}")
    
    with col2:
        st.write(f"**Country:** {info.get('country', 'N/A')}")
        st.write(f"**Website:** {info.get('website', 'N/A')}")
        st.write(f"**Employees:** {info.get('fullTimeEmployees', 'N/A')}")
        st.write(f"**Business Summary:**")
        st.write(info.get('longBusinessSummary', 'N/A')[:500] + "..." if info.get('longBusinessSummary') else 'N/A')


def display_price_chart(ticker_obj, period="1y"):
    """Display price chart."""
    st.subheader("📊 Price Chart")
    
    # Get historical data
    hist = ticker_obj.history(period=period)
    
    if not hist.empty:
        # Create candlestick chart
        fig = go.Figure(data=go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name="Price"
        ))
        
        fig.update_layout(
            title=f"{ticker_obj.ticker} Price Chart ({period})",
            xaxis_title="Date",
            yaxis_title="Price",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        fig_volume = go.Figure(data=go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name="Volume"
        ))
        
        fig_volume.update_layout(
            title=f"{ticker_obj.ticker} Volume Chart ({period})",
            xaxis_title="Date",
            yaxis_title="Volume",
            height=300
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
    else:
        st.warning("No historical data available for the selected period.")


def display_financial_statements(ticker_obj):
    """Display financial statements."""
    st.subheader("💰 Financial Statements")
    
    # Income statement
    try:
        income_stmt = ticker_obj.financials
        if not income_stmt.empty:
            st.write("**Income Statement (Annual)**")
            st.dataframe(income_stmt.head(10), use_container_width=True)
        else:
            st.warning("No income statement data available.")
    except Exception as e:
        st.warning(f"Could not load income statement: {str(e)}")
    
    # Balance sheet
    try:
        balance_sheet = ticker_obj.balance_sheet
        if not balance_sheet.empty:
            st.write("**Balance Sheet (Annual)**")
            st.dataframe(balance_sheet.head(10), use_container_width=True)
        else:
            st.warning("No balance sheet data available.")
    except Exception as e:
        st.warning(f"Could not load balance sheet: {str(e)}")
    
    # Cash flow statement
    try:
        cash_flow = ticker_obj.cashflow
        if not cash_flow.empty:
            st.write("**Cash Flow Statement (Annual)**")
            st.dataframe(cash_flow.head(10), use_container_width=True)
        else:
            st.warning("No cash flow statement data available.")
    except Exception as e:
        st.warning(f"Could not load cash flow statement: {str(e)}")


def display_recommendations(ticker_obj):
    """Display analyst recommendations."""
    st.subheader("🎯 Analyst Recommendations")
    
    try:
        recommendations = ticker_obj.recommendations
        if not recommendations.empty:
            st.dataframe(recommendations.tail(10), use_container_width=True)
        else:
            st.warning("No analyst recommendations available.")
    except Exception as e:
        st.warning(f"Could not load recommendations: {str(e)}")


def main():
    """Main Streamlit application for advanced Yahoo Finance data viewer."""
    st.set_page_config(
        page_title="Advanced Yahoo Finance Data Viewer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Advanced Yahoo Finance Data Viewer")
    st.markdown("Comprehensive view of Yahoo Finance data including charts, financial statements, and more.")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    ticker = st.sidebar.text_input(
        "Enter Stock Ticker",
        value="AAPL",
        help="Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
    ).upper().strip()
    
    period = st.sidebar.selectbox(
        "Chart Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        index=5,  # Default to 1y
        help="Select the time period for price charts"
    )
    
    # Display options
    st.sidebar.subheader("Display Options")
    show_info = st.sidebar.checkbox("Show Stock Info", value=True)
    show_company = st.sidebar.checkbox("Show Company Info", value=True)
    show_charts = st.sidebar.checkbox("Show Price Charts", value=True)
    show_financials = st.sidebar.checkbox("Show Financial Statements", value=False)
    show_recommendations = st.sidebar.checkbox("Show Analyst Recommendations", value=False)
    
    if ticker:
        # Fetch button
        if st.sidebar.button("Fetch Data", type="primary"):
            try:
                # Create ticker object
                ticker_obj = yf.Ticker(ticker)
                
                # Show loading spinner
                with st.spinner(f"Fetching comprehensive data for {ticker} from Yahoo Finance..."):
                    # Test if ticker exists by getting info
                    info = ticker_obj.info
                    if not info:
                        st.error(f"No data found for ticker: {ticker}")
                        return
                
                st.success(f"Data fetched successfully for {ticker}")
                
                if show_info:
                    display_stock_info(ticker_obj)
                    st.markdown("---")
                
                if show_company:
                    display_company_info(ticker_obj)
                    st.markdown("---")
                
                if show_charts:
                    display_price_chart(ticker_obj, period)
                    st.markdown("---")
                
                if show_financials:
                    display_financial_statements(ticker_obj)
                    st.markdown("---")
                
                if show_recommendations:
                    display_recommendations(ticker_obj)
                
            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {str(e)}")
                st.info("Please check that the ticker symbol is valid and try again.")
    
    # Instructions
    st.markdown("---")
    st.subheader("📖 Instructions")
    st.markdown("""
    1. **Enter a ticker symbol** in the sidebar (e.g., AAPL, MSFT, GOOGL)
    2. **Select chart period** for price charts
    3. **Choose display options** to show/hide different data sections
    4. **Click "Fetch Data"** to retrieve comprehensive data from Yahoo Finance
    
    **Features:**
    - Real-time stock information and metrics
    - Company information and business summary
    - Interactive price and volume charts
    - Financial statements (Income, Balance Sheet, Cash Flow)
    - Analyst recommendations
    
    **Note**: This tool fetches comprehensive data from Yahoo Finance. Some data may be missing 
    for certain tickers or may take a moment to load.
    """)


if __name__ == "__main__":
    main()
