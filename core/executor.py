from __future__ import annotations
from core.schemas import (AnyCommand, DeployCommand, RestartCommand,
    BlockIPCommand, LogsCommand, StatusCommand, ScanCommand)
from bridge.docker_manager import DockerManager
from bridge.filesystem import SandboxedFS
from bridge.sglang_monitor import SGLangMonitor
from bridge.gpu_monitor import get_gpu_info, format_gpu_status, pick_quantization
from osint.log_scanner import LogScanner
from protocol.cat import cat_block

docker = DockerManager()
fs = SandboxedFS()
sglang = SGLangMonitor()
scanner = LogScanner()

async def preview(cmd: AnyCommand) -> str:
    if isinstance(cmd, DeployCommand):
        # Авто-квантизация под доступный VRAM
        gpus = get_gpu_info()
        quant = ""
        quant_desc = "FP16"
        if gpus:
            free = gpus[0].vram_free_gb
            quant, quant_desc = pick_quantization(free)
            if quant == "fp16": quant = ""
        yaml = docker.generate_compose(cmd, quant=quant)
        gpu_info = f"\n🎮 GPU: {gpus[0].name} | Свободно: `{gpus[0].vram_free_gb} ГБ`\n🔢 Квантизация: `{quant_desc}`" if gpus else ""
        return (
            f"📦 Предпросмотр деплоя `{cmd.model_name}`\n"
            f"🌐 Порт: `{cmd.port}` | VRAM лимит: `{cmd.vram_gb} ГБ`{gpu_info}\n\n"
            + cat_block("docker-compose.yml", "yaml", yaml)
            + "\n\n⚠️ Нажми **✅ Выполнить** или **❌ Отмена**"
        )
    if isinstance(cmd, RestartCommand):
        return f"🔄 Перезапуск `{cmd.service}`\n⚠️ **✅ Выполнить** или **❌ Отмена**"
    if isinstance(cmd, BlockIPCommand):
        return (f"🚫 Блокировка `{cmd.ip}`\nПричина: _{cmd.reason}_\n"
                "⚠️ **✅ Заблокировать** или **❌ Отмена**")
    return await execute(cmd)

async def execute(cmd: AnyCommand) -> str:
    if isinstance(cmd, DeployCommand):
        gpus = get_gpu_info()
        quant = ""
        if gpus:
            quant, _ = pick_quantization(gpus[0].vram_free_gb)
            if quant == "fp16": quant = ""
        yaml = docker.generate_compose(cmd, quant=quant)
        path = fs.write_compose(cmd.model_name, yaml)
        out = docker.compose_up(path)
        return f"🚀 `{cmd.model_name}` запущен!\n\n" + cat_block("docker-compose.yml","yaml",yaml) + f"\n\n```\n{out}\n```"
    if isinstance(cmd, RestartCommand):
        out = docker.restart_service(cmd.service)
        return f"🔄 `{cmd.service}` перезапущен:\n```\n{out}\n```"
    if isinstance(cmd, BlockIPCommand):
        out = docker.block_ip(cmd.ip)
        return f"🚫 `{cmd.ip}` заблокирован:\n```\n{out}\n```"
    if isinstance(cmd, LogsCommand):
        logs = docker.get_logs(cmd.service, cmd.tail)
        return f"📋 Логи `{cmd.service}` (последние {cmd.tail}):\n" + cat_block(f"{cmd.service}.log","log",logs)
    if isinstance(cmd, StatusCommand):
        gpus = get_gpu_info()
        parts = ["📊 *Статус системы*\n"]
        if cmd.include_docker:
            parts.append("*Docker:*\n```\n" + docker.get_ps() + "\n```")
        if gpus:
            parts.append("\n*GPU:*\n" + format_gpu_status(gpus))
        if cmd.include_sglang:
            parts.append(f"\n*SGLang:* {await sglang.check_health()}")
        return "\n".join(parts)
    if isinstance(cmd, ScanCommand):
        entries = scanner.scan(cmd.log_path or None, cmd.threshold_rpm)
        if not entries: return "✅ Подозрительных IP не найдено."
        rows = "\n".join(f"| `{e.ip}` | {e.count} | {e.pattern} |" for e in entries)
        return f"🔍 *OSINT-сканирование*\n\n| IP | Req | Паттерн |\n|---|---|---|\n{rows}"
    return "❓ Неизвестная команда"
