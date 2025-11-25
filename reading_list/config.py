from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field("dev", alias="APP_ENV")
    debug: bool = Field(True, alias="DEBUG")

    database_url: str = Field(..., alias="DATABASE_URL")

    model_config = {
        "env_file": ".env",  # для локального запуска вне Docker
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
