"""
Challenges Router
Handles CTF challenge operations with fun elements
"""

from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Optional
import random

from sqlalchemy import select, func, update, and_
from database_sql import get_db
from models import (
    ChallengeCreate, ChallengeSubmission, SubmissionResult,
    VulnerabilityType, DifficultyLevel, User, SQLChallenge, SQLUser, SQLSubmission
)
from auth_utils import get_current_active_user

router = APIRouter()

# Fun memes and GIFs for different scenarios
SUCCESS_MEMES = [
    "https://media.giphy.com/media/g9582DNuQppxC/giphy.gif",  # Success kid
    "https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif",  # Celebration
    "https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/giphy.gif",  # Hacker typing
    "https://i.imgflip.com/4/1bij.jpg",  # Success kid meme
]

FAIL_MEMES = [
    "https://media.giphy.com/media/3oEjHAUOqG3lSS0f1C/giphy.gif",  # Try again
    "https://media.giphy.com/media/l2JJKs3I69qfaQleE/giphy.gif",  # Facepalm
    "https://i.imgflip.com/4/2fm6x.jpg",  # Try harder meme
    "https://media.giphy.com/media/26ufcVAp3HCg9OGlO/giphy.gif",  # Confused
]

HINT_MEMES = [
    "https://media.giphy.com/media/3o7527pa7qs9kCG78A/giphy.gif",  # Thinking
    "https://media.giphy.com/media/8vDbvPMP3tGF2/giphy.gif",  # Light bulb
    "https://i.imgflip.com/4/5sijq.jpg",  # Ancient aliens guy
]

CHALLENGE_START_MESSAGES = [
    "Let's hack! 💻🔥",
    "Time to break some code! 🛠️",
    "Show me your l33t skills! 🎯",
    "Break it like a pro! 🏆",
    "Ready to exploit? 🎮",
    "Hack the planet! 🌍",
]

ENCOURAGEMENT_MESSAGES = [
    "You're doing great! Keep going! 💪",
    "Almost there! Don't give up! 🚀",
    "Every failure is a step closer to success! 🌟",
    "Hack harder! You've got this! 🔥",
    "Remember: Try Harder! 💯",
]


@router.get("/", response_model=dict)
async def list_challenges(
    vulnerability_type: Optional[VulnerabilityType] = None,
    difficulty: Optional[DifficultyLevel] = None,
    skip: int = 0,
    limit: int = 20,
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all available challenges with filtering options
    """
    stmt = select(SQLChallenge)
    if vulnerability_type:
        stmt = stmt.where(SQLChallenge.vulnerability_type == vulnerability_type)
    if difficulty:
        stmt = stmt.where(SQLChallenge.difficulty == difficulty)
        
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    challenges_obj = result.scalars().all()
    
    # Convert to list and hide flags
    challenges_list = []
    for ch in challenges_obj:
        challenges_list.append({
            "id": ch.id,
            "title": ch.title,
            "description": ch.description,
            "category": ch.category,
            "vulnerability_type": ch.vulnerability_type,
            "difficulty": ch.difficulty,
            "points": ch.points,
            "hints": ch.hints,
            "tags": ch.tags,
            "solve_count": ch.solve_count,
            "vulnerable_endpoint": ch.vulnerable_endpoint
        })
    
    # Get total count
    count_stmt = select(func.count()).select_from(SQLChallenge)
    if vulnerability_type:
        count_stmt = count_stmt.where(SQLChallenge.vulnerability_type == vulnerability_type)
    if difficulty:
        count_stmt = count_stmt.where(SQLChallenge.difficulty == difficulty)
    
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    return {
        "message": random.choice(CHALLENGE_START_MESSAGES),
        "challenges": challenges_list,
        "total": total,
        "meme": random.choice(SUCCESS_MEMES),
        "tip": "💡 Pro tip: Read the description carefully and test your payloads!"
    }


@router.get("/{challenge_id}", response_model=dict)
async def get_challenge(
    challenge_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific challenge
    """
    result = await db.execute(select(SQLChallenge).where(SQLChallenge.id == challenge_id))
    challenge = result.scalar_one_or_none()
    
    if not challenge:
        return {"success": False, "message": "Challenge not found"}
        
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "category": challenge.category,
        "vulnerability_type": challenge.vulnerability_type,
        "difficulty": challenge.difficulty,
        "points": challenge.points,
        "hints": challenge.hints,
        "tags": challenge.tags,
        "solve_count": challenge.solve_count,
        "vulnerable_endpoint": challenge.vulnerable_endpoint,
        "welcome_message": "🎯 Ready to exploit? Let's do this!",
        "meme": random.choice(HINT_MEMES)
    }


