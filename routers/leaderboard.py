"""
Leaderboard Router
User rankings and statistics
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from database_sql import get_db
from models import Leaderboard, User, SQLUser, SQLSubmission
from auth_utils import get_current_active_user

router = APIRouter()


@router.get("/", response_model=Leaderboard)
async def get_leaderboard(
    limit: int = 10,
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    🏆 Get the CTF leaderboard
    """
    # Fetch top users sorted by score and then by username
    stmt = select(SQLUser).order_by(SQLUser.score.desc(), SQLUser.username.asc()).limit(limit)
    result = await db.execute(stmt)
    users_list = result.scalars().all()
    
    top_users = []
    for i, u in enumerate(users_list):
        # Count solved challenges for this user
        count_stmt = select(func.count(SQLSubmission.id)).where(
            and_(
                SQLSubmission.user_id == u.id,
                SQLSubmission.is_correct
            )
        )
        solved_result = await db.execute(count_stmt)
        solved_count = solved_result.scalar()
        
        top_users.append({
            "user_id": u.id,
            "username": u.username,
            "total_score": u.score or 0,
            "solved_challenges": solved_count,
            "rank": i + 1,
            "last_solve": datetime.utcnow().isoformat()
        })
    
    # Get total users count
    total_users_stmt = select(func.count()).select_from(SQLUser)
    total_result = await db.execute(total_users_stmt)
    total_users = total_result.scalar()
    
    return {
        "top_users": top_users,
        "total_users": total_users,
        "last_updated": datetime.utcnow()
    }


@router.get("/user/{username}", response_model=dict)
async def get_user_rank(
    username: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Get specific user's ranking and stats
    """
    result = await db.execute(select(SQLUser).where(SQLUser.username == username))
    user_obj = result.scalar_one_or_none()
    
    if not user_obj:
        return {"success": False, "message": "User not found"}
        
    # Calculate rank
    higher_scores_stmt = select(func.count()).select_from(SQLUser).where(SQLUser.score > user_obj.score)
    higher_result = await db.execute(higher_scores_stmt)
    rank = higher_result.scalar() + 1
    
    total_users_stmt = select(func.count()).select_from(SQLUser)
    total_result = await db.execute(total_users_stmt)
    total_users = total_result.scalar()
    
    # Get recent solves
    recent_solves_stmt = (
        select(SQLSubmission)
        .where(and_(SQLSubmission.user_id == user_obj.id, SQLSubmission.is_correct))
        .order_by(SQLSubmission.submitted_at.desc())
        .limit(3)
    )
    recent_result = await db.execute(recent_solves_stmt)
    recent_solves = recent_result.scalars().all()
    
    return {
        "username": username,
        "rank": rank,
        "total_score": user_obj.score or 0,
        "solved_challenges": 0, # Placeholder or count
        "badges": ["🛡️ Verified", "🧪 Tester"],
        "recent_solves": [
            {"challenge_id": s.challenge_id, "points": 100, "time": s.submitted_at.isoformat()}
            for s in recent_solves
        ],
        "message": f"🎯 {username} is ranked #{rank} out of {total_users} users! Keep hacking! 💪"
    }
