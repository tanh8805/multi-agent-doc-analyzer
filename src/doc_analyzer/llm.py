from functools import lru_cache
from pathlib import Path

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
