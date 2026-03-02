import pytest
from pydantic import ValidationError
from core.schemas import DeployCommand, BlockIPCommand, RestartCommand, LogsCommand

def test_deploy_valid():
    cmd = DeployCommand(model_name="deepseek", port=30000, vram_gb=12)
    assert cmd.port == 30000

def test_deploy_bad_port():
    with pytest.raises(ValidationError): DeployCommand(model_name="x", port=80, vram_gb=12)

def test_deploy_bad_vram():
    with pytest.raises(ValidationError): DeployCommand(model_name="x", port=8080, vram_gb=999)

def test_deploy_empty_name():
    with pytest.raises(ValidationError): DeployCommand(model_name="  ", port=8080, vram_gb=12)

def test_block_ip_valid():
    cmd = BlockIPCommand(ip="1.2.3.4")
    assert cmd.ip == "1.2.3.4"

def test_block_ip_invalid():
    with pytest.raises(ValidationError): BlockIPCommand(ip="not-an-ip")

def test_restart_unsafe_name():
    with pytest.raises(ValidationError): RestartCommand(service="rm -rf /")

def test_logs_tail_bounds():
    with pytest.raises(ValidationError): LogsCommand(service="sglang", tail=9999)
