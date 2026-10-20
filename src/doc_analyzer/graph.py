from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from doc_analyzer.agents.executor import executor
from doc_analyzer.agents.planner import planner, synthesize
from doc_analyzer.agents.reviewer import reviewer
from doc_analyzer.config import settings
from doc_analyzer.state import GraphState, TaskState


def route_review(state: TaskState) -> str:
    receiver = state["messages"][-1]["receiver"]
    return "executor" if receiver == "executor" else END


def build_task_graph():
    graph = StateGraph(TaskState)
    graph.add_node("executor", executor)
    graph.add_node("reviewer", reviewer)
    graph.add_edge(START, "executor")
    graph.add_edge("executor", "reviewer")
    graph.add_conditional_edges("reviewer", route_review, ["executor", END])
    return graph.compile()


def dispatch_tasks(state: GraphState):
    sends = [Send("task", {"task": task}) for task in state["tasks"]]
    return sends or "synthesize"


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("planner", planner)
    graph.add_node("task", build_task_graph())
    graph.add_node("synthesize", synthesize)
    graph.add_edge(START, "planner")
    graph.add_conditional_edges("planner", dispatch_tasks, ["task", "synthesize"])
    graph.add_edge("task", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile().with_config(max_concurrency=settings.max_concurrency)
