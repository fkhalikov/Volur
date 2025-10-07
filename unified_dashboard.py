"""Volur - Financial Dashboard with multiple data sources."""

import streamlit as st
import logging
import traceback
from volur.config import settings
from volur.plugins.sec_source import SECSource
from dashboard_utils import (
    get_cached_alpha_vantage_data, get_cached_finnhub_data, get_cached_sec_data,
    get_cached_finnhub_news, get_cached_finnhub_financials, get_cached_finnhub_basic_financials,
    get_cached_alpha_vantage_listing_status, get_cache_info, clear_cache_for_ticker, get_cache_stats
)
from event_system import publish_ticker_changed, EventTypes, get_event_bus
from tabs.alpha_vantage_tab import render_alpha_vantage_tab
from tabs.sec_edgar_tab import render_sec_edgar_tab
from tabs.finnhub_tab import render_finnhub_tab
from tabs.finnhub_news_tab import render_finnhub_news_tab
from tabs.finnhub_financials_tab import render_finnhub_financials_tab
from tabs.finnhub_basic_financials_tab import render_finnhub_basic_financials_tab
from tabs.securities_listing_tab import render_securities_listing_tab
from tabs.comparison_tab import render_comparison_tab
from tabs.debug_logs_tab import render_debug_logs_tab
from tabs.all_sources_tab import render_all_sources_tab

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('volur_dashboard.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="Volur - Financial Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Volur - Financial Dashboard")
    
    
    # Initialize ticker management with event-driven architecture
    if 'current_ticker' not in st.session_state:
        st.session_state.current_ticker = "AAPL"
    
    # Check if a ticker was selected from the securities listing
    if 'selected_ticker_from_listing' in st.session_state and st.session_state.selected_ticker_from_listing:
        new_ticker = st.session_state.selected_ticker_from_listing
        # Clear the selection after using it
        del st.session_state.selected_ticker_from_listing
        
        # Update current ticker and fire event
        st.session_state.current_ticker = new_ticker
        publish_ticker_changed(new_ticker, "securities_listing")
        
        # Force the ticker input widget to update by using a dynamic key
        widget_key = f"ticker_input_widget_{new_ticker}_{st.session_state.get('widget_counter', 0)}"
        st.session_state.widget_counter = st.session_state.get('widget_counter', 0) + 1
    else:
        widget_key = "ticker_input_widget"
    
    # Ticker input - event-driven
    ticker = st.sidebar.text_input(
        "Stock Ticker",
        value=st.session_state.current_ticker,
        help="Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)",
        key=widget_key
    ).upper().strip()
    
    # Check if ticker changed and fire event
    if ticker != st.session_state.current_ticker:
        st.session_state.current_ticker = ticker
        publish_ticker_changed(ticker, "user_input")
    
    # Create tabs for different data sources
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📋 Securities Listing",
        "🔄 All Sources", 
        "📈 Alpha Vantage", 
        "🏛️ SEC EDGAR",
        "📊 Finnhub",
        "📰 Finnhub News",
        "📊 Finnhub Financials",
        "📊 Finnhub Basic Financials",
        "📊 Comparison", 
        "🐛 Debug Logs"
    ])
    
    # Initialize session state for data if not exists
    if 'market_data' not in st.session_state:
        st.session_state.market_data = None
    if 'finnhub_data' not in st.session_state:
        st.session_state.finnhub_data = None
    if 'finnhub_news' not in st.session_state:
        st.session_state.finnhub_news = []
    if 'finnhub_financials' not in st.session_state:
        st.session_state.finnhub_financials = {}
    if 'finnhub_basic_financials' not in st.session_state:
        st.session_state.finnhub_basic_financials = {}
    if 'sec_fundamentals' not in st.session_state:
        st.session_state.sec_fundamentals = None
    if 'securities_listing' not in st.session_state:
        # Prefetch securities listing data since it's always available
        logger.info("Prefetching securities listing data on startup...")
        try:
            securities_listing = get_cached_alpha_vantage_listing_status()
            if securities_listing:
                logger.info(f"[SUCCESS] Securities listing prefetch successful - {securities_listing.get('total_count', 0)} securities")
                st.session_state.securities_listing = securities_listing
            else:
                logger.warning("[WARNING] Securities listing prefetch returned empty result")
                st.session_state.securities_listing = None
        except Exception as e:
            logger.error(f"❌ Securities listing prefetch error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.session_state.securities_listing = None
    
    
    # Main content area
    st.markdown("### Compare financial data from multiple sources:")
    st.markdown("""
    - **Alpha Vantage:** Real-time market data
    - **Finnhub:** Market data with company profiles and news  
    - **SEC EDGAR:** Official financial filings
    """)
    
    # Cache management section
    with st.expander("🗄️ Cache Management"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh All", key="refresh_all"):
                # Clear all caches and force refresh
                total_cleared = 0
                total_cleared += clear_cache_for_source("alpha_vantage")
                total_cleared += clear_cache_for_source("finnhub")
                total_cleared += clear_cache_for_source("sec")
                st.success(f"Cleared {total_cleared} total cache entries")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Alpha Vantage Cache", key="clear_alpha"):
                cleared = clear_cache_for_source("alpha_vantage")
                st.success(f"Cleared {cleared} Alpha Vantage cache entries")
                st.rerun()
        
        with col3:
            if st.button("🗑️ Clear Finnhub Cache", key="clear_finnhub"):
                cleared = clear_cache_for_source("finnhub")
                st.success(f"Cleared {cleared} Finnhub cache entries")
                st.rerun()
        
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.button("🗑️ Clear SEC Cache", key="clear_sec"):
                cleared = clear_cache_for_source("sec")
                st.success(f"Cleared {cleared} SEC cache entries")
                st.rerun()
        
        with col5:
            if st.button("🗑️ Clear All Cache", key="clear_all"):
                total_cleared = 0
                total_cleared += clear_cache_for_source("alpha_vantage")
                total_cleared += clear_cache_for_source("finnhub")
                total_cleared += clear_cache_for_source("sec")
                st.success(f"Cleared {total_cleared} total cache entries")
                st.rerun()
        
        # Cache statistics
        with st.expander("📊 Cache Statistics"):
            stats = get_cache_stats()
            if stats:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Entries", stats.get("total_entries", 0))
                with col2:
                    st.metric("Active Entries", stats.get("active_entries", 0))
                with col3:
                    st.metric("Expired Entries", stats.get("expired_entries", 0))
                
                if stats.get("source_counts"):
                    st.markdown("**Entries by Source:**")
                    for source, count in stats["source_counts"].items():
                        st.write(f"- {source.title()}: {count}")
        
        st.divider()
        
        # Fetch Data button - let individual tabs handle their own data fetching
        if st.sidebar.button("Fetch Data", type="primary", key="fetch_data_main") and ticker:
            st.success(f"Fetching data for {ticker}... Each tab will load its own data.")
            st.rerun()
        
        # Render all tabs - event-driven architecture
        with tab1:
            # Generic dataset tab - independent of ticker
            render_securities_listing_tab(st.session_state.securities_listing)
        
        with tab2:
            # Ticker-driven tab - subscribes to ticker events
            render_all_sources_tab(st.session_state.current_ticker)
        
        with tab3:
            # Ticker-driven tab - subscribes to ticker events
            render_alpha_vantage_tab(st.session_state.current_ticker)
        
        with tab4:
            # Ticker-driven tab - subscribes to ticker events
            render_sec_edgar_tab(st.session_state.current_ticker)
        
        with tab5:
            # Ticker-driven tab - subscribes to ticker events
            render_finnhub_tab(st.session_state.current_ticker)
        
        with tab6:
            # Ticker-driven tab - subscribes to ticker events
            render_finnhub_news_tab(st.session_state.current_ticker)
        
        with tab7:
            # Ticker-driven tab - subscribes to ticker events
            render_finnhub_financials_tab(st.session_state.current_ticker)
        
        with tab8:
            # Ticker-driven tab - subscribes to ticker events
            render_finnhub_basic_financials_tab(st.session_state.current_ticker)
        
        with tab9:
            # Ticker-driven tab - subscribes to ticker events
            render_comparison_tab(st.session_state.current_ticker)
        
        with tab10:
            # Generic tab - independent of ticker
            render_debug_logs_tab()

if __name__ == "__main__":
    main()
