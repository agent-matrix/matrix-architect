from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class RepoKind(str, Enum):
    github = "github"
    local = "local"


class RepoSpec(BaseModel):
    kind: RepoKind = Field(..., description="Target repository type")
    # github
    owner: Optional[str] = None
    repo: Optional[str] = None
    ref: Optional[str] = Field(default=None, description="branch/tag/sha")
    # local
    path: Optional[str] = None


class FileOpType(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"


class FileOp(BaseModel):
    op: FileOpType
    path: str
    content: Optional[str] = None
    message: Optional[str] = None


class Step(BaseModel):
    id: str
    title: str
    rationale: Optional[str] = None
    ops: List[FileOp] = Field(default_factory=list)
    verify: List[str] = Field(default_factory=list, description="Commands to run to verify this step")


class Plan(BaseModel):
    goal: str
    summary: str
    steps: List[Step]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class PolicyGate(BaseModel):
    allowed: bool
    risk: RiskLevel = RiskLevel.low
    reasons: List[str] = Field(default_factory=list)
    requires_guardian_approval: bool = False


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    blocked = "blocked"


class ArtifactKind(str, Enum):
    log = "log"
    plan = "plan"
    patch = "patch"
    bundle = "bundle"
    report = "report"


class Artifact(BaseModel):
    kind: ArtifactKind
    name: str
    uri: Optional[str] = None
    content_type: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    id: str
    status: JobStatus
    repo: RepoSpec
    goal: str
    plan: Optional[Plan] = None
    gate: Optional[PolicyGate] = None
    artifacts: List[Artifact] = Field(default_factory=list)
    error: Optional[str] = None
