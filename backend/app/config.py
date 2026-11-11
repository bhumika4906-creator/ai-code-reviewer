from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GROQ_API_KEY: str | None = None
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
