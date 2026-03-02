import asyncio, os
from core.schemas import *

COMPOSE_DIR = os.getenv("COMPOSE_FILES_DIR", "/opt/compose-files")

async def _run(cmd: str, timeout: int = 15) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return out.decode(errors="replace").strip()
    except asyncio.TimeoutError:
        return "⏱ Timeout"
    except Exception as e:
        return f"❌ {e}"

async def preview(cmd) -> str:
    if isinstance(cmd, DeployCommand):
        from bridge.gpu_monitor import choose_quantization
        quant = choose_quantization(cmd.vram_gb)
        mem = round(cmd.vram_gb / 1.2, 2)
        return (
            f"🚀 *Деплой {cmd.model}*\n"
            f"🔌 Порт: `{cmd.port}` | VRAM: `{cmd.vram_gb} ГБ`\n"
            f"⚙️ Квантизация: `{quant}`\n\n"
            f"📦 CAT: [docker-compose.yml](cci:7://file:///c:/Unionoffice.kz/invisible-sysadmin/docker-compose.yml:0:0-0:0)\n```yaml\n"
            f"version: \"3.9\"\nservices:\n  {cmd.model}:\n"
            f"    image: lmsysorg/sglang:latest\n"
            f"    container_name: {cmd.model}\n"
            f"    restart: unless-stopped\n"
            f"    runtime: nvidia\n"
            f"    environment:\n      - NVIDIA_VISIBLE_DEVICES=0\n"
            f"    command: >\n"
            f"      python -m sglang.launch_server\n"
            f"      --model-path {cmd.model}\n"
            f"      --port {cmd.port}\n"
            f"      --mem-fraction-static {mem}\n"
            f"    ports:\n      - \"{cmd.port}:{cmd.port}\"\n"
            f"    deploy:\n      resources:\n        reservations:\n"
            f"          devices:\n            - driver: nvidia\n"
            f"              count: 1\n              capabilities: [gpu]\n```"
        )
    elif isinstance(cmd, RestartCommand):
        return f"🔁 *Рестарт* `{cmd.service}`\n\nВыполнит:\n`docker restart {cmd.service}`"
    elif isinstance(cmd, BlockIPCommand):
        return f"🚫 *Блокировка* `{cmd.ip}`\n\nВыполнит:\n`iptables -A INPUT -s {cmd.ip} -j DROP`"
    elif isinstance(cmd, KillProcessCommand):
        return f"💀 *Убить процесс* `{cmd.process}`\n\nВыполнит:\n`pkill -f {cmd.process}`"
    elif isinstance(cmd, ReadFileCommand):
        safe = any(cmd.path.startswith(d) for d in SAFE_DIRS)
        if not safe:
            return f"❌ Путь `{cmd.path}` не разрешён.\nДопустимые: `{', '.join(SAFE_DIRS)}`"
        return f"📄 *Файл* `{cmd.path}`\n\nВыполнит:\n`cat {cmd.path}`"
    return "✅ Готов к выполнению"

async def execute(cmd) -> str:
    if isinstance(cmd, StatusCommand):
        docker = await _run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
        try:
            from bridge.gpu_monitor import get_gpu_info
            gpu = get_gpu_info()
            gpu_text = "\n".join(f"  GPU {g['index']}: {g['name']} | {g['vram_used_gb']:.1f}/{g['vram_total_gb']:.1f}GB | {g['temperature']}°C | {g['utilization']}%" for g in gpu) if gpu else "  nvidia-smi недоступен"
        except:
            gpu_text = "  nvidia-smi недоступен"
        return f"📊 *Статус системы*\n\n*Docker:*\n```\n{docker}\n```\n\n*GPU:*\n```\n{gpu_text}\n```"

    elif isinstance(cmd, ScanCommand):
        from osint.log_scanner import scan_logs
        return await asyncio.get_event_loop().run_in_executor(None, scan_logs)

    elif isinstance(cmd, DeployCommand):
        from bridge.docker_manager import DockerManager
        dm = DockerManager()
        return await dm.generate_and_deploy(cmd.model, cmd.port, cmd.vram_gb)

    elif isinstance(cmd, RestartCommand):
        out = await _run(f"docker restart {cmd.service}")
        return f"🔁 *{cmd.service}* перезапущен:\n```\n{out}\n```"

    elif isinstance(cmd, BlockIPCommand):
        out = await _run(f"iptables -A INPUT -s {cmd.ip} -j DROP")
        return f"🚫 `{cmd.ip}` заблокирован\n```\n{out or 'OK'}\n```"

    elif isinstance(cmd, LogsCommand):
        out = await _run(f"docker logs --tail {cmd.lines} {cmd.service} 2>&1")
        if "No such container" in out:
            out = await _run(f"journalctl -u {cmd.service} -n {cmd.lines} --no-pager")
        return f"📋 *Логи {cmd.service}* (последние {cmd.lines}):\n```\n{out[-3000:]}\n```"

    elif isinstance(cmd, DiskCommand):
        out = await _run("df -h --output=source,size,used,avail,pcent,target | grep -v tmpfs | grep -v udev")
        return f"💾 *Диск:*\n```\n{out}\n```"

    elif isinstance(cmd, SystemInfoCommand):
        cpu = await _run("top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4\"%\"}'")
        ram = await _run("free -h | awk 'NR==2{printf \"%s / %s (%.0f%%)\", $3,$2,$3/$2*100}'")
        uptime = await _run("uptime -p")
        load = await _run("cat /proc/loadavg | awk '{print $1, $2, $3}'")
        return f"🖥 *Система:*\n\n• CPU: `{cpu}`\n• RAM: `{ram}`\n• Uptime: `{uptime}`\n• Load: `{load}`"

    elif isinstance(cmd, PortsCommand):
        out = await _run("ss -tlnp | grep LISTEN")
        return f"🌐 *Открытые порты:*\n```\n{out}\n```"

    elif isinstance(cmd, DockerStatsCommand):
        out = await _run("docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}'")
        return f"🐳 *Docker Stats:*\n```\n{out}\n```"

    elif isinstance(cmd, PingCommand):
        out = await _run(f"ping -c 4 {cmd.host}")
        return f"🏓 *Ping {cmd.host}:*\n```\n{out}\n```"

    elif isinstance(cmd, KillProcessCommand):
        out = await _run(f"pkill -f {cmd.process} && echo 'killed' || echo 'not found'")
        return f"💀 `{cmd.process}`: `{out}`"

    elif isinstance(cmd, ReadFileCommand):
        safe = any(cmd.path.startswith(d) for d in SAFE_DIRS)
        if not safe:
            return f"❌ Путь не разрешён. Допустимые: `{', '.join(SAFE_DIRS)}`"
        out = await _run(f"cat {cmd.path}")
        return f"📄 `{cmd.path}`:\n```\n{out[:3000]}\n```"

    return "❓ Неизвестная команда"
