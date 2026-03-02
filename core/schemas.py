from pydantic import BaseModel, Field
from typing import Literal, Optional

class DeployCommand(BaseModel):
    action: Literal["deploy"] = "deploy"
    model: str
    port: int
    vram_gb: float

class RestartCommand(BaseModel):
    action: Literal["restart"] = "restart"
    service: str

class BlockIPCommand(BaseModel):
    action: Literal["block_ip"] = "block_ip"
    ip: str

class LogsCommand(BaseModel):
    action: Literal["logs"] = "logs"
    service: str
    lines: int = 50

class StatusCommand(BaseModel):
    action: Literal["status"] = "status"

class ScanCommand(BaseModel):
    action: Literal["scan"] = "scan"

class DiskCommand(BaseModel):
    action: Literal["disk"] = "disk"

class SystemInfoCommand(BaseModel):
    action: Literal["sysinfo"] = "sysinfo"

class PortsCommand(BaseModel):
    action: Literal["ports"] = "ports"

class DockerStatsCommand(BaseModel):
    action: Literal["docker_stats"] = "docker_stats"

class PingCommand(BaseModel):
    action: Literal["ping"] = "ping"
    host: str

class KillProcessCommand(BaseModel):
    action: Literal["kill_process"] = "kill_process"
    process: str

class ReadFileCommand(BaseModel):
    action: Literal["read_file"] = "read_file"
    path: str

SAFE_DIRS = ["/etc/nginx", "/var/log", "/opt", "/tmp"]

Command = (
    DeployCommand | RestartCommand | BlockIPCommand | LogsCommand |
    StatusCommand | ScanCommand | DiskCommand | SystemInfoCommand |
    PortsCommand | DockerStatsCommand | PingCommand |
    KillProcessCommand | ReadFileCommand
)
