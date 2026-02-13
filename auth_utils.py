"""
Authentication and Security Utilities
This module handles JWT token generation, password hashing, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

import hashlib

from sqlalchemy import select
from models import User, TokenData, SQLUser
from database_sql import get_db

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # BCrypt has a 72-byte limit. We handle this by using the truncated form if needed.
    if len(plain_password) > 72:
        plain_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    if len(password) > 72:
        password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if username is None:
            return None
        
        token_data = TokenData(username=username, user_id=user_id)
        return token_data
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
) -> User:
    """Get the current authenticated user from the database"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    
    # Query SQLAlchemy for the user
    result = await db.execute(select(SQLUser).where(SQLUser.id == token_data.user_id))
    user_obj = result.scalar_one_or_none()
    
    if user_obj is None:
        # Check by username if ID fails (for migration/legacy tokens)
        result = await db.execute(select(SQLUser).where(SQLUser.username == token_data.username))
        user_obj = result.scalar_one_or_none()
    
    if user_obj is None:
        raise credentials_exception
    
    # Convert SQLAlchemy object to Pydantic User model
    return User.model_validate(user_obj)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user and check status"""
    if isinstance(current_user, TokenData):
        # Fallback for mock/test cases where DB is bypassed but token is valid
        return current_user
        
    if not getattr(current_user, 'is_active', True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def hash_flag(flag: str) -> str:
    """Hash a CTF flag for secure storage"""
    return get_password_hash(flag)


def verify_flag(plain_flag: str, hashed_flag: str) -> bool:
    """Verify a submitted flag against its hash"""
    return verify_password(plain_flag, hashed_flag)
