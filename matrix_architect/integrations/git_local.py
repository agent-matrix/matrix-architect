from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Optional, Iterable

class LocalRepo:
    """Very small local-workspace adapter.

    This is intentionally simple:
    - Tree listing walks the filesystem
    - Read/write/delete are direct file ops
    - Optional git usage is handled in sandbox_tools (via `git` commands)
    """

    def __init__(self, path: str):
        self.root = Path(path).expanduser().resolve()
        if not self.root.exists():
            raise FileNotFoundError(f"Local repo path not found: {self.root}")

    def list_files(self) -> List[str]:
        files: List[str] = []
        for p in self.root.rglob("*"):
            if p.is_file() and ".git" not in p.parts:
                files.append(str(p.relative_to(self.root)))
        return sorted(files)

    def read_text(self, rel_path: str) -> str:
        p = (self.root / rel_path).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError("Path escapes repo root")
        return p.read_text(encoding="utf-8", errors="ignore")

    def write_text(self, rel_path: str, content: str) -> None:
        p = (self.root / rel_path).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError("Path escapes repo root")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def delete(self, rel_path: str) -> None:
        p = (self.root / rel_path).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError("Path escapes repo root")
        if p.exists():
            p.unlink()
