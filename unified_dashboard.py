"""Refactored Unified Dashboard for Volur - Modular Tab Structure."""

import streamlit as st
import logging
import traceback
from typing import Optional, Dict, Any

# Import tab modules
from tabs.all_sources_tab import render_all_sources_tab
from tabs.alpha_vantage_tab import render_alpha_vantage_tab
from tabs.sec_edgar_tab import render_sec_edgar_tab
from tabs.finnhub_tab import render_finnhub_tab
from tabs.finnhub_news_tab import render_finnhub_news_tab
from tabs.finnhub_financials_tab import render_finnhub_financials_tab
from tabs.finnhub_basic_financials_tab import render_finnhub_basic_financials_tab
from tabs.securities_listing_tab import render_securities_listing_tab
from tabs.comparison_tab import render_comparison_tab
from tabs.debug_logs_tab import render_debug_logs_tab

# Import utilities
from dashboard_utils import (
    get_cached_alpha_vantage_data, 
    get_cached_finnhub_data, 
    get_cached_finnhub_news,
    get_cached_finnhub_financials,
    get_cached_finnhub_basic_financials,
    get_cached_sec_data,
    get_cached_alpha_vantage_listing_status,
    get_cache_info,
    clear_cache_for_source,
    clear_cache_for_ticker,
    get_cache_stats,
    SECSource
)

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

