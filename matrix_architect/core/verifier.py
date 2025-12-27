from __future__ import annotations

from typing import List, Optional, Dict, Any

from .models import RepoSpec, RepoKind
from ..tools.sandbox_tools import run_cmd


async def verify(repo: RepoSpec, commands: List[str], *, cwd: Optional[str] = None) -> Dict[str, Any]:
    if not commands:
        return {"ok": True, "results": []}

    if repo.kind != RepoKind.local:
        return {"ok": False, "error": "Verification requires a local workspace (clone the repo first).", "results": []}

    workdir = cwd or repo.path
    results = []
    ok = True
    for cmd in commands:
        r = run_cmd(cmd.split(), cwd=workdir)
        results.append({"cmd": cmd, "returncode": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
        if r.returncode != 0:
            ok = False
    return {"ok": ok, "results": results}
