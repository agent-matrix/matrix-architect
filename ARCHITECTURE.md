# Matrix Architect - Architecture Documentation

## Overview

Matrix Architect is a production-grade build/executor service that provides safe, auditable code modification, verification, deployment, and publishing capabilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Matrix Ecosystem                          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Matrix AI   │  │   Guardian   │  │  Matrix Hub  │           │
│  │  (Planning)  │  │  (Approval)  │  │  (Registry)  │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                      │
│                    ┌───────▼────────┐                            │
│                    │  ARCHITECT API │                            │
│                    └───────┬────────┘                            │
│                            │                                      │
│         ┌──────────────────┼──────────────────┐                  │
│         │                  │                  │                  │
│    ┌────▼────┐      ┌──────▼─────┐    ┌──────▼─────┐           │
│    │  Redis  │      │  Postgres  │    │   Worker   │           │
│    │ (Queue) │      │  (Storage) │    │   Fleet    │           │
│    └─────────┘      └────────────┘    └────────────┘           │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer (`matrix_architect/api/`)

**Purpose**: RESTful API for job management and execution

**Key Routes**:
- `POST /plan` - Create execution plan
- `POST /execute` - Execute job
- `GET /jobs` - List jobs
- `GET /jobs/{id}` - Job details
- `GET /artifacts/{job_id}` - Download artifacts

### 2. Job Execution Engine (`matrix_architect/queue/`)

**Purpose**: Distributed job processing with Celery

**Components**:
- **Celery App**: Task orchestration
- **Workers**: Parallel job execution
- **Beat**: Periodic tasks (cleanup, monitoring)

**Features**:
- Priority queuing (high/normal/low)
- Retry logic with exponential backoff
- Job checkpointing and resumption
- Concurrency controls

### 3. Sandbox System (`matrix_architect/sandbox/`)

**Purpose**: Isolated code execution

**Implementation**:
- Docker-based sandboxes
- Network isolation (`--network=none`)
- Resource limits (CPU, memory)
- Read-only root filesystem
- Writable tmpfs mounts

### 4. Verification System (`matrix_architect/core/verifier_enhanced.py`)

**Purpose**: Evidence-based verification

**Verification Steps**:
1. **Lint**: Code quality checks (ruff)
2. **Tests**: Unit and integration tests
3. **Build**: Package building
4. **Security Scan**: Vulnerability detection (safety)
5. **Dependency Audit**: pip-audit
6. **SBOM Generation**: Software Bill of Materials

**Evidence Output**:
- Test results
- Build logs
- Security scan reports
- SBOM (CycloneDX/SPDX format)

### 5. Deployment Adapters (`matrix_architect/deployment/`)

**Purpose**: Multi-target deployment

**Supported Targets**:
- **Kubernetes**: Helm/ArgoCD integration
- **Docker Compose**: Local/staging deployments
- **Serverless**: AWS Lambda, Google Cloud Run
- **VM/Systemd**: Traditional deployments

**Features**:
- Dry-run mode
- Rollback support
- Health checks
- Log retrieval

### 6. Observability (`matrix_architect/observability/`)

**Components**:
- **Structured Logging**: JSON logs with trace IDs
- **Metrics**: Prometheus-compatible metrics
- **Tracing**: Distributed tracing support

**Key Metrics**:
- Job execution duration
- Success/failure rates
- Queue depth
- Worker utilization

### 7. Security (`matrix_architect/security/`)

**Features**:
- **Authentication**: JWT-based auth
- **Authorization**: Role-Based Access Control (RBAC)
- **Secrets Management**: Integration with Vault, AWS Secrets Manager
- **Roles**: Viewer, Operator, Admin

**Permissions**:
- Job operations (create, read, update, execute)
- Deployment permissions (staging, production)
- Admin operations (user management, policies)

## Job Execution Pipeline

```
PLAN → PATCH → VERIFY → GATE → DEPLOY → PUBLISH
  ↓      ↓       ↓        ↓       ↓        ↓
Agent  Apply   Tests   Policy  Target   Hub
       Code    Build   Check   Deploy   Push
```

### Stage Details

