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
    
    # Compact summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Securities", f"{len(df):,}")
    
    with col2:
        active_count = len(df[df.get('status', '') == 'Active']) if 'status' in df.columns else 0
        st.metric("Active", f"{active_count:,}")
    
    with col3:
        unique_exchanges = df['exchange'].nunique() if 'exchange' in df.columns else 0
        st.metric("Exchanges", unique_exchanges)
    
    with col4:
        unique_asset_types = df['assetType'].nunique() if 'assetType' in df.columns else 0
        st.metric("Asset Types", unique_asset_types)
    
    # Compact search and filter controls
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
        
        st.caption(f"📋 **{len(filtered_data)} results**")
        
        # Paginated display with action buttons
        items_per_page = 50
        total_pages = (len(filtered_data) + items_per_page - 1) // items_per_page
        
        # Page selector
        if total_pages > 1:
            page = st.selectbox("Page", range(1, total_pages + 1), key="securities_page")
            page -= 1  # Convert to 0-based index
        else:
            page = 0
        
        # Get data for current page
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_data))
        page_data = filtered_data[start_idx:end_idx]
        
        st.markdown(f"**Page {page + 1} of {total_pages} | Showing {start_idx + 1}-{end_idx} of {len(filtered_data)} results**")
        st.markdown("**Click '📊 Analyze' button for any ticker to load all data sources:**")
        
        # Create a custom display with buttons for current page
        for i, row in enumerate(page_data):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 3, 1, 1, 1, 1, 1])
            
            with col1:
                if st.button(f"📊", key=f"analyze_{row.get('symbol', '')}_{start_idx + i}", help=f"Analyze {row.get('symbol', '')} - {row.get('name', '')}"):
                    # Set the ticker in session state for event-driven architecture
                    selected_symbol = row.get('symbol', '')
                    st.session_state.selected_ticker_from_listing = selected_symbol
                    st.success(f"✅ Selected **{selected_symbol}** for analysis! Event fired to update all tabs.")
                    # Force a rerun to process the event
                    st.rerun()
            
            with col2:
                symbol = row.get('symbol', '')
                name = row.get('name', '')
                st.write(f"**{symbol}** - {name}")
            
            with col3:
                st.write(row.get('exchange', ''))
            
            with col4:
                st.write(row.get('assetType', ''))
            
            with col5:
                st.write(row.get('ipoDate', ''))
            
            with col6:
                st.write(row.get('delistingDate', ''))
            
            with col7:
                st.write(row.get('status', ''))
        
        # Download button for filtered data
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"securities_list_{len(filtered_data)}_results.csv",
            mime="text/csv"
        )
        
        # Compact distribution info
        if len(filtered_data) > 0:
            with st.expander("📈 Distribution"):
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
    st.markdown("### 📋 US Securities Listing")
    
    # Compact cache status
    cache_info = get_cache_info("alpha_vantage", "ALL", "listing_status")
    if cache_info:
        st.caption(f"📅 Cached: {cache_info['cached_at'].strftime('%m/%d %H:%M')} (Expires: {cache_info['expires_at'].strftime('%m/%d %H:%M')})")
    else:
        st.caption("ℹ️ Data not cached - fetched fresh from API")
    
    # Show current ticker analysis status
    if 'selected_ticker_from_listing' in st.session_state and st.session_state.selected_ticker_from_listing:
        st.success(f"🎯 **{st.session_state.selected_ticker_from_listing}** selected - Ready for analysis!")
        # Clear the selection after showing it to avoid persistent display
        del st.session_state.selected_ticker_from_listing
    
    if listing_data and 'securities' in listing_data:
        securities_data = listing_data['securities']
        total_count = listing_data.get('total_count', len(securities_data))
        
        # Compact data source info
        st.caption(f"**Data Source:** Alpha Vantage LISTING_STATUS API | **Total Securities:** {total_count:,}")
        
        # Compact tip
        st.caption("💡 **Tip:** Select a ticker below and click '📊 Analyze Ticker' to set it in the main input.")
        
        display_securities_table(securities_data)
        
        # Compact raw data section
        with st.expander("🔍 Raw Data"):
            st.json(listing_data.get('securities', [])[:5])  # Show first 5 entries
            if len(securities_data) > 5:
                st.caption(f"Showing first 5 of {len(securities_data)} securities.")
        
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
        st.caption("**Alpha Vantage LISTING_STATUS API** provides comprehensive list of all US securities with symbols, names, exchanges, and status information.")
