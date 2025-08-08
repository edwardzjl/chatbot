# Copilot Instructions for Chatbot Repository

## Repository Overview

**Chatbot** is a Single-page application (SPA) that recreates key features of popular LLM-based chatbots like ChatGPT, Gemini, and Le Chat. It consists of a **FastAPI backend** (Python) and **React frontend** (JavaScript/Vite) with support for tool usage, multimodal inputs, reasoning models, and working memory.

### High-Level Architecture
- **Backend**: FastAPI with LangChain, SQLAlchemy, and LangGraph for agent workflows
- **Frontend**: React 19 with Material-UI, Vite build system, and WebSocket support
- **Database**: SQLite (development) / PostgreSQL (production) with Alembic migrations
- **Deployment**: Docker containers with Kubernetes support (vanilla and Knative)
- **Authentication**: OpenID Connect via external OAuth clients

### Project Structure
```
/api/           - FastAPI backend with Python 3.13
/web/           - React frontend with Node.js LTS
/manifests/     - Kubernetes deployment configurations  
/.github/       - CI/CD workflows and issue templates
/.devcontainer/ - VS Code development container setup
```

## Build Requirements & Setup

### Prerequisites
- **Python 3.13** (3.12 works with warnings)
- **Node.js LTS** (v20+)
- **pipenv** for Python dependency management
- **Yarn 4.9.2** via corepack for Node.js dependencies

### Initial Setup Commands
```bash
# API setup
cd api
pip install pipenv
pipenv sync -d  # Install development dependencies

# Web setup  
cd web
corepack enable
yarn install --frozen-lockfile  # Use --immutable in newer versions
```

## Build, Test, and Lint Commands

### API (Python/FastAPI)
```bash
cd api

# Install dependencies
pipenv sync -d

# Linting (uses ruff)
make lint
# OR: pipenv run ruff check && pipenv run ruff format --check

# Formatting
make format  
# OR: pipenv run ruff check --fix && pipenv run ruff format

# Testing (36 tests)
make test
# OR: pipenv run python -m unittest

# Database migrations (requires PostgreSQL connection)
pipenv run alembic check
pipenv run alembic upgrade head
```

### Web (React/Vite)
```bash
cd web

# Install dependencies
corepack enable
yarn install --frozen-lockfile

# Linting (uses ESLint)
make lint
# OR: yarn lint

# Formatting
make format
# OR: yarn format  

# Testing (52 tests, 1 typically skipped)
make test
# OR: yarn test --run

# Building for production
make build
# OR: yarn build

# Development server
yarn dev  # Runs on port 3000 with API proxy
```

## Known Issues & Workarounds

### Python Version Compatibility
- **Issue**: Pipfile specifies Python 3.13, but most systems have 3.12
- **Workaround**: Use `pipenv --python python3.12 sync -d` to override version
- **Warning**: Pipenv will show version mismatch warnings but builds succeed

### Web Build Warnings
- **Issue**: Vite warns about chunks >500KB after minification
- **Status**: Known issue, not breaking - application builds and runs correctly
- **Details**: Main bundle is ~1.87MB, likely due to Material-UI and React dependencies

### Yarn Lockfile Commands
- **Issue**: `--frozen-lockfile` is deprecated
- **Current**: Use `--frozen-lockfile` (still works)
- **Future**: Migrate to `--immutable` when updating CI

### Database Requirements
- **Development**: SQLite (default, no setup needed)
- **Production**: PostgreSQL required for full feature set
- **CI Limitation**: Database check job disabled due to external dependency requirements

## Continuous Integration

The repository uses GitHub Actions with separate workflows:

### API CI (`.github/workflows/api-ci.yml`)
- **Triggers**: Changes to `api/**` or workflow file
- **Jobs**: lint, test, check-db (disabled)
- **Runtime**: Ubuntu latest with Python 3.13
- **Dependencies**: `pipenv sync -d`

### Web CI (`.github/workflows/web-ci.yml`)  
- **Triggers**: Changes to `web/**` or workflow file
- **Jobs**: lint, test, build
- **Runtime**: Ubuntu latest with Node.js LTS
- **Dependencies**: `corepack enable && yarn install --frozen-lockfile`

