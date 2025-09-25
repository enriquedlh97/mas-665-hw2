from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    anthropic_api_key: str
    environment: Literal["local", "development", "production", "prod", "live"] = "local"
    domain_name: str = "localhost"
    ssl_enabled: bool = False
    agent_port: int = 6000
    claude_model: str = "claude-3-haiku-20240307"


settings = Settings()
