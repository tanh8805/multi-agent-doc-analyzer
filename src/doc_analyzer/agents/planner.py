import json

from langchain_core.messages import HumanMessage

from doc_analyzer.llm import get_llm, invoke_with_tools, load_prompt
from doc_analyzer.messages import TaskAssigned
from doc_analyzer.state import GraphState, MessageState
from doc_analyzer.tools import read_file


def planner(state: GraphState) -> dict:
    doc_paths = "\n".join(f"- {path}" for path in state["doc_paths"])
    prompt = HumanMessage(load_prompt("planner", doc_paths=doc_paths))
    messages = invoke_with_tools([prompt], [read_file])

    instructions = {}
    for line in messages[-1].text.splitlines():
        path, _, instruction = line.strip("- ").partition("|")
        if path.strip() in state["doc_paths"]:
            instructions.setdefault(path.strip(), instruction.strip())

    tasks = [
        TaskAssigned(
            run_id=state["run_id"],
            task_id=f"t{i}",
            doc_path=path,
            instruction=instruction,
        )
        for i, (path, instruction) in enumerate(instructions.items(), start=1)
    ]
    return {
        "tasks": tasks,
        "messages": [
            MessageState(sender="planner", receiver="executor", content=task)
            for task in tasks
        ],
    }


def synthesize(state: GraphState) -> dict:
    doc_paths = {task.task_id: task.doc_path for task in state["tasks"]}
    latest_reviews = {review.task_id: review for review in state["reviews"]}

    sections = []
    for task_id, result in state["results"].items():
        sections.append(
            f"### {doc_paths[task_id]}\n"
            f"- Phân loại: {result.category}\n"
            f"- Tóm tắt: {result.summary}\n"
            f"- Thông tin trích xuất: {json.dumps(result.extracted_info, ensure_ascii=False)}"
        )

    failed = [
        f"- {doc_paths[task_id]}: {review.comment}"
        for task_id, review in latest_reviews.items()
        if not review.approved
    ]

    prompt = load_prompt(
        "synthesize",
        results="\n\n".join(sections),
        failed="\n".join(failed) or "Không có",
    )
    return {"report": get_llm().invoke(prompt).text}
