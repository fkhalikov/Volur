"""SEC EDGAR Tab for Volur Dashboard."""

import streamlit as st
from typing import Optional
from volur.plugins.base import Fundamentals
from dashboard_utils import display_fundamentals_data


def render_sec_edgar_tab(ticker: str, sec_fundamentals: Optional[Fundamentals]):
    """Render the SEC EDGAR tab."""
    st.header(f"🏛️ SEC EDGAR Data for {ticker}")
    
    if sec_fundamentals:
        display_fundamentals_data(sec_fundamentals, "SEC EDGAR")
        
        # Raw data
        with st.expander("🔍 Raw SEC EDGAR Data"):
            st.json(sec_fundamentals.__dict__)
    else:
        st.error("Could not retrieve SEC EDGAR data. Please check the ticker symbol.")
