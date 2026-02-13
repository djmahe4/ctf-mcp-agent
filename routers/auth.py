"""
Authentication Router
Handles user registration, login, and token management
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from models import User, UserCreate, Token
from auth_utils import (
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db=Depends(lambda: None)):
    """
    Register a new user
    
    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Strong password (min 8 chars, uppercase, digit)
    - **full_name**: Optional full name
    """
    # In production, replace with actual database operations
    return {
        "message": "User registered successfully! 🎉 Welcome to the CTF Lab!",
        "username": user.username,
        "fun_fact": "Did you know? The first computer bug was an actual bug (a moth) found in a computer in 1947! 🐛"
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(lambda: None)
):
    """
    Login with username and password to get access token
    
    - **username**: Username or email
    - **password**: User password
    
    Returns JWT access token
    """
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username, "user_id": "mock_id"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    
    Requires authentication token
    """
    return {
        "username": current_user.username if hasattr(current_user, 'username') else "mock_user",
        "message": "User authenticated successfully"
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """
    Refresh access token
    
    Requires valid authentication token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username, "user_id": current_user.user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
