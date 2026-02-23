from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    stage: str = Field(default="dev")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)

    log_dir: str = Field(default="logs")

    xlsx_path: str = Field(default="data/exhibits.xlsx")
    photos_dir: str = Field(default="data/photos")

    admin_token: str = Field(default="")