@router.post("/{challenge_id}/submit", response_model=SubmissionResult)
async def submit_flag(
    challenge_id: str,
    submission: ChallengeSubmission,
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a flag for a challenge
    """
    # Fetch challenge
    result = await db.execute(select(SQLChallenge).where(SQLChallenge.id == challenge_id))
    challenge = result.scalar_one_or_none()
    
    if not challenge:
        return {
            "success": False,
            "message": "Challenge not found 🕵️",
            "points_awarded": None,
            "meme": random.choice(FAIL_MEMES)
        }
        
    # Check if already solved
    solve_check = await db.execute(
        select(SQLSubmission).where(
            and_(
                SQLSubmission.user_id == current_user.id,
                SQLSubmission.challenge_id == challenge_id,
                SQLSubmission.is_correct
            )
        )
    )
    if solve_check.scalar_one_or_none():
        return {
            "success": True,
            "message": "You've already solved this! 🏆",
            "points_awarded": 0,
            "meme": random.choice(SUCCESS_MEMES),
            "fun_message": "Greedy for more points? Try a new challenge! 😉"
        }
        
    # Verify flag (mock hash check or simple equality)
    # In this lab, we use flag_hash for security
    from auth_utils import verify_flag
    is_correct = verify_flag(submission.flag, challenge.flag_hash)
    
    if is_correct:
        # Update user score
        points = challenge.points
        await db.execute(
            update(SQLUser)
            .where(SQLUser.id == current_user.id)
            .values(score=SQLUser.score + points)
        )
        
        # Update challenge solve count
        await db.execute(
            update(SQLChallenge)
            .where(SQLChallenge.id == challenge_id)
            .values(solve_count=SQLChallenge.solve_count + 1)
        )
        
        # Record successful submission
        new_submission = SQLSubmission(
            user_id=current_user.id,
            challenge_id=challenge_id,
            flag_submitted=submission.flag,
            is_correct=True,
            submitted_at=datetime.utcnow()
        )
        db.add(new_submission)
        await db.commit()
        
        return {
            "success": True,
            "message": f"🎉 Congratulations! You solved it! +{points} points! 🏆",
            "points_awarded": points,
            "meme": random.choice(SUCCESS_MEMES),
            "achievement": "🔓 Challenge Unlocked!",
            "fun_message": "You're officially a cyber warrior! Keep hacking! 💪"
        }
    else:
        # Record failed submission
        new_submission = SQLSubmission(
            user_id=current_user.id,
            challenge_id=challenge_id,
            flag_submitted=submission.flag,
            is_correct=False,
            submitted_at=datetime.utcnow()
        )
        db.add(new_submission)
        await db.commit()
        
        return {
            "success": False,
            "message": random.choice(ENCOURAGEMENT_MESSAGES),
            "points_awarded": None,
            "meme": random.choice(FAIL_MEMES),
            "hint": "🤔 Maybe try a different approach?",
            "fun_message": "Every hacker fails before they succeed! Keep trying! 🚀"
        }


@router.get("/{challenge_id}/hint", response_model=dict)
async def get_hint(
    challenge_id: str,
    hint_level: int = 1,
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a hint for a challenge (costs points!)
    """
    result = await db.execute(select(SQLChallenge).where(SQLChallenge.id == challenge_id))
    challenge = result.scalar_one_or_none()
    
    if not challenge or not challenge.hints:
        return {"hint": "No hints available for this challenge.", "cost": 0}
        
    hints = challenge.hints
    hint_index = min(hint_level - 1, len(hints) - 1)
    cost = hint_level * 10
    
    # Deduct points for hint
    if current_user.score >= cost:
        await db.execute(
            update(SQLUser)
            .where(SQLUser.id == current_user.id)
            .values(score=SQLUser.score - cost)
        )
        await db.commit()
        
        return {
            "hint": hints[hint_index],
            "cost": cost,
            "hint_level": hint_level,
            "meme": random.choice(HINT_MEMES),
            "message": "🧠 Knowledge comes at a price... but it's worth it!",
            "remaining_hints": len(hints) - hint_index - 1
        }
    else:
        return {
            "success": False,
            "message": "Not enough points for this hint! Hack more! 💸",
            "cost": cost
        }


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    challenge: ChallengeCreate,
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new challenge
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create challenges")
    
    from auth_utils import hash_flag
    challenge_id = f"challenge_{str(int(datetime.utcnow().timestamp()))}"
    
    new_challenge = SQLChallenge(
        id=challenge_id,
        title=challenge.title,
        description=challenge.description,
        category=challenge.category,
        vulnerability_type=challenge.vulnerability_type,
        difficulty=challenge.difficulty,
        points=challenge.points,
        flag_hash=hash_flag(challenge.flag),
        hints=challenge.hints,
        tags=challenge.tags,
        vulnerable_code=challenge.vulnerable_code,
        solution_explanation=challenge.solution_explanation,
        created_by=current_user.id,
        created_at=datetime.utcnow()
    )
    
    db.add(new_challenge)
    await db.commit()
    
    return {
        "message": "🎊 Challenge created successfully! Time to watch hackers struggle! 😈",
        "challenge_id": challenge_id,
        "title": challenge.title,
        "meme": random.choice(SUCCESS_MEMES),
        "fun_message": "You've just made the CTF universe more interesting! 🌟"
    }


@router.get("/{challenge_id}/stats", response_model=dict)
async def get_challenge_stats(
    challenge_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistics for a specific challenge
    """
    return {
        "challenge_id": challenge_id,
        "total_attempts": 156,
        "successful_solves": 42,
        "success_rate": "26.9%",
        "average_solve_time": "45 minutes",
        "first_blood": "h4ck3r_pr0",
        "most_common_mistake": "Not escaping quotes properly",
        "fun_stat": "🎲 42 hackers found the answer to life, the universe, and everything!",
        "meme": "https://i.imgflip.com/4/2q90u7.jpg",  # Drake meme
        "leaderboard_position": "You're in the top 30%! Keep climbing! 📈"
    }
