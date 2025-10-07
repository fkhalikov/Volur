"""Finnhub Tab for Volur Dashboard."""

import streamlit as st
from typing import Dict, Any, Optional
from dashboard_utils import format_currency, format_number, format_percentage


def display_finnhub_data(data: Dict[str, Any]):
    """Display comprehensive Finnhub data with logo."""
    st.subheader("📊 Finnhub Market Data")
    
    # Company Logo and Basic Info
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        if data.get('logo'):
            st.image(data['logo'], width=100, caption=data.get('longName', 'Company Logo'))
        else:
            st.write("📊")
    with col2:
        st.metric("Company", data.get('longName', 'N/A'))
        st.metric("Ticker", data.get('ticker', 'N/A'))
    with col3:
        st.metric("Exchange", data.get('exchange', 'N/A'))
        st.metric("Country", data.get('country', 'N/A'))
    
    # Price Data
    st.subheader("💰 Price Information")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", format_currency(data.get('regularMarketPrice')))
    with col2:
        st.metric("Previous Close", format_currency(data.get('regularMarketPreviousClose')))
    with col3:
        st.metric("Day High", format_currency(data.get('regularMarketDayHigh')))
    with col4:
        st.metric("Day Low", format_currency(data.get('regularMarketDayLow')))
    
    # Additional Price Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Open", format_currency(data.get('open')))
    with col2:
        st.metric("Change", format_currency(data.get('change')))
    with col3:
        st.metric("Change %", format_percentage(data.get('change_percent')))
    with col4:
        st.metric("Volume", format_number(data.get('regularMarketVolume')))
    
    # Market Data
    st.subheader("📈 Market Information")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Market Cap", format_currency(data.get('marketCap')))
    with col2:
        st.metric("Shares Outstanding", format_number(data.get('sharesOutstanding')))
    with col3:
        st.metric("Currency", data.get('currency', 'N/A'))
    with col4:
        st.metric("IPO Date", data.get('ipo', 'N/A'))
    
    # Company Details
    st.subheader("🏢 Company Details")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sector", data.get('sector', 'N/A'))
    with col2:
        st.metric("Industry", data.get('industry', 'N/A'))
    with col3:
        st.metric("Phone", data.get('phone', 'N/A'))
    with col4:
        if data.get('weburl'):
            st.markdown(f"[Website]({data['weburl']})")
        else:
            st.metric("Website", "N/A")


def render_finnhub_tab(ticker: str):
    """Render the Finnhub tab."""
    st.header(f"📊 Finnhub Data for {ticker}")
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Finnhub", key="refresh_finnhub"):
            from dashboard_utils import get_cached_finnhub_data
            finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
            st.success("Finnhub data refreshed!")
            st.rerun()
    
    # Fetch data for this tab
    from dashboard_utils import get_cached_finnhub_data
    finnhub_data = get_cached_finnhub_data(ticker)
    
    # Display cache status
    from dashboard_utils import get_cache_info
    cache_info = get_cache_info("finnhub", ticker, "quote_data")
    if cache_info:
        st.success(f"📅 Data cached at: {cache_info['cached_at'].strftime('%Y-%m-%d %H:%M:%S')} (Expires: {cache_info['expires_at'].strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        st.info("ℹ️ Data not cached - fetched fresh from API")
    
    if finnhub_data:
        display_finnhub_data(finnhub_data)
        
        # Raw data
        with st.expander("🔍 Raw Finnhub Data"):
            st.json(finnhub_data)
    else:
        st.error("Could not retrieve Finnhub data. Please check the ticker symbol and API key configuration.")
