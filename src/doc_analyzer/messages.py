from typing import Any

from pydantic import BaseModel, Field


class TaskAssigned(BaseModel):
    run_id: str
    task_id: str
    doc_path: str
    instruction: str


class TaskResult(BaseModel):
    task_id: str
    summary: str
    extracted_info: dict[str, Any] = Field(default_factory=dict)
    category: str
    attempts: int = 1


class ReviewFeedback(BaseModel):
    task_id: str
    approved: bool
    comment: str = ""


AgentMessage = TaskAssigned | TaskResult | ReviewFeedback

