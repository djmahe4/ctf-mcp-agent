"""
Eisenhower Matrix Router
Task prioritization using the Eisenhower Decision Matrix
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from models import EisenhowerTask, TaskPriority, TaskUpdate, User
from auth_utils import get_current_active_user

router = APIRouter()


@router.get("/tasks", response_model=dict)
async def get_all_tasks(
    priority: Optional[TaskPriority] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    📋 Get all tasks organized by Eisenhower Matrix
    
    Returns tasks categorized by priority quadrant
    """
    # Mock tasks
    tasks = {
        "do_first": [
            {
                "id": "1",
                "title": "Fix critical SQL injection",
                "description": "Production vulnerability needs immediate fix",
                "is_urgent": True,
                "is_important": True,
                "priority": "do_first",
                "deadline": "2024-01-21T12:00:00Z"
            }
        ],
        "schedule": [
            {
                "id": "2",
                "title": "Study XSS prevention techniques",
                "description": "Important for long-term security knowledge",
                "is_urgent": False,
                "is_important": True,
                "priority": "schedule",
                "deadline": "2024-01-25T12:00:00Z"
            }
        ],
        "delegate": [
            {
                "id": "3",
                "title": "Update documentation",
                "description": "Needs to be done but not critical",
                "is_urgent": True,
                "is_important": False,
                "priority": "delegate",
                "deadline": None
            }
        ],
        "eliminate": [
            {
                "id": "4",
                "title": "Reorganize file structure",
                "description": "Nice to have but not necessary",
                "is_urgent": False,
                "is_important": False,
                "priority": "eliminate",
                "deadline": None
            }
        ]
    }
    
    if priority:
        return {
            "priority": priority,
            "tasks": tasks.get(priority, []),
            "emoji": "🔴" if priority == "do_first" else "📅" if priority == "schedule" else "👥" if priority == "delegate" else "🗑️"
        }
    
    return {
        "message": "📊 Eisenhower Decision Matrix - All Tasks",
        "matrix": tasks,
        "legend": {
            "do_first": "🔴 Urgent & Important - Do it NOW!",
            "schedule": "📅 Important, Not Urgent - Schedule it",
            "delegate": "👥 Urgent, Not Important - Delegate it",
            "eliminate": "🗑️ Neither - Eliminate it"
        }
    }


@router.post("/tasks", response_model=dict)
async def create_task(
    task: EisenhowerTask,
    current_user: User = Depends(get_current_active_user)
):
    """
    ➕ Create a new task with automatic priority assignment
    
    Priority is automatically calculated based on urgency and importance
    """
    return {
        "success": True,
        "message": "✅ Task created and prioritized!",
        "task": {
            "id": "new_task_123",
            "title": task.title,
            "priority": task.priority,
            "emoji": "🔴" if task.priority == TaskPriority.DO_FIRST else "📅"
        }
    }
