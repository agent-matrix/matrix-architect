from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes_plan import router as plan_router
from .routes_execute import router as execute_router
from .routes_jobs import router as jobs_router
from .routes_artifacts import router as artifacts_router

app = FastAPI(title="Matrix Architect", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_router, prefix="/plan", tags=["plan"])
app.include_router(execute_router, prefix="/execute", tags=["execute"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(artifacts_router, prefix="/artifacts", tags=["artifacts"])
