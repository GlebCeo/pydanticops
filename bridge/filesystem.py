import os, re
from pathlib import Path

class SandboxedFS:
    def __init__(self):
        raw = os.getenv("ALLOWED_DIRS", "/opt/compose-files")
        self.allowed = [Path(p.strip()).resolve() for p in raw.split(",")]
        self.compose_dir = Path(os.getenv("COMPOSE_FILES_DIR", "/opt/compose-files"))
        self.compose_dir.mkdir(parents=True, exist_ok=True)

    def _assert_allowed(self, path: Path):
        path = path.resolve()
        if not any(path.is_relative_to(a) for a in self.allowed):
            raise PermissionError(f"Путь за пределами sandbox: {path}")

    def read_file(self, path: str) -> str:
        p = Path(path)
        self._assert_allowed(p)
        return p.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str):
        p = Path(path)
        self._assert_allowed(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def write_compose(self, model_name: str, content: str) -> Path:
        safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", model_name)
        path = self.compose_dir / safe / "docker-compose.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path.parent
