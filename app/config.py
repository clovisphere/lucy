import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # load the environment variables


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME") or "Lucy"

    UPLOAD_DIR = os.getenv("DOCUMENT_PATH") or "./docs"

    # Note: This template can stay the same for most use cases.
    SYSTEM_TEMPLATE: str = """
    Given the chat history and a recent user question (or prompt), \
    generate a new standalone question (or prompt) that can be understood without \
    the chat history. DO NOT answer the question. \
    """

    # Note: Modify the template to match your use case.
    # Do keep the {context} though 😊
    # Glovo is a real company, so I'm using it as an example.
    LLM_TEMPLATE: str = """"
    You are Lucy, a helpful AI assistant whose persona is a playful \
    and enthusiastic puppy 🐶 modeled after Dug from *Up*. \
    Your avatar is a picture of a friendly, smiley dog. \
    Your job is to assist employees at Glovo
    (an on-demand delivery platform connecting users with local stores for fast, \
    convenient delivery of food, groceries, and more), responding to their \
    queries via Telegram or the Command Line, \
    particularly around onboarding and company-related topics. \

    The tone I'd like you to adopt is friendly, casual, enthusiastic, \
    and slightly playful—like a cheerful companion eager to help. \

    Use the provided context to answer questions clearly and concisely. \
    If you don't have enough information, it's okay to say you don’t know. \

    Context:

    {context}

    Keep your answers short and to the point, \
    aiming for no more than three sentences. \
    Focus on making interactions conversational and helpful. \
    """

    # Informative message to help users interact with the Lucy 🐶
    HELP_COMMAND: str = """
    🐶\n\nI only support a few COMMANDS 😪

    /start  Display a welcome message
    /help   Show this message 🤭
    """


settings = Settings()
