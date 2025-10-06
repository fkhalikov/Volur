"""Streamlit web UI for Volur."""

from typing import Optional

import pandas as pd
import streamlit as st

from volur.config import settings
from volur.models.types import DCFParams
from volur.plugins.base import get_source, list_sources
from volur.valuation.engine import analyze_stock
from volur.valuation.scoring import get_value_score_interpretation


def format_currency(value: Optional[float]) -> str:
    """Format currency value for display."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_percentage(value: Optional[float]) -> str:
    """Format percentage value for display."""
    if value is None:
        return "N/A"
    return f"{value:.2%}"


def format_number(value: Optional[float]) -> str:
    """Format number for display."""
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Volur - Valuation Platform",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Volur - Pluggable Valuation Platform")
    st.markdown("A comprehensive valuation platform with multiple data sources for value investing analysis.")

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # Data source selection
    available_sources = list_sources()
    if not available_sources:
        st.error("No data sources available. Please check your configuration.")
        return

    data_source_name = st.sidebar.selectbox(
        "Data Source",
        available_sources,
        index=0,
        help="Select the data source for financial data"
    )

    # DCF parameters
    st.sidebar.subheader("DCF Parameters")

    discount_rate = st.sidebar.slider(
        "Discount Rate",
        min_value=0.01,
        max_value=0.30,
        value=settings.discount_rate,
        step=0.01,
        format="%.1%",
        help="Required rate of return for the investment"
    )

    long_term_growth = st.sidebar.slider(
        "Long-term Growth Rate",
        min_value=0.0,
        max_value=0.20,
        value=settings.long_term_growth,
        step=0.01,
        format="%.1%",
        help="Expected long-term growth rate"
    )

    years = st.sidebar.slider(
        "Projection Years",
        min_value=5,
        max_value=20,
        value=settings.years,
        step=1,
        help="Number of years for DCF projection"
    )

    terminal_growth = st.sidebar.slider(
        "Terminal Growth Rate",
        min_value=0.0,
        max_value=0.10,
        value=settings.long_term_growth,
        step=0.01,
        format="%.1%",
        help="Terminal growth rate (must be less than discount rate)"
    )

    # Validate terminal growth
    if terminal_growth >= discount_rate:
        st.sidebar.error("Terminal growth rate must be less than discount rate")
        return

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Stock Analysis")

        # Ticker input
        ticker = st.text_input(
            "Enter Stock Ticker",
            value="AAPL",
            help="Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
        ).upper().strip()

        if ticker:
            # Analyze button
            if st.button("Analyze Stock", type="primary"):
                try:
                    # Get data source
                    data_source = get_source(data_source_name)

                    # Create DCF parameters
                    dcf_params = DCFParams(
                        discount_rate=discount_rate,
                        long_term_growth=long_term_growth,
                        years=years,
                        terminal_growth=terminal_growth
                    )

                    # Show loading spinner
                    with st.spinner(f"Analyzing {ticker} using {data_source_name}..."):
                        result = analyze_stock(data_source, ticker, dcf_params)

                    # Display results
                    display_valuation_results(result)

                except Exception as e:
                    st.error(f"Error analyzing {ticker}: {str(e)}")

    with col2:
        st.header("About")
        st.info("""
        **Volur** is a pluggable valuation platform that supports multiple data sources:
        
        - **Yahoo Finance**: Free, real-time data
        - **SEC EDGAR**: Official SEC filings
        - **Financial Modeling Prep**: Professional-grade data (requires API key)
        
        The platform calculates:
        - DCF intrinsic value
        - Margin of safety
        - Value score
        - Key financial ratios
        """)


def display_valuation_results(result):
    """Display valuation results in a formatted layout."""
    st.success(f"Analysis complete for {result.ticker}")

    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Current Price",
            format_currency(result.intrinsic_value_per_share) if result.intrinsic_value_per_share else "N/A"
        )
        st.metric(
            "Intrinsic Value",
            format_currency(result.intrinsic_value_per_share)
        )

    with col2:
        st.metric(
            "Margin of Safety",
            format_percentage(result.margin_of_safety)
        )
        st.metric(
            "Value Score",
            f"{format_number(result.value_score)}/100"
        )

    with col3:
        st.metric(
            "P/E Ratio",
            format_number(result.pe_ratio)
        )
        st.metric(
            "P/B Ratio",
            format_number(result.pb_ratio)
        )

    with col4:
        st.metric(
            "ROE",
            format_percentage(result.roe)
        )
        st.metric(
            "FCF Yield",
            format_percentage(result.fcf_yield)
        )

    # Value score interpretation
    if result.value_score is not None:
        interpretation = get_value_score_interpretation(result.value_score)
        if result.value_score >= 60:
            st.success(f"Value Assessment: {interpretation}")
        elif result.value_score >= 40:
            st.warning(f"Value Assessment: {interpretation}")
        else:
            st.error(f"Value Assessment: {interpretation}")

    # Detailed metrics table
    st.subheader("Detailed Metrics")

    metrics_data = {
        "Metric": [
            "Current Price",
            "Intrinsic Value per Share",
            "Intrinsic Value Total",
            "Margin of Safety",
            "Value Score",
            "P/E Ratio",
            "P/B Ratio",
            "ROE",
            "ROA",
            "Debt-to-Equity",
            "FCF Yield"
        ],
        "Value": [
            format_currency(result.intrinsic_value_per_share),
            format_currency(result.intrinsic_value_per_share),
            format_currency(result.intrinsic_value_total),
            format_percentage(result.margin_of_safety),
            format_number(result.value_score),
            format_number(result.pe_ratio),
            format_number(result.pb_ratio),
            format_percentage(result.roe),
            "N/A",  # ROA not in result
            format_number(result.debt_to_equity),
            format_percentage(result.fcf_yield)
        ]
    }

    df = pd.DataFrame(metrics_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Disclaimer
    st.markdown("---")
    st.markdown("""
    **Disclaimer**: This analysis is for educational and informational purposes only. 
    It should not be considered as financial advice. Always conduct your own research 
    and consult with a qualified financial advisor before making investment decisions.
    """)


if __name__ == "__main__":
    main()
