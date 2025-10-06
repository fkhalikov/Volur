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
from tabs.comparison_tab import render_comparison_tab
from tabs.debug_logs_tab import render_debug_logs_tab

# Import utilities
from dashboard_utils import (
    get_alpha_vantage_data, 
    get_finnhub_data, 
    get_finnhub_news,
    get_finnhub_financials,
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
    st.title("📊 Volur - Unified Financial Dashboard")
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🔄 All Sources", 
        "📈 Alpha Vantage", 
        "🏛️ SEC EDGAR", 
        "📊 Finnhub", 
        "📰 Finnhub News", 
        "📊 Finnhub Financials",
        "📊 Comparison", 
        "🐛 Debug Logs"
    ])
    
    if st.sidebar.button("Fetch Data", type="primary") and ticker:
        
        # Initialize data sources
        sec_source = SECSource()
        
        # Initialize data variables
        market_data = None
        finnhub_data = None
        finnhub_news = []
        finnhub_financials = {}
        sec_fundamentals = None
        
        # Fetch data from all sources
        logger.info(f"Starting data fetch for ticker: {ticker}")
        
        # Alpha Vantage market data
        logger.info("Attempting to fetch Alpha Vantage market data...")
        try:
            market_data = get_alpha_vantage_data(ticker)
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
            finnhub_data = get_finnhub_data(ticker)
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
            finnhub_news = get_finnhub_news(ticker)
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
            finnhub_financials = get_finnhub_financials(ticker)
            if finnhub_financials:
                logger.info(f"[SUCCESS] Finnhub financials fetch successful")
            else:
                logger.warning("[WARNING] Finnhub financials fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ Finnhub financials API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"Finnhub financials API error: {e}")
        
        # SEC data
        logger.info("Attempting to fetch SEC EDGAR data...")
        try:
            sec_fundamentals = sec_source.get_fundamentals(ticker)
            if sec_fundamentals:
                logger.info("[SUCCESS] SEC EDGAR data fetch successful")
                logger.info(f"SEC data fields: {[f for f in sec_fundamentals.__dataclass_fields__ if getattr(sec_fundamentals, f) is not None]}")
            else:
                logger.warning("[WARNING] SEC EDGAR data fetch returned empty result")
        except Exception as e:
            logger.error(f"❌ SEC EDGAR API error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            st.warning(f"SEC EDGAR API error: {e}")
        
        # Calculate total fetch time
        logger.info(f"Data fetch completed")
        
        # Render tabs with data
        with tab1:
            render_all_sources_tab(ticker, market_data, finnhub_data, sec_fundamentals)
        
        with tab2:
            render_alpha_vantage_tab(ticker, market_data)
        
        with tab3:
            render_sec_edgar_tab(ticker, sec_fundamentals)
        
        with tab4:
            render_finnhub_tab(ticker, finnhub_data)
        
        with tab5:
            render_finnhub_news_tab(ticker, finnhub_news)
        
        with tab6:
            render_finnhub_financials_tab(ticker, finnhub_financials)
        
        with tab7:
            render_comparison_tab(ticker, market_data, finnhub_data, sec_fundamentals)
        
        with tab8:
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
