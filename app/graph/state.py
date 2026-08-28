from typing import Annotated, TypedDict, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class GoalDefine(BaseModel):
    skills: List[str] = Field(description="Required skills to achieve the goal")
    roadmap: List[str] = Field(description="Step-by-step practical learning roadmap")
    first_project: str = Field(description="First practical hands-on project")


class PriorityTasks(BaseModel):
    tasks: List[str] = Field(description="Ordered list of actionable standalone tasks (10-15 items maximum)")


class StudentState(TypedDict, total=False):
    goal: str
    skills: List[str]
    roadmap: List[str]
    first_project: str

    task_plan: str
    priority_tasks: List[str]

    current_task: str
    completed_tasks: List[str]
    next_task: str
    progress: int

    student_status: str  # "progressing" | "stuck"

    messages: Annotated[list, add_messages]
