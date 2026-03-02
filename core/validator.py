import os, re, json, logging
from core.schemas import *

log = logging.getLogger(__name__)

def _keyword_parse(text: str):
    t = text.lower()
    # Deploy
    m = re.search(r'(подними|запусти|deploy|launch|run)\s+([\w\-\.]+)\s+.*?(\d+)\s*гб', t)
    if m:
        port_m = re.search(r'(\d{4,5})', t)
        return DeployCommand(model=m.group(2), port=int(port_m.group(1)) if port_m else 30000, vram_gb=float(m.group(3)))
    # Restart
    m = re.search(r'(перезапусти|рестарт|restart)\s+([\w\-]+)', t)
    if m:
        return RestartCommand(service=m.group(2))
    # Block IP
    m = re.search(r'(заблокируй|block)\s+([\d\.]+)', t)
    if m:
        return BlockIPCommand(ip=m.group(2))
    # Logs
    m = re.search(r'(логи|logs?)\s+([\w\-]+)(?:\s+(\d+))?', t)
    if m:
        return LogsCommand(service=m.group(2), lines=int(m.group(3)) if m.group(3) else 50)
    # Disk
    if any(x in t for x in ['диск', 'disk', 'место', 'df']):
        return DiskCommand()
    # SysInfo
    if any(x in t for x in ['cpu', 'ram', 'память', 'нагрузка', 'sysinfo', 'система', 'uptime']):
        return SystemInfoCommand()
    # Ports
    if any(x in t for x in ['порт', 'port', 'netstat', 'listen']):
        return PortsCommand()
    # Docker stats
    if any(x in t for x in ['docker stats', 'статистика', 'ресурс']):
        return DockerStatsCommand()
    # Ping
    m = re.search(r'(пингани|ping)\s+([\w\.\-]+)', t)
    if m:
        return PingCommand(host=m.group(2))
    # Kill process
    m = re.search(r'(убей|убить|kill)\s+([\w\-]+)', t)
    if m:
        return KillProcessCommand(process=m.group(2))
    # Read file
    m = re.search(r'(покажи файл|cat|читай)\s+(/[\w/\.\-]+)', t)
    if m:
        return ReadFileCommand(path=m.group(2))
    return None

async def _llm_parse(text: str):
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:30000/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "local"),
        )
        model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

        system = """You are a server command parser. Extract commands from user text and return ONLY valid JSON.

Available commands:
- deploy: {"action":"deploy","model":"name","port":30000,"vram_gb":12}
- restart: {"action":"restart","service":"name"}
- block_ip: {"action":"block_ip","ip":"1.2.3.4"}
- logs: {"action":"logs","service":"name","lines":50}
- status: {"action":"status"}
- scan: {"action":"scan"}
- disk: {"action":"disk"}
- sysinfo: {"action":"sysinfo"}
- ports: {"action":"ports"}
- docker_stats: {"action":"docker_stats"}
- ping: {"action":"ping","host":"google.com"}
- kill_process: {"action":"kill_process","process":"name"}
- read_file: {"action":"read_file","path":"/etc/nginx/nginx.conf"}

Return ONLY the JSON object, no explanation. If unclear, return {"action":"unknown"}."""

        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": text}],
            temperature=0, max_tokens=150
        )
        raw = resp.choices[0].message.content.strip()
        # Extract JSON
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return None
        data = json.loads(m.group())
        if data.get("action") == "unknown":
            return None

        action = data.get("action")
        if action == "deploy":
            return DeployCommand(**{k: v for k, v in data.items()})
        elif action == "restart":
            return RestartCommand(**{k: v for k, v in data.items()})
        elif action == "block_ip":
            return BlockIPCommand(**{k: v for k, v in data.items()})
        elif action == "logs":
            return LogsCommand(**{k: v for k, v in data.items()})
        elif action == "status":
            return StatusCommand()
        elif action == "scan":
            return ScanCommand()
        elif action == "disk":
            return DiskCommand()
        elif action == "sysinfo":
            return SystemInfoCommand()
        elif action == "ports":
            return PortsCommand()
        elif action == "docker_stats":
            return DockerStatsCommand()
        elif action == "ping":
            return PingCommand(**{k: v for k, v in data.items()})
        elif action == "kill_process":
            return KillProcessCommand(**{k: v for k, v in data.items()})
        elif action == "read_file":
            return ReadFileCommand(**{k: v for k, v in data.items()})
    except Exception as e:
        log.warning(f"LLM parse failed: {e}")
    return None

async def parse_command(text: str):
    cmd = _keyword_parse(text)
    if cmd:
        log.info(f"Keyword parse: {cmd}")
        return cmd
    log.info("Falling back to LLM")
    return await _llm_parse(text)
