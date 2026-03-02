from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

GITHUB = "https://github.com/pydanticops/pydanticops"

TEXT = {
    "welcome": {
        "ru": "👋 Привет! Я *PydanticOps HQ* — гид по AI-инфраструктуре.\n\nУзнай как управлять GPU-сервером прямо из Telegram 👇",
        "en": "👋 Hey! I'm *PydanticOps HQ* — your AI infrastructure guide.\n\nLearn how to control your GPU server from Telegram 👇",
    },
    "what": {
        "ru": "🤖 *Что такое PydanticOps?*\n\nTelegram-бот на *твоём сервере* который умеет:\n\n🚀 *Деплой моделей* — «Подними DeepSeek на 30000 с 12 ГБ» → авто-квантизация + docker-compose + запуск\n\n📊 *Мониторинг* — GPU температура, VRAM, Docker в реальном времени\n\n🩺 *Auto-healing* — SGLang упал? Бот сам перезапустит и пришлёт отчёт\n\n🔍 *OSINT защита* — сканирует логи, находит атакующих, блокирует IP одной кнопкой\n\n🔒 *Safety first* — опасные команды ждут твоего ✅\n\n_Open Source • MIT • Python 3.12_",
        "en": "🤖 *What is PydanticOps?*\n\nA Telegram bot living on *your server* that can:\n\n🚀 *Deploy models* — 'Launch DeepSeek on 30000 with 12GB' → auto-quantization + docker-compose + run\n\n📊 *Monitor* — GPU temp, VRAM, Docker in real time\n\n🩺 *Auto-healing* — SGLang crashed? Bot restarts it and reports\n\n🔍 *OSINT protection* — scans logs, finds attackers, blocks IPs with one button\n\n🔒 *Safety first* — destructive actions wait for your ✅\n\n_Open Source • MIT • Python 3.12_",
    },
    "install": {
        "ru": "⚡ *Установка на свой сервер*\n\n*Требования:* Linux, Python 3.12+, Docker\n\n```bash\ngit clone https://github.com/pydanticops/pydanticops\ncd pydanticops\nbash install.sh\n```\n\nУстановщик сам:\n✅ Установит зависимости\n✅ Спросит Telegram-токен и твой chat ID\n✅ Выберет LLM — SGLang локально (*бесплатно*) или OpenAI\n✅ Создаст systemd сервис — автозапуск при ребуте\n\nПосле установки пишешь /start своему боту — и он твой 🎉",
        "en": "⚡ *Installation on your server*\n\n*Requirements:* Linux, Python 3.12+, Docker\n\n```bash\ngit clone https://github.com/pydanticops/pydanticops\ncd pydanticops\nbash install.sh\n```\n\nThe installer will:\n✅ Install all dependencies\n✅ Ask for Telegram token and your chat ID\n✅ Configure LLM — SGLang locally (*free*) or OpenAI\n✅ Create systemd service — auto-start on reboot\n\nAfter install, send /start to your bot — and it's yours 🎉",
    },
    "demo": {
        "ru": "💬 *Примеры команд*\n\nПосле установки на свой сервер пишешь:\n\n`Подними DeepSeek-R1 на 30000 с 12 ГБ VRAM`\n→ docker-compose с авто-квантизацией + кнопка запуска\n\n`Покажи логи nginx последние 100 строк`\n→ хвост логов прямо в Telegram\n\n`Заблокируй 89.248.168.239`\n→ preview + подтверждение → iptables блокировка\n\n`/status` → Docker ps + GPU + SGLang health\n\n`/scan` → OSINT таблица: кто атакует сервер прямо сейчас",
        "en": "💬 *Command examples*\n\nAfter installing on your server, you write:\n\n`Launch DeepSeek-R1 on port 30000 with 12GB VRAM`\n→ docker-compose with auto-quantization + deploy button\n\n`Show nginx logs last 100 lines`\n→ log tail directly in Telegram\n\n`Block 89.248.168.239`\n→ preview + confirm → iptables block\n\n`/status` → Docker ps + GPU + SGLang health\n\n`/scan` → OSINT table: who is attacking your server right now",
    },
    "stack": {
        "ru": "🛠 *Технический стек*\n\n• *Telegram Bot API* — интерфейс (polling / webhook)\n• *Pydantic v2* — type-safe валидация команд (без галлюцинаций)\n• *FastAPI + uvicorn* — async сервер\n• *OpenAI-compatible* — SGLang/vLLM локально = *бесплатно*\n• *Jinja2* — генерация docker-compose\n• *nvidia-smi* — GPU мониторинг\n• *iptables* — блокировка IP\n• *CAT Protocol* — код как артефакты в Telegram\n\n*Работает без GPU* — keyword-парсер не нужен LLM",
        "en": "🛠 *Tech Stack*\n\n• *Telegram Bot API* — interface (polling / webhook)\n• *Pydantic v2* — type-safe command validation (no hallucinations)\n• *FastAPI + uvicorn* — async server\n• *OpenAI-compatible* — SGLang/vLLM locally = *free*\n• *Jinja2* — docker-compose generation\n• *nvidia-smi* — GPU monitoring\n• *iptables* — IP blocking\n• *CAT Protocol* — code as artifacts in Telegram\n\n*Works without GPU* — keyword parser requires no LLM",
    },
    "courses": {
        "ru": "📚 *Курсы — скоро!*\n\n*Модуль 1* — Сервер с нуля: Ubuntu + Docker + NVIDIA\n*Модуль 2* — Локальные LLM: DeepSeek, Qwen, Llama\n*Модуль 3* — PydanticOps: установка и настройка\n*Модуль 4* — Auto-healing и мониторинг\n*Модуль 5* — OSINT: защита сервера от атак\n\n🔔 Подпишись чтобы не пропустить релиз",
        "en": "📚 *Courses — coming soon!*\n\n*Module 1* — Server from scratch: Ubuntu + Docker + NVIDIA\n*Module 2* — Local LLMs: DeepSeek, Qwen, Llama\n*Module 3* — PydanticOps: install & configure\n*Module 4* — Auto-healing and monitoring\n*Module 5* — OSINT: protecting your server\n\n🔔 Subscribe to get notified on release",
    },
}

