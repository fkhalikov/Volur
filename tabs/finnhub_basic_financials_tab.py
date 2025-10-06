"""Finnhub Basic Financials Tab for Volur Dashboard."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from dashboard_utils import format_currency, format_number, format_percentage


def display_metric_section(metrics: Dict[str, Any], section_name: str, section_icon: str):
    """Display a section of financial metrics."""
    st.subheader(f"{section_icon} {section_name}")
    
    if not metrics:
        st.info(f"No {section_name.lower()} data available")
        return
    
    # Convert metrics to DataFrame for better display
    df_data = []
    for key, value in metrics.items():
        if value is not None:
            # Format the key name for display
            display_key = key.replace('_', ' ').title()
            df_data.append({
                "Metric": display_key,
                "Value": value,
                "Formatted Value": format_metric_value(key, value)
            })
    
    if df_data:
        df = pd.DataFrame(df_data)
        st.dataframe(df[['Metric', 'Formatted Value']], width='stretch', hide_index=True)
    else:
        st.info(f"No data available for {section_name}")


def format_metric_value(key: str, value: Any) -> str:
    """Format metric values based on their type and key."""
    if value is None:
        return "N/A"
    
    # Handle different metric types
    if isinstance(value, (int, float)):
        # Financial ratios and percentages
        if any(keyword in key.lower() for keyword in ['ratio', 'margin', 'yield', 'return', 'pe', 'pb', 'ps', 'pcf', 'roe', 'roa', 'roic']):
            if abs(value) < 1:
                return f"{value:.4f}"
            else:
                return f"{value:.2f}"
        
        # Currency values (large numbers)
        elif any(keyword in key.lower() for keyword in ['capitalization', 'enterprise', 'marketcap', 'revenue', 'income', 'assets', 'equity', 'eps', 'bookvalue', 'cashflow']):
            return format_currency(value)
        
        # Small numbers
        else:
            return f"{value:.2f}"
    
    # String values
    elif isinstance(value, str):
        return value
    
    # Other types
    else:
        return str(value)


def display_key_metrics_summary(basic_financials_data: Dict[str, Any]):
    """Display a summary of key financial metrics."""
    st.subheader("📈 Key Financial Metrics Summary")
    
    if not basic_financials_data or 'metric' not in basic_financials_data:
        st.info("No basic financials data available")
        return
    
    # Extract metrics from the 'metric' key
    metrics = basic_financials_data.get('metric', {})
    
    # Common key metrics to display
    metric_mappings = {
        'marketCapitalization': 'Market Cap',
        'enterpriseValue': 'Enterprise Value',
        'peTTM': 'P/E Ratio (TTM)',
        'pb': 'P/B Ratio',
        'psTTM': 'P/S Ratio (TTM)',
        'pcfShareTTM': 'P/CF Ratio (TTM)',
        'evEbitdaTTM': 'EV/EBITDA (TTM)',
        'roeTTM': 'ROE (TTM)',
        'roaTTM': 'ROA (TTM)',
        'roicTTM': 'ROIC (TTM)',
        'grossMarginTTM': 'Gross Margin (TTM)',
        'operatingMarginTTM': 'Operating Margin (TTM)',
        'netProfitMarginTTM': 'Net Margin (TTM)',
        'longTermDebt/equityQuarterly': 'Debt/Equity',
        'currentRatioQuarterly': 'Current Ratio',
        'quickRatioQuarterly': 'Quick Ratio',
        'revenuePerShareTTM': 'Revenue/Share (TTM)',
        'epsTTM': 'EPS (TTM)',
        'bookValuePerShareQuarterly': 'Book Value/Share',
        'cashFlowPerShareTTM': 'Cash Flow/Share (TTM)'
    }
    
    # Extract metrics from the data
    key_metrics = {}
    for key, display_name in metric_mappings.items():
        if key in metrics and metrics[key] is not None:
            key_metrics[display_name] = metrics[key]
    
    if key_metrics:
        # Display in columns
        col1, col2, col3, col4 = st.columns(4)
        metrics_list = list(key_metrics.items())
        
        for i, (name, value) in enumerate(metrics_list[:4]):
            with [col1, col2, col3, col4][i]:
                formatted_value = format_metric_value(name.lower().replace(' ', ''), value)
                st.metric(name, formatted_value)
        
        if len(metrics_list) > 4:
            col5, col6, col7, col8 = st.columns(4)
            for i, (name, value) in enumerate(metrics_list[4:8]):
                with [col5, col6, col7, col8][i]:
                    formatted_value = format_metric_value(name.lower().replace(' ', ''), value)
                    st.metric(name, formatted_value)
        
        if len(metrics_list) > 8:
            col9, col10, col11, col12 = st.columns(4)
            for i, (name, value) in enumerate(metrics_list[8:12]):
                with [col9, col10, col11, col12][i]:
                    formatted_value = format_metric_value(name.lower().replace(' ', ''), value)
                    st.metric(name, formatted_value)
    else:
        st.info("No key metrics found in the basic financials data")


def render_finnhub_basic_financials_tab(ticker: str, basic_financials_data: Dict[str, Any]):
    """Render the Finnhub Basic Financials tab."""
    st.header(f"📊 Finnhub Basic Financials for {ticker}")
    
    if basic_financials_data and 'metric' in basic_financials_data:
        # Display key metrics summary
        display_key_metrics_summary(basic_financials_data)
        
        st.divider()
        
        # Get metrics from the nested structure
        metrics = basic_financials_data.get('metric', {})
        
        # Categorize metrics by type
        valuation_metrics = {}
        profitability_metrics = {}
        liquidity_metrics = {}
        leverage_metrics = {}
        efficiency_metrics = {}
        other_metrics = {}
        
        # Categorize metrics
        for key, value in metrics.items():
            if value is not None:
                key_lower = key.lower()
                
                # Valuation metrics
                if any(keyword in key_lower for keyword in ['pe', 'pb', 'ps', 'pcf', 'ev', 'marketcap', 'enterprise']):
                    valuation_metrics[key] = value
                
                # Profitability metrics
                elif any(keyword in key_lower for keyword in ['margin', 'roe', 'roa', 'roic', 'return']):
                    profitability_metrics[key] = value
                
                # Liquidity metrics
                elif any(keyword in key_lower for keyword in ['current', 'quick', 'cash']):
                    liquidity_metrics[key] = value
                
                # Leverage metrics
                elif any(keyword in key_lower for keyword in ['debt', 'equity', 'leverage']):
                    leverage_metrics[key] = value
                
                # Efficiency metrics
                elif any(keyword in key_lower for keyword in ['turnover', 'efficiency', 'per_share']):
                    efficiency_metrics[key] = value
                
                # Other metrics
                else:
                    other_metrics[key] = value
        
        # Display categorized metrics
        if valuation_metrics:
            display_metric_section(valuation_metrics, "Valuation Metrics", "💰")
            st.divider()
        
        if profitability_metrics:
            display_metric_section(profitability_metrics, "Profitability Metrics", "📈")
            st.divider()
        
        if liquidity_metrics:
            display_metric_section(liquidity_metrics, "Liquidity Metrics", "💧")
            st.divider()
        
        if leverage_metrics:
            display_metric_section(leverage_metrics, "Leverage Metrics", "⚖️")
            st.divider()
        
        if efficiency_metrics:
            display_metric_section(efficiency_metrics, "Efficiency Metrics", "⚡")
            st.divider()
        
        if other_metrics:
            display_metric_section(other_metrics, "Other Metrics", "📋")
            st.divider()
        
        # Historical data section
        if 'series' in basic_financials_data:
            st.subheader("📊 Historical Data")
            
            series_data = basic_financials_data['series']
            
            # Annual data
            if 'annual' in series_data:
                st.markdown("**Annual Data**")
                annual_data = series_data['annual']
                
                # Display key annual metrics
                key_annual_metrics = ['revenue', 'netIncome', 'totalAssets', 'totalEquity', 'eps']
                for metric in key_annual_metrics:
                    if metric in annual_data and annual_data[metric]:
                        st.markdown(f"**{metric.replace('_', ' ').title()}**")
                        df_data = []
                        for dp in annual_data[metric]:
                            value = dp.get('v')
                            formatted_value = format_metric_value(metric, value)
                            df_data.append({
                                "Period": dp.get('period', 'N/A'),
                                "Value": formatted_value
                            })
                        if df_data:
                            st.dataframe(df_data, width='stretch', hide_index=True)
            
            # Quarterly data
            if 'quarterly' in series_data:
                st.markdown("**Quarterly Data**")
                quarterly_data = series_data['quarterly']
                
                # Display key quarterly metrics
                key_quarterly_metrics = ['revenue', 'netIncome', 'totalAssets', 'totalEquity']
                for metric in key_quarterly_metrics:
                    if metric in quarterly_data and quarterly_data[metric]:
                        st.markdown(f"**{metric.replace('_', ' ').title()}**")
                        df_data = []
                        for dp in quarterly_data[metric]:
                            value = dp.get('v')
                            formatted_value = format_metric_value(metric, value)
                            df_data.append({
                                "Period": dp.get('period', 'N/A'),
                                "Value": formatted_value
                            })
                        if df_data:
                            st.dataframe(df_data, width='stretch', hide_index=True)
        
        # Raw data section
        with st.expander("🔍 Raw Basic Financials Data"):
            st.json(basic_financials_data)
            
    else:
        st.error("Could not retrieve Finnhub basic financials. Please check the ticker symbol and API key configuration.")
        
        # Show API information
        st.info("""
        **Finnhub Company Basic Financials API:**
        - Provides key financial metrics and ratios
        - Includes valuation, profitability, liquidity, and leverage ratios
        - Real-time calculated metrics from financial statements
        - Standardized financial ratios for comparison
        
        **Data includes:**
        - Valuation ratios (P/E, P/B, P/S, EV/EBITDA)
        - Profitability ratios (ROE, ROA, margins)
        - Liquidity ratios (Current, Quick ratios)
        - Leverage ratios (Debt/Equity, Interest coverage)
        - Per-share metrics (EPS, Book value per share)
        - Efficiency ratios (Asset turnover, Inventory turnover)
        """)
