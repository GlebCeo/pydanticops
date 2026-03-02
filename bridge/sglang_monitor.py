import os, asyncio, httpx
from datetime import datetime
from bridge.gpu_monitor import get_gpu_info

class SGLangMonitor:
    def __init__(self):
        self.host = os.getenv("SGLANG_HOST", "localhost")
        self.port = int(os.getenv("SGLANG_PORT", "30000"))
        self.interval = int(os.getenv("SGLANG_HEALTH_INTERVAL", "30"))
        self.max_failures = int(os.getenv("SGLANG_MAX_FAILURES", "3"))
        self.gpu_temp_limit = int(os.getenv("GPU_TEMP_LIMIT", "85"))
        self._failures = 0
        self._temp_alerted = False

    @property
    def url(self): return f"http://{self.host}:{self.port}/health"

    async def check_health(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(self.url)
                if r.status_code == 200:
                    self._failures = 0
                    return f"✅ Онлайн (порт {self.port})"
                return f"⚠️ HTTP {r.status_code}"
        except Exception as e:
            return f"❌ Недоступен: {e}"

    async def watchdog(self, notify_fn):
        while True:
            # ── SGLang health ──────────────────────────────────
            status = await self.check_health()
            if "❌" in status or "⚠️" in status:
                self._failures += 1
                if self._failures >= self.max_failures:
                    ts = datetime.now().strftime("%H:%M:%S")
                    await notify_fn(f"🚨 [{ts}] SGLang упал {self._failures}x — перезапускаю...")
                    from bridge.docker_manager import DockerManager
                    out = DockerManager().restart_service("sglang")
                    self._failures = 0
                    await notify_fn(f"🔄 SGLang перезапущен:\n```\n{out}\n```")
            else:
                self._failures = 0

            # ── GPU температура ────────────────────────────────
            gpus = get_gpu_info()
            for gpu in gpus:
                if gpu.temp_c >= self.gpu_temp_limit and not self._temp_alerted:
                    self._temp_alerted = True
                    await notify_fn(
                        f"🔥 *GPU {gpu.index} перегрев!* `{gpu.temp_c}°C` / лимит `{self.gpu_temp_limit}°C`\n"
                        f"VRAM: `{gpu.vram_used_gb}/{gpu.vram_total_gb} ГБ`\n"
                        f"Рекомендую снизить нагрузку или увеличить охлаждение."
                    )
                elif gpu.temp_c < self.gpu_temp_limit - 5:
                    self._temp_alerted = False

            await asyncio.sleep(self.interval)
