import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from lib.llm import OpenAILlm
from lib.rag import Rag

load_dotenv()  # load the environment variables

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Informative message to help users interact with the Lucy 🐶
HELP = """
🐶

I only support a few COMMANDS as of now 😪

/start  Display a welcome message
/help   Show this message 🤭
"""

# TO BE MODIFIED 🤭
llm = OpenAILlm(Rag.get_vector_store())


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=HELP.strip(),
    )


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # type: ignore
    message: str = str(update.message.text) if update.message else ""

    logging.info(f"-> Received message: {message} from user with id: {chat_id}")

    ai_answer = "Sorry 😞, I do not understand.."  # default response :-)
    if message and message != "None":
        ai_answer = llm.ask_question(message, session_id=f"telegram-{chat_id}")

    await context.bot.send_message(chat_id=chat_id, text=ai_answer)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="Hey, I'm Lucy 🐶, a helpful AI assistant. You can ask me anything or "
        + "you can send /help to get a list of all the pre-defined commands",
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN", "")).build()

    # Define handlers
    help_handler = CommandHandler("help", help)
    reply_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), reply)
    start_handler = CommandHandler("start", start)

    # Register handlers
    application.add_handler(start_handler)
    application.add_handler(reply_handler)
    application.add_handler(help_handler)

    # Run bot :-)
    application.run_polling()
