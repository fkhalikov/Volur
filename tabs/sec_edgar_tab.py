"""SEC EDGAR Tab for Volur Dashboard."""

import streamlit as st
from typing import Optional
from volur.plugins.base import Fundamentals
from dashboard_utils import display_fundamentals_data


def render_sec_edgar_tab(ticker: str):
    """Render the SEC EDGAR tab."""
    st.header(f"🏛️ SEC EDGAR Data for {ticker}")
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh SEC", key="refresh_sec"):
            from dashboard_utils import get_cached_sec_data
            sec_data = get_cached_sec_data(ticker, force_refresh=True)
            st.success("SEC data refreshed!")
            st.rerun()
    
    # Fetch data for this tab
    from dashboard_utils import get_cached_sec_data
    sec_data = get_cached_sec_data(ticker)
    
    # Convert SEC data to Fundamentals object if available
    sec_fundamentals = None
    if sec_data:
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
    
    # Display cache status
    from dashboard_utils import get_cache_info
    cache_info = get_cache_info("sec", ticker, "fundamentals")
    if cache_info:
        st.success(f"📅 Data cached at: {cache_info['cached_at'].strftime('%Y-%m-%d %H:%M:%S')} (Expires: {cache_info['expires_at'].strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        st.info("ℹ️ Data not cached - fetched fresh from API")
    
    if sec_fundamentals:
        display_fundamentals_data(sec_fundamentals, "SEC EDGAR")
        
        # Raw data
        with st.expander("🔍 Raw SEC EDGAR Data"):
            st.json(sec_fundamentals.__dict__)
    else:
        st.error("Could not retrieve SEC EDGAR data. Please check the ticker symbol.")
