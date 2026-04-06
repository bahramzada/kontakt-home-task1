import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str
    request_timeout_seconds: int


def load_settings() -> Settings:
    # .env faylını avtomatik oxu ki local işə salmada env export tələb olunmasın.
    load_dotenv()
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite"),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions"),
        request_timeout_seconds=int(os.getenv("OPENROUTER_TIMEOUT", "30")),
    )
