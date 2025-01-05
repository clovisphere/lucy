import os

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME") or "Lucy"

    # Informative message to help users interact with the Lucy 🐶
    HELP_COMMAND: str = """
    🐶

    I only support a few COMMANDS as of now 😪

    /start  Display a welcome message
    /help   Show this message 🤭
    """

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return v

    class Config:
        case_sensitive: bool = True


settings = Settings()
