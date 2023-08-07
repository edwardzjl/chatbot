from pydantic import BaseSettings, RedisDsn, AnyHttpUrl


class Settings(BaseSettings):
    log_level: str = "INFO"
    redis_om_url: RedisDsn = "redis://localhost:6379"
    inference_server_url: AnyHttpUrl = "http://localhost:8080"


settings = Settings()
