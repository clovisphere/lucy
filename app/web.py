import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.background import BackgroundTasks
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
from app.helpers.rag import Rag

# Initialize FastAPI app :-)
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Make sure the upload directory 📁 exist at app startup 🐶
(lambda dir: os.makedirs(dir) if not os.path.exists(dir) else None)(settings.UPLOAD_DIR)

# Mount static files for serving CSS, JS, and other assets
static_dir_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir_path), name="static")


# TODO: add auth to this endpoint
@app.get("/", response_class=HTMLResponse, status_code=HTTP_200_OK)
def index():
    with open(f"{static_dir_path}/index.html") as f:
        html = f.read()
    return HTMLResponse(content=html)


# TODO: add auth to this endpoint
@app.post("/api/upload", status_code=HTTP_201_CREATED)
async def upload(files: list[UploadFile], background_tasks: BackgroundTasks):
    saved_files: list[dict[str, Any]] = []
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
            saved_files.append({"name": file.filename, "path": file_path})
    log.debug("File(s) processed", total=len(saved_files), files=saved_files)
    # start `etl` process in the background if we have uploaded some files
    if saved_files:
        log.debug("Initiate ETL in the background...")
        background_tasks.add_task(Rag(settings.UPLOAD_DIR, log).etl)


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
