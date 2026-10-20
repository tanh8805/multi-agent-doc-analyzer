import json
from typing import cast

from pydantic import BaseModel

from doc_analyzer.llm import get_llm, load_prompt
from doc_analyzer.messages import TaskAssigned
from doc_analyzer.state import GraphState, MessageState
from doc_analyzer.tools import read_file


class Plan(BaseModel):
    doc_paths: list[str]


def planner(state: GraphState) -> dict:
    previews = []
    for path in state["doc_paths"]:
        try:
            content = read_file.invoke({"path": path})
        except (OSError, UnicodeDecodeError):
            previews.append(f"- {path}: không đọc được")
            continue
        previews.append(f"- {path} ({len(content)} ký tự): {content[:300]!r}")

    prompt = load_prompt("planner", documents="\n".join(previews))
    chain = get_llm().with_structured_output(Plan)
    plan = cast(Plan, chain.invoke(prompt))

    doc_paths = [path for path in plan.doc_paths if path in state["doc_paths"]]
    tasks = [
        TaskAssigned(run_id=state["run_id"], task_id=f"t{i}", doc_path=path)
        for i, path in enumerate(doc_paths, start=1)
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

    prompt = (
        "Tổng hợp kết quả phân tích các tài liệu dưới đây thành một báo cáo Markdown "
        "gồm các mục: Tổng quan, Chi tiết từng tài liệu, Nhận xét chung giữa các tài liệu, "
        "Hạn chế. Chỉ dùng thông tin có trong kết quả, không bịa thêm.\n\n"
        "## Kết quả\n\n" + "\n\n".join(sections) + "\n\n"
        "## Tài liệu chưa được reviewer chấp nhận (đưa vào mục Hạn chế)\n\n"
        + ("\n".join(failed) or "Không có")
    )
    return {"report": get_llm().invoke(prompt).text}
