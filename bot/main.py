import os, logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers import cmd_start, cmd_myid, handle_text, handle_callback

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ptb = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
ptb.add_handler(CommandHandler("start", cmd_start))
ptb.add_handler(CommandHandler("myid", cmd_myid))
ptb.add_handler(CallbackQueryHandler(handle_callback))
ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb.initialize()
    await ptb.start()
    await ptb.updater.start_polling()
    yield
    await ptb.updater.stop()
    await ptb.stop()
    await ptb.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health(): return {"status": "ok"}
