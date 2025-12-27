# Matrix Architect - Production-Grade Build/Executor Service

> **Builder/Executor layer of the Matrix Ecosystem**
>
> A service that plans, implements, verifies, and deploys changes to software repositories in a controlled, auditable way.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

---

## 🚀 What's New in v2.0

Matrix Architect has been completely rebuilt as a **production-grade, enterprise-ready system**:

### Major Upgrades

✅ **Distributed Job Execution Engine**
- Celery-based worker fleet with priority queuing
- Job checkpointing and automatic retries
- Horizontal scaling support

✅ **Docker-Based Sandboxing**
- Isolated, secure code execution
- Network isolation and resource limits
- Read-only filesystems with tmpfs mounts

✅ **Evidence-Based Verification**
- Comprehensive test suites (lint, test, build)
- Security scanning (safety, pip-audit)
- SBOM generation (Software Bill of Materials)
- Cryptographic attestations

✅ **Multi-Target Deployment**
- Kubernetes adapter (Helm/ArgoCD)
- Docker Compose adapter
- Serverless adapters (AWS Lambda, Cloud Run)
- Rollback and health check support

✅ **Production Observability**
- Structured JSON logging with trace IDs
- Prometheus-compatible metrics
- OpenTelemetry tracing support

✅ **Enterprise Security**
- JWT authentication
- Role-Based Access Control (RBAC)
- Secrets management integration
- Policy gating with Guardian

