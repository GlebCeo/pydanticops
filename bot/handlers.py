import asyncio, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.auth import require_admin
from core.validator import parse_command
from core.executor import preview, execute
from core.schemas import StatusCommand, ScanCommand

# ── i18n ──────────────────────────────────────────────────────
S = {
    "welcome": {
        "ru": "⚡ *PydanticOps* — управление сервером из Telegram\n\nВыбери раздел или просто напиши что нужно 👇",
        "en": "⚡ *PydanticOps* — server control from Telegram\n\nChoose a section or just type what you need 👇",
    },
    "loading": {
        "ru": ["⏳ Обрабатываю", "⌛ Обрабатываю.", "⏳ Обрабатываю..", "⌛ Обрабатываю..."],
        "en": ["⏳ Processing", "⌛ Processing.", "⏳ Processing..", "⌛ Processing..."],
    },
    "loading_status": {
        "ru": ["📊 Получаю статус", "📊 Получаю статус.", "📊 Опрашиваю Docker..", "📊 Проверяю GPU..."],
        "en": ["📊 Getting status", "📊 Fetching Docker.", "📊 Checking GPU..", "📊 Done..."],
    },
    "loading_scan": {
        "ru": ["🔍 Сканирую логи", "🔍 Ищу атаки.", "🔍 Анализирую IP..", "🔍 Почти готово..."],
        "en": ["🔍 Scanning logs", "🔍 Finding attacks.", "🔍 Analyzing IPs..", "🔍 Almost done..."],
    },
    "executing": {
        "ru": ["⚙️ Выполняю", "⚙️ Выполняю.", "⚙️ Работаю..", "⚙️ Почти..."],
        "en": ["⚙️ Executing", "⚙️ Running.", "⚙️ Working..", "⚙️ Almost..."],
    },
    "not_understood": {
        "ru": "❓ Не понял команду.\n\nПримеры:\n`Подними DeepSeek на 30000 с 12 ГБ VRAM`\n`Покажи логи nginx`\n`Заблокируй 1.2.3.4`",
        "en": "❓ Command not recognized.\n\nExamples:\n`Launch DeepSeek on 30000 with 12GB VRAM`\n`Show nginx logs`\n`Block 1.2.3.4`",
    },
    "cancelled": {
        "ru": "❌ Отменено\n\nВыбери раздел или напиши команду 👇",
        "en": "❌ Cancelled\n\nChoose a section or type a command 👇",
    },
    "myid": {
        "ru": "🪪 Твой *Chat ID*: `{cid}`\n\nДобавь в `.env`:\n`ADMIN_CHAT_ID={cid}`",
        "en": "🪪 Your *Chat ID*: `{cid}`\n\nAdd to `.env`:\n`ADMIN_CHAT_ID={cid}`",
    },
    "btn_status":  {"ru": "📊 Статус сервера",  "en": "📊 Server Status"},
    "btn_deploy":  {"ru": "🚀 Деплой модели",   "en": "🚀 Deploy Model"},
    "btn_restart": {"ru": "🔁 Рестарт",          "en": "🔁 Restart"},
    "btn_scan":    {"ru": "🔍 OSINT Скан",       "en": "🔍 OSINT Scan"},
    "btn_block":   {"ru": "🚫 Блок IP",          "en": "🚫 Block IP"},
    "btn_logs":    {"ru": "📋 Логи",             "en": "📋 Logs"},
    "btn_help":    {"ru": "❓ Помощь",            "en": "❓ Help"},
    "btn_back":    {"ru": "⬅️ Главное меню",     "en": "⬅️ Main menu"},
    "btn_ok":      {"ru": "✅ Выполнить",         "en": "✅ Execute"},
    "btn_cancel":  {"ru": "❌ Отмена",            "en": "❌ Cancel"},
    "btn_lang":    {"ru": "🌐 English",           "en": "🌐 Русский"},
    "sections": {
        "m_deploy": {
            "ru": "🚀 *Деплой AI-модели*\n\nНапиши в чат:\n`Подними DeepSeek-R1 на 30000 с 12 ГБ VRAM`\n`Запусти Qwen2 на 8080 с 24 ГБ VRAM`\n\nБот подберёт квантизацию под твой GPU и покажет docker-compose на подтверждение.",
            "en": "🚀 *Deploy AI Model*\n\nType in chat:\n`Launch DeepSeek-R1 on 30000 with 12GB VRAM`\n`Start Qwen2 on 8080 with 24GB VRAM`\n\nBot picks quantization for your GPU and shows docker-compose for confirmation.",
        },
        "m_restart": {
            "ru": "🔁 *Рестарт сервиса*\n\nНапиши в чат:\n`Перезапусти sglang`\n`Перезапусти nginx`\n\nБот покажет превью и попросит подтверждение.",
            "en": "🔁 *Restart Service*\n\nType in chat:\n`Restart sglang`\n`Restart nginx`\n\nBot shows preview and asks for confirmation.",
        },
        "m_block": {
            "ru": "🚫 *Блокировка IP*\n\nНапиши в чат:\n`Заблокируй 89.248.168.239`\n`Block IP 1.2.3.4`\n\nБот покажет правило iptables и попросит подтверждение.",
            "en": "🚫 *Block IP*\n\nType in chat:\n`Block 89.248.168.239`\n`Заблокируй 1.2.3.4`\n\nBot shows iptables rule and asks for confirmation.",
        },
        "m_logs": {
            "ru": "📋 *Просмотр логов*\n\nНапиши в чат:\n`Покажи логи sglang последние 50 строк`\n`Покажи логи nginx`\n\nХвост логов придёт прямо в Telegram.",
            "en": "📋 *View Logs*\n\nType in chat:\n`Show sglang logs last 50 lines`\n`Show nginx logs`\n\nLog tail comes directly to Telegram.",
        },
        "m_help": {
            "ru": "❓ *Помощь*\n\n*Команды:*\n`/status` — Docker + GPU + SGLang\n`/scan` — OSINT сканирование\n`/start` — главное меню\n`/myid` — твой Telegram ID\n\n*Натуральный язык:*\nПросто пиши что нужно — бот поймёт через Groq llama-3.3-70b ⚡\n\n*Safety:* опасные команды требуют ✅",
            "en": "❓ *Help*\n\n*Commands:*\n`/status` — Docker + GPU + SGLang\n`/scan` — OSINT scan\n`/start` — main menu\n`/myid` — your Telegram ID\n\n*Natural language:*\nJust type what you need — bot understands via Groq llama-3.3-70b ⚡\n\n*Safety:* destructive actions require ✅",
        },
    },
}

