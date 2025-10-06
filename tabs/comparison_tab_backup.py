"""Comparison Tab for Volur Dashboard."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from volur.plugins.base import Fundamentals
from dashboard_utils import format_currency, format_number, format_percentage


def render_comparison_tab(ticker: str, market_data: Optional[Dict[str, Any]], 
                        finnhub_data: Optional[Dict[str, Any]], 
                        sec_fundamentals: Optional[Fundamentals]):
    """Render the Comparison tab."""
    st.header(f"📊 Detailed Comparison for {ticker}")
    
    if market_data or finnhub_data or sec_fundamentals:
        st.subheader("📈 Financial Metrics Comparison")
        
        # Create comparison data
        comparison_data = []
        
        # Alpha Vantage data
        if market_data:
            comparison_data.append({
                "Metric": "Current Price",
                "Alpha Vantage": format_currency(market_data.get('regularMarketPrice')),
                "Finnhub": format_currency(finnhub_data.get('regularMarketPrice')) if finnhub_data else "N/A",
                "SEC EDGAR": "N/A"
            })
            
            comparison_data.append({
                "Metric": "Volume",
                "Alpha Vantage": format_number(market_data.get('regularMarketVolume')),
                "Finnhub": format_number(finnhub_data.get('regularMarketVolume')) if finnhub_data else "N/A",
                "SEC EDGAR": "N/A"
            })
            
            comparison_data.append({
                "Metric": "Change %",
                "Alpha Vantage": format_percentage(market_data.get('change_percent')),
                "Finnhub": format_percentage(finnhub_data.get('change_percent')) if finnhub_data else "N/A",
                "SEC EDGAR": "N/A"
            })
        
        # Finnhub-specific data
        if finnhub_data:
            comparison_data.append({
                "Metric": "Market Cap",
                "Alpha Vantage": "N/A",
                "Finnhub": format_currency(finnhub_data.get('marketCap')),
                "SEC EDGAR": "N/A"
            })
            
            comparison_data.append({
                "Metric": "Shares Outstanding",
                "Alpha Vantage": "N/A",
                "Finnhub": format_number(finnhub_data.get('sharesOutstanding')),
                "SEC EDGAR": "N/A"
            })
        
        # SEC EDGAR data
        if sec_fundamentals:
            comparison_data.append({
                "Metric": "Revenue",
                "Alpha Vantage": "N/A",
                "Finnhub": "N/A",
                "SEC EDGAR": format_currency(sec_fundamentals.revenue)
            })
            
            comparison_data.append({
                "Metric": "Free Cash Flow",
                "Alpha Vantage": "N/A",
                "Finnhub": "N/A",
                "SEC EDGAR": format_currency(sec_fundamentals.free_cash_flow)
            })
            
            comparison_data.append({
                "Metric": "Operating Margin",
                "Alpha Vantage": "N/A",
                "Finnhub": "N/A",
                "SEC EDGAR": format_percentage(sec_fundamentals.operating_margin)
            })
            
            comparison_data.append({
                "Metric": "Trailing PE",
                "Alpha Vantage": "N/A",
                "Finnhub": "N/A",
                "SEC EDGAR": f"{sec_fundamentals.trailing_pe:.2f}" if sec_fundamentals.trailing_pe else "N/A"
            })
            
            comparison_data.append({
                "Metric": "ROE",
                "Alpha Vantage": "N/A",
                "Finnhub": "N/A",
                "SEC EDGAR": format_percentage(sec_fundamentals.roe)
            })
            
            comparison_data.append({
                "Metric": "ROA",
                "Alpha Vantage": "N/A",
                "Finnhub": "N/A",
                "SEC EDGAR": format_percentage(sec_fundamentals.roa)
            })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, width='stretch')
        
        # Data source comparison
        st.subheader("📊 Data Source Comparison")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **Alpha Vantage**
            - Real-time quotes
            - Volume data
            - Price changes
            - Technical indicators
            """)
        
        with col2:
            st.info("""
            **Finnhub**
            - Real-time quotes
            - Company profiles
            - Market cap data
            - News & sentiment
            """)
        
        with col3:
            st.info("""
            **SEC EDGAR**
            - Official filings
            - Revenue data
            - Cash flow metrics
            - Financial ratios
            """)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        
        if market_data and finnhub_data:
            st.success("✅ Both Alpha Vantage and Finnhub are providing real-time data. Cross-reference for accuracy.")
        
        if sec_fundamentals:
            st.info("📊 SEC EDGAR provides official financial data. Use for fundamental analysis.")
        
        if not market_data and not finnhub_data and not sec_fundamentals:
            st.warning("⚠️ No data sources are available. Check API keys and ticker symbol.")
        
    else:
        st.warning("Need data from at least one source to show detailed comparison.")
