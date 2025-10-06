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
