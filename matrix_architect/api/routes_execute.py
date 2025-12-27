from __future__ import annotations

import uuid
from typing import Optional, List

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from ..core.models import RepoSpec, Plan, Job, JobStatus, Artifact, ArtifactKind
from ..core.executor import execute as run_execute
from ..core.verifier import verify as run_verify
from ..core.policies import score_plan
from ..storage.job_store import JobStore
from ..storage.artifact_store import ArtifactStore

router = APIRouter()
jobs = JobStore()
artifacts = ArtifactStore()


class ExecuteRequest(BaseModel):
    repo: RepoSpec
    plan: Plan
    matrix_ai_url: Optional[str] = None
    verify_commands: List[str] = Field(default_factory=list)


@router.post("", response_model=Job)
async def execute(req: ExecuteRequest, authorization: Optional[str] = Header(default=None)) -> Job:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    job_id = uuid.uuid4().hex
    job = Job(id=job_id, status=JobStatus.running, repo=req.repo, goal=req.plan.goal, plan=req.plan)
    jobs.put(job)

    gate = score_plan(req.plan)
    job.gate = gate
    if not gate.allowed:
        job.status = JobStatus.blocked
        jobs.put(job)
        artifacts.write_text(job_id, "policy_gate.json", gate.model_dump_json(indent=2))
        return job

    try:
        await run_execute(req.repo, req.plan, token=token, matrix_ai_url=req.matrix_ai_url)
        artifacts.write_text(job_id, "plan.json", req.plan.model_dump_json(indent=2))

        if req.verify_commands:
            report = await run_verify(req.repo, req.verify_commands)
            artifacts.write_text(job_id, "verify_report.json", __import__("json").dumps(report, indent=2))
            if not report.get("ok", True):
                job.status = JobStatus.failed
                job.error = "Verification failed"
            else:
                job.status = JobStatus.succeeded
        else:
            job.status = JobStatus.succeeded

    except Exception as e:
        job.status = JobStatus.failed
        job.error = str(e)
        artifacts.write_text(job_id, "error.txt", str(e))

    jobs.put(job)
    job.artifacts.append(Artifact(kind=ArtifactKind.plan, name="plan.json"))
    if req.verify_commands:
        job.artifacts.append(Artifact(kind=ArtifactKind.report, name="verify_report.json"))
    if job.error:
        job.artifacts.append(Artifact(kind=ArtifactKind.log, name="error.txt"))
    return job
