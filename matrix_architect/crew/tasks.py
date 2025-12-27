from __future__ import annotations

from textwrap import dedent
try:
    from crewai import Task, Agent
except Exception:  # pragma: no cover
    Agent = Crew = Process = Task = None  # type: ignore

def plan_task(agent: Agent, goal: str, repo_file_list: str) -> Task:
    prompt = dedent(f"""
    Goal:
    {goal}

    File list:
    {repo_file_list}

    Output ONLY JSON for a Plan (see API schema in README).
    """)
    return Task(description=prompt, expected_output="JSON Plan", agent=agent)
