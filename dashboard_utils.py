"""Shared utilities for the Volur dashboard."""

import streamlit as st
import requests
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime, timedelta

# Import Volur components
from volur.plugins.sec_source import SECSource
from volur.plugins.finnhub_source import FinnhubSource
from volur.plugins.base import Quote, Fundamentals
from volur.config import settings
from volur.mongodb_cache import get_cache

logger = logging.getLogger(__name__)


def format_currency(value: Optional[float]) -> str:
    """Format a value as currency."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_percentage(value: Optional[float]) -> str:
    """Format a value as percentage."""
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def format_number(value: Optional[float]) -> str:
    """Format a large number with appropriate suffixes."""
    if value is None:
        return "N/A"
    
    if value >= 1e12:
        return f"{value/1e12:.2f}T"
    elif value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{value/1e6:.2f}M"
    elif value >= 1e3:
        return f"{value/1e3:.2f}K"
    else:
        return f"{value:.2f}"


def get_alpha_vantage_data(ticker: str) -> Dict[str, Any]:
    """Get market data from Alpha Vantage API."""
    logger.info(f"Fetching Alpha Vantage data for ticker: {ticker}")
    
    try:
        api_key = settings.alpha_vantage_api_key
        if not api_key:
            logger.error("Alpha Vantage API key not configured")
            return {}
        
        logger.info(f"Using Alpha Vantage API key: {api_key[:8]}...")
        
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Alpha Vantage response keys: {list(data.keys())}")
        
        if "Global Quote" in data:
            quote_data = data["Global Quote"]
            logger.info("Alpha Vantage data retrieved successfully")
            
            return {
                "regularMarketPrice": float(quote_data.get("05. price", 0)),
                "regularMarketPreviousClose": float(quote_data.get("08. previous close", 0)),
                "regularMarketDayHigh": float(quote_data.get("03. high", 0)),
                "regularMarketDayLow": float(quote_data.get("04. low", 0)),
                "regularMarketVolume": int(quote_data.get("06. volume", 0)),
                "open": float(quote_data.get("02. open", 0)),
                "change": float(quote_data.get("09. change", 0)),
                "change_percent": float(quote_data.get("10. change percent", 0).replace("%", "")),
                "timestamp": quote_data.get("07. latest trading day", ""),
                "marketCap": None,  # Not available in Global Quote
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
            logger.warning(f"Unexpected Alpha Vantage response: {data}")
            return {}
            
    except Exception as e:
        logger.error(f"Alpha Vantage API error: {e}")
        return {}


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


def get_finnhub_financials(ticker: str) -> Dict[str, Any]:
    """Get financial statements from Finnhub API."""
    logger.info(f"Fetching Finnhub financials for ticker: {ticker}")
    
    try:
        # Get financial statements from Finnhub API
        financials_url = f"https://finnhub.io/api/v1/stock/financials-reported"
        params = {
            "symbol": ticker,
            "freq": "annual"  # annual or quarterly
        }
        headers = {
            "X-Finnhub-Token": settings.finnhub_api_key,
            "User-Agent": "Volur/0.1.0"
        }
        
        logger.info(f"Fetching financials for {ticker} (annual frequency)")
        response = requests.get(financials_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        financials_data = response.json()
        logger.info(f"Retrieved financials data for {ticker}")
        
        return financials_data
        
    except Exception as e:
        logger.error(f"Finnhub financials API error: {e}")
        return {}


def get_finnhub_basic_financials(ticker: str) -> Dict[str, Any]:
    """Get basic financial metrics from Finnhub API."""
    logger.info(f"Fetching Finnhub basic financials for ticker: {ticker}")
    
    try:
        # Get basic financial metrics from Finnhub API
        basic_financials_url = f"https://finnhub.io/api/v1/stock/metric"
        params = {
            "symbol": ticker,
            "metric": "all"  # Get all available metrics
        }
        headers = {
            "X-Finnhub-Token": settings.finnhub_api_key,
            "User-Agent": "Volur/0.1.0"
        }
        
        logger.info(f"Fetching basic financials for {ticker}")
        response = requests.get(basic_financials_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        basic_financials_data = response.json()
        logger.info(f"Retrieved basic financials data for {ticker}")
        
        return basic_financials_data
        
    except Exception as e:
        logger.error(f"Finnhub basic financials API error: {e}")
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
        st.metric("Price", format_currency(quote.price))
    with col2:
        st.metric("Currency", quote.currency or "N/A")
    with col3:
        st.metric("Shares Outstanding", format_number(quote.shares_outstanding))
    with col4:
        st.metric("Ticker", quote.ticker)


def display_fundamentals_data(fundamentals: Fundamentals, source_name: str):
    """Display fundamentals data in a formatted way."""
    st.subheader(f"📊 Fundamentals Data ({source_name})")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Revenue", format_currency(fundamentals.revenue))
    with col2:
        st.metric("Free Cash Flow", format_currency(fundamentals.free_cash_flow))
    with col3:
        st.metric("Operating Margin", format_percentage(fundamentals.operating_margin))
    with col4:
        st.metric("Trailing PE", f"{fundamentals.trailing_pe:.2f}" if fundamentals.trailing_pe else "N/A")
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("ROE", format_percentage(fundamentals.roe))
    with col6:
        st.metric("ROA", format_percentage(fundamentals.roa))
    with col7:
        st.metric("Debt-to-Equity", f"{fundamentals.debt_to_equity:.2f}" if fundamentals.debt_to_equity else "N/A")
    with col8:
        st.metric("Price-to-Book", f"{fundamentals.price_to_book:.2f}" if fundamentals.price_to_book else "N/A")


# MongoDB Cached API Functions
def get_cached_alpha_vantage_data(ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get Alpha Vantage data with MongoDB caching."""
    cache = get_cache()
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get("alpha_vantage", ticker, "quote_data")
        if cached_data:
            logger.info(f"Retrieved Alpha Vantage data from cache for {ticker}")
            return cached_data["data"]
    
    # Fetch fresh data
    logger.info(f"Fetching fresh Alpha Vantage data for {ticker}")
    data = get_alpha_vantage_data(ticker)
    
    # Cache the data
    if data:
        cache.set("alpha_vantage", ticker, "quote_data", data, ttl_hours=24)
    
    return data


