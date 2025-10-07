"""All Sources Overview Tab for Volur Dashboard."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from dashboard_utils import (
    format_currency, format_number, format_percentage,
    get_cached_alpha_vantage_data, get_cached_finnhub_data, get_cached_sec_data,
    get_cache_info
)


def render_all_sources_tab(ticker: str):
    """Render the All Sources Overview tab."""
    st.header(f"🔄 All Sources Overview for {ticker}")
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh All Sources", key="refresh_all_sources"):
            # Force refresh all sources
            market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
            finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
            sec_data = get_cached_sec_data(ticker, force_refresh=True)
            st.success("All sources refreshed!")
            st.rerun()
    
    # Fetch data for this tab
    market_data = get_cached_alpha_vantage_data(ticker)
    finnhub_data = get_cached_finnhub_data(ticker)
    sec_data = get_cached_sec_data(ticker)
    
    # Convert SEC data to Fundamentals object if available
    sec_fundamentals = None
    if sec_data:
        from volur.plugins.base import Fundamentals
        sec_fundamentals = Fundamentals(
            ticker=sec_data.get("ticker", ticker),
            trailing_pe=sec_data.get("trailing_pe"),
            price_to_book=sec_data.get("price_to_book"),
            roe=sec_data.get("roe"),
            roa=sec_data.get("roa"),
            debt_to_equity=sec_data.get("debt_to_equity"),
            free_cash_flow=sec_data.get("free_cash_flow"),
            revenue=sec_data.get("revenue"),
            operating_margin=sec_data.get("operating_margin"),
            sector=sec_data.get("sector"),
            name=sec_data.get("name")
        )
    
    # Data source status
    st.subheader("📊 Data Source Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if market_data:
            st.success("✅ Alpha Vantage: Connected")
            st.metric("Price", format_currency(market_data.get('regularMarketPrice')))
        else:
            st.error("❌ Alpha Vantage: Not Available")
    
    with col2:
        if finnhub_data:
            st.success("✅ Finnhub: Connected")
            st.metric("Price", format_currency(finnhub_data.get('regularMarketPrice')))
        else:
            st.error("❌ Finnhub: Not Available")
    
    with col3:
        if sec_fundamentals:
            st.success("✅ SEC EDGAR: Connected")
            st.metric("Revenue", format_currency(sec_fundamentals.revenue))
        else:
            st.error("❌ SEC EDGAR: Not Available")
    
    # Quick comparison table
    if market_data or finnhub_data or sec_fundamentals:
        st.subheader("📈 Quick Comparison")
        
        comparison_data = []
        
        # Alpha Vantage row
        if market_data:
            comparison_data.append({
                "Source": "Alpha Vantage",
                "Price": format_currency(market_data.get('regularMarketPrice')),
                "Volume": format_number(market_data.get('regularMarketVolume')),
                "Change": format_percentage(market_data.get('change_percent')),
                "Market Cap": "N/A",
                "PE Ratio": "N/A"
            })
        
        # Finnhub row
        if finnhub_data:
            comparison_data.append({
                "Source": "Finnhub",
                "Price": format_currency(finnhub_data.get('regularMarketPrice')),
                "Volume": format_number(finnhub_data.get('regularMarketVolume')),
                "Change": format_percentage(finnhub_data.get('change_percent')),
                "Market Cap": format_currency(finnhub_data.get('marketCap')),
                "PE Ratio": "N/A"
            })
        
        # SEC EDGAR row
        if sec_fundamentals:
            comparison_data.append({
                "Source": "SEC EDGAR",
                "Price": "N/A",
                "Volume": "N/A",
                "Change": "N/A",
                "Market Cap": "N/A",
                "PE Ratio": f"{sec_fundamentals.trailing_pe:.2f}" if sec_fundamentals.trailing_pe else "N/A"
            })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, width='stretch')
    
    # Data source advantages
    st.subheader("ℹ️ Data Source Advantages")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **Alpha Vantage**
        - Real-time market data
        - Global stock coverage
        - Technical indicators
        - Economic indicators
        """)
    
    with col2:
        st.info("""
        **Finnhub**
        - Real-time market data
        - Company profiles & logos
        - News & sentiment
        - Financial statements
        """)
    
    with col3:
        st.info("""
        **SEC EDGAR**
        - Official filings
        - Regulatory compliance
        - Historical data
        - Fundamental metrics
        """)