### Pre-commit Hooks
Configuration in `.pre-commit-config.yaml`:
- **check-yaml, end-of-file-fixer, trailing-whitespace** from pre-commit-hooks
- **ruff linting and formatting** for Python files in `api/`
- **Note**: Pre-commit must be installed separately: `pip install pre-commit && pre-commit install`

## Configuration Files

### Python/API Configuration
- **`api/Pipfile`**: Dependencies for packages, dev-packages, and prod-packages
- **`api/ruff.toml`**: Minimal ruff configuration for flake8-type-checking
- **`api/alembic.ini`**: Database migration configuration with PostgreSQL default
- **`api/Makefile`**: Build commands (lint, format, test)

### JavaScript/Web Configuration  
- **`web/package.json`**: Dependencies and npm scripts
- **`web/eslint.config.js`**: ESLint v9 flat config with React plugins
- **`web/vite.config.js`**: Build config with proxy setup for API during development
- **`web/vitest.config.js`**: Test configuration
- **`web/Makefile`**: Build commands (lint, format, test, build)

## Development Environment

### Local Development
```bash
# Start API server (port 8000)
cd api
pipenv run uvicorn chatbot.main:app --reload

# Start web dev server (port 3000)  
cd web
yarn dev  # Includes API proxy configuration
```

### Docker Development
- **Dockerfile**: Multi-stage build (frontend builder → backend builder → final app)
- **Dev Container**: VS Code devcontainer with Python 3.13 base image
- **Compose**: Simple service definition in `.devcontainer/docker-compose.yml`

### Environment Variables
Key configuration via environment variables (see README for full list):
- **`LLM`**: ChatOpenAI instance configuration (required)
- **`DB_PRIMARY_URL`**: Database connection (default: SQLite)
- **`SERP_API_KEY`**: Web search tool API key (optional)
- **`OPENMETEO_API_KEY`**: Weather tool API key (optional)

## Testing Strategy

### API Tests
- **Location**: `api/tests/`
- **Framework**: Python unittest
- **Coverage**: Agent, LLM client, schemas, configuration
- **Command**: `make test` or `pipenv run python -m unittest`
- **Duration**: ~0.2 seconds, 36 tests

### Web Tests  
- **Location**: `web/src/**/*.test.js(x)`
- **Framework**: Vitest with React Testing Library
- **Coverage**: Components, contexts, utilities
- **Command**: `make test` or `yarn test --run`
- **Duration**: ~4 seconds, 52 tests (1 typically skipped)

## Deployment

### Container Build
```bash
# Build multi-stage Docker image
docker build -t chatbot .

# Run container
docker run -p 8000:8000 chatbot
```

### Kubernetes Deployment
```bash
# Vanilla Kubernetes
kubectl kustomize manifests/overlays/istio | kubectl apply -f -

# Knative Service (auto-scaling)
kubectl kustomize manifests/overlays/knative-serving | kubectl apply -f -
```

## Key Source Files

### API Structure
- **`api/chatbot/main.py`**: FastAPI application entry point
- **`api/chatbot/config.py`**: Configuration management
- **`api/chatbot/agent/`**: LangGraph agent implementation
- **`api/chatbot/routers/`**: API endpoint definitions
- **`api/chatbot/tools/`**: External tool integrations (web search, weather)

### Web Structure
- **`web/src/main.jsx`**: React application entry point
- **`web/src/App.jsx`**: Main application component
- **`web/src/components/`**: Reusable UI components
- **`web/src/contexts/`**: React context providers
- **`web/src/routes/`**: Application routing

## Agent Instructions

**ALWAYS follow these practices when working in this repository:**

1. **Run builds in correct order**: Install dependencies before linting/testing/building
2. **Use pipenv for Python**: Never use pip directly for this project's dependencies
3. **Enable corepack for yarn**: Always run `corepack enable` before yarn commands
4. **Work in appropriate directories**: `cd api/` for backend changes, `cd web/` for frontend
5. **Test incrementally**: Run tests after each significant change to catch issues early
6. **Respect the architecture**: Backend changes in `/api`, frontend in `/web`, deployments in `/manifests`

**Trust these instructions and avoid unnecessary exploration unless:**
- Instructions appear outdated or incorrect
- Encountering unexpected build failures not covered here
- Working on areas not documented in these instructions

When in doubt, refer to the Makefiles (`api/Makefile`, `web/Makefile`) for the canonical build commands.