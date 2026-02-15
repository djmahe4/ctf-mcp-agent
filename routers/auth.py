"""
Authentication Router
Handles user registration, login, and token management
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy import select, or_
from database_sql import get_db
from models import UserCreate, Token, User, UserLogin, SQLUser, UserRole
from auth_utils import (
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import random
import uuid

router = APIRouter()

# Hardcoded Admin Registration Secret (Better in .env, but fulfilling "hardcoded" request)
ADMIN_REGISTRATION_SECRET = "SUPER_SECRET_ADMIN_2024"

# Fun facts for the registration response
FUN_FACTS = [
    "The first computer bug was an actual bug (a moth) found in 1947! 🐛",
    "The first hacker was Nevil Maskelyne, who intercepted a wireless telegraphy demo in 1903! 🕵️",
    "The most expensive computer virus ever was 'MyDoom', causing $38 billion in damage! 💸",
    "Hacking used to mean 'a creative solution to a complex problem'. 💡"
]


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db=Depends(get_db)):
    try:
        """
        Register a new user
        """
        # Check if user already exists
        result = await db.execute(
            select(SQLUser).where(
                or_(
                    SQLUser.username == user.username,
                    SQLUser.email == user.email
                )
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Security Check: Restrict Admin Registration
        if user.role == UserRole.ADMIN or user.role == "admin":
            if user.admin_secret != ADMIN_REGISTRATION_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid admin registration secret. 🚫"
                )
            user_role = UserRole.ADMIN
        else:
            user_role = UserRole.USER

        # Hash password and save to DB
        hashed_password = get_password_hash(user.password)
        user_id = str(uuid.uuid4())
        
        new_user = SQLUser(
            id=user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user_role,
            is_active=True,
            created_at=datetime.utcnow(),
            score=0
        )
        
        db.add(new_user)
        await db.commit()
        
        return {
            "message": "User registered successfully! 🎉 Welcome to the CTF Lab!",
            "username": user.username,
            "user_id": user_id,
            "fun_fact": random.choice(FUN_FACTS)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in register_user: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db=Depends(get_db)
):
    """
    Login with username and password to get access token
    
    - **username**: Username or email
    - **password**: User password
    
    Returns JWT access token
    """
    # Find user by username or email
    result = await db.execute(
        select(SQLUser).where(
            or_(
                SQLUser.username == login_data.username,
                SQLUser.email == login_data.username
            )
        )
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
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
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "score": current_user.score,
        "solved_challenges_count": len(current_user.solved_challenges),
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
        data={"sub": current_user.username, "user_id": current_user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