1. **PLAN**: Generate structured plan using AI or human input
2. **PATCH**: Apply file operations (create/update/delete)
3. **VERIFY**: Run verification suite, generate evidence
4. **GATE**: Policy check, require approval if high risk
5. **DEPLOY**: Deploy to target environment
6. **PUBLISH**: Publish artifacts to Matrix Hub

## Data Models

### Job

```python
class Job:
    id: str
    status: JobStatus
    current_stage: JobStage
    repo: RepoSpec
    plan: Plan
    evidence: List[Evidence]
    artifacts: List[Artifact]
    deployment_config: DeploymentConfig
    attestation: Attestation
    constraints: JobConstraints
```

### Evidence

```python
class Evidence:
    kind: EvidenceKind  # test_results, security_scan, etc.
    passed: bool
    summary: str
    details: Dict
    artifacts: List[str]
    timestamp: datetime
```

### Attestation

```python
class Attestation:
    job_id: str
    plan_hash: str
    patch_hash: str
    evidence: List[Evidence]
    artifacts: List[str]
    signed_by: str
    signature: str  # Cryptographic signature
```

## Storage

### Job Store (`matrix_architect/storage/job_store.py`)

- Persistent job state
- Audit trail
- Query interface

### Artifact Store (`matrix_architect/storage/artifact_store.py`)

- Immutable artifact storage
- Content-addressed (SHA256)
- Compression support
- Retention policies

## Frontend Architecture

### Technology Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React

### Key Views

1. **Dashboard**: System overview, active jobs
2. **Job Detail**: Live logs, pipeline visualization
3. **Plan Builder**: Create new jobs
4. **Chat**: AI interaction interface
5. **Settings**: Configuration management

## Deployment

### Docker Compose (Development)

```bash
docker-compose up --build
```

**Services**:
- API (port 8080)
- Worker (4 concurrent workers)
- Beat (periodic tasks)
- Redis (message broker)
- Postgres (storage)
- Frontend (port 3000)

### Kubernetes (Production)

```yaml
- Deployment: matrix-architect-api
- Deployment: matrix-architect-worker (HPA enabled)
- StatefulSet: redis-cluster
- StatefulSet: postgres-cluster
- Service: LoadBalancer for API
- Ingress: TLS termination
```

## Security Considerations

### Sandbox Isolation

- No network access by default
- Read-only root filesystem
- Limited CPU and memory
- Ephemeral containers

### Secrets Management

- Environment variable injection
- Vault integration for production
- No secrets in logs or artifacts

### Policy Enforcement

- Risk scoring (low/medium/high/critical)
- Automatic gating for high-risk operations
- Guardian approval workflow
- Audit logging

## Observability

### Logging

```json
{
  "timestamp": "2025-01-01T10:00:00Z",
  "level": "INFO",
  "logger": "matrix_architect.queue.tasks",
  "message": "Job execution started",
  "job_id": "job_992a",
  "worker_id": "worker-01",
  "trace_id": "abc123"
}
```

### Metrics

- `jobs_total{status}` - Total jobs by status
- `job_duration_seconds` - Job execution duration
- `worker_utilization` - Worker CPU/memory usage
- `queue_depth{priority}` - Queue depth by priority

### Tracing

- OpenTelemetry compatible
- Trace IDs propagated across services
- Integration with Jaeger/Zipkin

## Future Enhancements

### Short Term

- [ ] GraphQL API
- [ ] WebSocket support for real-time updates
- [ ] Advanced scheduling (cron jobs)
- [ ] Multi-tenancy

### Long Term

- [ ] Machine learning for plan optimization
- [ ] Self-healing capabilities
- [ ] Advanced rollback strategies (canary, blue/green)
- [ ] Integration testing framework

## Performance

### Throughput

- **API**: 1000 req/s (single instance)
- **Workers**: 100 jobs/hour (per worker)
- **Queue**: 10,000 jobs (pending)

### Latency

- **API Response**: <100ms (p95)
- **Job Start**: <5s (queued to running)
- **Verification**: 2-10 min (depends on test suite)

## References

- [Matrix AI](../matrix-ai/README.md)
- [Matrix Guardian](../matrix-guardian/README.md)
- [Matrix Hub](../matrix-hub/README.md)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker SDK](https://docker-py.readthedocs.io/)
- [Kubernetes Client](https://kubernetes.io/docs/reference/using-api/client-libraries/)
