"""Securities Listing Tab for Volur Dashboard."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from dashboard_utils import get_cache_info


def filter_securities_data(securities_data: List[Dict[str, Any]], 
                          search_term: str = "",
                          exchange_filter: str = "All",
                          asset_type_filter: str = "All",
                          status_filter: str = "All") -> List[Dict[str, Any]]:
    """Filter securities data based on search criteria."""
    filtered_data = securities_data.copy()
    
    # Text search across symbol and name
    if search_term:
        search_lower = search_term.lower()
        filtered_data = [
            sec for sec in filtered_data
            if (search_lower in sec.get('symbol', '').lower() or 
                search_lower in sec.get('name', '').lower())
        ]
    
    # Exchange filter
    if exchange_filter != "All":
        filtered_data = [
            sec for sec in filtered_data
            if sec.get('exchange') == exchange_filter
        ]
    
    # Asset type filter
    if asset_type_filter != "All":
        filtered_data = [
            sec for sec in filtered_data
            if sec.get('assetType') == asset_type_filter
        ]
    
    # Status filter
    if status_filter != "All":
        filtered_data = [
            sec for sec in filtered_data
            if sec.get('status') == status_filter
        ]
    
    return filtered_data


def display_securities_table(securities_data: List[Dict[str, Any]]):
    """Display securities data in a searchable table."""
    if not securities_data:
        st.warning("No securities data available")
        return
    
    # Create DataFrame
    df = pd.DataFrame(securities_data)
    
    # Ensure we have the expected columns
    expected_columns = ['symbol', 'name', 'exchange', 'assetType', 'ipoDate', 'delistingDate', 'status']
    available_columns = [col for col in expected_columns if col in df.columns]
    
    if not available_columns:
        st.error("No valid securities data found")
        return
    
    # Display summary
    st.subheader(f"📊 Securities Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Securities", len(df))
    
    with col2:
        active_count = len(df[df.get('status', '') == 'Active']) if 'status' in df.columns else 0
        st.metric("Active", active_count)
    
    with col3:
        unique_exchanges = df['exchange'].nunique() if 'exchange' in df.columns else 0
        st.metric("Exchanges", unique_exchanges)
    
    with col4:
        unique_asset_types = df['assetType'].nunique() if 'assetType' in df.columns else 0
        st.metric("Asset Types", unique_asset_types)
    
    st.divider()
    
    # Search and filter controls
    st.subheader("🔍 Search & Filter")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_term = st.text_input(
            "Search Symbol/Name",
            placeholder="e.g., AAPL, Apple",
            key="securities_search"
        )
    
    with col2:
        exchange_options = ["All"] + sorted(df['exchange'].unique().tolist()) if 'exchange' in df.columns else ["All"]
        exchange_filter = st.selectbox("Exchange", exchange_options, key="exchange_filter")
    
    with col3:
        asset_type_options = ["All"] + sorted(df['assetType'].unique().tolist()) if 'assetType' in df.columns else ["All"]
        asset_type_filter = st.selectbox("Asset Type", asset_type_options, key="asset_type_filter")
    
    with col4:
        status_options = ["All"] + sorted(df['status'].unique().tolist()) if 'status' in df.columns else ["All"]
        status_filter = st.selectbox("Status", status_options, key="status_filter")
    
    # Apply filters
    filtered_data = filter_securities_data(
        securities_data,
        search_term=search_term,
        exchange_filter=exchange_filter,
        asset_type_filter=asset_type_filter,
        status_filter=status_filter
    )
    
    # Display filtered results
    if filtered_data:
        filtered_df = pd.DataFrame(filtered_data)
        
        st.subheader(f"📋 Securities List ({len(filtered_data)} results)")
        
        # Display table with selected columns
        display_columns = available_columns[:7]  # Limit to first 7 columns for better display
        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Download button for filtered data
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"securities_list_{len(filtered_data)}_results.csv",
            mime="text/csv"
        )
        
        # Show top exchanges and asset types
        if len(filtered_data) > 0:
            st.subheader("📈 Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'exchange' in filtered_df.columns:
                    exchange_counts = filtered_df['exchange'].value_counts().head(10)
                    st.markdown("**Top Exchanges:**")
                    for exchange, count in exchange_counts.items():
                        st.write(f"- {exchange}: {count}")
            
            with col2:
                if 'assetType' in filtered_df.columns:
                    asset_type_counts = filtered_df['assetType'].value_counts().head(10)
                    st.markdown("**Asset Types:**")
                    for asset_type, count in asset_type_counts.items():
                        st.write(f"- {asset_type}: {count}")
    else:
        st.info("No securities match your search criteria")


def render_securities_listing_tab(listing_data: Optional[Dict[str, Any]]):
    """Render the Securities Listing tab."""
    st.header("📋 US Securities Listing")
    
    # Display cache status
    cache_info = get_cache_info("alpha_vantage", "ALL", "listing_status")
    if cache_info:
        st.success(f"📅 Data cached at: {cache_info['cached_at'].strftime('%Y-%m-%d %H:%M:%S')} (Expires: {cache_info['expires_at'].strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        st.info("ℹ️ Data not cached - fetched fresh from API")
    
    if listing_data and 'securities' in listing_data:
        securities_data = listing_data['securities']
        total_count = listing_data.get('total_count', len(securities_data))
        
        st.markdown(f"""
        **Data Source:** [Alpha Vantage LISTING_STATUS API](https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=)
        
        This dataset contains comprehensive information about all US securities including:
        - **Symbols**: Stock ticker symbols
        - **Names**: Company names
        - **Exchanges**: Trading exchanges (NYSE, NASDAQ, etc.)
        - **Asset Types**: Stock types (Stock, ETF, etc.)
        - **IPO Dates**: Initial public offering dates
        - **Status**: Active or delisted status
        """)
        
        display_securities_table(securities_data)
        
        # Raw data section
        with st.expander("🔍 Raw Listing Data"):
            st.markdown(f"**Total Securities:** {total_count}")
            st.json(listing_data.get('securities', [])[:10])  # Show first 10 entries
            if len(securities_data) > 10:
                st.info(f"Showing first 10 of {len(securities_data)} securities. Use the table above to view all data.")
        
        # Download full dataset
        if 'raw_csv' in listing_data:
            st.download_button(
                label="📥 Download Full Dataset (CSV)",
                data=listing_data['raw_csv'],
                file_name="us_securities_listing.csv",
                mime="text/csv"
            )
    
    else:
        st.error("Could not retrieve securities listing data. Please check the API key configuration.")
        
        st.info("""
        **Alpha Vantage LISTING_STATUS API:**
        - Provides comprehensive list of all US securities
        - Includes active and delisted securities
        - Contains symbol, name, exchange, and status information
        - Updated regularly to reflect current market listings
        
        **Data includes:**
        - Stock symbols and company names
        - Trading exchanges (NYSE, NASDAQ, etc.)
        - Asset types (Stock, ETF, etc.)
        - IPO and delisting dates
        - Current status (Active/Delisted)
        """)
