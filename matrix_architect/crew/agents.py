from __future__ import annotations

try:
    from crewai import Agent
except Exception:  # pragma: no cover
    Agent = Crew = Process = Task = None  # type: ignore
from ..core.llm_provider import build_llm

def architect_agent() -> Agent:
    return Agent(
        role="Architect",
        goal="Design safe, incremental changes and ensure they are verifiable",
        backstory="You design minimal-risk plans and produce clear step-by-step modifications.",
        llm=build_llm(),
    )

def executor_agent() -> Agent:
    return Agent(
        role="Executor",
        goal="Implement the plan precisely and safely",
        backstory="You apply patches carefully and keep changes small and reviewable.",
        llm=build_llm(),
    )