def t(key, lang, **kw):
    val = S.get(key, {})
    if isinstance(val, dict):
        text = val.get(lang) or val.get("en") or key
        return text.format(**kw) if kw else text
    return key

def get_lang(update, ctx):
    if "lang" not in ctx.user_data:
        lc = getattr(update.effective_user, "language_code", "") or ""
        ctx.user_data["lang"] = "ru" if lc.startswith("ru") else "en"
    return ctx.user_data["lang"]

# ── KEYBOARDS ─────────────────────────────────────────────────
def main_kb(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_status", lang),  callback_data="m_status")],
        [InlineKeyboardButton(t("btn_deploy", lang),  callback_data="m_deploy"),
         InlineKeyboardButton(t("btn_restart", lang), callback_data="m_restart")],
        [InlineKeyboardButton(t("btn_scan", lang),    callback_data="m_scan"),
         InlineKeyboardButton(t("btn_block", lang),   callback_data="m_block")],
        [InlineKeyboardButton(t("btn_logs", lang),    callback_data="m_logs"),
         InlineKeyboardButton(t("btn_help", lang),    callback_data="m_help")],
        [InlineKeyboardButton(t("btn_lang", lang),    callback_data=f"lang|{'en' if lang=='ru' else 'ru'}")],
    ])

def back_kb(lang):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_back", lang), callback_data="m_back")
    ]])

def confirm_kb(lang):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_ok", lang),     callback_data="confirm_exec"),
        InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_exec"),
    ]])

