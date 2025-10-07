"""Alpha Vantage Tab for Volur Dashboard."""

import streamlit as st
from typing import Dict, Any, Optional
from dashboard_utils import format_currency, format_number, format_percentage, get_cache_info, get_cached_alpha_vantage_data
from tabs.base_tab import TickerDrivenTab

# Global tab instance
alpha_vantage_tab = TickerDrivenTab("Alpha Vantage")

def render_alpha_vantage_tab(ticker: str):
    """Render the Alpha Vantage tab - event-driven."""
    # Subscribe to ticker change events
    alpha_vantage_tab.subscribe_to_events()
    
    # Update current ticker
    alpha_vantage_tab.current_ticker = ticker
    
    st.header(f"📈 Alpha Vantage Data for {ticker}")
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Alpha Vantage", key="refresh_alpha_vantage"):
            # Force refresh data
            market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
            st.success("Alpha Vantage data refreshed!")
            st.rerun()
    
    # Fetch data for this tab (event-driven)
    market_data = get_cached_alpha_vantage_data(ticker)
    
    # Display cache status
    cache_info = get_cache_info("alpha_vantage", ticker, "quote_data")
    if cache_info:
        st.success(f"📅 Data cached at: {cache_info['cached_at'].strftime('%Y-%m-%d %H:%M:%S')} (Expires: {cache_info['expires_at'].strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        st.info("ℹ️ Data not cached - fetched fresh from API")
    
    if market_data:
        # Price Information
        st.subheader("💰 Price Information")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", format_currency(market_data.get('regularMarketPrice')))
        with col2:
            st.metric("Previous Close", format_currency(market_data.get('regularMarketPreviousClose')))
        with col3:
            st.metric("Day High", format_currency(market_data.get('regularMarketDayHigh')))
        with col4:
            st.metric("Day Low", format_currency(market_data.get('regularMarketDayLow')))
        
        # Additional Metrics
        st.subheader("📊 Market Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Open", format_currency(market_data.get('open')))
        with col2:
            st.metric("Change", format_currency(market_data.get('change')))
        with col3:
            st.metric("Change %", format_percentage(market_data.get('change_percent')))
        with col4:
            st.metric("Volume", format_number(market_data.get('regularMarketVolume')))
        
        # Raw data
        with st.expander("🔍 Raw Alpha Vantage Data"):
            st.json(market_data)
    else:
        st.error("Could not retrieve Alpha Vantage data. Please check the ticker symbol and API key configuration.")