# Page configuration
st.set_page_config(
    page_title="Volur - Unified Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main dashboard function."""
    
    # Header
    st.title("📊 Volur - Financial Dashboard")
    st.markdown("""
    **Compare financial data from multiple sources:**
    - 📈 **Alpha Vantage**: Real-time market data
    - 📊 **Finnhub**: Market data with company profiles and news
    - 🏛️ **SEC EDGAR**: Official financial filings
    """)
    
    # Sidebar
    st.sidebar.header("🔧 Configuration")
    
    # API Key Status
    st.sidebar.subheader("🔑 API Key Status")
    
    from volur.config import settings
    
    alpha_status = "✅ Configured" if settings.alpha_vantage_api_key else "❌ Missing"
    finnhub_status = "✅ Configured" if settings.finnhub_api_key else "❌ Missing"
    
    st.sidebar.write(f"**Alpha Vantage**: {alpha_status}")
    st.sidebar.write(f"**Finnhub**: {finnhub_status}")
    st.sidebar.write("**SEC EDGAR**: ✅ Free (No API key required)")
    
    # Instructions
    st.sidebar.subheader("📋 Instructions")
    st.sidebar.markdown("""
    1. Enter a stock ticker symbol
    2. Click "Fetch Data" to retrieve information
    3. Navigate between tabs to view different data sources
    4. Use the Comparison tab to analyze differences
    """)
    
    # Ticker input
    ticker = st.sidebar.text_input(
        "Stock Ticker",
        value="AAPL",
        help="Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
    ).upper().strip()
    
    # Create tabs for different data sources
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🔄 All Sources", 
        "📈 Alpha Vantage", 
        "🏛️ SEC EDGAR",
        "📊 Finnhub",
        "📰 Finnhub News",
        "📊 Finnhub Financials",
        "📊 Finnhub Basic Financials",
        "📋 Securities Listing",
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
        st.session_state.securities_listing = None
    
    if st.sidebar.button("Fetch Data", type="primary") and ticker:
        
        # Initialize data sources
        sec_source = SECSource()
        
        # Initialize data variables
        market_data = None
        finnhub_data = None
        finnhub_news = []
        finnhub_financials = {}
        finnhub_basic_financials = {}
        sec_fundamentals = None
        
        # Fetch data from all sources
        logger.info(f"Starting data fetch for ticker: {ticker}")
        
        # Alpha Vantage market data
        logger.info("Attempting to fetch Alpha Vantage market data...")
        try:
            market_data = get_cached_alpha_vantage_data(ticker)
            if market_data:
                logger.info("[SUCCESS] Alpha Vantage data fetch successful")
            else:
                logger.warning("[WARNING] Alpha Vantage data fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ Alpha Vantage API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"Alpha Vantage API error: {e}")
        
        # Finnhub market data
        logger.info("Attempting to fetch Finnhub market data...")
        try:
            finnhub_data = get_cached_finnhub_data(ticker)
            if finnhub_data:
                logger.info("[SUCCESS] Finnhub data fetch successful")
            else:
                logger.warning("[WARNING] Finnhub data fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ Finnhub API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"Finnhub API error: {e}")
        
        # Finnhub news data
        logger.info("Attempting to fetch Finnhub news data...")
        try:
            finnhub_news = get_cached_finnhub_news(ticker)
            if finnhub_news:
                logger.info(f"[SUCCESS] Finnhub news fetch successful - {len(finnhub_news)} articles")
            else:
                logger.warning("[WARNING] Finnhub news fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ Finnhub news API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"Finnhub news API error: {e}")
        
        # Finnhub financials data
        logger.info("Attempting to fetch Finnhub financials data...")
        try:
            finnhub_financials = get_cached_finnhub_financials(ticker)
            if finnhub_financials:
                logger.info(f"[SUCCESS] Finnhub financials fetch successful")
            else:
                logger.warning("[WARNING] Finnhub financials fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ Finnhub financials API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"Finnhub financials API error: {e}")
        
        # Finnhub basic financials data
        logger.info("Attempting to fetch Finnhub basic financials data...")
        try:
            finnhub_basic_financials = get_cached_finnhub_basic_financials(ticker)
            if finnhub_basic_financials:
                logger.info(f"[SUCCESS] Finnhub basic financials fetch successful")
            else:
                logger.warning("[WARNING] Finnhub basic financials fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ Finnhub basic financials API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"Finnhub basic financials API error: {e}")
        
        # SEC data
        logger.info("Attempting to fetch SEC EDGAR data...")
        try:
            sec_data = get_cached_sec_data(ticker)
            if sec_data:
                logger.info("[SUCCESS] SEC EDGAR data fetch successful")
                # Convert back to Fundamentals object for compatibility
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
                logger.info(f"SEC data fields: {[f for f in sec_fundamentals.__dataclass_fields__ if getattr(sec_fundamentals, f) is not None]}")
            else:
                logger.warning("[WARNING] SEC EDGAR data fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ SEC EDGAR API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"SEC EDGAR API error: {e}")
        
        # Calculate total fetch time
        logger.info(f"Data fetch completed")
        
        # Store data in session state
        st.session_state.market_data = market_data
        st.session_state.finnhub_data = finnhub_data
        st.session_state.finnhub_news = finnhub_news
        st.session_state.finnhub_financials = finnhub_financials
        st.session_state.finnhub_basic_financials = finnhub_basic_financials
        st.session_state.sec_fundamentals = sec_fundamentals
        
        # Fetch securities listing data (this is independent of ticker)
        logger.info("Fetching securities listing data...")
        try:
            securities_listing = get_cached_alpha_vantage_listing_status()
            if securities_listing:
                logger.info(f"[SUCCESS] Securities listing fetch successful - {securities_listing.get('total_count', 0)} securities")
                st.session_state.securities_listing = securities_listing
            else:
                logger.warning("[WARNING] Securities listing fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ Securities listing API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"Securities listing API error: {e}")
        
        # Display cache status and refresh controls
        st.divider()
        st.subheader("🗄️ Cache Status & Controls")
        
        # Create columns for cache info and refresh buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**Cache Status**")
            # Get cache info for each source
            alpha_cache = get_cache_info("alpha_vantage", ticker, "quote_data")
            if alpha_cache:
                st.success(f"✅ Alpha Vantage: {alpha_cache['cached_at'].strftime('%H:%M:%S')}")
            else:
                st.info("ℹ️ Alpha Vantage: Not cached")
        
        with col2:
            finnhub_cache = get_cache_info("finnhub", ticker, "quote_data")
            if finnhub_cache:
                st.success(f"✅ Finnhub: {finnhub_cache['cached_at'].strftime('%H:%M:%S')}")
            else:
                st.info("ℹ️ Finnhub: Not cached")
        
        with col3:
            sec_cache = get_cache_info("sec", ticker, "fundamentals")
            if sec_cache:
                st.success(f"✅ SEC: {sec_cache['cached_at'].strftime('%H:%M:%S')}")
            else:
                st.info("ℹ️ SEC: Not cached")
        
        with col4:
            st.markdown("**Quick Actions**")
            if st.button("🔄 Refresh All", key="refresh_all"):
                st.rerun()
        
        # Cache management buttons
        st.markdown("**Cache Management**")
        cache_col1, cache_col2, cache_col3, cache_col4 = st.columns(4)
        
        with cache_col1:
            if st.button("🗑️ Clear Alpha Vantage Cache", key="clear_alpha"):
                cleared = clear_cache_for_source("alpha_vantage")
                st.success(f"Cleared {cleared} Alpha Vantage cache entries")
                st.rerun()
        
        with cache_col2:
            if st.button("🗑️ Clear Finnhub Cache", key="clear_finnhub"):
                cleared = clear_cache_for_source("finnhub")
                st.success(f"Cleared {cleared} Finnhub cache entries")
                st.rerun()
        
        with cache_col3:
            if st.button("🗑️ Clear SEC Cache", key="clear_sec"):
                cleared = clear_cache_for_source("sec")
                st.success(f"Cleared {cleared} SEC cache entries")
                st.rerun()
        
        with cache_col4:
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
        
        # Render tabs with data and individual refresh buttons
        with tab1:
            # Add refresh button for this tab
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh All Sources", key="refresh_tab1"):
                    # Force refresh all sources and update session state
                    market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
                    finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
                    sec_data = get_cached_sec_data(ticker, force_refresh=True)
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
                    # Update session state with fresh data
                    st.session_state.market_data = market_data
                    st.session_state.finnhub_data = finnhub_data
                    st.session_state.sec_fundamentals = sec_fundamentals
                    st.rerun()
            render_all_sources_tab(ticker, st.session_state.market_data, st.session_state.finnhub_data, st.session_state.sec_fundamentals)
        
        with tab2:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Alpha Vantage", key="refresh_tab2"):
                    market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
                    st.session_state.market_data = market_data
                    st.rerun()
            render_alpha_vantage_tab(ticker, st.session_state.market_data)
        
        with tab3:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh SEC", key="refresh_tab3"):
                    sec_data = get_cached_sec_data(ticker, force_refresh=True)
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
                        st.session_state.sec_fundamentals = sec_fundamentals
                    st.rerun()
            render_sec_edgar_tab(ticker, st.session_state.sec_fundamentals)
        
        with tab4:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Finnhub", key="refresh_tab4"):
                    finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
                    st.session_state.finnhub_data = finnhub_data
                    st.rerun()
            render_finnhub_tab(ticker, st.session_state.finnhub_data)
        
        with tab5:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh News", key="refresh_tab5"):
                    finnhub_news = get_cached_finnhub_news(ticker, force_refresh=True)
                    st.session_state.finnhub_news = finnhub_news
                    st.rerun()
            render_finnhub_news_tab(ticker, st.session_state.finnhub_news)
        
        with tab6:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Financials", key="refresh_tab6"):
                    finnhub_financials = get_cached_finnhub_financials(ticker, force_refresh=True)
                    st.session_state.finnhub_financials = finnhub_financials
                    st.rerun()
            render_finnhub_financials_tab(ticker, st.session_state.finnhub_financials)
        
        with tab7:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Basic Financials", key="refresh_tab7"):
                    finnhub_basic_financials = get_cached_finnhub_basic_financials(ticker, force_refresh=True)
                    st.session_state.finnhub_basic_financials = finnhub_basic_financials
                    st.rerun()
            render_finnhub_basic_financials_tab(ticker, st.session_state.finnhub_basic_financials)

        with tab8:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Securities Listing", key="refresh_tab8"):
                    securities_listing = get_cached_alpha_vantage_listing_status(force_refresh=True)
                    st.session_state.securities_listing = securities_listing
                    st.rerun()
            render_securities_listing_tab(st.session_state.securities_listing)

        with tab9:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Comparison", key="refresh_tab9"):
                    # Force refresh all sources for comparison
                    market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
                    finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
                    sec_data = get_cached_sec_data(ticker, force_refresh=True)
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
                    # Update session state with fresh data
                    st.session_state.market_data = market_data
                    st.session_state.finnhub_data = finnhub_data
                    st.session_state.sec_fundamentals = sec_fundamentals
                    st.rerun()
            render_comparison_tab(ticker, st.session_state.market_data, st.session_state.finnhub_data, st.session_state.sec_fundamentals)
        
        with tab10:
            render_debug_logs_tab()
    
    elif any([st.session_state.market_data, st.session_state.finnhub_data, st.session_state.sec_fundamentals]):
        # Render tabs with cached data from session state
        with tab1:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh All Sources", key="refresh_tab1"):
                    market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
                    finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
                    sec_data = get_cached_sec_data(ticker, force_refresh=True)
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
                    st.session_state.market_data = market_data
                    st.session_state.finnhub_data = finnhub_data
                    st.session_state.sec_fundamentals = sec_fundamentals
                    st.rerun()
            render_all_sources_tab(ticker, st.session_state.market_data, st.session_state.finnhub_data, st.session_state.sec_fundamentals)
        
        with tab2:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Alpha Vantage", key="refresh_tab2"):
                    market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
                    st.session_state.market_data = market_data
                    st.rerun()
            render_alpha_vantage_tab(ticker, st.session_state.market_data)
        
        with tab3:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh SEC", key="refresh_tab3"):
                    sec_data = get_cached_sec_data(ticker, force_refresh=True)
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
                        st.session_state.sec_fundamentals = sec_fundamentals
                    st.rerun()
            render_sec_edgar_tab(ticker, st.session_state.sec_fundamentals)
        
        with tab4:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Finnhub", key="refresh_tab4"):
                    finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
                    st.session_state.finnhub_data = finnhub_data
                    st.rerun()
            render_finnhub_tab(ticker, st.session_state.finnhub_data)
        
        with tab5:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh News", key="refresh_tab5"):
                    finnhub_news = get_cached_finnhub_news(ticker, force_refresh=True)
                    st.session_state.finnhub_news = finnhub_news
                    st.rerun()
            render_finnhub_news_tab(ticker, st.session_state.finnhub_news)
        
        with tab6:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Financials", key="refresh_tab6"):
                    finnhub_financials = get_cached_finnhub_financials(ticker, force_refresh=True)
                    st.session_state.finnhub_financials = finnhub_financials
                    st.rerun()
            render_finnhub_financials_tab(ticker, st.session_state.finnhub_financials)
        
        with tab7:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Basic Financials", key="refresh_tab7"):
                    finnhub_basic_financials = get_cached_finnhub_basic_financials(ticker, force_refresh=True)
                    st.session_state.finnhub_basic_financials = finnhub_basic_financials
                    st.rerun()
            render_finnhub_basic_financials_tab(ticker, st.session_state.finnhub_basic_financials)
        
        with tab8:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Securities Listing", key="refresh_tab8"):
                    securities_listing = get_cached_alpha_vantage_listing_status(force_refresh=True)
                    st.session_state.securities_listing = securities_listing
                    st.rerun()
            render_securities_listing_tab(st.session_state.securities_listing)
        
        with tab9:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Comparison", key="refresh_tab9"):
                    market_data = get_cached_alpha_vantage_data(ticker, force_refresh=True)
                    finnhub_data = get_cached_finnhub_data(ticker, force_refresh=True)
                    sec_data = get_cached_sec_data(ticker, force_refresh=True)
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
                    st.session_state.market_data = market_data
                    st.session_state.finnhub_data = finnhub_data
                    st.session_state.sec_fundamentals = sec_fundamentals
                    st.rerun()
            render_comparison_tab(ticker, st.session_state.market_data, st.session_state.finnhub_data, st.session_state.sec_fundamentals)
        
        with tab10:
            render_debug_logs_tab()
    
    else:
        # Show placeholder when no data is fetched
        st.info("👆 Enter a ticker symbol and click 'Fetch Data' to get started!")
        
        # Show example data structure
        with st.expander("📋 Example Data Structure"):
            st.markdown("""
            **Alpha Vantage Data:**
            - Current price, volume, change percentage
            - Day high/low, open price
            - Previous close
            
            **Finnhub Data:**
            - Real-time market data
            - Company profile with logo
            - Market cap, shares outstanding
            - Industry and sector information
            
            **SEC EDGAR Data:**
            - Revenue, net income, cash flow
            - Financial ratios (PE, ROE, ROA)
            - Operating margin, debt metrics
            
            **Finnhub News:**
            - Latest company news (last 7 days)
            - Article headlines and summaries
            - Source information and publication dates
            """)

if __name__ == "__main__":
    main()
