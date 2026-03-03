import asyncio, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.auth import require_admin
from core.validator import parse_command
from core.executor import preview, execute
from core.schemas import StatusCommand, ScanCommand

S = {
    "welcome": {
        "ru": "⚡ *PydanticOps* — управление сервером из Telegram\n\nВыбери раздел или напиши команду 👇",
        "en": "⚡ *PydanticOps* — server control from Telegram\n\nChoose a section or type a command 👇",
    },
    "loading_status": {
        "ru": ["📊 Получаю статус...", "📊 Опрашиваю Docker..", "📊 Проверяю GPU...", "📊 Почти готово..."],
        "en": ["📊 Getting status...", "📊 Fetching Docker..", "📊 Checking GPU...", "📊 Almost done..."],
    },
    "loading_scan": {
        "ru": ["🔍 Сканирую логи...", "🔍 Ищу атаки..", "🔍 Анализирую IP...", "🔍 Почти готово..."],
        "en": ["🔍 Scanning logs...", "🔍 Finding attacks..", "🔍 Analyzing IPs...", "🔍 Almost done..."],
    },
    "loading": {
        "ru": ["⏳ Обрабатываю...", "⌛ Думаю..", "⏳ Парсю команду...", "⌛ Почти..."],
        "en": ["⏳ Processing...", "⌛ Thinking..", "⏳ Parsing command...", "⌛ Almost..."],
    },
    "executing": {
        "ru": ["⚙️ Выполняю...", "⚙️ Работаю..", "⚙️ Почти..."],
        "en": ["⚙️ Executing...", "⚙️ Working..", "⚙️ Almost..."],
    },
    "sections": {
        "m_deploy": {
            "ru": "🚀 *Деплой AI-модели*\n\nНапиши:\n`Подними DeepSeek-R1 на 30000 с 12 ГБ VRAM`\n`Запусти Qwen2 на 8080 с 24 ГБ VRAM`\n\nБот подберёт квантизацию и покажет docker-compose на подтверждение.",
            "en": "🚀 *Deploy AI Model*\n\nType:\n`Launch DeepSeek-R1 on 30000 with 12GB VRAM`\n`Start Qwen2 on 8080 with 24GB VRAM`\n\nBot picks quantization and shows docker-compose for confirmation.",
        },
        "m_restart": {
            "ru": "🔁 *Рестарт сервиса*\n\nНапиши:\n`Перезапусти sglang`\n`Перезапусти nginx`",
            "en": "🔁 *Restart Service*\n\nType:\n`Restart sglang`\n`Restart nginx`",
        },
        "m_block": {
            "ru": "🚫 *Блокировка IP*\n\nНапиши:\n`Заблокируй 89.248.168.239`",
            "en": "🚫 *Block IP*\n\nType:\n`Block 89.248.168.239`",
        },
        "m_logs": {
            "ru": "📋 *Просмотр логов*\n\nНапиши:\n`Покажи логи sglang последние 50 строк`\n`Покажи логи nginx`",
            "en": "📋 *View Logs*\n\nType:\n`Show sglang logs last 50 lines`\n`Show nginx logs`",
        },
        "m_help": {
            "ru": (
                "❓ *Все команды*\n\n"
                "*📊 Мониторинг:*\n"
                "`Сколько места на диске?`\n"
                "`Покажи нагрузку CPU и RAM`\n"
                "`Какие порты открыты?`\n"
                "`docker stats`\n"
                "`/status` — Docker + GPU + SGLang\n\n"
                "*🚀 Деплой:*\n"
                "`Подними DeepSeek-R1 на 30000 с 12 ГБ VRAM`\n"
                "`Перезапусти nginx`\n"
                "`Покажи логи nginx последние 50 строк`\n\n"
                "*🔍 Безопасность:*\n"
                "`Пингани 8.8.8.8`\n"
                "`Заблокируй 1.2.3.4`\n"
                "`/scan` — OSINT атакующие IP\n\n"
                "`Покажи файл /etc/nginx/nginx.conf`\n\n"
                "⚡ Groq llama-3.3-70b понимает любые формулировки\n"
                "🔒 Опасные команды требуют ✅"
            ),
            "en": (
                "❓ *All commands*\n\n"
                "*📊 Monitoring:*\n"
                "`How much disk space?`\n"
                "`Show CPU and RAM load`\n"
                "`What ports are open?`\n"
                "`docker stats`\n"
                "`/status` — Docker + GPU + SGLang\n\n"
                "*🚀 Deploy:*\n"
                "`Launch DeepSeek-R1 on 30000 with 12GB VRAM`\n"
                "`Restart nginx`\n"
                "`Show nginx logs last 50 lines`\n\n"
                "*🔍 Security:*\n"
                "`Ping 8.8.8.8`\n"
                "`Block 1.2.3.4`\n"
                "`/scan` — OSINT attacking IPs\n\n"
                "`Show file /etc/nginx/nginx.conf`\n\n"
                "⚡ Groq llama-3.3-70b understands any phrasing\n"
                "🔒 Dangerous commands require ✅"
            ),
        },
    },
}

def get_lang(update, ctx):
    if "lang" not in ctx.user_data:
        lc = getattr(update.effective_user, "language_code", "") or ""
        ctx.user_data["lang"] = "ru" if lc.startswith("ru") else "en"
    return ctx.user_data["lang"]

