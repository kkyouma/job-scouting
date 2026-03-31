from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # External APIs
    JSEARCH_API_KEY: SecretStr
    GEMINI_API_KEY: SecretStr | None = None
    GEMINI_MODEL_ID: str = "gemini-2.5-flash"

    # Notifications
    TELEGRAM_BOT_TOKEN: SecretStr | None = None
    TELEGRAM_CHAT_ID: str | None = None

    # Database
    TURSO_AUTH_TOKEN: SecretStr
    TURSO_URL: str

    # Paths
    PROMPT_PATH: Path = Path(__file__).resolve().parent / "prompts" / "system_prompt.md"

    # Optional default criteria
    DEFAULT_QUERY: str = "Junior Data Engineer"
    DEFAULT_LOCATION: str = "cl"


settings = Settings()  # ty:ignore[missing-argument]
