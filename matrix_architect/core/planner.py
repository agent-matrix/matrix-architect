from __future__ import annotations

import json
import logging
from textwrap import dedent
from typing import Optional

from pydantic import ValidationError
from .models import Plan, RepoSpec
from ..tools.repo_tools import RepoContext, list_paths
from ..integrations.matrix_ai_client import MatrixAIClient
from .llm_provider import build_llm

logger = logging.getLogger(__name__)


async def plan(repo: RepoSpec, goal: str, *, token: Optional[str] = None, matrix_ai_url: Optional[str] = None) -> Plan:
    """Create a Plan for the requested goal.

    Strategy:
    - If `matrix_ai_url` is provided: delegate to matrix-ai.
    - Otherwise: run a lightweight local CrewAI planner that emits a Plan JSON.
    """
    if matrix_ai_url:
        client = MatrixAIClient(matrix_ai_url, token=token)
        data = await client.plan({"repo": repo.model_dump(), "goal": goal})
        return Plan.model_validate(data)

    # Local planning (CrewAI)
    try:
        from crewai import Agent, Crew, Process, Task
    except Exception as e:
        return Plan(goal=goal, summary="CrewAI not installed/available.", steps=[], metadata={"error": str(e)})

    ctx = RepoContext(repo=repo, token=token)
    paths = await list_paths(ctx)
    # Keep context small
    sample = paths[:250]
    context = "\n".join(sample)

    llm = build_llm()

    planner_agent = Agent(
        role="Software Architect",
        goal="Produce a safe, incremental plan expressed as JSON",
        backstory="You plan changes carefully, minimizing risk and making steps verifiable.",
        llm=llm,
    )

    prompt = dedent(f"""
    You are planning changes to a repository.

    Goal:
    {goal}

    Repository file list (sample):
    {context}

    Produce a JSON object matching this schema:

    {{
      "goal": string,
      "summary": string,
      "steps": [
        {{
          "id": string,
          "title": string,
          "rationale": string,
          "ops": [
            {{
              "op": "create"|"update"|"delete",
              "path": string,
              "content": string|null,
              "message": string|null
            }}
          ],
          "verify": [string]
        }}
      ],
      "metadata": {{}}
    }}

    Rules:
    - Prefer small steps (<=5 file ops per step).
    - Use verify commands that are safe (no destructive commands).
    - If you don't know file contents, propose exploration-only steps with no ops.
    - Return ONLY valid JSON.
    """)

    task = Task(description=prompt, expected_output="Valid JSON Plan", agent=planner_agent)
    crew = Crew(agents=[planner_agent], tasks=[task], process=Process.sequential)

    result = crew.kickoff()
    text = str(result).strip()
    # Attempt to extract JSON if wrapped
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    try:
        data = json.loads(text)
        return Plan.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.exception("Planner failed to produce valid Plan JSON")
        # Fallback minimal plan
        return Plan(goal=goal, summary="Fallback plan (planner output invalid).", steps=[], metadata={"error": str(e)})
