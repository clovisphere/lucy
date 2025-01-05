import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # load the environment variables


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME") or "Lucy"

    # Informative message to help users interact with the Lucy 🐶
    HELP_COMMAND: str = """
    🐶\n\nI only support a few COMMANDS 😪

    /start  Display a welcome message
    /help   Show this message 🤭
    """


settings = Settings()
