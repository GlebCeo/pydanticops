#!/bin/bash
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
info()    { echo -e "${CYAN}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $1${NC}"; }

clear
echo -e "${CYAN}${BOLD}"
cat << 'BANNER'
██████╗ ██╗   ██╗██████╗  █████╗ ███╗   ██╗████████╗██╗ ██████╗ ██████╗ ██████╗ ███████╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗████╗  ██║╚══██╔══╝██║██╔════╝██╔═══██╗██╔══██╗██╔════╝
██████╔╝ ╚████╔╝ ██║  ██║███████║██╔██╗ ██║   ██║   ██║██║     ██║   ██║██████╔╝███████╗
██╔═══╝   ╚██╔╝  ██║  ██║██╔══██║██║╚██╗██║   ██║   ██║██║     ██║   ██║██╔═══╝ ╚════██║
██║        ██║   ██████╔╝██║  ██║██║ ╚████║   ██║   ██║╚██████╗╚██████╔╝██║     ███████║
╚═╝        ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝
BANNER
echo -e "${NC}"
echo -e "${BOLD}        AI Infrastructure Control — control your server from Telegram${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Python ────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    info "Устанавливаем Python..."
    apt-get update -qq && apt-get install -y python3 python3-venv python3-pip -qq
fi
success "Python $(python3 --version | cut -d' ' -f2) найден"

# ── Venv ──────────────────────────────────────────────────────
INSTALL_DIR="${1:-$PWD}"
cd "$INSTALL_DIR"
if [ ! -d ".venv" ]; then
    info "Создаём виртуальное окружение..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q fastapi "uvicorn[standard]" python-telegram-bot pydantic \
    "pydantic-ai>=0.0.15" python-dotenv httpx jinja2 pyyaml aiofiles openai
success "Зависимости установлены"

# ── Интерактивная настройка ───────────────────────────────────
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📋 Настройка PydanticOps${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

[ -f .env ] && source .env 2>/dev/null || true

echo -e "${CYAN}[1/4] Telegram Bot Token${NC}"
echo "      1. Открой @BotFather в Telegram"
echo "      2. /newbot → задай имя → получи токен"
read -p "  Токен: " TOKEN
TOKEN="${TOKEN:-$TELEGRAM_TOKEN}"

echo ""
echo -e "${CYAN}[2/4] Твой Telegram ID${NC}"
echo "      Напиши своему боту /myid — он ответит твоим ID"
echo "      (Запусти бота сначала: source .venv/bin/activate && python -m uvicorn bot.main:app --port 8443)"
read -p "  ADMIN_CHAT_ID: " ADMIN_ID
ADMIN_ID="${ADMIN_ID:-$ADMIN_CHAT_ID}"

echo ""
echo -e "${CYAN}[3/4] LLM Backend для парсинга команд${NC}"
echo "      1) Локальный SGLang/vLLM (БЕСПЛАТНО) — Enter"
echo "      2) OpenAI — введи API ключ"
read -p "  OpenAI API Key [Enter = local]: " OKEY
if [ -z "$OKEY" ]; then
    OPENAI_BASE_URL="http://37.140.243.164:8001/v1"
    OPENAI_API_KEY="local"
    LLM_MODEL="default"
    success "Используем локальный SGLang (бесплатно)"
else
    OPENAI_BASE_URL="https://api.openai.com/v1"
    OPENAI_API_KEY="$OKEY"
    LLM_MODEL="gpt-4o-mini"
    success "OpenAI gpt-4o-mini настроен"
fi

echo ""
echo -e "${CYAN}[4/4] SGLang порт${NC}"
read -p "  Порт SGLang [30000]: " SGLANG_PORT
SGLANG_PORT="${SGLANG_PORT:-30000}"

# ── .env ──────────────────────────────────────────────────────
cat > .env << EOF
# PydanticOps — Configuration
TELEGRAM_TOKEN=$TOKEN
ADMIN_CHAT_ID=$ADMIN_ID

# LLM Backend
OPENAI_BASE_URL=$OPENAI_BASE_URL
OPENAI_API_KEY=$OPENAI_API_KEY
LLM_MODEL=$LLM_MODEL

# SGLang / Inference Server
SGLANG_HOST=localhost
SGLANG_PORT=$SGLANG_PORT
SGLANG_HEALTH_INTERVAL=30
SGLANG_MAX_FAILURES=3
GPU_TEMP_LIMIT=85

# Webhook (leave empty for polling mode)
WEBHOOK_URL=

# OpenClaw Bridge — allowed paths for sandboxed access
ALLOWED_DIRS=/opt/compose-files,/var/log/nginx
COMPOSE_FILES_DIR=/opt/compose-files
EOF
success ".env создан"

# ── Systemd ───────────────────────────────────────────────────
VENV_UV="$INSTALL_DIR/.venv/bin/uvicorn"
SERVICE_FILE="/etc/systemd/system/pydanticops.service"
cat > /tmp/pydanticops.service << EOF
[Unit]
Description=PydanticOps — AI Infrastructure Control Bot
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_UV bot.main:app --host 127.0.0.1 --port 8443
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pydanticops

[Install]
WantedBy=multi-user.target
EOF

if command -v systemctl &>/dev/null && [ "$EUID" -eq 0 ]; then
    cp /tmp/pydanticops.service "$SERVICE_FILE"
    systemctl daemon-reload
    systemctl enable pydanticops
    systemctl restart pydanticops
    success "systemd сервис запущен (auto-start при перезагрузке)"
else
    warn "Запусти от root для systemd. Или вручную:"
    echo ""
    echo -e "  ${BOLD}source .venv/bin/activate"
    echo -e "  python -m uvicorn bot.main:app --port 8443${NC}"
fi

# ── Итог ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}🎉 PydanticOps установлен!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  📱 Найди бота в Telegram и напиши /start"
echo ""
echo "  Команды:"
echo "  ┌─────────────────────────────────────────────────┐"
echo "  │ /start  — меню                                  │"
echo "  │ /status — Docker + GPU + SGLang                 │"
echo "  │ /scan   — OSINT сканирование логов              │"
echo "  │ /myid   — твой Telegram ID                      │"
echo "  │                                                 │"
echo "  │ «Подними DeepSeek на 30000 с 12 ГБ VRAM»       │"
echo "  │ «Покажи логи nginx»                             │"
echo "  │ «Заблокируй 1.2.3.4»                           │"
echo "  └─────────────────────────────────────────────────┘"
echo ""
echo "  Логи: journalctl -u pydanticops -f"
echo ""
