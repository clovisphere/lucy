import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from starlette.status import HTTP_200_OK
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.handlers import ask, help, start
from app.helpers.logger import log

# Initialize Telegram 🤖
telegram = (
    ApplicationBuilder()
    .token(os.getenv("TELEGRAM_TOKEN", ""))
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await telegram.bot.setWebhook(os.getenv("WEBHOOK_ENDPOINT", ""))
    async with telegram:
        await telegram.start()
        yield
        await telegram.stop()


# Initialize FastAPI app :-)
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)


@app.get("/", status_code=HTTP_200_OK)
async def index():
    return "hello, world!"


@app.post("/upload")
async def upload():
    pass


@app.post("/webhook", status_code=status.HTTP_200_OK)
async def process_update(request: Request):
    req = await request.json()
    log.debug("Received a request from Telegram via webhook 😉...", req=req)
    update = Update.de_json(req, telegram.bot)
    await telegram.process_update(update=update)
    return {"message": "telegram request well received 🤭"}


# Register Telegram handlers
telegram.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ask))
telegram.add_handler(CommandHandler("help", help))
telegram.add_handler(CommandHandler("start", start))
