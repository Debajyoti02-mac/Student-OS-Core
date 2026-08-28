import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END

from app.core.config import settings
from app.graph.state import StudentState
from app.graph.nodes import (
    analysis_goal,
    project_planer,
    task_planer,
    priority_planer,
    task_tracker,
    mark_progress,
    adaptive_planner,
    final_plan,
    route_from_start,
    route_after_tracker
)


def create_graph(db_path: str = None):
    database_path = db_path or settings.DB_PATH
    conn = sqlite3.connect(database_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()

    graph = StateGraph(StudentState)

    graph.add_node("analysis", analysis_goal)
    graph.add_node("project", project_planer)
    graph.add_node("plan", task_planer)
    graph.add_node("priority", priority_planer)
    graph.add_node("tracker", task_tracker)
    graph.add_node("mark_progress", mark_progress)
    graph.add_node("adaptive", adaptive_planner)
    graph.add_node("final", final_plan)

    graph.add_conditional_edges(
        START,
        route_from_start,
        {"analysis": "analysis", "mark_progress": "mark_progress"}
    )
    graph.add_edge("analysis", "project")
    graph.add_edge("project", "plan")
    graph.add_edge("plan", "priority")
    graph.add_edge("priority", "mark_progress")
    graph.add_edge("mark_progress", "adaptive")
    graph.add_edge("adaptive", "tracker")
    graph.add_conditional_edges(
        "tracker",
        route_after_tracker,
        {"final": "final", END: END}
    )
    graph.add_edge("final", END)

    return graph.compile(checkpointer=checkpointer)


agent_app = create_graph()
