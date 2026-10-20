from pathlib import Path
from typing import Literal, cast

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from doc_analyzer.llm import get_llm


DocType = Literal[
    "ghi chú",       
    "email/tin nhắn",
    "hóa đơn/biên lai",
    "hợp đồng/thỏa thuận",
    "kế hoạch/lịch trình",
    "tài liệu học tập",
    "bài viết",
    "khác",
]


class ExtractedInfo(BaseModel):
    people: list[str] = Field(
        default_factory=list,
        description="Tên người được nhắc đến, đúng như cách viết trong văn bản.",
    )
    organizations: list[str] = Field(
        default_factory=list,
        description="Tên công ty, cửa hàng, trường, cơ quan được nhắc đến.",
    )
    dates: list[str] = Field(
        default_factory=list,
        description="Ngày hoặc mốc thời gian, kèm ý nghĩa ngắn gọn nếu có, ví dụ '15/11/2026 - hạn nộp'.",
    )
    amounts: list[str] = Field(
        default_factory=list,
        description="Số tiền hoặc số lượng quan trọng, kèm đơn vị, ví dụ '350.000 VND'.",
    )
    action_items: list[str] = Field(
        default_factory=list,
        description="Việc cần làm, kèm người phụ trách và hạn nếu văn bản có nêu.",
    )


@tool
def read_file(path: str) -> str:
    """Đọc nội dung một file văn bản (.txt, .md) và trả về dạng chuỗi."""
    return Path(path).read_text(encoding="utf-8")


@tool
def summarize(text: str) -> str:
    """Tóm tắt văn bản thành vài ý chính, cùng ngôn ngữ với văn bản."""
    prompt = (
        "Tóm tắt văn bản sau thành vài ý chính, cùng ngôn ngữ với văn bản. "
        "Chỉ dùng thông tin có trong văn bản.\n\n" + text
    )
    return get_llm().invoke(prompt).text


@tool
def extract_info(text: str) -> dict:
    """Trích xuất thông tin chính từ văn bản."""
    chain = get_llm().with_structured_output(ExtractedInfo)
    result = chain.invoke(text)
    return result if isinstance(result, dict) else result.model_dump()


class Classification(BaseModel):
    doc_type: DocType

@tool
def classify(text: str) -> str:
    """Phân loại văn bản vào một nhóm cố định."""
    chain = get_llm().with_structured_output(Classification)
    result = cast(Classification, chain.invoke(
        "Phân loại văn bản sau vào đúng một nhóm.\n\n" + text
    ))
    return result.doc_type


tools = [read_file, summarize, extract_info, classify]
