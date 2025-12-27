from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich import print

from ..core.models import RepoSpec, RepoKind, Plan
from ..core.planner import plan as make_plan
from ..core.executor import execute as run_execute

app = typer.Typer(add_completion=False, help="Matrix Architect CLI")


def _repo_from_args(repo: str) -> RepoSpec:
    # Heuristic: if it looks like owner/name treat as github else local path
    if "/" in repo and not Path(repo).exists() and repo.count("/") == 1:
        owner, name = repo.split("/", 1)
        return RepoSpec(kind=RepoKind.github, owner=owner, repo=name)
    return RepoSpec(kind=RepoKind.local, path=str(Path(repo).expanduser().resolve()))


@app.command()
def plan(repo: str, goal: str, out: Path = Path("plan.json"), matrix_ai_url: Optional[str] = None):
    """Generate a plan for a repo (GitHub 'owner/name' or local path)."""
    rs = _repo_from_args(repo)
    p = asyncio.run(make_plan(rs, goal, token=None, matrix_ai_url=matrix_ai_url))
    out.write_text(p.model_dump_json(indent=2), encoding="utf-8")
    print(f"[green]Wrote plan to {out}[/green]")


@app.command()
def execute(repo: str, plan_file: Path = Path("plan.json"), matrix_ai_url: Optional[str] = None):
    """Execute a plan against a repo (local path recommended)."""
    rs = _repo_from_args(repo)
    p = Plan.model_validate_json(plan_file.read_text(encoding="utf-8"))
    asyncio.run(run_execute(rs, p, token=None, matrix_ai_url=matrix_ai_url))
    print("[green]Execution complete[/green]")