# ── ANIMATED LOADER ───────────────────────────────────────────
async def animate(msg, frames, lang, task):
    """Show animated loading while coroutine runs."""
    result_holder = {}
    async def runner():
        result_holder["out"] = await task
    run_task = asyncio.create_task(runner())
    i = 0
    while not run_task.done():
        try:
            await msg.edit_text(frames[i % len(frames)])
        except Exception:
            pass
        i += 1
        await asyncio.sleep(0.9)
    await run_task
    return result_holder["out"]

# ── PUBLIC ────────────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    await update.message.reply_text(
        t("welcome", lang), reply_markup=main_kb(lang), parse_mode="Markdown"
    )

async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    lang = get_lang(update, ctx)
    await update.message.reply_text(
        t("myid", lang, cid=cid), parse_mode="Markdown"
    )

# ── ADMIN ─────────────────────────────────────────────────────
@require_admin
async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    msg = await update.message.reply_text(S["loading_status"][lang][0])
    result = await animate(msg, S["loading_status"][lang], lang, execute(StatusCommand()))
    await msg.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")

@require_admin
async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    msg = await update.message.reply_text(S["loading_scan"][lang][0])
    result = await animate(msg, S["loading_scan"][lang], lang, execute(ScanCommand()))
    await msg.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")

@require_admin
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    lang = ctx.user_data.get("lang", "ru")

    if data.startswith("lang|"):
        lang = data.split("|")[1]
        ctx.user_data["lang"] = lang
        await q.edit_message_text(
            t("welcome", lang), reply_markup=main_kb(lang), parse_mode="Markdown"
        )

    elif data == "m_back":
        await q.edit_message_text(
            t("welcome", lang), reply_markup=main_kb(lang), parse_mode="Markdown"
        )

    elif data == "m_status":
        await q.edit_message_text(S["loading_status"][lang][0])
        result = await animate(q.message, S["loading_status"][lang], lang, execute(StatusCommand()))
        await q.message.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")

    elif data == "m_scan":
        await q.edit_message_text(S["loading_scan"][lang][0])
        result = await animate(q.message, S["loading_scan"][lang], lang, execute(ScanCommand()))
        await q.message.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")

    elif data in S["sections"]:
        text = S["sections"][data].get(lang) or S["sections"][data].get("en")
        await q.edit_message_text(text, reply_markup=back_kb(lang), parse_mode="Markdown")

    elif data == "confirm_exec" and ctx.user_data.get("pending_command"):
        await q.edit_message_text(S["executing"][lang][0])
        result = await animate(q.message, S["executing"][lang], lang, execute(ctx.user_data.pop("pending_command")))
        await q.message.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")

    elif data == "cancel_exec":
        ctx.user_data.pop("pending_command", None)
        await q.edit_message_text(
            t("cancelled", lang), reply_markup=main_kb(lang), parse_mode="Markdown"
        )

@require_admin
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    msg = await update.message.reply_text(S["loading"][lang][0])
    try:
        await update.message.chat.send_action(ChatAction.TYPING)

        async def parse_and_preview():
            cmd = await parse_command(update.message.text)
            if cmd is None:
                return None, None
            return cmd, await preview(cmd)

        result_holder = {}
        async def runner():
            result_holder["out"] = await parse_and_preview()
        run_task = asyncio.create_task(runner())
        i = 0
        while not run_task.done():
            try:
                await msg.edit_text(S["loading"][lang][i % len(S["loading"][lang])])
            except Exception:
                pass
            i += 1
            await asyncio.sleep(0.9)
        await run_task
        cmd, result = result_holder["out"]

        if cmd is None:
            await msg.edit_text(
                t("not_understood", lang),
                reply_markup=back_kb(lang), parse_mode="Markdown"
            )
            return

        ctx.user_data["pending_command"] = cmd
        await msg.edit_text(result, reply_markup=confirm_kb(lang), parse_mode="Markdown")

    except Exception as e:
        await msg.edit_text(f"❌ `{e}`", reply_markup=back_kb(lang), parse_mode="Markdown")
