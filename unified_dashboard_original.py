"""Unified Dashboard for Volur - Compare Alpha Vantage and SEC EDGAR Data."""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
import requests
import json
import logging
import traceback
from datetime import datetime, timedelta

# Import Volur components
from volur.plugins.sec_source import SECSource
from volur.plugins.finnhub_source import FinnhubSource
from volur.plugins.base import Quote, Fundamentals
from volur.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('volur_dashboard.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def format_currency(value: Optional[float]) -> str:
    """Format currency values."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_percentage(value: Optional[float]) -> str:
    """Format percentage values."""
    if value is None:
        return "N/A"
    return f"{value:.2%}"


def format_number(value: Optional[float]) -> str:
    """Format number values."""
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def get_data_completeness(data_object) -> float:
    """Calculate the percentage of non-None fields in a dataclass."""
    if not data_object:
        return 0.0
    total_fields = 0
    filled_fields = 0
    for field_name in data_object.__dataclass_fields__:
        total_fields += 1
        if getattr(data_object, field_name) is not None:
            filled_fields += 1
    return (filled_fields / total_fields) * 100 if total_fields > 0 else 0.0


def get_alpha_vantage_data(ticker: str) -> Dict[str, Any]:
    """Get stock data from Alpha Vantage API."""
    logger.info(f"Fetching Alpha Vantage data for ticker: {ticker}")
    
    # Use API key from environment variables
    api_key = settings.alpha_vantage_api_key
    if not api_key:
        logger.error("Alpha Vantage API key not configured")
        st.error("❌ Alpha Vantage API key not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.")
        return {}
    
    logger.info(f"Using Alpha Vantage API key: {api_key[:8]}...")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Alpha Vantage response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            logger.info("Alpha Vantage data retrieved successfully")
            
            # Convert Alpha Vantage format to standard market data format
            return {
                "regularMarketPrice": float(quote.get("05. price", 0)),
                "regularMarketPreviousClose": float(quote.get("08. previous close", 0)),
                "regularMarketDayHigh": float(quote.get("03. high", 0)),
                "regularMarketDayLow": float(quote.get("04. low", 0)),
                "regularMarketVolume": int(quote.get("06. volume", 0)),
                "longName": f"{ticker} Corporation",  # Alpha Vantage doesn't provide company name
                "sector": "Technology",  # Default sector
                "industry": "Software",  # Default industry
                "exchange": "NASDAQ",  # Default exchange
                "trailingPE": None,  # Not available in Global Quote
                "forwardPE": None,  # Not available in Global Quote
                "priceToBook": None,  # Not available in Global Quote
                "beta": None,  # Not available in Global Quote
                "dividendYield": None,  # Not available in Global Quote
                "fiftyTwoWeekHigh": float(quote.get("03. high", 0)),  # Using day high as approximation
                "fiftyTwoWeekLow": float(quote.get("04. low", 0)),  # Using day low as approximation
                "marketCap": None  # Not available in Global Quote
            }
        
        logger.warning("Alpha Vantage returned empty Global Quote")
        return {}
        
    except Exception as e:
        logger.error(f"Alpha Vantage API error: {e}")
        return {}


def get_market_data(ticker: str) -> Dict[str, Any]:
    """Get market data from Alpha Vantage API."""
    logger.info(f"Fetching market data for ticker: {ticker}")
    
    # Use Alpha Vantage as primary data source
    return get_alpha_vantage_data(ticker)


def get_finnhub_data(ticker: str) -> Dict[str, Any]:
    """Get market data from Finnhub API."""
    logger.info(f"Fetching Finnhub data for ticker: {ticker}")
    
    try:
        finnhub_source = FinnhubSource()
        quote = finnhub_source.get_quote(ticker)
        
        if quote:
            logger.info("[SUCCESS] Finnhub data retrieved successfully")
            
            # Get additional data from Finnhub API directly for dashboard display
            try:
                # Get quote data for additional fields
                quote_url = f"https://finnhub.io/api/v1/quote"
                params = {"symbol": ticker}
                headers = {
                    "X-Finnhub-Token": settings.finnhub_api_key,
                    "User-Agent": "Volur/0.1.0"
                }
                
                response = requests.get(quote_url, params=params, headers=headers, timeout=10)
                quote_data = response.json() if response.status_code == 200 else {}
                
                # Get company profile for additional fields
                profile_url = f"https://finnhub.io/api/v1/stock/profile2"
                profile_params = {"symbol": ticker}
                
                profile_response = requests.get(profile_url, params=profile_params, headers=headers, timeout=10)
                profile_data = profile_response.json() if profile_response.status_code == 200 else {}
                
                return {
                    # Basic quote data
                    "regularMarketPrice": quote.price,
                    "regularMarketPreviousClose": quote_data.get('pc', 0.0),
                    "regularMarketDayHigh": quote_data.get('h', 0.0),
                    "regularMarketDayLow": quote_data.get('l', 0.0),
                    "regularMarketVolume": quote_data.get('v', 0),
                    "open": quote_data.get('o', 0.0),
                    "change": quote_data.get('d', 0.0),
                    "change_percent": quote_data.get('dp', 0.0),
                    "timestamp": quote_data.get('t', 0),
                    
                    # Company profile data
                    "marketCap": profile_data.get('marketCapitalization', 0.0),
                    "longName": profile_data.get('name', ticker),
                    "ticker": profile_data.get('ticker', ticker),
                    "sector": profile_data.get('finnhubIndustry', 'Unknown'),
                    "industry": profile_data.get('finnhubIndustry', 'Unknown'),
                    "exchange": profile_data.get('exchange', 'Unknown'),
                    "country": profile_data.get('country', 'Unknown'),
                    "currency": profile_data.get('currency', 'USD'),
                    "sharesOutstanding": profile_data.get('shareOutstanding'),
                    "ipo": profile_data.get('ipo', 'N/A'),
                    "phone": profile_data.get('phone', 'N/A'),
                    "weburl": profile_data.get('weburl', ''),
                    "logo": profile_data.get('logo', ''),
                    
                    # Additional fields (not available from basic quote)
                    "trailingPE": None,
                    "forwardPE": None,
                    "priceToBook": None,
                    "beta": None,
                    "dividendYield": None,
                    "fiftyTwoWeekHigh": None,
                    "fiftyTwoWeekLow": None
                }
            except Exception as e:
                logger.error(f"Error getting additional Finnhub data: {e}")
                # Return basic data from Quote object
                return {
                    "regularMarketPrice": quote.price,
                    "regularMarketPreviousClose": None,
                    "regularMarketDayHigh": None,
                    "regularMarketDayLow": None,
                    "regularMarketVolume": None,
                    "marketCap": None,
                    "longName": ticker,
                    "sector": "Unknown",
                    "industry": "Unknown",
                    "exchange": "Unknown",
                    "trailingPE": None,
                    "forwardPE": None,
                    "priceToBook": None,
                    "beta": None,
                    "dividendYield": None,
                    "fiftyTwoWeekHigh": None,
                    "fiftyTwoWeekLow": None
                }
        else:
            logger.warning("Finnhub returned empty quote data")
            return {}
            
    except Exception as e:
        logger.error(f"Finnhub API error: {e}")
        return {}


def get_finnhub_news(ticker: str) -> List[Dict[str, Any]]:
    """Get company news from Finnhub API."""
    logger.info(f"Fetching Finnhub news for ticker: {ticker}")
    
    try:
        # Get company news from Finnhub API
        news_url = f"https://finnhub.io/api/v1/company-news"
        params = {
            "symbol": ticker,
            "from": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # Last 7 days
            "to": datetime.now().strftime('%Y-%m-%d')
        }
        headers = {
            "X-Finnhub-Token": settings.finnhub_api_key,
            "User-Agent": "Volur/0.1.0"
        }
        
        logger.info(f"Fetching news from: {params['from']} to {params['to']}")
        response = requests.get(news_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        news_data = response.json()
        logger.info(f"Retrieved {len(news_data)} news articles for {ticker}")
        
        # Sort by datetime (most recent first)
        news_data.sort(key=lambda x: x.get('datetime', 0), reverse=True)
        
        return news_data[:20]  # Return top 20 most recent articles
        
    except Exception as e:
        logger.error(f"Finnhub news API error: {e}")
        return []


def display_quote_data(quote: Quote, source_name: str):
    """Display quote data in a formatted way."""
    st.subheader(f"📈 Quote Data ({source_name})")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", format_currency(quote.price), help="Last traded price")
    with col2:
        st.metric("Currency", quote.currency or "N/A")
    with col3:
        st.metric("Shares Outstanding", format_number(quote.shares_outstanding) if quote.shares_outstanding else "N/A")
    with col4:
        st.metric("Data Completeness", f"{get_data_completeness(quote):.1f}%")


def display_fundamentals_data(fundamentals: Fundamentals, source_name: str):
    """Display fundamentals data in a formatted way."""
    st.subheader(f"📊 Fundamentals Data ({source_name})")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("P/E Ratio", format_number(fundamentals.trailing_pe))
        st.metric("ROE", format_percentage(fundamentals.roe))
    with col2:
        st.metric("P/B Ratio", format_number(fundamentals.price_to_book))
        st.metric("ROA", format_percentage(fundamentals.roa))
    with col3:
        st.metric("Debt/Equity", format_number(fundamentals.debt_to_equity))
        st.metric("Free Cash Flow", format_currency(fundamentals.free_cash_flow))
    with col4:
        st.metric("Revenue", format_currency(fundamentals.revenue))
        st.metric("Operating Margin", format_percentage(fundamentals.operating_margin))
    
    st.metric("Fundamentals Data Completeness", f"{get_data_completeness(fundamentals):.1f}%")


def display_market_data(data: Dict[str, Any]):
    """Display market data from Alpha Vantage."""
    st.subheader("📈 Alpha Vantage Market Data")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", format_currency(data.get('regularMarketPrice')))
        st.metric("Previous Close", format_currency(data.get('regularMarketPreviousClose')))
    with col2:
        st.metric("Day High", format_currency(data.get('regularMarketDayHigh')))
        st.metric("Day Low", format_currency(data.get('regularMarketDayLow')))
    with col3:
        st.metric("Volume", format_number(data.get('regularMarketVolume')))
        st.metric("Market Cap", format_currency(data.get('marketCap')))
    with col4:
        st.metric("P/E Ratio", format_number(data.get('trailingPE')))
        st.metric("Forward P/E", format_number(data.get('forwardPE')))
    
    # Company Information
    st.subheader("🏢 Company Information")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Company Name", data.get('longName', 'N/A'))
    with col2:
        st.metric("Sector", data.get('sector', 'N/A'))
    with col3:
        st.metric("Industry", data.get('industry', 'N/A'))
    with col4:
        st.metric("Exchange", data.get('exchange', 'N/A'))
    
    # Additional Ratios
    st.subheader("📊 Additional Ratios")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Price to Book", format_number(data.get('priceToBook')))
    with col2:
        st.metric("Beta", format_number(data.get('beta')))
    with col3:
        st.metric("Dividend Yield", format_percentage(data.get('dividendYield')))
    with col4:
        st.metric("52 Week High", format_currency(data.get('fiftyTwoWeekHigh')))
        st.metric("52 Week Low", format_currency(data.get('fiftyTwoWeekLow')))


def display_finnhub_news(news_data: List[Dict[str, Any]], ticker: str):
    """Display Finnhub company news in a formatted way."""
    st.subheader(f"📰 Latest News for {ticker}")
    
    if not news_data:
        st.warning("No news articles found for this ticker.")
        return
    
    st.info(f"Found {len(news_data)} news articles from the last 7 days")
    
    for i, article in enumerate(news_data):
        with st.expander(f"📄 {article.get('headline', 'No headline')[:80]}...", expanded=(i < 3)):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{article.get('headline', 'No headline')}**")
                st.write(article.get('summary', 'No summary available'))
                
                # Source and datetime
                source = article.get('source', 'Unknown source')
                datetime_str = article.get('datetime', 0)
                if datetime_str:
                    try:
                        dt = datetime.fromtimestamp(datetime_str)
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M UTC')
                    except:
                        formatted_time = str(datetime_str)
                else:
                    formatted_time = 'Unknown time'
                
                st.caption(f"Source: {source} | Published: {formatted_time}")
            
            with col2:
                # Related tickers
                related = article.get('related', [])
                if related:
                    st.write("**Related:**")
                    for ticker_symbol in related[:3]:  # Show max 3 related tickers
                        st.write(f"• {ticker_symbol}")
                
                # Category
                category = article.get('category', '')
                if category:
                    st.write(f"**Category:** {category}")
            
            # URL if available
            url = article.get('url', '')
            if url:
                st.markdown(f"[Read full article →]({url})")
            
            st.divider()


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


def main():
    st.set_page_config(
        page_title="Volur Unified Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Volur Unified Dashboard")
    st.markdown("Compare stock data from multiple sources: Alpha Vantage, Finnhub, and SEC EDGAR")

    # Sidebar for ticker input
    st.sidebar.header("Input")
    ticker = st.sidebar.text_input(
        "Enter Stock Ticker",
        value="AAPL",
        help="Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
    ).upper().strip()

    # Create tabs for different data sources
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🔄 All Sources", "📈 Alpha Vantage", "🏛️ SEC EDGAR", "📊 Finnhub", "📰 Finnhub News", "📊 Comparison", "🐛 Debug Logs"])

    if st.sidebar.button("Fetch Data", type="primary") and ticker:
        
        # Initialize data sources
        sec_source = SECSource()
        
        # Fetch data from all sources
        logger.info(f"Starting data fetch for ticker: {ticker}")
        start_time = datetime.now()
        
        with st.spinner(f"Fetching data for {ticker}..."):
            # Alpha Vantage market data
            market_data = None
            logger.info("Attempting to fetch Alpha Vantage market data...")
            try:
                market_data = get_market_data(ticker)
                if market_data:
                    logger.info("[SUCCESS] Alpha Vantage data fetch successful")
                else:
                    logger.warning("[WARNING] Alpha Vantage data fetch returned empty result")
            except Exception as e:
                logger.error(f"❌ Alpha Vantage API error: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                st.warning(f"Alpha Vantage API error: {e}")
            
            # Finnhub market data
            finnhub_data = None
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
            finnhub_news = []
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
            
            # SEC data
            sec_fundamentals = None
            logger.info("Attempting to fetch SEC EDGAR data...")
            try:
                sec_fundamentals = sec_source.get_fundamentals(ticker)
                if sec_fundamentals:
                    logger.info("[SUCCESS] SEC EDGAR data fetch successful")
                    logger.info(f"SEC data fields: {[f for f in sec_fundamentals.__dataclass_fields__ if getattr(sec_fundamentals, f) is not None]}")
                else:
                    logger.warning("[WARNING] SEC EDGAR data fetch returned empty result")
            except Exception as e:
                logger.error(f"❌ SEC EDGAR error: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                st.warning(f"SEC EDGAR error: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Data fetch completed in {duration:.2f} seconds")

        # Tab 1: All Sources Overview
        with tab1:
            st.header(f"📊 All Sources Overview for {ticker}")
            
            if market_data:
                st.success("✅ Alpha Vantage - Available")
            else:
                st.error("❌ Alpha Vantage - Failed")
            
            if finnhub_data:
                st.success("✅ Finnhub - Available")
            else:
                st.error("❌ Finnhub - Failed")
            
            if sec_fundamentals:
                st.success("✅ SEC EDGAR - Available")
            else:
                st.error("❌ SEC EDGAR - Failed")
            
            # Quick comparison table
            if market_data or finnhub_data or sec_fundamentals:
                st.subheader("📊 Quick Comparison")
                
                comparison_data = []
                
                # Alpha Vantage
                if market_data:
                    comparison_data.append({
                        "Source": "Alpha Vantage",
                        "Price": format_currency(market_data.get('regularMarketPrice')),
                        "P/E": format_number(market_data.get('trailingPE')),
                        "Market Cap": format_currency(market_data.get('marketCap')),
                        "Company": market_data.get('longName', 'N/A')
                    })
                
                # Finnhub
                if finnhub_data:
                    comparison_data.append({
                        "Source": "Finnhub",
                        "Price": format_currency(finnhub_data.get('regularMarketPrice')),
                        "P/E": format_number(finnhub_data.get('trailingPE')),
                        "Market Cap": format_currency(finnhub_data.get('marketCap')),
                        "Company": finnhub_data.get('longName', 'N/A')
                    })
                
                # SEC EDGAR
                if sec_fundamentals:
                    comparison_data.append({
                        "Source": "SEC EDGAR",
                        "Price": "N/A (No real-time quotes)",
                        "P/E": format_number(sec_fundamentals.trailing_pe),
                        "Market Cap": "N/A",
                        "Company": sec_fundamentals.name or "N/A"
                    })
                
                if comparison_data:
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, width='stretch')

        # Tab 2: Alpha Vantage
        with tab2:
            st.header(f"📈 Alpha Vantage Data for {ticker}")
            
            if market_data:
                display_market_data(market_data)
                
                # Raw data
                with st.expander("🔍 Raw Alpha Vantage Data"):
                    st.json(market_data)
            else:
                st.error("Could not retrieve Alpha Vantage data. Please check the ticker symbol and API key configuration.")

        # Tab 3: SEC EDGAR
        with tab3:
            st.header(f"🏛️ SEC EDGAR Data for {ticker}")
            
            if sec_fundamentals:
                st.info("ℹ️ SEC EDGAR provides official financial filings data (no real-time quotes)")
                
                display_fundamentals_data(sec_fundamentals, "SEC EDGAR")
                
                # Additional SEC-specific information
                st.subheader("📋 SEC Filing Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Sector", sec_fundamentals.sector or "N/A")
                with col2:
                    st.metric("Company Name", sec_fundamentals.name or "N/A")
                
                # Raw data
                with st.expander("🔍 Raw SEC EDGAR Data"):
                    st.json(sec_fundamentals.__dict__)
            else:
                st.error("Could not retrieve SEC EDGAR data. Please check the ticker symbol.")

        # Tab 4: Finnhub
        with tab4:
            st.header(f"📊 Finnhub Data for {ticker}")
            
            if finnhub_data:
                display_finnhub_data(finnhub_data)
                
                # Raw data
                with st.expander("🔍 Raw Finnhub Data"):
                    st.json(finnhub_data)
            else:
                st.error("Could not retrieve Finnhub data. Please check the ticker symbol and API key configuration.")

        # Tab 5: Finnhub News
        with tab5:
            st.header(f"📰 Finnhub News for {ticker}")
            
            if finnhub_news:
                display_finnhub_news(finnhub_news, ticker)
                
                # Raw news data
                with st.expander("🔍 Raw News Data"):
                    st.json(finnhub_news)
            else:
                st.error("Could not retrieve Finnhub news. Please check the ticker symbol and API key configuration.")

        # Tab 6: Detailed Comparison
        with tab6:
            st.header(f"📊 Detailed Comparison for {ticker}")
            
            if market_data or finnhub_data or sec_fundamentals:
                st.subheader("📈 Financial Metrics Comparison")
                
                # Create comparison table
                metrics_data = {
                    "Metric": [
                        "P/E Ratio",
                        "Free Cash Flow",
                        "Revenue",
                        "Operating Margin",
                        "ROE",
                        "ROA",
                        "Debt/Equity"
                    ],
                    "Alpha Vantage": [
                        format_number(market_data.get('trailingPE') if market_data else None),
                        "N/A (Not available via Alpha Vantage)",
                        "N/A (Not available via Alpha Vantage)",
                        "N/A (Not available via Alpha Vantage)",
                        "N/A (Not available via Alpha Vantage)",
                        "N/A (Not available via Alpha Vantage)",
                        "N/A (Not available via Alpha Vantage)"
                    ],
                    "Finnhub": [
                        format_number(finnhub_data.get('trailingPE') if finnhub_data else None),
                        "N/A (Not available via Finnhub)",
                        "N/A (Not available via Finnhub)",
                        "N/A (Not available via Finnhub)",
                        "N/A (Not available via Finnhub)",
                        "N/A (Not available via Finnhub)",
                        "N/A (Not available via Finnhub)"
                    ],
                    "SEC EDGAR": [
                        format_number(sec_fundamentals.trailing_pe if sec_fundamentals else None),
                        format_currency(sec_fundamentals.free_cash_flow if sec_fundamentals else None),
                        format_currency(sec_fundamentals.revenue if sec_fundamentals else None),
                        format_percentage(sec_fundamentals.operating_margin if sec_fundamentals else None),
                        format_percentage(sec_fundamentals.roe if sec_fundamentals else None),
                        format_percentage(sec_fundamentals.roa if sec_fundamentals else None),
                        format_number(sec_fundamentals.debt_to_equity if sec_fundamentals else None)
                    ]
                }
                
                df = pd.DataFrame(metrics_data)
                st.dataframe(df, width='stretch')
                
                # Data source comparison
                st.subheader("📊 Data Source Comparison")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Alpha Vantage Advantages:**")
                    st.markdown("""
                    ✅ Real-time stock prices  
                    ✅ Market data (volume, high/low)  
                    ✅ Technical indicators  
                    ✅ Historical data  
                    ✅ Fast and reliable  
                    ✅ Free tier available  
                    """)
                
                with col2:
                    st.markdown("**Finnhub Advantages:**")
                    st.markdown("""
                    ✅ Real-time stock prices  
                    ✅ Market data (volume, high/low)  
                    ✅ Company profiles  
                    ✅ Financial metrics  
                    ✅ News and sentiment  
                    ✅ Free tier available  
                    """)
                
                with col3:
                    st.markdown("**SEC EDGAR Advantages:**")
                    st.markdown("""
                    ✅ Official audited financial data  
                    ✅ Detailed financial statements  
                    ✅ Regulatory compliance data  
                    ✅ Free and reliable  
                    ✅ Historical filing data  
                    ✅ No rate limits  
                    """)
                
            else:
                st.warning("Need data from both sources to show detailed comparison.")

        # Tab 7: Debug Logs
        with tab7:
            st.header("🐛 Debug Logs")
            st.markdown("Real-time logging information for debugging issues")
            
            # Show recent log entries
            try:
                with open('volur_dashboard.log', 'r') as f:
                    log_content = f.read()
                
                if log_content:
                    st.subheader("📄 Recent Log Entries")
                    st.text_area("Log Content", log_content, height=400)
                    
                    # Parse and display structured log info
                    st.subheader("📊 Log Summary")
                    log_lines = log_content.split('\n')
                    error_count = len([line for line in log_lines if 'ERROR' in line])
                    warning_count = len([line for line in log_lines if 'WARNING' in line])
                    info_count = len([line for line in log_lines if 'INFO' in line])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Errors", error_count)
                    with col2:
                        st.metric("Warnings", warning_count)
                    with col3:
                        st.metric("Info Messages", info_count)
                    
                    # Show recent errors
                    if error_count > 0:
                        st.subheader("❌ Recent Errors")
                        recent_errors = [line for line in log_lines[-20:] if 'ERROR' in line]
                        for error in recent_errors[-5:]:  # Show last 5 errors
                            st.error(error)
                
            except FileNotFoundError:
                st.info("No log file found yet. Logs will appear here after data fetching attempts.")
            except Exception as e:
                st.error(f"Error reading log file: {e}")
            
            # Manual refresh button
            if st.button("🔄 Refresh Logs"):
                st.rerun()

    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Data Sources:**
    - 📈 Alpha Vantage: Real-time market data
    - 📊 Finnhub: Real-time market data & company profiles
    - 🏛️ SEC EDGAR: Official financial filings
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Volur Platform** - Pluggable Valuation Platform")


if __name__ == "__main__":
    main()
