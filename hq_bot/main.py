import os, asyncio, logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from hq_bot.i18n import t, detect_lang

load_dotenv()
logging.basicConfig(level=logging.INFO)
HQ_TOKEN = os.environ["HQ_TELEGRAM_TOKEN"]
GITHUB_URL = os.getenv("GITHUB_URL", "https://github.com/pydanticops/pydanticops")

def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_what", lang),    callback_data=f"what|{lang}"),
         InlineKeyboardButton(t("btn_install", lang), callback_data=f"install|{lang}")],
        [InlineKeyboardButton(t("btn_demo", lang),    callback_data=f"demo|{lang}"),
         InlineKeyboardButton(t("btn_stack", lang),   callback_data=f"stack|{lang}")],
        [InlineKeyboardButton(t("btn_github", lang),  url=GITHUB_URL),
         InlineKeyboardButton(t("btn_lang", lang),    callback_data=f"lang|{'en' if lang=='ru' else 'ru'}")],
    ])

def back_btn(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_back", lang), callback_data=f"menu|{lang}"),
        InlineKeyboardButton(t("btn_github", lang), url=GITHUB_URL),
    ]])

async def cmd_start(update: Update, ctx):
    lang = ctx.user_data.get("lang") or detect_lang(update)
    ctx.user_data["lang"] = lang
    await update.message.reply_text(
        t("welcome", lang), reply_markup=main_menu(lang), parse_mode="Markdown"
    )

async def handle_callback(update: Update, ctx):
    query = update.callback_query
    await query.answer()
    action, lang = query.data.split("|", 1)
    ctx.user_data["lang"] = lang

    if action == "menu":
        await query.edit_message_text(
            t("welcome", lang), reply_markup=main_menu(lang), parse_mode="Markdown"
        )
    elif action == "lang":
        await query.edit_message_text(
            t("welcome", lang), reply_markup=main_menu(lang), parse_mode="Markdown"
        )
    elif action in ("what", "install", "demo", "stack"):
        await query.edit_message_text(
            t(action, lang), reply_markup=back_btn(lang), parse_mode="Markdown"
        )

async def handle_text(update: Update, ctx):
    lang = ctx.user_data.get("lang") or detect_lang(update)
    ctx.user_data["lang"] = lang
    await update.message.reply_text(
        t("welcome", lang), reply_markup=main_menu(lang), parse_mode="Markdown"
    )

ptb = Application.builder().token(HQ_TOKEN).build()
ptb.add_handler(CommandHandler("start", cmd_start))
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
async def health(): return {"status": "ok", "bot": "PydanticOps HQ"}
