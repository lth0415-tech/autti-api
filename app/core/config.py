from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Autti"
    env: str = "local"
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/autti"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()