def main_kb(lang):
    r = lang == "ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Что это" if r else "🤖 What is it", callback_data=f"what|{lang}"),
         InlineKeyboardButton("⚡ Установка" if r else "⚡ Install",   callback_data=f"install|{lang}")],
        [InlineKeyboardButton("💬 Примеры" if r else "💬 Examples",   callback_data=f"demo|{lang}"),
         InlineKeyboardButton("🛠 Стек" if r else "🛠 Stack",          callback_data=f"stack|{lang}")],
        [InlineKeyboardButton("📚 Курсы" if r else "📚 Courses",      callback_data=f"courses|{lang}"),
         InlineKeyboardButton("⭐ GitHub",                              url=GITHUB)],
        [InlineKeyboardButton("🌐 Switch to English" if r else "🌐 На Русский",
                              callback_data=f"menu|{'en' if r else 'ru'}")],
    ])

def back_kb(lang):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⬅️ Назад" if lang=="ru" else "⬅️ Back", callback_data=f"menu|{lang}"),
        InlineKeyboardButton("⭐ GitHub", url=GITHUB),
    ]])

def get_lang(update, ctx):
    if "lang" not in ctx.user_data:
        lc = getattr(update.effective_user, "language_code", "") or ""
        ctx.user_data["lang"] = "ru" if lc.startswith("ru") else "en"
    return ctx.user_data["lang"]

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    await update.message.reply_text(TEXT["welcome"][lang], reply_markup=main_kb(lang), parse_mode="Markdown")

async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.reply_text(f"🪪 Chat ID: `{cid}`", parse_mode="Markdown")

async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, ctx)
    await update.message.reply_text(TEXT["welcome"][lang], reply_markup=main_kb(lang), parse_mode="Markdown")

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action, lang = q.data.split("|", 1)
    ctx.user_data["lang"] = lang
    if action == "menu":
        await q.edit_message_text(TEXT["welcome"][lang], reply_markup=main_kb(lang), parse_mode="Markdown")
    elif action in TEXT:
        await q.edit_message_text(TEXT[action][lang], reply_markup=back_kb(lang), parse_mode="Markdown")
