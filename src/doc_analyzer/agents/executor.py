import json

from langchain_core.messages import HumanMessage, ToolMessage

from doc_analyzer.llm import invoke_with_tools, load_prompt
from doc_analyzer.messages import TaskResult
from doc_analyzer.state import MessageState, TaskState
from doc_analyzer.tools import tools


def executor(state: TaskState) -> dict:
    task = state["task"]
    feedback = state.get("feedback")
    note = feedback.comment if feedback and not feedback.approved else "Không có"
    prompt = HumanMessage(
        load_prompt(
            "executor",
            doc_path=task.doc_path,
            instruction=task.instruction,
            feedback=note,
        )
    )
    messages = invoke_with_tools([prompt], tools)

    outputs = {
        message.name: str(message.content)
        for message in messages
        if isinstance(message, ToolMessage)
    }
    try:
        extracted_info = json.loads(outputs.get("extract_info", "{}"))
    except ValueError:
        extracted_info = {}

    previous = state.get("result")
    result = TaskResult(
        task_id=task.task_id,
        summary=outputs.get("summarize", ""),
        extracted_info=extracted_info,
        category=outputs.get("classify", ""),
        attempts=previous.attempts + 1 if previous else 1,
    )
    return {
        "result": result,
        "results": {task.task_id: result},
        "messages": [
            MessageState(sender="executor", receiver="reviewer", content=result)
        ],
    }
