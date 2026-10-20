from functools import lru_cache
from pathlib import Path

from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from doc_analyzer.config import settings

PROMPTS_DIR = Path(__file__).parent / "prompts"


@lru_cache
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model, api_key=settings.gemini_api_key
    )


def load_prompt(name: str, **variables: str) -> str:
    text = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def invoke_with_tools(
    messages: list[BaseMessage], tools: list[BaseTool]
) -> list[BaseMessage]:
    llm = get_llm().bind_tools(tools)
    tools_by_name = {tool.name: tool for tool in tools}

    messages = list(messages)
    response = llm.invoke(messages)
    messages.append(response)
    while response.tool_calls:
        for call in response.tool_calls:
            messages.append(tools_by_name[call["name"]].invoke(call))
        response = llm.invoke(messages)
        messages.append(response)
    return messages
