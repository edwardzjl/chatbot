from pydantic import HttpUrl, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    inference_server_url: HttpUrl = "http://localhost:8080"
    log_level: str = "INFO"
    redis_om_url: RedisDsn = "redis://localhost:6379"
    """This env name (REDIS_OM_URL) is required by redis-om"""
    user_id_header: str = "X-Forwarded-User"


settings = Settings()
