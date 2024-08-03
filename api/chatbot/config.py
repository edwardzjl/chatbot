from pydantic import BaseModel, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMServiceSettings(BaseModel):
    url: HttpUrl = "http://localhost:8080"
    """llm service url"""
    model: str = "cognitivecomputations/dolphin-2.6-mistral-7b-dpo-laser"
    creds: str = "EMPTY"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    llm: LLMServiceSettings = LLMServiceSettings()
    log_level: str = "INFO"
    redis_om_url: RedisDsn = "redis://localhost:6379"
    """This env name (REDIS_OM_URL) is required by redis-om"""


settings = Settings()
