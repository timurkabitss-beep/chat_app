from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:pass@localhost:5432/chat_db"

    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000022

    REDIS_URL: str = "redis://redis:6379"
    CACHE_TTL_SECONDS: int = 60

    WS_PING_INTERVAL: int = 5

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    MESSAGE_MAX_LENGTH: int = 2048
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()