"""
Main FastAPI Application for CTF Security Lab
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import traceback
from datetime import datetime

from database_sql import init_sql_db
from routers import auth, challenges, vulnerabilities, mcp_agent, eisenhower, leaderboard, admin

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Initialize SQL Database
    await init_sql_db()
    
    yield


# Initialize FastAPI app
app = FastAPI(
    title="CTF Security Lab API",
    description="A powerful CTF simulation platform with AI orchestration",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Global exception: {str(exc)}\n{traceback.format_exc()}"
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(f"--- {datetime.utcnow()} ---\n{error_msg}\n")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Check error.log for details.", "error": str(exc)},
    )

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Ensure static directory exists
if not os.path.exists("static"):
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- HTML Template Routes ---

@app.get("/", tags=["Frontend"])
async def serve_home(request: Request):
    """Serve home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", tags=["Frontend"])
async def serve_login(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", tags=["Frontend"])
async def serve_register(request: Request):
    """Serve register page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/challenges", tags=["Frontend"])
async def serve_challenges(request: Request):
    """Serve challenges page"""
    return templates.TemplateResponse("challenges.html", {"request": request})

@app.get("/profile", tags=["Frontend"])
async def serve_profile(request: Request):
    """Serve user profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/leaderboard-ui", tags=["Frontend"])
async def serve_leaderboard_ui(request: Request):
    """Serve leaderboard page"""
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


# API Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(challenges.router, prefix="/api/v1/challenges", tags=["Challenges"])
app.include_router(vulnerabilities.router, prefix="/api/v1/vulnerabilities", tags=["Vulnerabilities"])
app.include_router(mcp_agent.router, prefix="/api/v1/mcp-agent", tags=["MCP Agent"])
app.include_router(eisenhower.router, prefix="/api/v1/eisenhower", tags=["Eisenhower Matrix"])
app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["Leaderboard"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin Operations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
