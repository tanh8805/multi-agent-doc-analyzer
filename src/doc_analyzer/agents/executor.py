from doc_analyzer.messages import TaskResult
from doc_analyzer.state import MessageState, TaskState
from doc_analyzer.tools import classify, extract_info, read_file, summarize


def executor(state: TaskState) -> dict:
    task = state["task"]
    previous = state.get("result")
    feedback = state.get("feedback")

    text = read_file.invoke({"path": task.doc_path})
    if feedback and not feedback.approved:
        text += f"\n\nGóp ý của reviewer ở lần trước: {feedback.comment}"

    result = TaskResult(
        task_id=task.task_id,
        summary=summarize.invoke({"text": text}),
        extracted_info=extract_info.invoke({"text": text}),
        category=classify.invoke({"text": text}),
        attempts=previous.attempts + 1 if previous else 1,
    )
    return {
        "result": result,
        "results": {task.task_id: result},
        "messages": [
            MessageState(sender="executor", receiver="reviewer", content=result)
        ],
    }
