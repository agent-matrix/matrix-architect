from __future__ import annotations

from pathlib import Path
from typing import Optional

DEFAULT_DIR = Path("data/artifacts")


class ArtifactStore:
    def __init__(self, root: Path = DEFAULT_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_bytes(self, job_id: str, name: str, data: bytes) -> Path:
        p = self.root / job_id
        p.mkdir(parents=True, exist_ok=True)
        out = p / name
        out.write_bytes(data)
        return out

    def write_text(self, job_id: str, name: str, text: str) -> Path:
        return self.write_bytes(job_id, name, text.encode("utf-8"))

    def path(self, job_id: str, name: str) -> Optional[Path]:
        p = self.root / job_id / name
        return p if p.exists() else None
