# Matrix Architect

Matrix Architect is the **build/apply/fix/deploy** component of the Matrix suite.

It complements:

- **matrix-system**: the runtime/orchestrator that runs agents and MCP servers.
- **matrix-hub**: the registry for manifests, tools, agent bundles, and published artifacts.
- **matrix-guardian**: approvals/policy gates and risk controls for sensitive operations.
- **matrix-ai**: model/agent intelligence (planning, code generation, refactoring).

## What it does

Matrix Architect provides a single service (API + optional CLI) that can:

1. **Plan** a change for a repository/workspace (LLM planner via CrewAI locally, or via matrix-ai).
2. **Execute** the plan by producing patches and applying them (GitHub repo or local workspace).
3. **Verify** results in a sandbox (run tests/build commands and capture logs).
4. **Deploy** via a pluggable adapter interface (optional).
5. **Publish** a signed manifest + artifacts back to matrix-hub (optional).
6. **Gate** actions with local policies and/or matrix-guardian approvals.

This repo is a refactor of the GitPilot project into a more general **Architect/Executor** that can power a
multi-intelligence “alive system” (multiple cooperating agents that can continuously improve the codebase).

## Quickstart (dev)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn matrix_architect.api.app:app --reload --port 8080
```

Open API docs at `http://localhost:8080/docs`.

## CLI

```bash
matrix-architect plan --repo /path/to/repo --goal "add healthcheck endpoint"
matrix-architect execute --repo /path/to/repo --plan plan.json
```

## Repository targets

- **GitHub**: uses the GitPilot GitHub integration (OAuth/App token).
- **Local workspace**: works on a folder path; can optionally use `git` for patch application.

## Project layout

See `matrix_architect/` for the full service layout (API routes, core planner/executor, tools, storage, integrations).
