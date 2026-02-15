"""
Role-Based Access Control (RBAC) and Admin Dependencies
Implements admin-only access and permission checks
"""

from fastapi import Depends, HTTPException, status
from typing import Callable
from functools import wraps

from models import User, UserRole
from auth_utils import get_current_active_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to verify user has admin role
    
    Raises:
        HTTPException: If user is not an admin
    
    Returns:
        User object if admin
    """
    # Check if user has admin role
    user_role = getattr(current_user, 'role', None)
    
    if user_role != UserRole.ADMIN and user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required. 🚫",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


async def get_current_moderator_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to verify user has moderator or admin role
    
    Raises:
        HTTPException: If user is not a moderator or admin
    
    Returns:
        User object if moderator or admin
    """
    user_role = getattr(current_user, 'role', None)
    
    allowed_roles = [UserRole.ADMIN, UserRole.MODERATOR, "admin", "moderator"]
    
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Moderator or Admin privileges required. 🚫"
        )
    
    return current_user


def require_admin(func: Callable) -> Callable:
    """
    Decorator to require admin access for a function
    
    Usage:
        @require_admin
        async def my_admin_function():
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract current_user from kwargs
        current_user = kwargs.get('current_user')
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        user_role = getattr(current_user, 'role', None)
        
        if user_role != UserRole.ADMIN and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required 🔐"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def check_permission(required_permission: str):
    """
    Decorator to check specific permissions
    
    Args:
        required_permission: Permission name required
    
    Usage:
        @check_permission("create_challenge")
        async def create_challenge():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check user permissions (would be stored in database in production)
            user_permissions = getattr(current_user, 'permissions', [])
            
            if required_permission not in user_permissions:
                user_role = getattr(current_user, 'role', None)
                
                # Admins have all permissions
                if user_role != UserRole.ADMIN and user_role != "admin":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission '{required_permission}' required 🔒"
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class PermissionChecker:
    """
    Permission checker class for more complex permission logic
    """
    
    ADMIN_ONLY_ENDPOINTS = [
        "/api/v1/admin/users",
        "/api/v1/admin/challenges/create",
        "/api/v1/admin/system",
        "/api/v1/admin/stats",
        "/api/v1/admin/flags",
    ]
    
    MODERATOR_ENDPOINTS = [
        "/api/v1/challenges/create",
        "/api/v1/challenges/edit",
        "/api/v1/challenges/delete",
    ]
    
    @staticmethod
    def is_admin_only_endpoint(path: str) -> bool:
        """Check if endpoint requires admin access"""
        return any(path.startswith(endpoint) for endpoint in PermissionChecker.ADMIN_ONLY_ENDPOINTS)
    
    @staticmethod
    def is_moderator_endpoint(path: str) -> bool:
        """Check if endpoint requires moderator access"""
        return any(path.startswith(endpoint) for endpoint in PermissionChecker.MODERATOR_ENDPOINTS)
    
    @staticmethod
    def check_access(user_role: str, endpoint: str) -> bool:
        """
        Check if user role has access to endpoint
        
        Args:
            user_role: User's role
            endpoint: Endpoint path
        
        Returns:
            True if access allowed, False otherwise
        """
        if PermissionChecker.is_admin_only_endpoint(endpoint):
            return user_role == UserRole.ADMIN or user_role == "admin"
        
        if PermissionChecker.is_moderator_endpoint(endpoint):
            return user_role in [UserRole.ADMIN, UserRole.MODERATOR, "admin", "moderator"]
        
        return True
