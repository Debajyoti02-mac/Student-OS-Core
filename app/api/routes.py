from fastapi import APIRouter, HTTPException, status
from typing import List

from app.graph.builder import agent_app
from app.models.schemas import (
    GoalRequest,
    StatusUpdateRequest,
    StudentStateResponse,
    MessageItem,
    HealthResponse
)
from app.core.config import settings

router = APIRouter()


def format_messages(messages: list) -> List[MessageItem]:
    formatted: List[MessageItem] = []
    if not messages:
        return formatted

    for msg in messages:
        if isinstance(msg, tuple) and len(msg) >= 2:
            formatted.append(MessageItem(role=str(msg[0]), content=str(msg[1])))
        elif hasattr(msg, "content"):
            role = getattr(msg, "type", "assistant")
            formatted.append(MessageItem(role=role, content=str(msg.content)))
        elif isinstance(msg, dict):
            formatted.append(MessageItem(role=msg.get("role", "unknown"), content=str(msg.get("content", ""))))
    return formatted


def state_to_response(student_id: str, state_values: dict) -> StudentStateResponse:
    messages = state_values.get("messages", [])
    return StudentStateResponse(
        student_id=student_id,
        goal=state_values.get("goal"),
        skills=state_values.get("skills", []),
        roadmap=state_values.get("roadmap", []),
        first_project=state_values.get("first_project"),
        task_plan=state_values.get("task_plan"),
        priority_tasks=state_values.get("priority_tasks", []),
        current_task=state_values.get("current_task"),
        completed_tasks=state_values.get("completed_tasks", []),
        next_task=state_values.get("next_task"),
        progress=state_values.get("progress", 0),
        student_status=state_values.get("student_status"),
        recent_messages=format_messages(messages)
    )


@router.post(
    "/student/goal",
    response_model=StudentStateResponse,
    summary="Initialize or set a student goal",
    description="Analyzes the student's learning goal, builds roadmap, first project, and initial priority tasks."
)
async def set_student_goal(req: GoalRequest):
    try:
        config = {"configurable": {"thread_id": req.student_id}}
        initial_input = {
            "goal": req.goal,
            "skills": [],
            "roadmap": [],
            "first_project": "",
            "task_plan": "",
            "priority_tasks": [],
            "current_task": "",
            "completed_tasks": [],
            "next_task": "",
            "progress": 0,
            "student_status": "progressing",
            "messages": [("human", req.goal)]
        }
        result = agent_app.invoke(initial_input, config=config)
        return state_to_response(req.student_id, result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process goal: {str(e)}"
        )


@router.post(
    "/student/status",
    response_model=StudentStateResponse,
    summary="Update student progress or stuck status",
    description="Pass 'progressing' to complete the current task and advance, or 'stuck' to adaptively decompose the task into simpler steps."
)
async def update_student_status(req: StatusUpdateRequest):
    try:
        config = {"configurable": {"thread_id": req.student_id}}
        
        # Verify thread exists
        current_state = agent_app.get_state(config=config)
        if not current_state or not current_state.values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active session found for student ID: {req.student_id}. Please initialize a goal first."
            )
        
        update_input = {"student_status": req.status}
        result = agent_app.invoke(update_input, config=config)
        return state_to_response(req.student_id, result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update student status: {str(e)}"
        )


@router.get(
    "/student/state/{student_id}",
    response_model=StudentStateResponse,
    summary="Get current state of a student",
    description="Retrieves the current learning roadmap, progress, and task details from checkpoints."
)
async def get_student_state(student_id: str):
    try:
        config = {"configurable": {"thread_id": student_id}}
        state = agent_app.get_state(config=config)
        if not state or not state.values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student session '{student_id}' not found."
            )
        return state_to_response(student_id, state.values)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve student state: {str(e)}"
        )


@router.get(
    "/student/history/{student_id}",
    response_model=List[MessageItem],
    summary="Get message history for a student",
    description="Retrieves chronological interaction messages and agent reasoning outputs."
)
async def get_student_history(student_id: str):
    try:
        config = {"configurable": {"thread_id": student_id}}
        state = agent_app.get_state(config=config)
        if not state or not state.values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student session '{student_id}' not found."
            )
        messages = state.values.get("messages", [])
        return format_messages(messages)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve student history: {str(e)}"
        )
