from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field


class GoalRequest(BaseModel):
    student_id: str = Field(..., example="student_debajyoti_001", description="Unique identifier for the student session")
    goal: str = Field(..., example="I want to become an ML engineer", description="Target learning goal")


class StatusUpdateRequest(BaseModel):
    student_id: str = Field(..., example="student_debajyoti_001", description="Unique identifier for the student session")
    status: Literal["progressing", "stuck"] = Field(
        ...,
        example="progressing",
        description="'progressing' to mark current task complete and move ahead, 'stuck' to trigger adaptive task breakdown"
    )


class MessageItem(BaseModel):
    role: str
    content: str


class StudentStateResponse(BaseModel):
    student_id: str
    goal: Optional[str] = None
    skills: List[str] = []
    roadmap: List[str] = []
    first_project: Optional[str] = None
    task_plan: Optional[str] = None
    priority_tasks: List[str] = []
    current_task: Optional[str] = None
    completed_tasks: List[str] = []
    next_task: Optional[str] = None
    progress: int = 0
    student_status: Optional[str] = None
    recent_messages: List[MessageItem] = []


class HealthResponse(BaseModel):
    status: str = "ok"
    project: str
    version: str
