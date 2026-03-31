from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    virustotal_api_key: str = Field(validation_alias="VT_API_KEY")
    vt_base_url: str = "https://www.virustotal.com/api/v3"
    vt_rate_limit_rpm: int = 4
    database_url: str = "sqlite+aiosqlite:///./virustotal.db"
    redis_url: str = ""
    cache_ttl_seconds: int = 3600
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

@lru_cache()
def get_settings() -> Settings:
    return Settings()
