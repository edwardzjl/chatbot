from pydantic import BaseSettings, RedisDsn, AnyHttpUrl


class Settings(BaseSettings):
    inference_server_url: AnyHttpUrl = "http://localhost:8080"
    log_level: str = "INFO"
    redis_om_url: RedisDsn = "redis://localhost:6379"
    """This env name (REDIS_OM_URL) is required by redis-om"""


settings = Settings()
