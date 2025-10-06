"""Finnhub News Tab for Volur Dashboard."""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime


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


def render_finnhub_news_tab(ticker: str, finnhub_news: List[Dict[str, Any]]):
    """Render the Finnhub News tab."""
    st.header(f"📰 Finnhub News for {ticker}")
    
    if finnhub_news:
        display_finnhub_news(finnhub_news, ticker)
        
        # Raw news data
        with st.expander("🔍 Raw News Data"):
            st.json(finnhub_news)
    else:
        st.error("Could not retrieve Finnhub news. Please check the ticker symbol and API key configuration.")
