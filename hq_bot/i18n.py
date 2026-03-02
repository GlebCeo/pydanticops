"""Bilingual strings — RU / EN"""

STRINGS = {
    "welcome": {
        "ru": (
            "👋 Привет! Я *PydanticOps HQ*\n\n"
            "Превращаю твой Linux-сервер с GPU в послушный инструмент — "
            "управляй моделями, Docker и мониторингом прямо из Telegram.\n\n"
            "Выбери раздел 👇"
        ),
        "en": (
            "👋 Hey! I'm *PydanticOps HQ*\n\n"
            "I turn your Linux GPU server into an obedient tool — "
            "deploy AI models, manage Docker and monitor everything from Telegram.\n\n"
            "Choose a section 👇"
        ),
    },
    "what_is": {
        "ru": (
            "🤖 *Что такое PydanticOps?*\n\n"
            "Telegram-бот, который живёт на *твоём сервере* и даёт полный контроль:\n\n"
            "🚀 *Деплой моделей* — «Подними DeepSeek на 30000 с 12 ГБ VRAM» "
            "→ бот генерирует docker-compose с авто-квантизацией и запускает\n\n"
            "📊 *Мониторинг* — GPU температура, VRAM, Docker ps в реальном времени\n\n"
            "🩺 *Auto-healing* — SGLang упал? Бот сам перезапустит и пришлёт отчёт\n\n"
            "🔍 *OSINT защита* — сканирует nginx-логи, блокирует атакующие IP\n\n"
            "🔒 *Safety first* — деструктивные команды требуют твоего «✅ Ок»"
        ),
        "en": (
            "🤖 *What is PydanticOps?*\n\n"
            "A Telegram bot that lives on *your server* and gives you full control:\n\n"
            "🚀 *Model Deploy* — 'Launch DeepSeek on port 30000 with 12GB VRAM' "
            "→ bot generates docker-compose with auto-quantization and runs it\n\n"
            "📊 *Monitoring* — GPU temp, VRAM usage, Docker ps in real time\n\n"
            "🩺 *Auto-healing* — SGLang crashed? Bot restarts it and sends a report\n\n"
            "🔍 *OSINT protection* — scans nginx logs, blocks attacking IPs\n\n"
            "🔒 *Safety first* — destructive actions require your '✅ OK'"
        ),
    },
    "install": {
        "ru": (
            "⚡ *Установка на свой сервер*\n\n"
            "Одна команда на твоём Linux-сервере:\n\n"
            "```bash\ngit clone https://github.com/pydanticops/pydanticops\n"
            "cd pydanticops && bash install.sh\n```\n\n"
            "Установщик сам:\n"
            "✅ Проверит Python\n"
            "✅ Установит зависимости\n"
            "✅ Спросит Telegram токен и твой ID\n"
            "✅ Зарегистрирует systemd сервис (автозапуск)\n\n"
            "_Требования: Linux, Python 3.12+, Docker_"
        ),
        "en": (
            "⚡ *Install on your server*\n\n"
            "One command on your Linux server:\n\n"
            "```bash\ngit clone https://github.com/pydanticops/pydanticops\n"
            "cd pydanticops && bash install.sh\n```\n\n"
            "The installer will:\n"
            "✅ Check Python\n"
            "✅ Install dependencies\n"
            "✅ Ask for Telegram token and your ID\n"
            "✅ Register as a systemd service (auto-start)\n\n"
            "_Requirements: Linux, Python 3.12+, Docker_"
        ),
    },
    "stack": {
        "ru": (
            "🛠 *Технический стек*\n\n"
            "• *Telegram Bot API* — интерфейс (polling или webhook)\n"
            "• *Pydantic v2* — type-safe валидация команд (защита от галлюцинаций)\n"
            "• *FastAPI + uvicorn* — async webhook сервер\n"
            "• *OpenAI-compatible API* — работает с локальным SGLang/vLLM *бесплатно*\n"
            "• *Jinja2* — генерация docker-compose шаблонов\n"
            "• *nvidia-smi* — GPU мониторинг\n"
            "• *CAT Protocol* — форматирование кода как артефактов в Telegram\n\n"
            "_Open Source • MIT License_"
        ),
        "en": (
            "🛠 *Tech Stack*\n\n"
            "• *Telegram Bot API* — interface (polling or webhook)\n"
            "• *Pydantic v2* — type-safe command validation (hallucination guard)\n"
            "• *FastAPI + uvicorn* — async webhook server\n"
            "• *OpenAI-compatible API* — works with local SGLang/vLLM *for free*\n"
            "• *Jinja2* — docker-compose template generation\n"
            "• *nvidia-smi* — GPU monitoring\n"
            "• *CAT Protocol* — code formatted as artifacts in Telegram\n\n"
            "_Open Source • MIT License_"
        ),
    },
    "demo": {
        "ru": (
            "💬 *Примеры команд*\n\n"
            "После установки на свой сервер ты пишешь:\n\n"
            "`Подними DeepSeek-R1 на 30000 с 12 ГБ VRAM`\n"
            "→ Бот генерирует compose + авто-квантизация под твой GPU\n\n"
            "`Покажи логи sglang последние 100 строк`\n"
            "→ Хвост логов прямо в Telegram\n\n"
            "`Заблокируй 89.248.168.239 — сканер портов`\n"
            "→ Preview блокировки + кнопка подтверждения\n\n"
            "`/status`\n"
            "→ Docker ps + GPU info + SGLang health\n\n"
            "`/scan`\n"
            "→ OSINT таблица подозрительных IP из логов"
        ),
        "en": (
            "💬 *Command examples*\n\n"
            "After installing on your server you write:\n\n"
            "`Launch DeepSeek-R1 on port 30000 with 12GB VRAM`\n"
            "→ Bot generates compose + auto-quantization for your GPU\n\n"
            "`Show sglang logs last 100 lines`\n"
            "→ Log tail directly in Telegram\n\n"
            "`Block 89.248.168.239 — port scanner`\n"
            "→ Block preview + confirmation button\n\n"
            "`/status`\n"
            "→ Docker ps + GPU info + SGLang health\n\n"
            "`/scan`\n"
            "→ OSINT table of suspicious IPs from logs"
        ),
    },
    # Кнопки меню
    "btn_what":    {"ru": "🤖 Что такое PydanticOps", "en": "🤖 What is PydanticOps"},
    "btn_install": {"ru": "⚡ Установка",              "en": "⚡ Installation"},
    "btn_demo":    {"ru": "💬 Примеры команд",         "en": "💬 Command examples"},
    "btn_stack":   {"ru": "🛠 Стек технологий",        "en": "🛠 Tech stack"},
    "btn_lang":    {"ru": "🌐 Switch to English",      "en": "🌐 Переключить на Русский"},
    "btn_back":    {"ru": "⬅️ Назад",                  "en": "⬅️ Back"},
    "btn_github":  {"ru": "⭐ GitHub",                  "en": "⭐ GitHub"},
}

def t(key: str, lang: str) -> str:
    """Get translated string. Falls back to 'en'."""
    entry = STRINGS.get(key, {})
    return entry.get(lang) or entry.get("en") or key

def detect_lang(update) -> str:
    """Auto-detect language from Telegram user locale."""
    lc = getattr(update.effective_user, "language_code", "") or ""
    return "ru" if lc.startswith("ru") else "en"