✅ **Modern Web UI**
- React-based mission control interface
- Real-time job monitoring
- Pipeline visualization
- AI chat interface

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Features](#features)
- [API Documentation](#api-documentation)
- [Frontend](#frontend)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Development](#development)
- [Production Checklist](#production-checklist)

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend)

### Run with Docker Compose

```bash
# Clone repository
git clone https://github.com/matrix-org/matrix-architect.git
cd matrix-architect

# Copy environment variables
cp .env.example .env

# Edit .env with your API keys and configuration

# Start all services
docker-compose up --build

# Access services:
# - API: http://localhost:8080
# - Frontend: http://localhost:3000
# - Redis: localhost:6379
# - Postgres: localhost:5432
```

### Manual Installation

```bash
# Install Python dependencies
pip install -e .

# Start Redis (required)
docker run -d -p 6379:6379 redis:7-alpine

# Start Postgres (required)
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=architect_pass \
  -e POSTGRES_DB=matrix_architect \
  postgres:15-alpine

# Run API server
uvicorn matrix_architect.api.app:app --reload --port 8080

# Run Celery worker (in another terminal)
celery -A matrix_architect.queue.celery_app worker --loglevel=info

# Run Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

---

## Architecture

Matrix Architect consists of several key subsystems:

```
┌─────────────────────────────────────────────────────────┐
│                    MATRIX ARCHITECT                      │
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐   │
│  │   API    │──▶│  Queue   │──▶│  Worker Fleet    │   │
│  │ FastAPI  │   │  Redis   │   │  Celery Workers  │   │
│  └──────────┘   └──────────┘   └──────────────────┘   │
│       │                                  │              │
│       ├──────────────────────────────────┤              │
│       │                                  │              │
│  ┌────▼────┐   ┌──────────┐   ┌─────────▼────────┐   │
│  │ Storage │   │ Sandbox  │   │   Deployment     │   │
│  │Postgres │   │ Docker   │   │   Adapters       │   │
│  └─────────┘   └──────────┘   └──────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.**

---

## Features

### 🎯 Core Capabilities

#### 1. Job Execution Pipeline

Every job flows through a controlled pipeline:

```
PLAN → PATCH → VERIFY → GATE → DEPLOY → PUBLISH
```

- **PLAN**: Generate structured execution plan
- **PATCH**: Apply code changes safely
- **VERIFY**: Run tests, builds, security scans
- **GATE**: Policy check, approval workflow
- **DEPLOY**: Deploy to target environment
- **PUBLISH**: Publish to Matrix Hub

#### 2. Sandboxed Execution

All code runs in isolated Docker containers:

- ✅ Network isolation (`--network=none`)
- ✅ Resource limits (CPU, memory)
- ✅ Read-only root filesystem
- ✅ Ephemeral workspaces
- ✅ No persistent side effects

#### 3. Evidence Generation

Comprehensive verification with artifacts:

- **Test Results**: Unit, integration, e2e tests
- **Build Logs**: Complete build output
- **Security Scans**: Vulnerability reports (safety, pip-audit)
- **SBOM**: Software Bill of Materials
- **Attestations**: Cryptographically signed evidence

#### 4. Multi-Target Deployment

Deploy anywhere:

| Target | Adapter | Features |
|--------|---------|----------|
| Kubernetes | ✅ | Helm, rollback, health checks |
| Docker Compose | ✅ | Local/staging deployments |
| AWS Lambda | ✅ | Serverless functions |
| Google Cloud Run | ✅ | Serverless containers |
| VM/Systemd | 🔜 | Coming soon |

#### 5. Observability

Production-ready monitoring:

```json
{
  "timestamp": "2025-01-01T10:00:00Z",
  "level": "INFO",
  "job_id": "job_992a",
  "trace_id": "abc123",
  "message": "Job execution started"
}
```

- Structured JSON logs
- Prometheus metrics
- OpenTelemetry tracing
- Distributed trace IDs

---

## API Documentation

### Core Endpoints

#### Create Job

```bash
POST /api/jobs

{
  "repo": {
    "kind": "github",
    "owner": "matrix-org",
    "repo": "backend-service"
  },
  "goal": "Upgrade to Python 3.11 and fix linting errors",
  "constraints": {
    "require_tests": true,
    "security_scan": true
  }
}
```

#### Get Job Status

```bash
GET /api/jobs/{job_id}
```

#### List Jobs

```bash
GET /api/jobs?status=running&limit=50
```

#### Download Artifacts

```bash
GET /api/artifacts/{job_id}/{artifact_name}
```

#### Execute Job

```bash
POST /api/execute/{job_id}
```

### Authentication

All API requests require a JWT token:

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/jobs
```

**Obtain token**:

```bash
POST /api/auth/token

{
  "username": "admin",
  "password": "secret"
}
```

---

## Frontend

### Mission Control UI

Matrix Architect includes a modern React-based web interface:

**Features**:
- 📊 Real-time dashboard with metrics
- 🔄 Live job monitoring
- 📈 Pipeline visualization
- 💬 AI chat interface
- ⚙️ Configuration management

**Screenshots**:

```
┌─────────────────────────────────────────────────┐
│  Dashboard    Plan Builder    Job Detail        │
│  ├─ Active Jobs (12)                            │
│  ├─ Success Rate: 98.5%                         │
│  ├─ Workers Online: 8                           │
│  └─ Avg Build Time: 2m 14s                      │
│                                                  │
│  [PLAN] → [PATCH] → [VERIFY] → [GATE] → [...]  │
│    ✓        ✓         🔄         ⏸              │
└─────────────────────────────────────────────────┘
```

**Run Frontend**:

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## Deployment

### Docker Compose (Development)

```bash
docker-compose up --build
```

**Services**:
- API (port 8080)
- Worker x4 (concurrent execution)
- Beat (periodic tasks)
- Redis (message broker)
- Postgres (storage)
- Frontend (port 3000)

### Kubernetes (Production)

```bash
# Build and push image
docker build -t matrix-architect:latest .
docker push your-registry/matrix-architect:latest

# Deploy with Helm
helm install matrix-architect ./helm \
  --set image.tag=latest \
  --set workers.replicas=10
```

**Kubernetes Components**:
- Deployment: `matrix-architect-api`
- Deployment: `matrix-architect-worker` (HPA enabled)
- StatefulSet: `redis-cluster`
- StatefulSet: `postgres-cluster`
- Service: LoadBalancer for API
- Ingress: TLS termination

---

## Configuration

### Environment Variables

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_URL=postgresql://architect:pass@localhost:5432/matrix_architect

# Security
JWT_SECRET=your-secret-key-change-in-production

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Matrix Services
MATRIX_HUB_URL=https://hub.matrix.ai
MATRIX_GUARDIAN_URL=https://guardian.matrix.ai

# Observability
LOG_LEVEL=INFO
JSON_LOGS=true

# Features
ENABLE_SANDBOXING=true
ENABLE_SECURITY_SCAN=true
REQUIRE_APPROVALS=true
```

### RBAC Roles

| Role | Permissions |
|------|-------------|
| **Viewer** | Read jobs, view artifacts |
| **Operator** | Create jobs, execute, deploy to staging |
| **Admin** | All permissions, manage users, policies |

---

## Development

### Project Structure

```
matrix-architect/
├── matrix_architect/
│   ├── api/              # FastAPI application
│   ├── queue/            # Celery tasks
│   ├── core/             # Business logic
│   ├── sandbox/          # Docker sandboxing
│   ├── deployment/       # Deployment adapters
│   ├── security/         # Auth, RBAC, secrets
│   ├── observability/    # Logging, metrics, tracing
│   └── storage/          # Persistence layer
├── frontend/             # React UI
├── docker-compose.yml    # Development stack
├── Dockerfile            # Production image
└── ARCHITECTURE.md       # Detailed docs
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy matrix_architect
```

---

## Production Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Configure secrets manager (Vault, AWS Secrets Manager)
- [ ] Enable TLS for API endpoints
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation (ELK, Datadog)
- [ ] Set up backup for Postgres
- [ ] Configure Redis persistence
- [ ] Enable rate limiting
- [ ] Set resource limits for workers
- [ ] Configure alerts for job failures
- [ ] Set up CI/CD pipeline
- [ ] Perform security audit
- [ ] Load testing
- [ ] Disaster recovery plan

---

## Roadmap

### v2.1 (Q1 2025)

- [ ] GraphQL API
- [ ] WebSocket support for real-time updates
- [ ] Advanced scheduling (cron jobs)
- [ ] Multi-tenancy support

### v2.2 (Q2 2025)

- [ ] Machine learning for plan optimization
- [ ] Self-healing capabilities
- [ ] Canary and blue/green deployments
- [ ] Integration testing framework

### v3.0 (Q3 2025)

- [ ] Distributed tracing with Jaeger
- [ ] Auto-scaling based on queue depth
- [ ] Advanced policy engine
- [ ] Multi-region support

---

## Integration with Matrix Ecosystem

Matrix Architect works alongside:

- **[Matrix AI](../matrix-ai/)** - Planning, reasoning, code generation
- **[Matrix Guardian](../matrix-guardian/)** - Policy enforcement, approvals
- **[Matrix Hub](../matrix-hub/)** - Artifact registry, distribution
- **[Matrix System](../matrix-system/)** - Orchestration, SDK, CLI

Together, these form a **closed-loop, safety-first multi-intelligence system**.

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

Apache 2.0 License - See [LICENSE](LICENSE)

---

## Support

- 📧 Email: support@matrix.ai
- 💬 Discord: https://discord.gg/matrix-ai
- 📚 Docs: https://docs.matrix.ai/architect
- 🐛 Issues: https://github.com/matrix-org/matrix-architect/issues

---

**Built with ❤️ by the Matrix Team**
