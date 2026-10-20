import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    max_retries: int
    max_concurrency: int
    database_url: str


def load_settings() -> Settings:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "doc_analyzer")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")

    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        max_retries=int(os.getenv("MAX_RETRIES", "2")),
        max_concurrency=int(os.getenv("MAX_CONCURRENCY", "4")),
        database_url=os.getenv("DATABASE_URL")
        or f"postgresql://{user}:{password}@{host}:{port}/{db}",
    )


settings = load_settings()
