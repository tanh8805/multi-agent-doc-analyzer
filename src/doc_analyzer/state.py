import operator
from typing import Annotated, TypedDict

from doc_analyzer.messages import AgentMessage, ReviewFeedback, TaskAssigned, TaskResult


class MessageState(TypedDict):

    sender: str
    receiver: str
    content: AgentMessage

class GraphState(TypedDict):
    run_id: str
    messages: Annotated[list[MessageState], operator.add]
    doc_paths: list[str]
    tasks: list[TaskAssigned]
    results: Annotated[dict[str, TaskResult], operator.or_]
    reviews: Annotated[list[ReviewFeedback], operator.add]
    report: str


class TaskState(TypedDict):
    task: TaskAssigned
    result: TaskResult
    feedback: ReviewFeedback
    messages: Annotated[list[MessageState], operator.add]
    results: Annotated[dict[str, TaskResult], operator.or_]
    reviews: Annotated[list[ReviewFeedback], operator.add]