def get_cached_finnhub_data(ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get Finnhub data with MongoDB caching."""
    cache = get_cache()
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get("finnhub", ticker, "quote_data")
        if cached_data:
            logger.info(f"Retrieved Finnhub data from cache for {ticker}")
            return cached_data["data"]
    
    # Fetch fresh data
    logger.info(f"Fetching fresh Finnhub data for {ticker}")
    data = get_finnhub_data(ticker)
    
    # Cache the data
    if data:
        cache.set("finnhub", ticker, "quote_data", data, ttl_hours=24)
    
    return data


def get_cached_finnhub_news(ticker: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Get Finnhub news with MongoDB caching."""
    cache = get_cache()
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get("finnhub", ticker, "news")
        if cached_data:
            logger.info(f"Retrieved Finnhub news from cache for {ticker}")
            return cached_data["data"]
    
    # Fetch fresh data
    logger.info(f"Fetching fresh Finnhub news for {ticker}")
    data = get_finnhub_news(ticker)
    
    # Cache the data
    if data:
        cache.set("finnhub", ticker, "news", data, ttl_hours=6)  # News expires faster
    
    return data


def get_cached_finnhub_financials(ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get Finnhub financials with MongoDB caching."""
    cache = get_cache()
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get("finnhub", ticker, "financials")
        if cached_data:
            logger.info(f"Retrieved Finnhub financials from cache for {ticker}")
            return cached_data["data"]
    
    # Fetch fresh data
    logger.info(f"Fetching fresh Finnhub financials for {ticker}")
    data = get_finnhub_financials(ticker)
    
    # Cache the data
    if data:
        cache.set("finnhub", ticker, "financials", data, ttl_hours=48)  # Financials can be cached longer
    
    return data


def get_cached_finnhub_basic_financials(ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get Finnhub basic financials with MongoDB caching."""
    cache = get_cache()
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get("finnhub", ticker, "basic_financials")
        if cached_data:
            logger.info(f"Retrieved Finnhub basic financials from cache for {ticker}")
            return cached_data["data"]
    
    # Fetch fresh data
    logger.info(f"Fetching fresh Finnhub basic financials for {ticker}")
    data = get_finnhub_basic_financials(ticker)
    
    # Cache the data
    if data:
        cache.set("finnhub", ticker, "basic_financials", data, ttl_hours=48)  # Basic financials can be cached longer
    
    return data


def get_cached_sec_data(ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get SEC data with MongoDB caching."""
    cache = get_cache()
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get("sec", ticker, "fundamentals")
        if cached_data:
            logger.info(f"Retrieved SEC data from cache for {ticker}")
            return cached_data["data"]
    
    # Fetch fresh data
    logger.info(f"Fetching fresh SEC data for {ticker}")
    try:
        sec_source = SECSource()
        fundamentals = sec_source.get_fundamentals(ticker)
        
        # Convert to dict for caching
        data = {
            "ticker": fundamentals.ticker,
            "trailing_pe": fundamentals.trailing_pe,
            "price_to_book": fundamentals.price_to_book,
            "roe": fundamentals.roe,
            "roa": fundamentals.roa,
            "debt_to_equity": fundamentals.debt_to_equity,
            "free_cash_flow": fundamentals.free_cash_flow,
            "revenue": fundamentals.revenue,
            "operating_margin": fundamentals.operating_margin,
            "sector": fundamentals.sector,
            "name": fundamentals.name
        }
        
        # Cache the data
        if data:
            cache.set("sec", ticker, "fundamentals", data, ttl_hours=72)  # SEC data can be cached longer
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching SEC data: {e}")
        return {}


def get_cache_info(source: str, ticker: str, endpoint: str) -> Optional[Dict[str, Any]]:
    """Get cache information for a specific request."""
    cache = get_cache()
    return cache.get(source, ticker, endpoint)


def clear_cache_for_source(source: str) -> int:
    """Clear all cache entries for a specific source."""
    cache = get_cache()
    return cache.clear_source(source)


def clear_cache_for_ticker(ticker: str) -> int:
    """Clear all cache entries for a specific ticker."""
    cache = get_cache()
    return cache.clear_ticker(ticker)


def get_cache_stats() -> Dict[str, Any]:
    """Get overall cache statistics."""
    cache = get_cache()
    return cache.get_cache_stats()


def get_alpha_vantage_listing_status() -> Dict[str, Any]:
    """Get Alpha Vantage listing status data (all US securities)."""
    logger.info("Fetching Alpha Vantage listing status data")
    
    try:
        if not settings.alpha_vantage_api_key:
            logger.warning("Alpha Vantage API key not configured")
            return {}
        
        # Alpha Vantage LISTING_STATUS endpoint
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "LISTING_STATUS",
            "apikey": settings.alpha_vantage_api_key,
            "datatype": "csv"
        }
        
        logger.info("Fetching listing status from Alpha Vantage API")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse CSV data
        csv_content = response.text
        logger.info(f"Retrieved listing status data: {len(csv_content)} characters")
        
        # Parse CSV into list of dictionaries
        import csv
        import io
        
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        securities_data = list(csv_reader)
        
        logger.info(f"Parsed {len(securities_data)} securities from listing status")
        
        return {
            "securities": securities_data,
            "total_count": len(securities_data),
            "raw_csv": csv_content
        }
        
    except Exception as e:
        logger.error(f"Alpha Vantage listing status API error: {e}")
        return {}


def get_cached_alpha_vantage_listing_status(force_refresh: bool = False) -> Dict[str, Any]:
    """Get Alpha Vantage listing status data with MongoDB caching."""
    cache = get_cache()
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get("alpha_vantage", "ALL", "listing_status")
        if cached_data:
            logger.info("Retrieved Alpha Vantage listing status from cache")
            return cached_data["data"]
    
    # Fetch fresh data
    logger.info("Fetching fresh Alpha Vantage listing status data")
    data = get_alpha_vantage_listing_status()
    
    # Cache the data (with longer TTL since this changes infrequently)
    if data:
        cache.set("alpha_vantage", "ALL", "listing_status", data, ttl_hours=168)  # 7 days
    
    return data
