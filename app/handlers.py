from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.helpers.llm import OpenAILlm
from app.helpers.rag import Rag


async def ask(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    message = str(update.message.text) if update.message else ""
    # fmt: off
    if (reply:= update.message.reply_text if update.message else None):
    # fmt: on
        ai_answer = "Sorry 😞, I do not understand.."  # default response :-)
        if message and message != "None":
            llm = OpenAILlm(Rag.get_vector_store())  # can we do better? 😮‍💨
            ai_answer = llm.ask_question(message, session_id=f"telegram-{chat_id}")
        await reply(ai_answer)


async def help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    # fmt: off
    if (reply:= update.message.reply_text if update.message else None):
    # fmt: on
        await reply(settings.HELP_COMMAND.strip())


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    greetings = f"Hey {update.message.chat.first_name}" if update.message else "Hey"
    # fmt: off
    if (reply:= update.message.reply_text if update.message else None):
    # fmt: on
        await reply(
            f"{greetings},\n\nI'm Lucy 🐶, a helpful AI assistant. "
            + "You can ask me anything or you can send /help to get a "
            + "list of all my pre-defined commands."
        )
