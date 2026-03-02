import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.auth import require_admin
from core.validator import parse_command
from core.executor import preview, execute

# ── PUBLIC ────────────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *PydanticOps* онлайн!\n\n"
        "Пиши что нужно:\n"
        "• `Подними DeepSeek на 30000 с 12 ГБ VRAM`\n"
        "• `Покажи логи sglang`\n"
        "• `Заблокируй 1.2.3.4`\n"
        "• `/status` — быстрый статус\n"
        "• `/scan` — OSINT сканирование",
        parse_mode="Markdown"
    )

async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.reply_text(
        f"🪪 Твой *Chat ID*: `{cid}`\n\nДобавь в `.env`:\n`ADMIN_CHAT_ID={cid}`",
        parse_mode="Markdown"
    )

# ── ADMIN ─────────────────────────────────────────────────────
@require_admin
async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from core.executor import execute
    from core.schemas import StatusCommand
    result = await execute(StatusCommand())
    await update.message.reply_text(result, parse_mode="Markdown")

@require_admin
async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from core.executor import execute
    from core.schemas import ScanCommand
    result = await execute(ScanCommand())
    await update.message.reply_text(result, parse_mode="Markdown")

@require_admin
async def handle_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "confirm_exec" and ctx.user_data.get("pending_command"):
        result = await execute(ctx.user_data["pending_command"])
        await q.edit_message_text(result, parse_mode="Markdown")
        ctx.user_data.pop("pending_command", None)
    elif q.data == "cancel_exec":
        await q.edit_message_text("❌ Отменено")
        ctx.user_data.pop("pending_command", None)

@require_admin
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    msg = await update.message.reply_text("⏳ Обрабатываю...")

    try:
        cmd = await parse_command(text)
        if cmd is None:
            await msg.edit_text("❓ Не понял команду. Попробуй:\n`Подними <model> на <port>`\n`Покажи логи <service>`\n`Заблокируй <ip>`", parse_mode="Markdown")
            return

        result = await preview(cmd)
        ctx.user_data["pending_command"] = cmd

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Выполнить", callback_data="confirm_exec"),
            InlineKeyboardButton("❌ Отмена",    callback_data="cancel_exec"),
        ]])
        await msg.edit_text(result, reply_markup=kb, parse_mode="Markdown")

    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")
