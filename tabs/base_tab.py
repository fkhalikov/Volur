"""Base classes for event-driven tabs."""

import streamlit as st
from typing import Dict, Any, Optional
from event_system import subscribe_to_ticker_changes, Event, EventTypes
import logging

logger = logging.getLogger(__name__)

class TickerDrivenTab:
    """Base class for tabs that respond to ticker changes."""
    
    def __init__(self, tab_name: str):
        self.tab_name = tab_name
        self.current_ticker = None
        self.subscribed = False
    
    def subscribe_to_events(self):
        """Subscribe to ticker change events."""
        if not self.subscribed:
            subscribe_to_ticker_changes(self._on_ticker_changed)
            self.subscribed = True
            logger.info(f"{self.tab_name} subscribed to ticker change events")
    
    def _on_ticker_changed(self, event: Event):
        """Handle ticker changed event."""
        ticker = event.data.get('ticker')
        source = event.data.get('source', 'unknown')
        
        if ticker != self.current_ticker:
            logger.info(f"{self.tab_name} received ticker change: {ticker} from {source}")
            self.current_ticker = ticker
            self._on_ticker_updated(ticker)
    
    def _on_ticker_updated(self, ticker: str):
        """Override this method to handle ticker updates."""
        pass
    
    def get_current_ticker(self) -> Optional[str]:
        """Get the current ticker."""
        return self.current_ticker

class GenericDatasetTab:
    """Base class for tabs that display generic datasets (not ticker-specific)."""
    
    def __init__(self, tab_name: str):
        self.tab_name = tab_name
    
    def render(self):
        """Override this method to render the tab content."""
        pass
