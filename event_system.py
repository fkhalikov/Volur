"""Event System for Volur Dashboard - Message-driven architecture."""

import streamlit as st
from typing import Dict, Any, List, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Event:
    """Event class to represent messages."""
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()
        self.event_id = f"{event_type}_{self.timestamp.strftime('%Y%m%d_%H%M%S_%f')}"

class EventBus:
    """Event bus for managing event subscriptions and publishing."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to {event_type}")
    
    def publish(self, event: Event):
        """Publish an event to all subscribers."""
        logger.info(f"Publishing event: {event.event_type}")
        self.event_history.append(event)
        
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
    
    def get_event_history(self, event_type: str = None) -> List[Event]:
        """Get event history, optionally filtered by event type."""
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type]
        return self.event_history

# Global event bus instance
event_bus = EventBus()

# Event Types
class EventTypes:
    TICKER_CHANGED = "ticker_changed"
    DATA_FETCH_REQUESTED = "data_fetch_requested"
    CACHE_CLEARED = "cache_cleared"
    TAB_REFRESH_REQUESTED = "tab_refresh_requested"

def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return event_bus

def publish_ticker_changed(ticker: str, source: str = "user_input"):
    """Publish a ticker changed event."""
    event = Event(EventTypes.TICKER_CHANGED, {
        "ticker": ticker,
        "source": source,
        "timestamp": datetime.now()
    })
    event_bus.publish(event)

def publish_data_fetch_requested(ticker: str, data_source: str):
    """Publish a data fetch requested event."""
    event = Event(EventTypes.DATA_FETCH_REQUESTED, {
        "ticker": ticker,
        "data_source": data_source,
        "timestamp": datetime.now()
    })
    event_bus.publish(event)

def subscribe_to_ticker_changes(callback: Callable):
    """Subscribe to ticker change events."""
    event_bus.subscribe(EventTypes.TICKER_CHANGED, callback)

def subscribe_to_data_fetch_requests(callback: Callable):
    """Subscribe to data fetch request events."""
    event_bus.subscribe(EventTypes.DATA_FETCH_REQUESTED, callback)
