"""MongoDB-based caching system for Volur API requests."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import json
import hashlib

logger = logging.getLogger(__name__)


class MongoDBCache:
    """MongoDB-based cache manager with TTL and timestamp tracking."""
    
    def __init__(self, connection_string: str = "mongodb://admin:password123@localhost:27017/", 
                 database_name: str = "volur_cache", default_ttl_hours: int = 24):
        """
        Initialize MongoDB cache manager.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to use
            default_ttl_hours: Default TTL in hours for cached data
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.default_ttl_hours = default_ttl_hours
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._collection: Optional[Collection] = None
        
    def _get_client(self) -> MongoClient:
        """Get MongoDB client, creating if necessary."""
        if self._client is None:
            try:
                self._client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
                # Test the connection
                self._client.admin.command('ping')
                logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        return self._client
    
    def _get_database(self) -> Database:
        """Get database, creating if necessary."""
        if self._db is None:
            client = self._get_client()
            self._db = client[self.database_name]
        return self._db
    
    def _get_collection(self, collection_name: str = "api_cache") -> Collection:
        """Get collection, creating if necessary."""
        if self._collection is None:
            db = self._get_database()
            self._collection = db[collection_name]
            
            # Create TTL index on expires_at field
            try:
                self._collection.create_index("expires_at", expireAfterSeconds=0)
                logger.info("Created TTL index on expires_at field")
            except Exception as e:
                logger.warning(f"Could not create TTL index: {e}")
                
        return self._collection
    
    def _generate_cache_key(self, source: str, ticker: str, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate a unique cache key for the request."""
        # Create a string representation of the request
        key_parts = [source, ticker, endpoint]
        if params:
            # Sort params for consistent key generation
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(sorted_params)
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, source: str, ticker: str, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a request.
        
        Args:
            source: Data source name (e.g., 'alpha_vantage', 'finnhub')
            ticker: Stock ticker symbol
            endpoint: API endpoint or data type
            params: Optional parameters for the request
            
        Returns:
            Cached data with metadata, or None if not found/expired
        """
        try:
            collection = self._get_collection()
            cache_key = self._generate_cache_key(source, ticker, endpoint, params)
            
            # Find the cached document
            cached_doc = collection.find_one({"cache_key": cache_key})
            
            if cached_doc is None:
                logger.debug(f"Cache miss for {source}:{ticker}:{endpoint}")
                return None
            
            # Check if expired
            if cached_doc.get("expires_at") and cached_doc["expires_at"] < datetime.utcnow():
                logger.debug(f"Cache expired for {source}:{ticker}:{endpoint}")
                # Remove expired document
                collection.delete_one({"cache_key": cache_key})
                return None
            
            logger.debug(f"Cache hit for {source}:{ticker}:{endpoint}")
            
            # Return the cached data with metadata
            return {
                "data": cached_doc.get("data"),
                "cached_at": cached_doc.get("cached_at"),
                "expires_at": cached_doc.get("expires_at"),
                "source": cached_doc.get("source"),
                "ticker": cached_doc.get("ticker"),
                "endpoint": cached_doc.get("endpoint"),
                "cache_key": cache_key
            }
            
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, source: str, ticker: str, endpoint: str, data: Any, 
            ttl_hours: Optional[int] = None, params: Optional[Dict] = None) -> bool:
        """
        Cache data for a request.
        
        Args:
            source: Data source name
            ticker: Stock ticker symbol
            endpoint: API endpoint or data type
            data: Data to cache
            ttl_hours: TTL in hours (uses default if None)
            params: Optional parameters for the request
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            collection = self._get_collection()
            cache_key = self._generate_cache_key(source, ticker, endpoint, params)
            
            # Calculate expiration time
            ttl = ttl_hours if ttl_hours is not None else self.default_ttl_hours
            cached_at = datetime.utcnow()
            expires_at = cached_at + timedelta(hours=ttl)
            
            # Prepare document for insertion
            cache_doc = {
                "cache_key": cache_key,
                "source": source,
                "ticker": ticker,
                "endpoint": endpoint,
                "data": data,
                "cached_at": cached_at,
                "expires_at": expires_at,
                "ttl_hours": ttl,
                "params": params
            }
            
            # Upsert the document
            collection.replace_one(
                {"cache_key": cache_key},
                cache_doc,
                upsert=True
            )
            
            logger.info(f"Cached data for {source}:{ticker}:{endpoint} (expires: {expires_at})")
            return True
            
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False
    
    def delete(self, source: str, ticker: str, endpoint: str, params: Optional[Dict] = None) -> bool:
        """
        Delete cached data for a request.
        
        Args:
            source: Data source name
            ticker: Stock ticker symbol
            endpoint: API endpoint or data type
            params: Optional parameters for the request
            
        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            collection = self._get_collection()
            cache_key = self._generate_cache_key(source, ticker, endpoint, params)
            
            result = collection.delete_one({"cache_key": cache_key})
            deleted = result.deleted_count > 0
            
            if deleted:
                logger.info(f"Deleted cache for {source}:{ticker}:{endpoint}")
            else:
                logger.debug(f"No cache found to delete for {source}:{ticker}:{endpoint}")
                
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            return False
    
    def clear_source(self, source: str) -> int:
        """
        Clear all cached data for a specific source.
        
        Args:
            source: Data source name
            
        Returns:
            Number of documents deleted
        """
        try:
            collection = self._get_collection()
            result = collection.delete_many({"source": source})
            deleted_count = result.deleted_count
            
            logger.info(f"Cleared {deleted_count} cache entries for source: {source}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing cache for source {source}: {e}")
            return 0
    
    def clear_ticker(self, ticker: str) -> int:
        """
        Clear all cached data for a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Number of documents deleted
        """
        try:
            collection = self._get_collection()
            result = collection.delete_many({"ticker": ticker})
            deleted_count = result.deleted_count
            
            logger.info(f"Cleared {deleted_count} cache entries for ticker: {ticker}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing cache for ticker {ticker}: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            collection = self._get_collection()
            
            # Get total count
            total_count = collection.count_documents({})
            
            # Get count by source
            pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            source_counts = list(collection.aggregate(pipeline))
            
            # Get count by ticker
            pipeline = [
                {"$group": {"_id": "$ticker", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            ticker_counts = list(collection.aggregate(pipeline))
            
            # Get expired count
            expired_count = collection.count_documents({"expires_at": {"$lt": datetime.utcnow()}})
            
            return {
                "total_entries": total_count,
                "expired_entries": expired_count,
                "active_entries": total_count - expired_count,
                "source_counts": {item["_id"]: item["count"] for item in source_counts},
                "top_tickers": {item["_id"]: item["count"] for item in ticker_counts}
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._collection = None
            logger.info("Closed MongoDB connection")


# Global cache instance
_cache_instance: Optional[MongoDBCache] = None


def get_cache() -> MongoDBCache:
    """Get the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MongoDBCache()
    return _cache_instance


def close_cache():
    """Close the global cache instance."""
    global _cache_instance
    if _cache_instance:
        _cache_instance.close()
        _cache_instance = None
