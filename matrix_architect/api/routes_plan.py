from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from ..core.models import RepoSpec, Job, JobStatus
from ..core.planner import plan as make_plan
from ..core.policies import score_plan
from ..storage.job_store import JobStore
from ..storage.artifact_store import ArtifactStore

router = APIRouter()
jobs = JobStore()
artifacts = ArtifactStore()


class PlanRequest(BaseModel):
    repo: RepoSpec
    goal: str = Field(..., min_length=3)
    matrix_ai_url: Optional[str] = None


@router.post("", response_model=Job)
async def create_plan(req: PlanRequest, authorization: Optional[str] = Header(default=None)) -> Job:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    job_id = uuid.uuid4().hex
    job = Job(id=job_id, status=JobStatus.running, repo=req.repo, goal=req.goal)
    jobs.put(job)

    p = await make_plan(req.repo, req.goal, token=token, matrix_ai_url=req.matrix_ai_url)
    gate = score_plan(p)

    job.plan = p
    job.gate = gate
    job.status = JobStatus.blocked if (not gate.allowed) else JobStatus.succeeded
    jobs.put(job)

    artifacts.write_text(job_id, "plan.json", p.model_dump_json(indent=2))
    artifacts.write_text(job_id, "policy_gate.json", gate.model_dump_json(indent=2))

    return job
