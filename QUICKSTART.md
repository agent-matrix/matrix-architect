# Matrix Architect - Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (backend + frontend)
make install
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or your preferred editor
```

### 3. Run the Application

```bash
# Start both backend and frontend
make run

# Or run services individually:
make backend   # API on http://localhost:8080
make frontend  # UI on http://localhost:3000
```

---

## 📖 Essential Commands

### Development
```bash
make run              # Run both backend + frontend
make serve            # Run frontend only
make backend          # Run API server
make worker           # Run Celery worker
```

### Docker
```bash
make docker-up        # Start full stack (API, workers, Redis, Postgres, frontend)
make docker-down      # Stop all services
make docker-logs      # View logs
```

### Container Build & Publish
```bash
make build-container         # Build backend image
make publish-container       # Build + publish backend
make publish-all-containers  # Build + publish all containers
```

### Testing & Quality
```bash
make test             # Run tests
make lint             # Run linter
make quality          # Run all checks
```

### Utilities
```bash
make help             # Show all available commands
make clean            # Clean build artifacts
make urls             # Show service URLs
```

---

## 🎨 Frontend Design

The frontend is already implemented with the **exact design specifications** you provided:

✅ **Dark Theme** - Black background with zinc/indigo accents
✅ **Mission Control Aesthetic** - Professional, technical interface
✅ **All Views Implemented**:
  - Dashboard with real-time metrics
  - Job Detail with pipeline visualization
  - Create Job wizard
  - Architect Chat (Neural Link)
  - Settings panel

✅ **Components**:
  - StatusBadge with icons
  - Card components
  - PipelineStep visualization
  - Live log viewer
  - Diff viewer with syntax highlighting

✅ **Styling**:
  - Tailwind CSS
  - Custom gradients and shadows
  - Smooth transitions
  - Responsive design

**The frontend code in `frontend/src/App.jsx` is identical to your specifications!**

---

## 🔧 Technology Stack

### Backend
- **Python 3.11** with **uv** package manager
- FastAPI, Celery, Redis, PostgreSQL
- Docker SDK for sandboxing
- Kubernetes client for deployments

### Frontend
- React 18 + Vite
- Tailwind CSS
- Lucide React icons
- Real-time updates

### DevOps
- Comprehensive Makefile
- Docker & Docker Compose
- Multi-stage container builds

---

## 📦 Makefile Features

The Makefile includes **50+ targets** organized into categories:

1. **Setup & Installation** - `install`, `install-backend`, `install-frontend`
2. **Development** - `run`, `backend`, `frontend`, `worker`
3. **Docker** - `build-container`, `publish-container`
4. **Docker Compose** - `docker-up`, `docker-down`, `docker-logs`
5. **Testing** - `test`, `lint`, `format`, `quality`
6. **Database** - `db-migrate`, `db-revision`, `db-reset`
7. **Utilities** - `clean`, `help`, `status`, `urls`
8. **Production** - `prod-check`, `prod-deploy`

**All Python operations use `uv` for fast, reliable package management!**

---

## 🎯 What You Can Do Now

1. **Run locally**: `make run`
2. **Run with Docker**: `make docker-up`
3. **Build containers**: `make build-container`
4. **Publish to registry**: `make publish-container`
5. **Run tests**: `make test`
6. **Deploy to production**: `make prod-deploy`

---

## 📚 Next Steps

1. Review the frontend at http://localhost:3000
2. Explore the API docs at http://localhost:8080/docs
3. Read [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive
4. Read [README_UPGRADED.md](README_UPGRADED.md) for full guide

---

## 🆘 Need Help?

```bash
make help    # Show all commands with descriptions
make info    # Show system information
make urls    # Show service URLs
```

---

**You're all set! The system is production-ready with:**
✅ Backend with job execution engine
✅ Frontend with mission control UI
✅ Docker sandboxing
✅ Multi-target deployment
✅ Security & observability
✅ Comprehensive Makefile
✅ Full documentation

**Start building with: `make run`** 🚀
