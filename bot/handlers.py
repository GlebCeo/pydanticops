import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.auth import require_admin
from core.validator import parse_command
from core.executor import preview, execute

# ── PUBLIC ────────────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Статус",     callback_data="quick_status"),
            InlineKeyboardButton("🔍 OSINT Скан", callback_data="quick_scan"),
        ],
        [
            InlineKeyboardButton("📋 Помощь",     callback_data="quick_help"),
            InlineKeyboardButton("🪪 Мой ID",     callback_data="quick_myid"),
        ],
    ])
    await update.message.reply_text(
        "👋 *PydanticOps* онлайн!\n\n"
        "Управляй сервером на естественном языке:\n\n"
        "🚀 `Подними DeepSeek на 30000 с 12 ГБ VRAM`\n"
        "📋 `Покажи логи nginx`\n"
        "🚫 `Заблокируй 1.2.3.4`\n"
        "🔁 `Перезапусти sglang`\n\n"
        "Или используй быстрые кнопки 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.reply_text(
        f"🪪 Твой *Chat ID*: `{cid}`\n\nДобавь в `.env`:\n`ADMIN_CHAT_ID={cid}`",
        parse_mode="Markdown"
    )

# ── ADMIN COMMANDS ────────────────────────────────────────────
@require_admin
async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)
    from core.schemas import StatusCommand
    result = await execute(StatusCommand())
    await update.message.reply_text(result, parse_mode="Markdown")

@require_admin
async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 Сканирую логи...")
    await update.message.chat.send_action(ChatAction.TYPING)
    from core.schemas import ScanCommand
    result = await execute(ScanCommand())
    await msg.edit_text(result, parse_mode="Markdown")

# ── QUICK BUTTONS ─────────────────────────────────────────────
@require_admin
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "quick_status":
        await q.message.chat.send_action(ChatAction.TYPING)
        from core.schemas import StatusCommand
        result = await execute(StatusCommand())
        await q.message.reply_text(result, parse_mode="Markdown")

    elif q.data == "quick_scan":
        msg = await q.message.reply_text("🔍 Сканирую логи...")
        from core.schemas import ScanCommand
        result = await execute(ScanCommand())
        await msg.edit_text(result, parse_mode="Markdown")

    elif q.data == "quick_myid":
        cid = q.message.chat.id
        await q.message.reply_text(f"🪪 Chat ID: `{cid}`", parse_mode="Markdown")

    elif q.data == "quick_help":
        await q.message.reply_text(
            "📋 *Команды*\n\n"
            "*Быстрые:*\n"
            "`/status` — Docker + GPU + SGLang\n"
            "`/scan` — OSINT сканирование\n"
            "`/myid` — твой Telegram ID\n\n"
            "*Натуральный язык:*\n"
            "`Подними <model> на <port> с <N> ГБ VRAM`\n"
            "`Покажи логи <service> [последние N строк]`\n"
            "`Перезапусти <service>`\n"
            "`Заблокируй <ip>`\n\n"
            "*LLM:* Groq llama-3.3-70b ⚡",
            parse_mode="Markdown"
        )

    elif q.data == "confirm_exec" and ctx.user_data.get("pending_command"):
        msg = await q.message.reply_text("⏳ Выполняю...")
        result = await execute(ctx.user_data.pop("pending_command"))
        await msg.edit_text(result, parse_mode="Markdown")
        await q.message.edit_reply_markup(reply_markup=None)

    elif q.data == "cancel_exec":
        ctx.user_data.pop("pending_command", None)
        await q.edit_message_text("❌ Отменено")

# ── NL MESSAGE ────────────────────────────────────────────────
@require_admin
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    msg = await update.message.reply_text("⏳ Обрабатываю...")

    try:
        await update.message.chat.send_action(ChatAction.TYPING)
        cmd = await parse_command(text)

        if cmd is None:
            await msg.edit_text(
                "❓ Не понял команду. Попробуй:\n\n"
                "`Подними <model> на <port>`\n"
                "`Покажи логи <service>`\n"
                "`Заблокируй <ip>`\n"
                "`Перезапусти <service>`",
                parse_mode="Markdown"
            )
            return

        result = await preview(cmd)
        ctx.user_data["pending_command"] = cmd

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Выполнить", callback_data="confirm_exec"),
            InlineKeyboardButton("❌ Отмена",    callback_data="cancel_exec"),
        ]])
        await msg.edit_text(result, reply_markup=kb, parse_mode="Markdown")

    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: `{e}`", parse_mode="Markdown")
