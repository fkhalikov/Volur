"""Alpha Vantage Tab for Volur Dashboard."""

import streamlit as st
from typing import Dict, Any, Optional
from dashboard_utils import format_currency, format_number, format_percentage


def render_alpha_vantage_tab(ticker: str, market_data: Optional[Dict[str, Any]]):
    """Render the Alpha Vantage tab."""
    st.header(f"📈 Alpha Vantage Data for {ticker}")
    
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
