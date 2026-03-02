import subprocess
from pathlib import Path
from jinja2 import Template
from core.schemas import DeployCommand

COMPOSE_TEMPLATE = """version: "3.9"
services:
  {{ service_name }}:
    image: {{ image }}
    container_name: {{ service_name }}
    restart: unless-stopped
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES={{ gpu_devices | join(",") }}
    command: >
      python -m sglang.launch_server
      --model-path {{ model_name }}
      --port {{ port }}
      --mem-fraction-static {{ mem_fraction }}
      {% if quant and quant != "fp16" %}--quantization {{ quant }}{% endif %}
      {% for k, v in extra_args.items() %}--{{ k }} {{ v }} {% endfor %}
    ports:
      - "{{ port }}:{{ port }}"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: {{ gpu_devices | length }}
              capabilities: [gpu]"""

BACKEND_IMAGES = {
    "sglang": "lmsysorg/sglang:latest",
    "vllm": "vllm/vllm-openai:latest",
    "ollama": "ollama/ollama:latest",
}

def _run(cmd, timeout=30, shell=False) -> str:
    try:
        if shell:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        else:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired: return "❌ Таймаут"
    except FileNotFoundError as e: return f"❌ Не найдено: {e}"

class DockerManager:
    def generate_compose(self, cmd: DeployCommand, quant: str = "") -> str:
        service_name = cmd.model_name.split("/")[-1].replace(".", "-").replace("_","-").lower()
        # Убираем кириллицу из имени
        service_name = "".join(c for c in service_name if c.isascii() and (c.isalnum() or c in "-"))
        if not service_name: service_name = "model"
        mem_fraction = round(min(cmd.vram_gb / 24.0, 0.90), 2)
        image = BACKEND_IMAGES.get(cmd.backend, BACKEND_IMAGES["sglang"])
        return Template(COMPOSE_TEMPLATE).render(
            service_name=service_name, model_name=cmd.model_name,
            port=cmd.port, backend=cmd.backend, image=image,
            gpu_devices=cmd.gpu_devices, mem_fraction=mem_fraction,
            quant=quant, extra_args=cmd.extra_args,
        )

    def compose_up(self, project_dir: Path) -> str:
        # Поддержка старого и нового docker compose
        return _run(
            f"cd '{project_dir}' && (docker compose up -d 2>/dev/null || docker-compose up -d)",
            shell=True, timeout=120
        )

    def compose_down(self, project_dir: Path) -> str:
        return _run(
            f"cd '{project_dir}' && (docker compose down 2>/dev/null || docker-compose down)",
            shell=True
        )

    def restart_service(self, service: str) -> str:
        return _run(["docker", "restart", service])

    def get_ps(self) -> str:
        return _run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])

    def get_logs(self, service: str, tail: int = 50) -> str:
        return _run(["docker", "logs", "--tail", str(tail), service], timeout=15)

    def block_ip(self, ip: str) -> str:
        return _run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
