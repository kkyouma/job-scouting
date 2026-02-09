from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    JSEARCH_API_KEY: SecretStr
    ADZUNA_APP_ID: str
    ADZUNA_API_KEY: SecretStr
    TELEGRAM_BOT_TOKEN: SecretStr
    TELEGRAM_CHAT_ID: str

    # Optional default criteria
    DEFAULT_QUERY: str = "Python Developer"
    DEFAULT_LOCATION: str = "Remote"


settings = Settings()
