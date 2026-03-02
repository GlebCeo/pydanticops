import os
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

def require_admin(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        admin_id = int(os.getenv("ADMIN_CHAT_ID", "0"))
        chat_id = update.effective_chat.id
        if chat_id != admin_id:
            await update.message.reply_text(
                f"🔒 Access Denied\. Твой ID: `{chat_id}`",
                parse_mode="MarkdownV2"
            )
            return
        return await func(update, ctx, *args, **kwargs)
    return wrapper
