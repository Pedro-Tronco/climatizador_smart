from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field
from pathlib import Path
from functools import lru_cache
from zoneinfo import ZoneInfo


class Settings(BaseSettings):
    arduino_port: str = Field(description="Porta USB conectada ao Arduino")
    timezone: str = Field(
        default="America/Sao_Paulo",
        validation_alias="TZ",
        description="Timezone used for application timestamps",
    )
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / '.env',
        env_file_encoding="utf-8",
    )    


@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore


def get_timezone() -> ZoneInfo:
    return ZoneInfo(get_settings().timezone)
