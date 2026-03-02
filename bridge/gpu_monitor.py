import subprocess
from dataclasses import dataclass

@dataclass
class GPUInfo:
    index: int
    name: str
    vram_total_gb: float
    vram_used_gb: float
    vram_free_gb: float
    temp_c: int
    util_pct: int

def get_gpu_info() -> list[GPUInfo]:
    try:
        out = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu",
            "--format=csv,noheader,nounits"
        ], text=True, timeout=10)
        gpus = []
        for line in out.strip().splitlines():
            idx, name, tot, used, free, temp, util = [x.strip() for x in line.split(",")]
            gpus.append(GPUInfo(
                index=int(idx), name=name,
                vram_total_gb=round(int(tot)/1024, 1),
                vram_used_gb=round(int(used)/1024, 1),
                vram_free_gb=round(int(free)/1024, 1),
                temp_c=int(temp), util_pct=int(util)
            ))
        return gpus
    except Exception:
        return []

def format_gpu_status(gpus: list[GPUInfo]) -> str:
    if not gpus:
        return "⚠️ nvidia-smi недоступен"
    lines = []
    for g in gpus:
        bar = "█" * (g.util_pct // 10) + "░" * (10 - g.util_pct // 10)
        temp_icon = "🔥" if g.temp_c > 80 else "🌡️"
        lines.append(
            f"*GPU {g.index}* — {g.name}\n"
            f"  VRAM: `{g.vram_used_gb}/{g.vram_total_gb} ГБ` (свободно `{g.vram_free_gb} ГБ`)\n"
            f"  {temp_icon} Темп: `{g.temp_c}°C` | Загрузка: `{bar}` {g.util_pct}%"
        )
    return "\n\n".join(lines)

def pick_quantization(vram_free_gb: float) -> tuple[str, str]:
    """Возвращает (quant_type, description) под доступный VRAM."""
    if vram_free_gb >= 40:  return ("fp16",  "FP16 — максимальное качество")
    if vram_free_gb >= 20:  return ("awq",   "AWQ 4-bit — баланс качества и памяти")
    if vram_free_gb >= 10:  return ("gptq",  "GPTQ 4-bit — экономия памяти")
    if vram_free_gb >= 6:   return ("gguf",  "GGUF Q4_K_M — минимальные требования")
    return ("gguf_q2", "GGUF Q2_K — критически мало VRAM")
