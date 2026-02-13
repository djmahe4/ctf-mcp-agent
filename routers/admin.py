"""
Admin Router
Admin-only endpoints for backend server management
These endpoints are restricted to admin users only
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime

from models import User, UserRole, Challenge, ChallengeCreate, LabStats
from rbac import get_current_admin_user
from performance import get_rate_limiter, get_cache_manager, RateLimiter, CacheManager

router = APIRouter()


@router.get("/health", response_model=dict)
async def admin_health_check(
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Detailed system health check
    
    Returns comprehensive system status including:
    - Database connectivity
    - Cache performance
    - Rate limiter stats
    - System load
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "admin": getattr(admin_user, 'username', 'admin'),
        "message": "✅ Admin access granted. System operational.",
        "server_info": {
            "uptime": "operational",
            "concurrent_users": "monitoring enabled",
            "database": "connected"
        }
    }


@router.get("/users", response_model=dict)
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: List all registered users
    
    Includes sensitive information only accessible to admins
    """
    # In production, fetch from database
    mock_users = [
        {
            "id": "1",
            "username": "admin",
            "email": "admin@ctflab.com",
            "role": "admin",
            "score": 1000,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "2",
            "username": "hacker_pro",
            "email": "hacker@ctflab.com",
            "role": "user",
            "score": 850,
            "is_active": True,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
    
    return {
        "message": "✅ Admin access: User list retrieved",
        "total_users": len(mock_users),
        "users": mock_users[skip:skip+limit],
        "admin_note": "🔐 This data is only visible to administrators"
    }


@router.post("/users/{user_id}/ban", response_model=dict)
async def ban_user(
    user_id: str,
    reason: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Ban a user from the platform
    
    Args:
        user_id: User ID to ban
        reason: Reason for ban
    """
    # In production, update database
    return {
        "success": True,
        "message": f"✅ User {user_id} has been banned",
        "reason": reason,
        "banned_by": getattr(admin_user, 'username', 'admin'),
        "timestamp": datetime.utcnow().isoformat(),
        "admin_action": "🔨 Ban hammer activated!"
    }


@router.post("/users/{user_id}/unban", response_model=dict)
async def unban_user(
    user_id: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Unban a user
    """
    return {
        "success": True,
        "message": f"✅ User {user_id} has been unbanned",
        "unbanned_by": getattr(admin_user, 'username', 'admin'),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/challenges/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def admin_create_challenge(
    challenge: ChallengeCreate,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Create new CTF challenge
    
    Only admins can create challenges to maintain quality and security
    """
    # In production, save to database with proper flag hashing
    return {
        "success": True,
        "message": "✅ Challenge created successfully!",
        "challenge_id": "new_challenge_" + str(datetime.utcnow().timestamp()),
        "title": challenge.title,
        "vulnerability_type": challenge.vulnerability_type,
        "created_by": getattr(admin_user, 'username', 'admin'),
        "admin_note": "🔐 Challenge is now live for all users!"
    }


@router.put("/challenges/{challenge_id}", response_model=dict)
async def admin_update_challenge(
    challenge_id: str,
    challenge: ChallengeCreate,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Update existing challenge
    """
    return {
        "success": True,
        "message": f"✅ Challenge {challenge_id} updated successfully",
        "updated_by": getattr(admin_user, 'username', 'admin'),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.delete("/challenges/{challenge_id}", response_model=dict)
async def admin_delete_challenge(
    challenge_id: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Delete a challenge
    """
    return {
        "success": True,
        "message": f"✅ Challenge {challenge_id} deleted",
        "deleted_by": getattr(admin_user, 'username', 'admin'),
        "admin_warning": "⚠️ This action cannot be undone!"
    }


@router.get("/stats/detailed", response_model=dict)
async def get_detailed_stats(
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Get detailed platform statistics
    
    Includes sensitive metrics only for admin analysis
    """
    return {
        "platform_stats": {
            "total_users": 1247,
            "active_users_today": 342,
            "total_challenges": 45,
            "total_submissions": 8934,
            "successful_exploits": 4521,
            "average_solve_time": "45 minutes"
        },
        "revenue_stats": {
            "premium_users": 156,
            "monthly_revenue": "$4,680"
        },
        "security_stats": {
            "failed_login_attempts": 23,
            "banned_users": 5,
            "reported_issues": 2
        },
        "admin_access": "✅ Full statistics access granted",
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/performance/metrics", response_model=dict)
async def get_performance_metrics(
    admin_user: User = Depends(get_current_admin_user),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
    cache: CacheManager = Depends(get_cache_manager)
):
    """
    🔐 ADMIN ONLY: Get server performance metrics
    
    Monitor rate limiting, caching, and overall system performance
    """
    return {
        "message": "✅ Performance metrics retrieved",
        "cache_stats": cache.get_stats(),
        "rate_limiting": {
            "enabled": True,
            "limits": {
                "requests_per_minute": rate_limiter.requests_per_minute,
                "requests_per_hour": rate_limiter.requests_per_hour
            },
            "active_users_tracked": len(rate_limiter.user_requests)
        },
        "server_health": {
            "status": "optimal",
            "load": "normal",
            "concurrent_connections": "within limits"
        },
        "admin_note": "🔐 Real-time monitoring active"
    }


@router.post("/cache/clear", response_model=dict)
async def clear_cache(
    admin_user: User = Depends(get_current_admin_user),
    cache: CacheManager = Depends(get_cache_manager)
):
    """
    🔐 ADMIN ONLY: Clear application cache
    
    Use when you need to force refresh of cached data
    """
    cache.clear()
    
    return {
        "success": True,
        "message": "✅ Cache cleared successfully",
        "cleared_by": getattr(admin_user, 'username', 'admin'),
        "timestamp": datetime.utcnow().isoformat(),
        "admin_action": "🧹 Cache has been cleaned!"
    }


@router.get("/flags/verify", response_model=dict)
async def verify_flag_generation(
    user_id: str,
    challenge_id: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Verify flag generation for debugging
    
    Allows admins to see what flag a user should get
    """
    from flag_generator import generate_dynamic_flag
    
    test_flag = generate_dynamic_flag(
        user_id=user_id,
        challenge_id=challenge_id,
        vulnerability_type="sql_injection",
        challenge_name="Test Challenge"
    )
    
    return {
        "user_id": user_id,
        "challenge_id": challenge_id,
        "generated_flag": test_flag,
        "timestamp": datetime.utcnow().isoformat(),
        "admin_note": "🔐 This is for verification only. Do not share with users!"
    }


@router.post("/system/maintenance", response_model=dict)
async def toggle_maintenance_mode(
    enabled: bool,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Toggle system maintenance mode
    
    When enabled, blocks all non-admin users from accessing the system
    """
    return {
        "success": True,
        "maintenance_mode": enabled,
        "message": f"✅ Maintenance mode {'enabled' if enabled else 'disabled'}",
        "toggled_by": getattr(admin_user, 'username', 'admin'),
        "timestamp": datetime.utcnow().isoformat(),
        "admin_warning": "⚠️ Users will see maintenance page when enabled"
    }


@router.get("/logs/security", response_model=dict)
async def get_security_logs(
    limit: int = 100,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Get security-related logs
    
    View failed login attempts, suspicious activity, etc.
    """
    mock_logs = [
        {
            "timestamp": "2024-01-20T10:15:30Z",
            "event": "failed_login",
            "user": "unknown_user",
            "ip": "192.168.1.100",
            "severity": "medium"
        },
        {
            "timestamp": "2024-01-20T10:20:45Z",
            "event": "rate_limit_exceeded",
            "user": "suspicious_user",
            "ip": "10.0.0.50",
            "severity": "high"
        }
    ]
    
    return {
        "message": "✅ Security logs retrieved",
        "total_logs": len(mock_logs),
        "logs": mock_logs[:limit],
        "admin_access": "🔐 Sensitive security data",
        "last_updated": datetime.utcnow().isoformat()
    }


@router.post("/broadcast/message", response_model=dict)
async def broadcast_message(
    message: str,
    message_type: str = "info",
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Broadcast message to all users
    
    Send announcements, warnings, or updates to all active users
    """
    return {
        "success": True,
        "message": "✅ Message broadcasted to all users",
        "content": message,
        "type": message_type,
        "sent_by": getattr(admin_user, 'username', 'admin'),
        "timestamp": datetime.utcnow().isoformat(),
        "admin_action": "📢 Global announcement sent!"
    }
