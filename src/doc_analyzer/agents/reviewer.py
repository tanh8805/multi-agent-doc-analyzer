from langchain_core.messages import HumanMessage

from doc_analyzer.config import settings
from doc_analyzer.llm import invoke_with_tools, load_prompt
from doc_analyzer.messages import ReviewFeedback
from doc_analyzer.state import MessageState, TaskState
from doc_analyzer.tools import read_file


def reviewer(state: TaskState) -> dict:
    task = state["task"]
    result = state["result"]
    prompt = HumanMessage(
        load_prompt(
            "reviewer", doc_path=task.doc_path, result=result.model_dump_json()
        )
    )
    messages = invoke_with_tools([prompt], [read_file])

    text = messages[-1].text.strip()
    feedback = ReviewFeedback(
        task_id=task.task_id, approved=text.upper().startswith("ĐẠT"), comment=text
    )
    retry = not feedback.approved and result.attempts <= settings.max_retries
    receiver = "executor" if retry else "planner"
    return {
        "feedback": feedback,
        "reviews": [feedback],
        "messages": [
            MessageState(sender="reviewer", receiver=receiver, content=feedback)
        ],
    }
