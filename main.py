"""
FastAPI Main Application for CTF Security Lab
This module sets up the main FastAPI application with all routes and middleware
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from typing import Optional

from models import (
    AppConfig, DatabaseConfig, SecurityConfig, GoogleGenAIConfig,
    User, UserCreate, UserLogin, Token
)

# Import and include routers (will be created next)
from routers import auth, challenges, vulnerabilities, mcp_agent, eisenhower, leaderboard


# Load environment variables
load_dotenv()

# Global variables for database connection
db_client: Optional[AsyncIOMotorClient] = None
database = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global db_client, database
    
    # Startup: Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_client = AsyncIOMotorClient(mongodb_uri)
    database = db_client[os.getenv("DATABASE_NAME", "ctf_lab")]
    
    # Create indexes
    await database.users.create_index("username", unique=True)
    await database.users.create_index("email", unique=True)
    await database.challenges.create_index("vulnerability_type")
    await database.submissions.create_index([("user_id", 1), ("challenge_id", 1)])
    
    print("✅ Connected to MongoDB Atlas")
    
    yield
    
    # Shutdown: Close database connection
    if db_client:
        db_client.close()
        print("✅ Closed MongoDB connection")


# Initialize FastAPI app
app = FastAPI(
    title="CTF Security Lab API",
    description="A comprehensive CTF platform with multiple vulnerability types",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_database():
    """Dependency to get database instance"""
    return database


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CTF Security Lab API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        if db_client:
            await db_client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return {
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(challenges.router, prefix="/api/v1/challenges", tags=["Challenges"])
app.include_router(vulnerabilities.router, prefix="/api/v1/vulnerabilities", tags=["Vulnerabilities"])
app.include_router(mcp_agent.router, prefix="/api/v1/mcp-agent", tags=["MCP Agent"])
app.include_router(eisenhower.router, prefix="/api/v1/eisenhower", tags=["Eisenhower Matrix"])
app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["Leaderboard"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
