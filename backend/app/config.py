from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    neis_api_key: str = Field(alias="NEIS_API_KEY")
    neis_base_url: str = Field(default="https://open.neis.go.kr", alias="NEIS_BASE_URL")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_origin: str | None = Field(default=None, alias="FRONTEND_ORIGIN")
    school_page_size: int = Field(default=100, alias="SCHOOL_PAGE_SIZE")
    school_result_limit: int = Field(default=100, alias="SCHOOL_RESULT_LIMIT")
    meal_max_range_days: int = Field(default=31, alias="MEAL_MAX_RANGE_DAYS")
    neis_connect_timeout: float = Field(default=3, alias="NEIS_CONNECT_TIMEOUT")
    neis_read_timeout: float = Field(default=10, alias="NEIS_READ_TIMEOUT")
    neis_max_retries: int = Field(default=2, alias="NEIS_MAX_RETRIES")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
