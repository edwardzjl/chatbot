from pydantic import BaseSettings, RedisDsn, AnyHttpUrl


class Settings(BaseSettings):
    inference_server_url: AnyHttpUrl = "http://localhost:8080"
    log_level: str = "INFO"
    redis_url: RedisDsn = "redis://localhost:6379"


settings = Settings()
