"""
Leaderboard Router
User rankings and statistics
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from models import Leaderboard, User
from auth_utils import get_current_active_user

router = APIRouter()


@router.get("/", response_model=Leaderboard)
async def get_leaderboard(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """
    🏆 Get the CTF leaderboard
    
    See who's dominating the challenges!
    """
    # Mock leaderboard data
    top_users = [
        {
            "user_id": "1",
            "username": "h4ck3r_pr0",
            "total_score": 2500,
            "solved_challenges": 45,
            "rank": 1,
            "last_solve": "2024-01-20T15:30:00Z"
        },
        {
            "user_id": "2",
            "username": "cyber_ninja",
            "total_score": 2100,
            "solved_challenges": 38,
            "rank": 2,
            "last_solve": "2024-01-20T14:20:00Z"
        },
        {
            "user_id": "3",
            "username": "code_breaker",
            "total_score": 1850,
            "solved_challenges": 32,
            "rank": 3,
            "last_solve": "2024-01-20T12:15:00Z"
        }
    ]
    
    return {
        "top_users": top_users[:limit],
        "total_users": 1247,
        "last_updated": datetime.utcnow()
    }


@router.get("/user/{username}", response_model=dict)
async def get_user_rank(
    username: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Get specific user's ranking and stats
    """
    # Mock user stats
    return {
        "username": username,
        "rank": 15,
        "total_score": 1200,
        "solved_challenges": 24,
        "badges": ["🥇 First Blood", "🔥 Speed Demon", "🧠 Puzzle Master"],
        "recent_solves": [
            {"challenge": "SQL Injection 101", "points": 100, "time": "2024-01-20T10:00:00Z"},
            {"challenge": "XSS Bypass", "points": 250, "time": "2024-01-19T18:30:00Z"}
        ],
        "message": f"🎯 {username} is ranked #15 out of 1247 users! Keep hacking! 💪"
    }
