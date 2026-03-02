import os, logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from telegram import Update
from telegram.ext import (Application, CommandHandler,
                           MessageHandler, CallbackQueryHandler, filters)
from bot.handlers import (cmd_start, cmd_myid, cmd_status,
                           cmd_scan, handle_message, handle_confirm)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

ptb = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
ptb.add_handler(CommandHandler("start",  cmd_start))
ptb.add_handler(CommandHandler("myid",   cmd_myid))
ptb.add_handler(CommandHandler("status", cmd_status))
ptb.add_handler(CommandHandler("scan",   cmd_scan))
ptb.add_handler(CallbackQueryHandler(handle_confirm))
ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb.initialize()
    await ptb.start()
    await ptb.updater.start_polling()
    log.info("Application started")
    yield
    log.info("Application is stopping. This might take a moment.")
    await ptb.updater.stop()
    await ptb.stop()
    await ptb.shutdown()
    log.info("Application.stop() complete")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health(): return {"status": "ok", "bot": "PydanticOps"}
