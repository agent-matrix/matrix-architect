from __future__ import annotations

import logging
from typing import Optional

from .models import Plan, RepoSpec, FileOpType, FileOp
from ..tools.patch_tools import apply_file_ops
from ..tools.repo_tools import RepoContext, read_text
from ..integrations.matrix_ai_client import MatrixAIClient
from .llm_provider import build_llm

logger = logging.getLogger(__name__)


async def _fill_missing_content(repo: RepoSpec, goal: str, op: FileOp, *, token: Optional[str], matrix_ai_url: Optional[str]) -> FileOp:
    if op.content is not None or op.op == FileOpType.delete:
        return op

    # Try matrix-ai first
    if matrix_ai_url:
        client = MatrixAIClient(matrix_ai_url, token=token)
        data = await client.code({"repo": repo.model_dump(), "goal": goal, "path": op.path, "op": op.op})
        op.content = data.get("content", "")
        return op

    # Local fallback: create empty file or preserve existing content
    try:
        ctx = RepoContext(repo=repo, token=token)
        existing = await read_text(ctx, op.path)
        op.content = existing
    except Exception:
        op.content = ""
    return op


async def execute(repo: RepoSpec, plan: Plan, *, token: Optional[str] = None, matrix_ai_url: Optional[str] = None) -> None:
    """Apply all file operations in the plan."""
    for step in plan.steps:
        filled_ops = []
        for op in step.ops:
            filled_ops.append(await _fill_missing_content(repo, plan.goal, op, token=token, matrix_ai_url=matrix_ai_url))
        await apply_file_ops(repo, filled_ops, token=token, ref=repo.ref)
