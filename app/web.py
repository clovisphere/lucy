import os

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.handlers import TELEGRAM, ask, help, lifespan, start
from app.helpers.logger import log

# Initialize FastAPI app :-)
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Make sure the upload directory 📁 exist at app startup 🐶
(lambda dir: os.makedirs(dir) if not os.path.exists(dir) else None)(settings.UPLOAD_DIR)

# Mount static files for serving CSS, JS, and other assets
app.mount("/static", StaticFiles(directory="static"), name="static")


# TODO: add auth to this endpoint
@app.get("/", response_class=HTMLResponse, status_code=HTTP_200_OK)
def index():
    with open("static/index.html") as f:
        html = f.read()
    return HTMLResponse(content=html)


# TODO: add auth to this endpoint
@app.post("/api/upload", status_code=HTTP_201_CREATED)
async def upload(files: list[UploadFile]):
    for file in files:
        if file.content_type != "application/pdf" or not file.filename:
            # fmt: off
            detail = f"{file.filename} is not a PDF" if file.filename \
                            else "filename not present"
            # fmt: on
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=detail)
        file_path: str = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    # TODO: start `etl` process if we have uploaded some files (i.e. indexing)


@app.post("/api/webhook", status_code=HTTP_200_OK)
async def process_update(request: Request):
    req = await request.json()
    log.debug("Received a request from Telegram via webhook 😉...", req=req)
    await TELEGRAM.process_update(update=Update.de_json(req, TELEGRAM.bot))
    # No return required. FastAPI will automatically return 200 OK with an empty body.


# Register Telegram handlers
TELEGRAM.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ask))
TELEGRAM.add_handler(CommandHandler("help", help))
TELEGRAM.add_handler(CommandHandler("start", start))
