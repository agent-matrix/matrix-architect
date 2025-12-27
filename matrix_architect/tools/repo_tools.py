from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from ..core.models import RepoSpec, RepoKind
from ..integrations import github as gh
from ..integrations.git_local import LocalRepo


@dataclass
class RepoContext:
    repo: RepoSpec
    token: Optional[str] = None


async def list_paths(ctx: RepoContext) -> List[str]:
    if ctx.repo.kind == RepoKind.github:
        if not (ctx.repo.owner and ctx.repo.repo):
            raise ValueError("GitHub RepoSpec requires owner+repo")
        tree = await gh.get_repo_tree(ctx.repo.owner, ctx.repo.repo, ctx.token, ref=ctx.repo.ref)
        return sorted([it["path"] for it in tree])
    if ctx.repo.kind == RepoKind.local:
        if not ctx.repo.path:
            raise ValueError("Local RepoSpec requires path")
        return LocalRepo(ctx.repo.path).list_files()
    raise ValueError(f"Unsupported repo kind: {ctx.repo.kind}")


async def read_text(ctx: RepoContext, path: str) -> str:
    if ctx.repo.kind == RepoKind.github:
        return await gh.get_file(ctx.repo.owner, ctx.repo.repo, path, ctx.token, ref=ctx.repo.ref)
    return LocalRepo(ctx.repo.path).read_text(path)


async def search(ctx: RepoContext, pattern: str, max_matches: int = 50) -> List[Dict[str, Any]]:
    """Naive grep across text files."""
    rx = re.compile(pattern)
    matches: List[Dict[str, Any]] = []
    for p in await list_paths(ctx):
        if len(matches) >= max_matches:
            break
        try:
            txt = await read_text(ctx, p)
        except Exception:
            continue
        for i, line in enumerate(txt.splitlines(), start=1):
            if rx.search(line):
                matches.append({"path": p, "line": i, "text": line[:500]})
                if len(matches) >= max_matches:
                    break
    return matches
