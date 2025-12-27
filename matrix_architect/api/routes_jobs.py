from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..storage.job_store import JobStore
from ..core.models import Job

router = APIRouter()
jobs = JobStore()

@router.get("/{job_id}", response_model=Job)
def get_job(job_id: str) -> Job:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("", response_model=list[Job])
def list_jobs(limit: int = 50) -> list[Job]:
    return jobs.list(limit=limit)
