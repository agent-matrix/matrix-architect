from __future__ import annotations

from datetime import datetime
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
    critical = "critical"


class PolicyGate(BaseModel):
    allowed: bool
    risk: RiskLevel = RiskLevel.low
    reasons: List[str] = Field(default_factory=list)
    requires_guardian_approval: bool = False
    approval_id: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class JobStatus(str, Enum):
    queued = "queued"
    planning = "planning"
    patching = "patching"
    verifying = "verifying"
    waiting_approval = "waiting_approval"
    deploying = "deploying"
    publishing = "publishing"
    succeeded = "succeeded"
    failed = "failed"
    aborted = "aborted"


class JobStage(str, Enum):
    """Execution pipeline stages"""
    PLAN = "PLAN"
    PATCH = "PATCH"
    VERIFY = "VERIFY"
    GATE = "GATE"
    DEPLOY = "DEPLOY"
    PUBLISH = "PUBLISH"


class StepStatus(str, Enum):
    """Individual step execution status"""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class StepExecution(BaseModel):
    """Track execution of individual step"""
    step_id: str
    status: StepStatus = StepStatus.pending
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)


class ArtifactKind(str, Enum):
    log = "log"
    plan = "plan"
    patch = "patch"
    bundle = "bundle"
    report = "report"
    sbom = "sbom"
    scan = "scan"
    attestation = "attestation"
    evidence = "evidence"


class Artifact(BaseModel):
    kind: ArtifactKind
    name: str
    uri: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    checksum: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class EvidenceKind(str, Enum):
    """Types of verification evidence"""
    test_results = "test_results"
    build_logs = "build_logs"
    lint_results = "lint_results"
    security_scan = "security_scan"
    coverage_report = "coverage_report"
    dependency_audit = "dependency_audit"
    sbom = "sbom"


class Evidence(BaseModel):
    """Evidence from verification steps"""
    kind: EvidenceKind
    passed: bool
    summary: str
    details: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DeploymentTarget(str, Enum):
    """Supported deployment targets"""
    kubernetes = "kubernetes"
    docker_compose = "docker_compose"
    serverless = "serverless"
    vm = "vm"
    none = "none"


class DeploymentConfig(BaseModel):
    """Deployment configuration"""
    target: DeploymentTarget
    environment: str = "staging"
    namespace: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class Attestation(BaseModel):
    """Final attestation document for a job"""
    job_id: str
    completed_at: datetime
    plan_hash: str
    patch_hash: str
    evidence: List[Evidence] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    signed_by: Optional[str] = None
    signature: Optional[str] = None


class JobConstraints(BaseModel):
    """Execution constraints for a job"""
    max_duration: int = 3600  # seconds
    require_tests: bool = True
    require_build: bool = True
    allow_breaking_changes: bool = False
    security_scan: bool = True
    coverage_threshold: Optional[float] = None


class Job(BaseModel):
    id: str
    status: JobStatus
    current_stage: Optional[JobStage] = None
    repo: RepoSpec
    goal: str
    plan: Optional[Plan] = None
    gate: Optional[PolicyGate] = None
    artifacts: List[Artifact] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    step_executions: List[StepExecution] = Field(default_factory=list)
    deployment_config: Optional[DeploymentConfig] = None
    attestation: Optional[Attestation] = None
    constraints: JobConstraints = Field(default_factory=JobConstraints)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    retry_count: int = 0
