"""Simple caching layer using diskcache."""

import functools
import hashlib
import os
from typing import Any, Callable, Optional

import diskcache as dc

from .config import settings


class Cache:
    """Simple disk-based cache."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache with optional custom directory."""
        self.cache_dir = cache_dir or settings.cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache = dc.Cache(self.cache_dir)

    def get(self, key: str) -> Any:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        if ttl is None:
            ttl = settings.cache_ttl_hours * 3600  # Convert hours to seconds
        
        try:
            self._cache.set(key, value, expire=ttl)
        except Exception as e:
            # If pickling fails, try to convert dataclass to dict
            if hasattr(value, '__dataclass_fields__'):
                try:
                    dict_value = value.__dict__
                    self._cache.set(key, dict_value, expire=ttl)
                except Exception:
                    # If all else fails, skip caching
                    pass

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()


# Global cache instance
cache = Cache()


def cached(ttl: Optional[int] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = hashlib.md5("|".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result

        return wrapper
    return decorator
