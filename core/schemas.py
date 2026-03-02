from __future__ import annotations
import re
from typing import Literal, Union
from pydantic import BaseModel, Field, field_validator

class DeployCommand(BaseModel):
    model_name: str
    port: int = Field(ge=1024, le=65535)
    vram_gb: float = Field(gt=0, le=80)
    gpu_devices: list[int] = Field(default=[0])
    backend: Literal["sglang", "vllm", "ollama"] = "sglang"
    extra_args: dict[str, str] = Field(default_factory=dict)
    dry_run: bool = True

    @field_validator("model_name")
    @classmethod
    def not_empty(cls, v):
        if not v.strip(): raise ValueError("model_name пустой")
        return v.strip()

class RestartCommand(BaseModel):
    service: str
    dry_run: bool = True

    @field_validator("service")
    @classmethod
    def safe_name(cls, v):
        if not re.fullmatch(r"[a-zA-Z0-9_\-]+", v):
            raise ValueError(f"Небезопасное имя: {v!r}")
        return v

class BlockIPCommand(BaseModel):
    ip: str
    reason: str = "Manual block"
    dry_run: bool = True

    @field_validator("ip")
    @classmethod
    def valid_ip(cls, v):
        v = v.strip()
        ipv4 = re.compile(r"^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$")
        ipv6 = re.compile(r"^[0-9a-fA-F:]{2,39}$")
        if not (ipv4.match(v) or ipv6.match(v)):
            raise ValueError(f"Невалидный IP: {v!r}")
        return v

class LogsCommand(BaseModel):
    service: str
    tail: int = Field(default=50, ge=1, le=500)

    @field_validator("service")
    @classmethod
    def safe_name(cls, v):
        if not re.fullmatch(r"[a-zA-Z0-9_\-]+", v):
            raise ValueError(f"Небезопасное имя: {v!r}")
        return v

class StatusCommand(BaseModel):
    include_sglang: bool = True
    include_docker: bool = True

class ScanCommand(BaseModel):
    log_path: str = ""
    threshold_rpm: int = Field(default=100, ge=10)

AnyCommand = Union[DeployCommand, RestartCommand, BlockIPCommand, LogsCommand, StatusCommand, ScanCommand]
