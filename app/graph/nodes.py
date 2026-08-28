import os
from langchain_groq import ChatGroq
from langgraph.graph import END

from app.core.config import settings
from app.graph.state import StudentState, GoalDefine, PriorityTasks


def get_chat_model(model_name: str = None):
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    return ChatGroq(
        model=model_name or settings.GROQ_MODEL,
        api_key=api_key,
        max_tokens=2048,
        temperature=0,
        reasoning_effort="low",
        max_retries=2
    )


def invoke_with_fallback(invoke_fn, prompt):
    """Executes invoke_fn(prompt) with primary model, falling back to secondary if rate-limited."""
    try:
        return invoke_fn(prompt)
    except Exception as primary_error:
        fallback_model = get_chat_model(settings.GROQ_FALLBACK_MODEL)
        try:
            return fallback_model.invoke(prompt)
        except Exception:
            raise primary_error


chat_model = get_chat_model()
fallback_chat_model = get_chat_model(settings.GROQ_FALLBACK_MODEL)

structured_llm = chat_model.with_structured_output(GoalDefine)
structured_fallback = fallback_chat_model.with_structured_output(GoalDefine)

priority_llm = chat_model.with_structured_output(PriorityTasks, method="json_mode")
priority_fallback = fallback_chat_model.with_structured_output(PriorityTasks, method="json_mode")


def analysis_goal(state: StudentState):
    goal = state.get("goal", "")
    prompt = f"""
Analyze this student's goal:

{goal}

Identify:

1. Required skills
2. Learning roadmap
3. First practical project

Make the roadmap practical and ordered.
"""
    try:
        response: GoalDefine = structured_llm.invoke(prompt)
    except Exception:
        response: GoalDefine = structured_fallback.invoke(prompt)

    return {
        "skills": response.skills,
        "roadmap": response.roadmap,
        "first_project": response.first_project,
        "messages": [
            (
                "assistant",
                f"Goal analysis completed for: {goal}"
            )
        ]
    }


def project_planer(state: StudentState):
    project = state.get("first_project", "")
    prompt = f""" 
Create a step-by-step implementation plan for this project:

{project}

Include:
1. Dataset
2. Data preprocessing
3. Model
4. Training
5. Evaluation
6. Deployment
"""
    try:
        response = chat_model.invoke(prompt)
    except Exception:
        response = fallback_chat_model.invoke(prompt)
    return {
        "messages": [response]
    }


def task_planer(state: StudentState):
    prompt = f"""
You are an AI learning task planner.

Student goal:
{state.get("goal", "")}

Required skills:
{state.get("skills", [])}

Learning roadmap:
{state.get("roadmap", [])}

First project:
{state.get("first_project", "")}

Create a practical, ordered learning task plan.

Rules:
1. Start from beginner level.
2. Move toward advanced topics.
3. Make each task specific and actionable.
4. Include practical exercises.
5. Connect tasks to the first project where useful.
6. Do not create unnecessary topics.
7. Do not complete the tasks.
8. Return ONLY the task list.
"""
    try:
        response = chat_model.invoke(prompt)
    except Exception:
        response = fallback_chat_model.invoke(prompt)

    tasks = [
        line.strip("-•* ").strip()
        for line in response.content.split("\n")
        if line.strip() and line.strip()[0] not in ("#",)
    ]

    return {
        "task_plan": response.content,
        "priority_tasks": tasks,
        "messages": [response]
    }


def priority_planer(state: StudentState):
    task_plan = state.get("task_plan", "")
    prompt = f"""
Task plan summary (numbered items only):
{task_plan[:1500]}

Extract and order the actionable, standalone tasks — one clear action per item.
Ignore headings and setup sub-bullets. Merge closely related steps.

First project: {state.get("first_project", "")}

Return your answer as a JSON object with a "tasks" key containing the ordered list, 10-15 items maximum.
"""
    try:
        response: PriorityTasks = priority_llm.invoke(prompt)
    except Exception:
        response: PriorityTasks = priority_fallback.invoke(prompt)
        
    return {
        "priority_tasks": response.tasks,
        "messages": [("assistant", "Priority order set.")]
    }


