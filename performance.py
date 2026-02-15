"""
Performance and Load Management Middleware
Implements rate limiting, caching, and connection pooling for high concurrency
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional
import time
import hashlib


class RateLimiter:
    """
    Token bucket rate limiter for API endpoints
    Handles high concurrent load by limiting requests per user
    """
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.user_requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove old request timestamps to prevent memory bloat"""
        current_time = time.time()
        
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff_time = current_time - 3600  # Keep last hour
            
            for user_id in list(self.user_requests.keys()):
                self.user_requests[user_id] = [
                    req_time for req_time in self.user_requests[user_id]
                    if req_time > cutoff_time
                ]
                
                # Remove empty entries
                if not self.user_requests[user_id]:
                    del self.user_requests[user_id]
            
            self.last_cleanup = current_time
    
    def is_allowed(self, user_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed for user
        
        Args:
            user_id: User identifier
        
        Returns:
            Tuple of (is_allowed, error_message)
        """
        current_time = time.time()
        
        # Cleanup old requests periodically
        self._cleanup_old_requests()
        
        # Get user's request history
        requests = self.user_requests[user_id]
        
        # Check requests in last minute
        minute_ago = current_time - 60
        recent_requests = [req for req in requests if req > minute_ago]
        
        if len(recent_requests) >= self.requests_per_minute:
            retry_after = int(60 - (current_time - recent_requests[0]))
            return False, f"Rate limit exceeded. Try again in {retry_after} seconds. 🐌"
        
        # Check requests in last hour
        hour_ago = current_time - 3600
        hourly_requests = [req for req in requests if req > hour_ago]
        
        if len(hourly_requests) >= self.requests_per_hour:
            return False, "Hourly rate limit exceeded. Please try again later. ⏰"
        
        # Add current request
        self.user_requests[user_id].append(current_time)
        
        return True, None
    
    def get_rate_limit_info(self, user_id: str) -> Dict:
        """Get rate limit info for user"""
        current_time = time.time()
        requests = self.user_requests[user_id]
        
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        recent_requests = len([req for req in requests if req > minute_ago])
        hourly_requests = len([req for req in requests if req > hour_ago])
        
        return {
            "requests_last_minute": recent_requests,
            "minute_limit": self.requests_per_minute,
            "requests_last_hour": hourly_requests,
            "hour_limit": self.requests_per_hour,
            "remaining_minute": max(0, self.requests_per_minute - recent_requests),
            "remaining_hour": max(0, self.requests_per_hour - hourly_requests)
        }


class CacheManager:
    """
    In-memory cache for frequently accessed data
    Reduces database load for high-traffic endpoints
    """
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, tuple] = {}  # key: (value, expiry_time)
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[any]:
        """Get value from cache"""
        if key in self.cache:
            value, expiry = self.cache[key]
            
            if time.time() < expiry:
                self.hits += 1
                return value
            else:
                # Expired, remove it
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%",
            "cached_items": len(self.cache)
        }
    
    def cleanup_expired(self):
        """Remove expired items from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self.cache.items()
            if current_time >= expiry
        ]
        
        for key in expired_keys:
            del self.cache[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to all requests
    Ensures server can handle high concurrent load
    """
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.exempt_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Get user ID from request (from token or IP)
        user_id = request.client.host  # Use IP as fallback
        
        # Try to get user ID from auth header
        auth_header = request.headers.get("authorization")
        if auth_header:
            # Hash the token to use as user ID
            user_id = hashlib.md5(auth_header.encode()).hexdigest()
        
        # Check rate limit
        is_allowed, error_message = self.rate_limiter.is_allowed(user_id)
        
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": error_message,
                    "rate_limit_info": self.rate_limiter.get_rate_limit_info(user_id)
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        rate_info = self.rate_limiter.get_rate_limit_info(user_id)
        
        response.headers["X-RateLimit-Remaining-Minute"] = str(rate_info["remaining_minute"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(rate_info["remaining_hour"])
        
        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track and log performance metrics
    Helps identify bottlenecks under high load
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.request_times = []
        self.slow_requests = []
        self.total_requests = 0
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        self.total_requests += 1
        self.request_times.append(process_time)
        
        # Keep only last 1000 requests
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
        
        # Track slow requests (> 1 second)
        if process_time > 1.0:
            self.slow_requests.append({
                "path": request.url.path,
                "method": request.method,
                "time": process_time,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only last 100 slow requests
            if len(self.slow_requests) > 100:
                self.slow_requests = self.slow_requests[-100:]
        
        # Add performance header
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        return response
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.request_times:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "slow_requests_count": 0
            }
        
        return {
            "total_requests": self.total_requests,
            "avg_response_time": f"{sum(self.request_times) / len(self.request_times):.3f}s",
            "min_response_time": f"{min(self.request_times):.3f}s",
            "max_response_time": f"{max(self.request_times):.3f}s",
            "slow_requests_count": len(self.slow_requests),
            "recent_slow_requests": self.slow_requests[-10:]  # Last 10 slow requests
        }


# Global instances
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
cache_manager = CacheManager(default_ttl=300)


async def get_rate_limiter() -> RateLimiter:
    """Dependency to get rate limiter instance"""
    return rate_limiter


async def get_cache_manager() -> CacheManager:
    """Dependency to get cache manager instance"""
    return cache_manager
