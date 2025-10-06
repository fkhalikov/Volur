"""Debug Logs Tab for Volur Dashboard."""

import streamlit as st
import os


def render_debug_logs_tab():
    """Render the Debug Logs tab."""
    st.header("🐛 Debug Logs")
    st.markdown("Real-time logging information for debugging issues")
    
    # Show recent log entries
    try:
        with open('volur_dashboard.log', 'r') as f:
            log_content = f.read()
            
        if log_content:
            st.subheader("📋 Recent Log Entries")
            st.text_area("Log Content", log_content, height=400)
        else:
            st.info("No log entries found.")
            
    except FileNotFoundError:
        st.warning("Log file not found. Logging may not be configured.")
    except Exception as e:
        st.error(f"Error reading log file: {e}")
    
    # Log file info
    st.subheader("📁 Log File Information")
    
    try:
        if os.path.exists('volur_dashboard.log'):
            stat = os.stat('volur_dashboard.log')
            st.info(f"""
            **Log File Status:**
            - File exists: ✅
            - Size: {stat.st_size} bytes
            - Last modified: {stat.st_mtime}
            """)
        else:
            st.warning("Log file does not exist.")
    except Exception as e:
        st.error(f"Error getting log file info: {e}")
    
    # Clear logs button
    if st.button("🗑️ Clear Logs"):
        try:
            with open('volur_dashboard.log', 'w') as f:
                f.write("")
            st.success("Logs cleared successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing logs: {e}")
    
    # Logging configuration info
    st.subheader("⚙️ Logging Configuration")
    st.info("""
    **Current Logging Setup:**
    - Log level: INFO
    - Log file: volur_dashboard.log
    - Format: Timestamp - Level - Message
    
    **To enable debug logging:**
    1. Set log level to DEBUG in the main dashboard
    2. Restart the application
    3. Check this tab for detailed logs
    """)
