from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    neis_api_key: str = Field(default="test-key", alias="NEIS_API_KEY")
    neis_base_url: str = Field(default="https://open.neis.go.kr", alias="NEIS_BASE_URL")
    mcp_port: int = Field(default=8080, alias="MCP_PORT")
    school_page_size: int = Field(default=100, alias="SCHOOL_PAGE_SIZE")
    school_result_limit: int = Field(default=100, alias="SCHOOL_RESULT_LIMIT")
    meal_max_range_days: int = Field(default=31, alias="MEAL_MAX_RANGE_DAYS")
    neis_connect_timeout: float = Field(default=3, alias="NEIS_CONNECT_TIMEOUT")
    neis_read_timeout: float = Field(default=10, alias="NEIS_READ_TIMEOUT")
    neis_max_retries: int = Field(default=2, alias="NEIS_MAX_RETRIES")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
