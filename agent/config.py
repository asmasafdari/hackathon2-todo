"""Configuration settings for the AI Agent."""

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI API Key (required)
    openai_api_key: str = ""

    # Todo API base URL
    todo_api_base_url: str = "http://localhost:8000"

    # Session database path
    session_db_path: Path = Path.home() / ".todo-agent" / "sessions.db"

    # HTTP request timeout in seconds
    request_timeout: int = 30

    @property
    def api_todos_url(self) -> str:
        """Full URL for the internal todos endpoint (no auth required)."""
        return f"{self.todo_api_base_url.rstrip('/')}/internal/todos"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