def main_kb(lang):
    r = lang == "ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Статус сервера" if r else "📊 Server Status", callback_data="m_status")],
        [InlineKeyboardButton("🚀 Деплой модели" if r else "🚀 Deploy Model",   callback_data="m_deploy"),
         InlineKeyboardButton("🔁 Рестарт" if r else "🔁 Restart",             callback_data="m_restart")],
        [InlineKeyboardButton("🔍 OSINT Скан" if r else "🔍 OSINT Scan",       callback_data="m_scan"),
         InlineKeyboardButton("🚫 Блок IP" if r else "🚫 Block IP",            callback_data="m_block")],
        [InlineKeyboardButton("📋 Логи" if r else "📋 Logs",                   callback_data="m_logs"),
         InlineKeyboardButton("❓ Помощь" if r else "❓ Help",                  callback_data="m_help")],
        [InlineKeyboardButton("🌐 English" if r else "🌐 Русский",             callback_data=f"lang|{'en' if r else 'ru'}")],
    ])

def back_kb(lang):
    r = lang == "ru"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⬅️ Главное меню" if r else "⬅️ Main menu", callback_data="m_back")
    ]])

def confirm_kb(lang):
    r = lang == "ru"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Выполнить" if r else "✅ Execute", callback_data="confirm_exec"),
        InlineKeyboardButton("❌ Отмена" if r else "❌ Cancel",     callback_data="cancel_exec"),
    ]])

async def animate(msg, frames, task):
    holder = {"out": None, "done": False}
    async def runner():
        holder["out"] = await task
        holder["done"] = True
    asyncio.create_task(runner())
    i, last = 0, ""
    while not holder["done"]:
        frame = frames[i % len(frames)]
        if frame != last:
            try:
                await msg.edit_text(frame)
                last = frame
            except Exception:
                pass
        i += 1
        await asyncio.sleep(1.2)
    return holder["out"]

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    await update.message.reply_text(
        S["welcome"][lang], reply_markup=main_kb(lang), parse_mode="Markdown"
    )

async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    lang = get_lang(update, ctx)
    r = lang == "ru"
    await update.message.reply_text(
        f"🪪 {'Твой' if r else 'Your'} Chat ID: `{cid}`\n\n{'Добавь в' if r else 'Add to'} `.env`:\n`ADMIN_CHAT_ID={cid}`",
        parse_mode="Markdown"
    )

@require_admin
async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    msg = await update.message.reply_text(S["loading_status"][lang][0])
    result = await animate(msg, S["loading_status"][lang], execute(StatusCommand()))
    await msg.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")

@require_admin
async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    msg = await update.message.reply_text(S["loading_scan"][lang][0])
    result = await animate(msg, S["loading_scan"][lang], execute(ScanCommand()))
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
        await q.edit_message_text(S["welcome"][lang], reply_markup=main_kb(lang), parse_mode="Markdown")
    elif data == "m_back":
        await q.edit_message_text(S["welcome"][lang], reply_markup=main_kb(lang), parse_mode="Markdown")
    elif data == "m_status":
        await q.edit_message_text(S["loading_status"][lang][0])
        result = await animate(q.message, S["loading_status"][lang], execute(StatusCommand()))
        await q.message.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")
    elif data == "m_scan":
        await q.edit_message_text(S["loading_scan"][lang][0])
        result = await animate(q.message, S["loading_scan"][lang], execute(ScanCommand()))
        await q.message.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")
    elif data in S["sections"]:
        text = S["sections"][data].get(lang) or S["sections"][data].get("en")
        await q.edit_message_text(text, reply_markup=back_kb(lang), parse_mode="Markdown")
    elif data == "confirm_exec" and ctx.user_data.get("pending_command"):
        await q.edit_message_text(S["executing"][lang][0])
        result = await animate(q.message, S["executing"][lang], execute(ctx.user_data.pop("pending_command")))
        await q.message.edit_text(result, reply_markup=back_kb(lang), parse_mode="Markdown")
    elif data == "cancel_exec":
        ctx.user_data.pop("pending_command", None)
        await q.edit_message_text(S["welcome"][lang], reply_markup=main_kb(lang), parse_mode="Markdown")

@require_admin
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    msg = await update.message.reply_text(S["loading"][lang][0])
    try:
        async def parse_and_preview():
            cmd = await parse_command(update.message.text)
            if cmd is None:
                return None, None
            return cmd, await preview(cmd)
        holder = {"out": None, "done": False}
        async def runner():
            holder["out"] = await parse_and_preview()
            holder["done"] = True
        asyncio.create_task(runner())
        i, last = 0, ""
        while not holder["done"]:
            frame = S["loading"][lang][i % len(S["loading"][lang])]
            if frame != last:
                try:
                    await msg.edit_text(frame)
                    last = frame
                except Exception:
                    pass
            i += 1
            await asyncio.sleep(1.2)
        cmd, result = holder["out"]
        if cmd is None:
            r = lang == "ru"
            await msg.edit_text(
                ("❓ Не понял команду.\n\nПримеры:\n`Подними DeepSeek на 30000 с 12 ГБ VRAM`\n`Покажи логи nginx`\n`Заблокируй 1.2.3.4`" if r else
                 "❓ Command not recognized.\n\nExamples:\n`Launch DeepSeek on 30000 with 12GB VRAM`\n`Show nginx logs`\n`Block 1.2.3.4`"),
                reply_markup=back_kb(lang), parse_mode="Markdown"
            )
            return
        ctx.user_data["pending_command"] = cmd
        await msg.edit_text(result, reply_markup=confirm_kb(lang), parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ `{e}`", reply_markup=back_kb(lang), parse_mode="Markdown")
