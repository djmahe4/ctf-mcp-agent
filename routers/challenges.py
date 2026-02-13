"""
Challenges Router
Handles CTF challenge operations with fun elements
"""

from fastapi import APIRouter, Depends, status
from typing import Optional
import random

from models import (
    ChallengeCreate, ChallengeSubmission, SubmissionResult,
    VulnerabilityType, DifficultyLevel, User
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
    current_user: User = Depends(get_current_active_user)
):
    """
    List all available challenges with filtering options
    
    Returns a fun welcome message with challenges!
    """
    # Mock challenge data
    challenges = [
        {
            "id": "1",
            "title": "Easy SQL Injection",
            "description": "Find the hidden flag in the database!",
            "vulnerability_type": "sql_injection",
            "difficulty": "easy",
            "points": 100,
            "solve_count": 42,
            "tags": ["beginner", "database", "sqli"]
        },
        {
            "id": "2",
            "title": "XSS Cookie Stealer",
            "description": "Steal the admin's cookies using XSS!",
            "vulnerability_type": "xss",
            "difficulty": "medium",
            "points": 250,
            "solve_count": 28,
            "tags": ["web", "javascript", "cookies"]
        },
        {
            "id": "3",
            "title": "Command Injection Master",
            "description": "Execute commands on the remote server!",
            "vulnerability_type": "command_injection",
            "difficulty": "hard",
            "points": 500,
            "solve_count": 15,
            "tags": ["linux", "shell", "rce"]
        }
    ]
    
    return {
        "message": random.choice(CHALLENGE_START_MESSAGES),
        "challenges": challenges,
        "total": len(challenges),
        "meme": random.choice(SUCCESS_MEMES),
        "tip": "💡 Pro tip: Read the description carefully and test your payloads!"
    }


@router.get("/{challenge_id}", response_model=dict)
async def get_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific challenge
    """
    # Mock challenge data
    challenge = {
        "id": challenge_id,
        "title": "Easy SQL Injection",
        "description": "Find the hidden flag in the database! The admin user has the flag.",
        "vulnerability_type": "sql_injection",
        "difficulty": "easy",
        "points": 100,
        "hints": [
            "Try using ' OR '1'='1",
            "Look for the admin user in the users table",
            "The flag is in the 'secret' column"
        ],
        "vulnerable_endpoint": "/api/v1/vulnerabilities/sql-injection/search",
        "tags": ["beginner", "database", "sqli"],
        "welcome_message": "🎯 Ready to exploit? Let's do this!",
        "fun_fact": "SQL Injection was discovered in 1998 and is still in the OWASP Top 10! 🏆",
        "meme": random.choice(HINT_MEMES)
    }
    
    return challenge


@router.post("/{challenge_id}/submit", response_model=SubmissionResult)
async def submit_flag(
    challenge_id: str,
    submission: ChallengeSubmission,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a flag for a challenge
    
    Returns success/failure with fun memes and messages!
    """
    # Mock flag verification (in production, verify against database)
    correct_flags = {
        "1": "FLAG{sql_1nj3ct10n_m4st3r}",
        "2": "FLAG{xss_c00k13_st34l3r}",
        "3": "FLAG{c0mm4nd_1nj3ct10n_pwn3d}"
    }
    
    is_correct = submission.flag == correct_flags.get(challenge_id, "")
    
    if is_correct:
        return {
            "success": True,
            "message": f"🎉 Congratulations! You solved it! +{100} points! 🏆",
            "points_awarded": 100,
            "meme": random.choice(SUCCESS_MEMES),
            "achievement": "🔓 Challenge Unlocked!",
            "fun_message": "You're officially a cyber warrior! Keep hacking! 💪"
        }
    else:
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
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a hint for a challenge (costs points!)
    
    Returns hints with fun elements!
    """
    hints = {
        "1": [
            "🔍 Hint 1: Look for input fields that interact with databases",
            "🔍 Hint 2: Try using SQL comments (--) to bypass authentication",
            "🔍 Hint 3: The payload is: ' OR '1'='1' --"
        ],
        "2": [
            "🔍 Hint 1: Think about where JavaScript code gets executed",
            "🔍 Hint 2: Try <script>alert(1)</script>",
            "🔍 Hint 3: Steal cookies using document.cookie"
        ]
    }
    
    challenge_hints = hints.get(challenge_id, ["No hints available"])
    hint_index = min(hint_level - 1, len(challenge_hints) - 1)
    
    cost = hint_level * 10  # Each hint costs more
    
    return {
        "hint": challenge_hints[hint_index],
        "cost": cost,
        "hint_level": hint_level,
        "meme": random.choice(HINT_MEMES),
        "message": "🧠 Knowledge comes at a price... but it's worth it!",
        "remaining_hints": len(challenge_hints) - hint_index - 1
    }


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    challenge: ChallengeCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new challenge (admin only)
    
    Returns success message with celebration!
    """
    # In production, check if user is admin and create challenge in database
    
    return {
        "message": "🎊 Challenge created successfully! Time to watch hackers struggle! 😈",
        "challenge_id": "new_challenge_123",
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
