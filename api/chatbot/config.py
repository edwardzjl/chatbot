from pydantic import BaseModel, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMServiceSettings(BaseModel):
    url: HttpUrl = "http://localhost:8080"
    """llm service url"""
    model: str = "cognitivecomputations/dolphin-2.6-mistral-7b-dpo-laser"
    creds: str = "EMPTY"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    llm: LLMServiceSettings = LLMServiceSettings()
    db_url: PostgresDsn = "postgresql+psycopg://postgres:postgres@localhost:5432/"
    """Database url. Must be a valid postgresql connection string."""


settings = Settings()