def mark_progress(state: StudentState):
    if state.get("student_status") == "progressing" and state.get("current_task"):
        completed = list(state.get("completed_tasks", []))
        if state["current_task"] not in completed:
            completed.append(state["current_task"])
        return {"completed_tasks": completed}
    return {}


def adaptive_planner(state: StudentState):
    if state.get("student_status") != "stuck":
        return {}

    current_task = state.get("current_task", "")
    if not current_task:
        return {"student_status": "progressing"}

    prompt = f"""
The student is stuck on this task: {current_task}

Simplify it into 2-4 smaller, more achievable steps.
First project context: {state.get("first_project", "")}

Return a JSON object with a "tasks" key containing only the simplified steps for this one task.
"""
    try:
        try:
            response: PriorityTasks = priority_llm.invoke(prompt)
        except Exception:
            response: PriorityTasks = priority_fallback.invoke(prompt)

        completed_tasks = state.get("completed_tasks", [])
        priority_tasks = list(state.get("priority_tasks", []))
        remaining_start = len(completed_tasks)

        new_priority = (
            priority_tasks[:remaining_start]
            + response.tasks
            + priority_tasks[remaining_start + 1:]
        )

        return {
            "priority_tasks": new_priority,
            "student_status": "progressing",
            "messages": [
                ("assistant", f"Adapted task: '{current_task}' into {len(response.tasks)} simpler steps.")
            ]
        }
    except Exception as e:
        fallback_tasks = [
            f"Step 1: Understand core concepts for {current_task}",
            f"Step 2: Hands-on mini exercise for {current_task}"
        ]
        completed_tasks = state.get("completed_tasks", [])
        priority_tasks = list(state.get("priority_tasks", []))
        remaining_start = len(completed_tasks)
        new_priority = (
            priority_tasks[:remaining_start]
            + fallback_tasks
            + priority_tasks[remaining_start + 1:]
        )
        return {
            "priority_tasks": new_priority,
            "student_status": "progressing",
            "messages": [
                ("assistant", f"Decomposed '{current_task}' into incremental steps.")
            ]
        }


def task_tracker(state: StudentState):
    tasks = state.get("priority_tasks", [])
    completed_tasks = state.get("completed_tasks", [])

    if not tasks:
        return {
            "current_task": "",
            "completed_tasks": completed_tasks,
            "next_task": "",
            "progress": 0
        }

    current_index = len(completed_tasks)

    if current_index >= len(tasks):
        return {
            "current_task": "All tasks completed",
            "completed_tasks": completed_tasks,
            "next_task": "No more tasks left",
            "progress": 100
        }

    current_task = tasks[current_index]

    next_task = (
        tasks[current_index + 1]
        if current_index + 1 < len(tasks)
        else "No more tasks left"
    )

    progress = int(len(completed_tasks) / len(tasks) * 100)

    return {
        "current_task": current_task,
        "completed_tasks": completed_tasks,
        "next_task": next_task,
        "progress": progress
    }


def final_plan(state: StudentState):
    prompt = f"""
Summarize this student's completed learning journey into a clean final report:

Goal: {state.get("goal", "")}
Skills covered: {state.get("skills", [])}
All completed tasks: {state.get("completed_tasks", [])}
First project: {state.get("first_project", "")}

Write a short, encouraging summary and suggest one next-level goal beyond this roadmap.
"""
    try:
        try:
            response = chat_model.invoke(prompt)
        except Exception:
            response = fallback_chat_model.invoke(prompt)
        return {"messages": [response]}
    except Exception:
        return {"messages": [("assistant", "Congratulations on completing your entire learning roadmap!")]}


def route_from_start(state: StudentState) -> str:
    if state.get("priority_tasks"):
        return "mark_progress"
    return "analysis"


def route_after_tracker(state: StudentState) -> str:
    if state.get("progress", 0) >= 100:
        return "final"
    return END
