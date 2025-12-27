from __future__ import annotations

import json
from typing import Optional
try:
    from crewai import Crew, Process
except Exception:  # pragma: no cover
    Agent = Crew = Process = Task = None  # type: ignore
from pydantic import ValidationError

from ..core.models import Plan
from ..tools.repo_tools import RepoContext, list_paths
from .agents import architect_agent
from .tasks import plan_task

async def kickoff_plan(ctx: RepoContext, goal: str) -> Plan:
    paths = await list_paths(ctx)
    repo_file_list = "\n".join(paths[:250])
    agent = architect_agent()
    task = plan_task(agent, goal, repo_file_list)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    result = crew.kickoff()
    text = str(result).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    data = json.loads(text)
    return Plan.model_validate(data)
