from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from doc_analyzer.config import settings


@lru_cache
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model, api_key=settings.gemini_api_key
    )
