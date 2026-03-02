from __future__ import annotations
import os, re, json
from openai import AsyncOpenAI
from pydantic import ValidationError
from core.schemas import (AnyCommand, DeployCommand, RestartCommand,
    BlockIPCommand, LogsCommand, StatusCommand, ScanCommand)

_client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "local"),
)

_SYSTEM = """
Разбери запрос и верни СТРОГО JSON с полем command_type.
Типы: DeployCommand, RestartCommand, BlockIPCommand, LogsCommand, StatusCommand, ScanCommand.
dry_run=true если пользователь явно не сказал "запусти/выполни/давай".
Если не можешь распознать: {"error": "причина"}.
Примеры:
"Подними DeepSeek на 30000 с 12 ГБ VRAM" -> {"command_type":"DeployCommand","model_name":"deepseek","port":30000,"vram_gb":12.0,"dry_run":true}
"Логи sglang 100 строк" -> {"command_type":"LogsCommand","service":"sglang","tail":100}
"Заблокируй 1.2.3.4" -> {"command_type":"BlockIPCommand","ip":"1.2.3.4","reason":"manual","dry_run":true}
"Статус" -> {"command_type":"StatusCommand"}
"""

_MAP = {
    "DeployCommand": DeployCommand, "RestartCommand": RestartCommand,
    "BlockIPCommand": BlockIPCommand, "LogsCommand": LogsCommand,
    "StatusCommand": StatusCommand, "ScanCommand": ScanCommand,
}

# ── Keyword fallback (работает без LLM) ───────────────────────
def _keyword_parse(text: str) -> AnyCommand | None:
    t = text.lower().strip()

    # Статус
    if any(w in t for w in ["статус", "status", "состояние", "что запущено"]):
        return StatusCommand()

    # Сканирование
    if any(w in t for w in ["скан", "scan", "атак", "osint", "подозрительн"]):
        return ScanCommand()

    # Логи: "логи nginx", "покажи логи sglang 100"
    m = re.search(r"лог[и]?\s+([a-z0-9_\-]+)(?:\s+(\d+))?|log[s]?\s+([a-z0-9_\-]+)(?:\s+(\d+))?", t)
    if m:
        service = m.group(1) or m.group(3)
        tail = int(m.group(2) or m.group(4) or 50)
        return LogsCommand(service=service, tail=min(tail, 500))

    # Перезапуск: "перезапусти sglang"
    m = re.search(r"перезапуст[и|ь]\s+([a-z0-9_\-]+)|restart\s+([a-z0-9_\-]+)", t)
    if m:
        return RestartCommand(service=m.group(1) or m.group(2))

    # Блокировка IP: "заблокируй 1.2.3.4"
    m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", t)
    if m and any(w in t for w in ["блокир", "ban", "block", "запрет"]):
        return BlockIPCommand(ip=m.group(1), reason="Blocked via bot")

    # Деплой: "подними X на PORT с N ГБ / GB VRAM"
    m = re.search(
        r"(подним|запуст|деплой|deploy|run|launch)[^\n]*?([a-zA-Z0-9\-\/\.]{3,}).*?(\d{4,5}).*?(\d+[\.,]?\d*)\s*(гб|gb|g)",
        t, re.IGNORECASE
    )
    if m:
        model = m.group(2)
        port = int(m.group(3))
        vram = float(m.group(4).replace(",", "."))
        return DeployCommand(model_name=model, port=port, vram_gb=vram)

    return None


async def parse_command(text: str) -> AnyCommand | str:
    # 1. Сначала пробуем keyword-парсер (мгновенно, без LLM)
    kw = _keyword_parse(text)
    if kw is not None:
        return kw

    # 2. Fallback на LLM если keyword не сработал
    try:
        resp = await _client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=256,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
        data = json.loads(raw)
        if "error" in data: return f"🤔 {data['error']}"
        cmd_type = data.pop("command_type", None)
        if cmd_type not in _MAP: return f"❌ Неизвестный тип: `{cmd_type}`"
        return _MAP[cmd_type](**data)
    except Exception:
        # LLM недоступен — говорим что не поняли
        return (
            "🤔 Не понял команду. Попробуй:\n"
            "• `Статус`\n"
            "• `Логи sglang`\n"
            "• `Перезапусти nginx`\n"
            "• `Подними deepseek на 30000 с 12 ГБ VRAM`\n"
            "• `Заблокируй 1.2.3.4`\n"
            "• `/scan`"
        )
