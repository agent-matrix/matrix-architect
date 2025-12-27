from __future__ import annotations

from typing import Optional, List

from ..core.models import RepoSpec, RepoKind, FileOp, FileOpType
from ..integrations import github as gh
from ..integrations.git_local import LocalRepo


async def apply_file_ops(repo: RepoSpec, ops: List[FileOp], token: Optional[str] = None, *, ref: Optional[str] = None) -> None:
    """Apply file operations to GitHub or local repos."""
    if repo.kind == RepoKind.github:
        owner, name = repo.owner, repo.repo
        if not (owner and name):
            raise ValueError("GitHub RepoSpec requires owner+repo")
        for op in ops:
            if op.op in (FileOpType.create, FileOpType.update):
                if op.content is None:
                    raise ValueError(f"Missing content for {op.op} {op.path}")
                await gh.put_file(owner, name, op.path, op.content, token, message=op.message or f"{op.op}: {op.path}", branch=ref or repo.ref)
            elif op.op == FileOpType.delete:
                await gh.delete_file(owner, name, op.path, token, message=op.message or f"delete: {op.path}", branch=ref or repo.ref)
        return

    if repo.kind == RepoKind.local:
        if not repo.path:
            raise ValueError("Local RepoSpec requires path")
        lr = LocalRepo(repo.path)
        for op in ops:
            if op.op in (FileOpType.create, FileOpType.update):
                if op.content is None:
                    raise ValueError(f"Missing content for {op.op} {op.path}")
                lr.write_text(op.path, op.content)
            elif op.op == FileOpType.delete:
                lr.delete(op.path)
        return

    raise ValueError(f"Unsupported repo kind: {repo.kind}")
