from bridge.docker_manager import DockerManager
from core.schemas import DeployCommand

dm = DockerManager()

def test_generate_compose_contains_port():
    cmd = DeployCommand(model_name="deepseek-ai/DeepSeek-R1", port=30000, vram_gb=12)
    yaml = dm.generate_compose(cmd)
    assert "30000" in yaml

def test_generate_compose_contains_model():
    cmd = DeployCommand(model_name="myorg/mymodel", port=8080, vram_gb=8)
    yaml = dm.generate_compose(cmd)
    assert "myorg/mymodel" in yaml

def test_generate_compose_mem_fraction():
    cmd = DeployCommand(model_name="x", port=8080, vram_gb=24)
    yaml = dm.generate_compose(cmd)
    assert "1.0" in yaml or "0.95" in yaml
