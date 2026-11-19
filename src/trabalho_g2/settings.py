from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    arduino_port: str = Field(description="Porta USB conectada ao Arduino")
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / '.env',
        env_file_encoding="utf-8",
    )    


@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore