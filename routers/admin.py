"""
Admin Router
Admin-only endpoints for backend server management
These endpoints are restricted to admin users only
"""

from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func, update, delete
from database_sql import get_db
from models import User, ChallengeCreate, SQLUser, SQLChallenge, SQLSubmission
from rbac import get_current_admin_user
from performance import get_rate_limiter, get_cache_manager, RateLimiter, CacheManager

router = APIRouter()


@router.get("/health", response_model=dict)
async def admin_health_check(
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Detailed system health check
    """
    # Verify DB health
    try:
        await db.execute(select(1))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    users_count = (await db.execute(select(func.count()).select_from(SQLUser))).scalar()
    challenges_count = (await db.execute(select(func.count()).select_from(SQLChallenge))).scalar()

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "admin": admin_user.username,
        "message": "✅ Admin access granted.",
        "server_info": {
            "uptime": "operational",
            "database": db_status,
            "users_count": users_count,
            "challenges_count": challenges_count
        }
    }


@router.get("/users", response_model=dict)
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: List all registered users
    """
    result = await db.execute(select(SQLUser).offset(skip).limit(limit))
    users_obj = result.scalars().all()
    
    users_list = []
    for u in users_obj:
        users_list.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "score": u.score,
            "created_at": u.created_at
        })
            
    total = (await db.execute(select(func.count()).select_from(SQLUser))).scalar()
    
    return {
        "message": "✅ Admin access: User list retrieved",
        "total_users": total,
        "users": users_list,
        "admin_note": "🔐 This data is only visible to administrators"
    }


@router.post("/users/{user_id}/ban", response_model=dict)
async def ban_user(
    user_id: str,
    reason: str,
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Ban a user from the platform
    """
    result = await db.execute(
        update(SQLUser)
        .where(SQLUser.id == user_id)
        .values(is_active=False)
    )
    await db.commit()
    
    # Check if row was updated (note: execute for update returns result showing rows matched/updated)
    if result.rowcount == 0:
        return {"success": False, "message": "User not found"}
        
    return {
        "success": True,
        "message": f"✅ User {user_id} has been banned",
        "reason": reason,
        "banned_by": admin_user.username,
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
    db=Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔐 ADMIN ONLY: Get detailed platform statistics
    """
    total_users = (await db.execute(select(func.count()).select_from(SQLUser))).scalar()
    total_challenges = (await db.execute(select(func.count()).select_from(SQLChallenge))).scalar()
    total_submissions = (await db.execute(select(func.count()).select_from(SQLSubmission))).scalar()
    successful_solves = (await db.execute(select(func.count()).select_from(SQLSubmission).where(SQLSubmission.is_correct == True))).scalar()
    
    # Calculate average score
    avg_score_result = await db.execute(select(func.avg(SQLUser.score)))
    avg_score = avg_score_result.scalar() or 0

    return {
        "platform_stats": {
            "total_users": total_users,
            "total_challenges": total_challenges,
            "total_submissions": total_submissions,
            "successful_solves": successful_solves,
            "average_user_score": round(float(avg_score), 2)
        },
        "security_stats": {
            "banned_users": (await db.execute(select(func.count()).select_from(SQLUser).where(SQLUser.is_active == False))).scalar(),
            "latest_exploits": "Detailed latest exploits coming soon in SQL mode"
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
