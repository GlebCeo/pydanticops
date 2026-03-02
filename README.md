<div align="center">

# ⚡ PydanticOps

**AI Infrastructure Control — from your phone**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram)](https://telegram.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square)](https://docs.pydantic.dev)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>

---

## 🤔 The Problem

In 2026, the biggest bottleneck for AI engineers isn't compute — it's **management overhead**.  
You want to run models and write code, not SSH into servers at 3AM to fix crashed containers.

## ✅ The Solution

**PydanticOps** turns your Linux GPU server into an obedient tool you control from Telegram — anywhere, no SSH required.



---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🚀 | **Smart Deploy** | Natural language → docker-compose with auto-quantization (FP16/AWQ/GPTQ/GGUF) |
| 📊 | **GPU Monitor** | Temperature, VRAM, utilization via `nvidia-smi` |
| 🩺 | **Auto-healing** | SGLang watchdog — auto-restarts on failure, sends report |
| 🔍 | **OSINT Scanner** | Parses nginx logs, detects scanners, shows attacking IPs |
| 🚫 | **IP Blocker** | Block any IP via iptables with one tap |
| 📋 | **Log Viewer** | `Покажи логи nginx` → last N lines in Telegram |
| 🔒 | **Safety First** | Destructive actions require explicit ✅ confirmation |
| 🌐 | **Bilingual** | Full RU/EN with auto-detection |
| ⚡ | **No LLM needed** | Keyword parser works instantly without any AI backend |

---

## ⚡ Quick Start

```bash
git clone https://github.com/GlebCeo/pydanticops
cd pydanticops && bash install.sh

Telegram
   │
   ▼
FastAPI + uvicorn
   │
   ▼
Keyword Parser + LLM fallback (OpenAI-compatible → local SGLang/vLLM = FREE)
   │
   ▼
Pydantic v2  ← type-safe validation, zero hallucinations
   │
   ▼
OpenClaw Bridge
├── DockerManager   — compose, logs, restart
├── GPUMonitor      — nvidia-smi
├── SGLangMonitor   — watchdog + auto-heal
└── LogScanner      — OSINT nginx analysis

TELEGRAM_TOKEN=...
ADMIN_CHAT_ID=...              # your Telegram user ID

OPENAI_BASE_URL=http://localhost:30000/v1  # local SGLang (free!)
OPENAI_API_KEY=local

SGLANG_PORT=30000
GPU_TEMP_LIMIT=85              # alert threshold °C

🛠 Tech Stack
Python 3.12 · Pydantic v2 · FastAPI · python-telegram-bot · Jinja2 · nvidia-smi · iptables · Docker

📬 Contact
Built by @GlebCeo
Try the HQ bot: @PydanticOpsBot

MIT License · Open Source · Made for AI Engineers
