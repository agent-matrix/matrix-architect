.PHONY: help install install-backend install-frontend run serve backend worker frontend build-container publish-container clean dev-setup check-uv

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON_VERSION := 3.11
DOCKER_REGISTRY ?= ghcr.io/agent-matrix
IMAGE_NAME := matrix-architect
IMAGE_TAG ?= latest
FRONTEND_IMAGE_NAME := matrix-architect-frontend

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

##@ Help

help: ## Display this help message
	@echo "Matrix Architect - Makefile Commands"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

check-uv: ## Check if uv is installed
	@which uv > /dev/null || (echo "$(RED)Error: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh$(NC)" && exit 1)
	@echo "$(GREEN)✓ uv is installed$(NC)"

dev-setup: check-uv ## Initial development setup (installs all dependencies)
	@echo "$(GREEN)Setting up Matrix Architect development environment...$(NC)"
	@$(MAKE) install-backend
	@$(MAKE) install-frontend
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run 'make run' to start both backend and frontend"

install: dev-setup ## Alias for dev-setup

install-backend: check-uv ## Install backend Python dependencies with uv
	@echo "$(GREEN)Installing backend dependencies with uv (Python $(PYTHON_VERSION))...$(NC)"
	@uv venv --python $(PYTHON_VERSION) || true
	@uv pip install -e ".[dev]"
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

##@ Development

run: ## Run both backend API and frontend (parallel)
	@echo "$(GREEN)Starting Matrix Architect (Backend + Frontend)...$(NC)"
	@trap 'kill 0' EXIT; \
		$(MAKE) backend & \
		$(MAKE) frontend & \
		wait

backend: check-uv ## Run backend API server with uv
	@echo "$(GREEN)Starting backend API on http://localhost:8080...$(NC)"
	@uv run uvicorn matrix_architect.api.app:app --reload --host 0.0.0.0 --port 8080

worker: check-uv ## Run Celery worker with uv
	@echo "$(GREEN)Starting Celery worker...$(NC)"
	@uv run celery -A matrix_architect.queue.celery_app worker --loglevel=info --concurrency=4

beat: check-uv ## Run Celery beat scheduler with uv
	@echo "$(GREEN)Starting Celery beat...$(NC)"
	@uv run celery -A matrix_architect.queue.celery_app beat --loglevel=info

serve: frontend ## Alias for running frontend only

frontend: ## Run frontend development server
	@echo "$(GREEN)Starting frontend on http://localhost:3000...$(NC)"
	@cd frontend && npm run dev

##@ Docker

build-container: ## Build Docker container for backend
	@echo "$(GREEN)Building Docker container: $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)...$(NC)"
	@docker build -t $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) \
		-t $(DOCKER_REGISTRY)/$(IMAGE_NAME):latest \
		-f Dockerfile .
	@echo "$(GREEN)✓ Container built successfully$(NC)"
	@echo ""
	@echo "Built images:"
	@echo "  - $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"
	@echo "  - $(DOCKER_REGISTRY)/$(IMAGE_NAME):latest"

build-frontend-container: ## Build Docker container for frontend
	@echo "$(GREEN)Building frontend Docker container...$(NC)"
	@docker build -t $(DOCKER_REGISTRY)/$(FRONTEND_IMAGE_NAME):$(IMAGE_TAG) \
		-t $(DOCKER_REGISTRY)/$(FRONTEND_IMAGE_NAME):latest \
		-f frontend/Dockerfile ./frontend
	@echo "$(GREEN)✓ Frontend container built successfully$(NC)"

build-all-containers: build-container build-frontend-container ## Build all Docker containers

publish-container: build-container ## Build and publish Docker container to registry
	@echo "$(GREEN)Publishing container to $(DOCKER_REGISTRY)...$(NC)"
	@docker push $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	@docker push $(DOCKER_REGISTRY)/$(IMAGE_NAME):latest
	@echo "$(GREEN)✓ Container published successfully$(NC)"
	@echo ""
	@echo "Published to:"
	@echo "  - $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"
	@echo "  - $(DOCKER_REGISTRY)/$(IMAGE_NAME):latest"

publish-frontend-container: build-frontend-container ## Build and publish frontend container
	@echo "$(GREEN)Publishing frontend container...$(NC)"
	@docker push $(DOCKER_REGISTRY)/$(FRONTEND_IMAGE_NAME):$(IMAGE_TAG)
	@docker push $(DOCKER_REGISTRY)/$(FRONTEND_IMAGE_NAME):latest
	@echo "$(GREEN)✓ Frontend container published$(NC)"

publish-all-containers: publish-container publish-frontend-container ## Publish all containers

