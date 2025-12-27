from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..storage.artifact_store import ArtifactStore

router = APIRouter()
store = ArtifactStore()

@router.get("/{job_id}/{name}")
def get_artifact(job_id: str, name: str):
    p = store.path(job_id, name)
    if not p:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(str(p))
