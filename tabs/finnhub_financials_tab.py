"""Finnhub Financials Tab for Volur Dashboard."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from dashboard_utils import format_currency, format_number, format_percentage


def display_financial_statement(statement_data: Dict[str, Any], statement_name: str):
    """Display a financial statement in a formatted table."""
    st.subheader(f"📊 {statement_name}")
    
    if not statement_data:
        st.warning(f"No {statement_name.lower()} data available")
        return
    
    # Convert to DataFrame for better display
    df_data = []
    for item in statement_data:
        df_data.append({
            "Metric": item.get("concept", "Unknown"),
            "Value": item.get("value", 0),
            "Unit": item.get("unit", ""),
            "Label": item.get("label", "")
        })
    
    if df_data:
        df = pd.DataFrame(df_data)
        
        # Format the value column
        def format_value(row):
            value = row['Value']
            if value is None or value == 0:
                return "N/A"
            
            # Format based on unit
            unit = row['Unit']
            if unit == 'USD':
                return format_currency(value)
            elif unit in ['shares', 'USD/shares']:
                return format_number(value)
            else:
                return f"{value:,.2f}"
        
        df['Formatted Value'] = df.apply(format_value, axis=1)
        
        # Display the table
        display_df = df[['Metric', 'Formatted Value', 'Label']].copy()
        st.dataframe(display_df, width='stretch', hide_index=True)
    else:
        st.info(f"No data available for {statement_name}")


def display_financials_summary(financials_data: Dict[str, Any]):
    """Display a summary of key financial metrics."""
    st.subheader("📈 Key Financial Metrics")
    
    # Extract key metrics from the most recent report
    key_metrics = {}
    
    if 'data' in financials_data and financials_data['data']:
        # Get the most recent report (first in the list)
        latest_report = financials_data['data'][0]
        if 'report' in latest_report:
            report_data = latest_report['report']
            
            # Extract from income statement (ic)
            if 'ic' in report_data:
                for item in report_data['ic']:
                    concept = item.get('concept', '').lower()
                    value = item.get('value', 0)
                    
                    if 'revenue' in concept and 'contract' in concept:
                        key_metrics['Revenue'] = value
                    elif 'net income' in concept and 'loss' in concept:
                        key_metrics['Net Income'] = value
                    elif 'operating income' in concept and 'loss' in concept:
                        key_metrics['Operating Income'] = value
                    elif 'gross profit' in concept:
                        key_metrics['Gross Profit'] = value
            
            # Extract from balance sheet (bs)
            if 'bs' in report_data:
                for item in report_data['bs']:
                    concept = item.get('concept', '').lower()
                    value = item.get('value', 0)
                    
                    if 'assets' in concept and 'total' in concept and 'current' not in concept:
                        key_metrics['Total Assets'] = value
                    elif 'liabilities' in concept and 'total' in concept and 'current' not in concept:
                        key_metrics['Total Liabilities'] = value
                    elif 'stockholders equity' in concept or 'shareholders equity' in concept:
                        key_metrics['Shareholders Equity'] = value
            
            # Extract from cash flow (cf)
            if 'cf' in report_data:
                for item in report_data['cf']:
                    concept = item.get('concept', '').lower()
                    value = item.get('value', 0)
                    
                    if 'operating activities' in concept and 'net cash' in concept:
                        key_metrics['Operating Cash Flow'] = value
    
    if key_metrics:
        col1, col2, col3, col4 = st.columns(4)
        metrics_list = list(key_metrics.items())
        
        for i, (name, value) in enumerate(metrics_list[:4]):
            with [col1, col2, col3, col4][i]:
                st.metric(name, format_currency(value) if value else "N/A")
        
        if len(metrics_list) > 4:
            col5, col6, col7, col8 = st.columns(4)
            for i, (name, value) in enumerate(metrics_list[4:8]):
                with [col5, col6, col7, col8][i]:
                    st.metric(name, format_currency(value) if value else "N/A")
    else:
        st.info("No key metrics found in the financial data")


def render_finnhub_financials_tab(ticker: str, financials_data: Dict[str, Any]):
    """Render the Finnhub Financials tab."""
    st.header(f"📊 Finnhub Financial Statements for {ticker}")
    
    if financials_data and 'data' in financials_data and financials_data['data']:
        # Display summary metrics
        display_financials_summary(financials_data)
        
        st.divider()
        
        # Display detailed financial statements for each report
        for i, report in enumerate(financials_data['data']):
            year = report.get('year', 'Unknown')
            form = report.get('form', 'Unknown')
            filed_date = report.get('filedDate', 'Unknown')
            
            st.subheader(f"📋 {form} Report - {year} (Filed: {filed_date})")
            
            if 'report' in report:
                report_data = report['report']
                
                # Display Income Statement
                if 'ic' in report_data and report_data['ic']:
                    display_financial_statement(report_data['ic'], f"Income Statement ({year})")
                    st.divider()
                
                # Display Balance Sheet
                if 'bs' in report_data and report_data['bs']:
                    display_financial_statement(report_data['bs'], f"Balance Sheet ({year})")
                    st.divider()
                
                # Display Cash Flow Statement
                if 'cf' in report_data and report_data['cf']:
                    display_financial_statement(report_data['cf'], f"Cash Flow Statement ({year})")
                    st.divider()
            
            # Add separator between reports
            if i < len(financials_data['data']) - 1:
                st.markdown("---")
        
        # Raw data section
        with st.expander("🔍 Raw Financial Data"):
            st.json(financials_data)
            
    else:
        st.error("Could not retrieve Finnhub financials. Please check the ticker symbol and API key configuration.")
        
        # Show API information
        st.info("""
        **Finnhub Financials Reported API:**
        - Provides comprehensive financial statements
        - Includes income statement, balance sheet, and cash flow data
        - Annual and quarterly frequency options
        - Detailed line items with standardized concepts
        
        **Data includes:**
        - Revenue and sales figures
        - Profit and loss metrics
        - Asset and liability information
        - Cash flow details
        - Financial ratios and metrics
        """)