##@ Docker Compose

docker-up: ## Start all services with docker-compose
	@echo "$(GREEN)Starting all services with docker-compose...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo ""
	@echo "Services available:"
	@echo "  - API: http://localhost:8080"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Redis: localhost:6379"
	@echo "  - PostgreSQL: localhost:5432"

docker-down: ## Stop all docker-compose services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-logs: ## Show docker-compose logs
	@docker-compose logs -f

docker-restart: docker-down docker-up ## Restart all docker-compose services

docker-build: ## Build docker-compose services
	@docker-compose build

##@ Testing & Quality

test: check-uv ## Run tests with uv
	@echo "$(GREEN)Running tests...$(NC)"
	@uv run pytest -v

test-coverage: check-uv ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@uv run pytest --cov=matrix_architect --cov-report=html --cov-report=term

lint: check-uv ## Run linter (ruff)
	@echo "$(GREEN)Running linter...$(NC)"
	@uv run ruff check .

lint-fix: check-uv ## Run linter and auto-fix issues
	@echo "$(GREEN)Running linter with auto-fix...$(NC)"
	@uv run ruff check . --fix

format: check-uv ## Format code with ruff
	@echo "$(GREEN)Formatting code...$(NC)"
	@uv run ruff format .

type-check: check-uv ## Run type checking with mypy
	@echo "$(GREEN)Running type checker...$(NC)"
	@uv run mypy matrix_architect || true

quality: lint test ## Run all quality checks

##@ Database

db-migrate: check-uv ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	@uv run alembic upgrade head

db-revision: check-uv ## Create new database migration
	@echo "$(GREEN)Creating new migration...$(NC)"
	@read -p "Migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

db-reset: ## Reset database (drops all data!)
	@echo "$(RED)WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		$(MAKE) db-migrate; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

##@ Utilities

clean: ## Clean build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true
	@cd frontend && rm -rf node_modules/.cache dist 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: clean ## Clean everything including node_modules and venv
	@echo "$(YELLOW)Deep cleaning (including dependencies)...$(NC)"
	@rm -rf .venv frontend/node_modules
	@echo "$(GREEN)✓ Deep clean complete$(NC)"

env-example: ## Generate .env from .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file from .env.example$(NC)"; \
		echo "$(YELLOW)⚠ Please update .env with your configuration$(NC)"; \
	else \
		echo "$(YELLOW).env already exists, skipping$(NC)"; \
	fi

logs-api: ## Tail API logs
	@docker-compose logs -f api

logs-worker: ## Tail worker logs
	@docker-compose logs -f worker

logs-frontend: ## Tail frontend logs
	@docker-compose logs -f frontend

status: ## Show service status
	@echo "$(GREEN)Matrix Architect Status:$(NC)"
	@echo ""
	@docker-compose ps 2>/dev/null || echo "Docker Compose not running"

##@ Production

prod-check: ## Run production readiness checks
	@echo "$(GREEN)Running production readiness checks...$(NC)"
	@echo ""
	@echo "1. Checking environment variables..."
	@test -f .env && echo "$(GREEN)✓ .env file exists$(NC)" || echo "$(RED)✗ .env file missing$(NC)"
	@echo ""
	@echo "2. Checking dependencies..."
	@$(MAKE) check-uv
	@echo ""
	@echo "3. Running tests..."
	@$(MAKE) test
	@echo ""
	@echo "4. Running linter..."
	@$(MAKE) lint
	@echo ""
	@echo "$(GREEN)Production checks complete!$(NC)"

prod-deploy: prod-check build-all-containers publish-all-containers ## Full production deployment
	@echo "$(GREEN)✓ Production deployment complete!$(NC)"
	@echo ""
	@echo "Containers published:"
	@echo "  - $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"
	@echo "  - $(DOCKER_REGISTRY)/$(FRONTEND_IMAGE_NAME):$(IMAGE_TAG)"

##@ Information

version: ## Show version information
	@echo "Matrix Architect v2.0"
	@echo ""
	@echo "Python version:"
	@uv run python --version 2>/dev/null || echo "Not installed"
	@echo ""
	@echo "Node version:"
	@cd frontend && node --version 2>/dev/null || echo "Not installed"
	@echo ""
	@echo "Docker version:"
	@docker --version 2>/dev/null || echo "Not installed"

info: version status ## Show system information

urls: ## Show service URLs
	@echo "$(GREEN)Matrix Architect Service URLs:$(NC)"
	@echo ""
	@echo "  API:      http://localhost:8080"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API Docs: http://localhost:8080/docs"
	@echo "  Redis:    localhost:6379"
	@echo "  Postgres: localhost:5432"
	@echo ""
