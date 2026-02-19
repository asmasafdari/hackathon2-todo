# Todo Platform

A full-stack, AI-agent-enabled todo application built through 5 progressive development phases — from a CLI console app to a cloud-native, event-driven platform with an AI chatbot.

---

## Deployed Application Links

| Phase | Component | URL |
|-------|-----------|-----|
| II — Fullstack | Frontend (Vercel) | _Deploy via [Vercel instructions](#phase-ii-deployment)_ |
| II — Fullstack | Backend API | _Deploy via [Railway/Render instructions](#phase-ii-deployment)_ |
| III–V — AI Chatbot | Chatbot UI | _Deploy via [chatbot instructions](#phase-iiiv-chatbot-deployment)_ |
| IV — Cloud Native | Minikube (local) | See [Minikube setup](#phase-iv-minikube-local-kubernetes) |
| V — Event-Driven | DigitalOcean (DOKS) | _Deploy via [DOKS instructions](#phase-v-digitalocean-deployment)_ |

> **Note:** Run `./scripts/doks-deploy.sh` to provision DigitalOcean infrastructure and obtain the live URL. See [Phase V deployment](#phase-v-digitalocean-deployment).

---

## Development Phases

| Phase | Feature | Tech Stack | Status |
|-------|---------|-----------|--------|
| **I** | Console App | Python CLI | ✅ Complete |
| **II** | Fullstack Web App | FastAPI + Next.js + PostgreSQL | ✅ Complete (60/61 tasks) |
| **III** | AI Agent + MCP | OpenAI Agents SDK + FastMCP | ✅ P1 Complete |
| **IV** | Cloud Native | Docker + Kubernetes + Helm | ✅ Containerized |
| **V** | Event-Driven + Chatbot | Kafka + Dapr + AI Chatbot | 🔄 In Progress |

---

## Project Structure

```
desktop-todo/
│
├── CLAUDE.md                    # Claude Code agent instructions (SDD workflow)
├── AGENTS.md                    # Cross-agent authority for all AI agents
├── .mcp.json                    # SpecKit MCP server registration
│
├── backend/                     # Phase II–V: FastAPI backend service
│   ├── main.py                  # FastAPI app entry point + CORS
│   ├── database.py              # Async SQLModel + PostgreSQL/SQLite
│   ├── dependencies/            # Auth + DB dependency injection
│   ├── models/                  # Pydantic/SQLModel data models
│   │   └── todo.py              # Todo model (priority, tags, due_date, recurrence)
│   ├── routers/                 # API route handlers
│   │   ├── todos.py             # CRUD + filter/sort/search endpoints
│   │   ├── auth.py              # Authentication routes
│   │   ├── chat.py              # AI chat endpoint
│   │   ├── websocket.py         # WebSocket real-time sync
│   │   └── dapr_subscriptions.py# Dapr event subscription handler
│   ├── services/                # Business logic layer
│   │   ├── todo_service.py      # Todo CRUD + filter/search/sort
│   │   ├── chat_service.py      # AI chat service
│   │   ├── event_publisher.py   # Dapr pub/sub event publishing
│   │   ├── notification_service.py  # Kafka reminder consumer
│   │   ├── recurring_task_service.py# Auto-recurring task logic
│   │   └── reminder_scheduler.py    # Dapr Jobs API scheduler
│   ├── events/                  # Kafka event schemas (CloudEvents)
│   ├── migrations/              # Alembic database migrations
│   ├── tests/                   # Backend test suite
│   ├── Dockerfile               # Multi-stage production build
│   └── requirements.txt         # Python dependencies
│
├── frontend/                    # Phase II–IV: Next.js web frontend
│   ├── app/                     # Next.js 14 App Router
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Todo list page
│   ├── components/              # React UI components
│   │   ├── TodoItem.tsx         # Todo card (priority badge, tags, due date)
│   │   └── NavBar.tsx           # Navigation bar
│   ├── lib/
│   │   └── api.ts               # Type-safe API client
│   ├── types/
│   │   └── todo.ts              # TypeScript types (Todo, TodoCreate, TodoUpdate)
│   ├── Dockerfile               # Multi-stage Next.js build
│   └── package.json
│
├── agent/                       # Phase III: AI Agent (OpenAI + MCP)
│   ├── mcp_server.py            # FastMCP tool definitions (14 tools)
│   ├── agent.py                 # OpenAI Agents SDK setup + system prompt
│   ├── cli.py                   # Interactive CLI interface
│   └── config.py                # Settings (API key, backend URL)
│
├── chatbot-frontend/            # Phase V: Next.js AI chatbot UI
│   ├── app/                     # App Router pages
│   └── components/
│       └── ChatInterface.tsx    # Chat window with todo display
│
├── activity_logger/             # Phase V: Kafka activity log consumer
│
├── charts/                      # Phase IV–V: Kubernetes Helm charts
│   ├── todo-platform/           # Phase II–IV umbrella chart (backend + frontend + mcp)
│   ├── backend/                 # Phase V backend Helm chart
│   ├── chatbot-frontend/        # Phase V chatbot Helm chart
│   ├── notification-service/    # Phase V notification Helm chart
│   └── recurring-task-service/  # Phase V recurring task Helm chart
│
├── k8s/                         # Phase IV–V: Raw Kubernetes manifests
│   └── kafka/                   # Strimzi Kafka + topic manifests
│
├── dapr/                        # Phase V: Dapr component configurations
│   └── components/
│       ├── kafka-pubsub.yaml    # Kafka pub/sub component
│       ├── statestore.yaml      # PostgreSQL state store
│       └── kubernetes-secrets.yaml
│
├── scripts/                     # Deployment and utility scripts
│   ├── speckit_mcp/             # SpecKit MCP server
│   │   ├── server.py            # MCP prompt server (13 prompts auto-discovered)
│   │   └── requirements.txt
│   ├── deploy-minikube.sh       # Phase IV: Minikube full-stack deploy
│   ├── deploy-chatbot-minikube.sh # Phase V: Chatbot Minikube deploy
│   └── doks-deploy.sh           # Phase V: DigitalOcean DOKS deploy
│
├── specs/                       # Spec-Driven Development artifacts
│   ├── overview.md              # Project evolution overview
│   ├── 001-fullstack-todo/      # Phase II specifications
│   ├── 002-ai-agent-mcp/        # Phase III specifications
│   ├── 003-cloud-native-k8s/    # Phase IV specifications
│   ├── 004-event-driven-kafka/  # Phase V specifications
│   └── 005-todo-ai-chatbot/     # Phase V chatbot specifications
│
├── history/                     # Prompt History Records + ADRs
│   ├── prompts/                 # PHR files per feature
│   └── adr/                     # Architecture Decision Records
│
├── .claude/
│   └── commands/                # 13 SpecKit SDD command files
├── .specify/
│   ├── memory/constitution.md   # Project principles (v2.1.0)
│   └── templates/               # PHR, spec, plan, ADR templates
│
├── docker-compose.yml           # Full stack Docker Compose
├── .env.example                 # Environment variable template
└── .mcp.json                    # MCP server config for Claude Code
```

---

## Specifications (`/specs`)

This project follows **Spec-Driven Development (SDD)**. Every feature is specified before implementation.

```
specs/
├── overview.md                  # High-level project evolution
│
├── 001-fullstack-todo/          # Phase II: Persistent Fullstack Web App
│   ├── spec.md                  # 5 user stories (view, create, toggle, update, delete)
│   ├── plan.md                  # FastAPI + Next.js + Neon PostgreSQL architecture
│   ├── tasks.md                 # 61 tasks (60 complete ✅)
│   ├── data-model.md            # Todo entity model
│   ├── research.md              # Tech choices + tradeoffs
│   ├── quickstart.md            # Phase II quick start
│   ├── contracts/openapi.yaml   # REST API OpenAPI spec
│   └── checklists/requirements.md
│
├── 002-ai-agent-mcp/            # Phase III: AI Agent + MCP Server
│   ├── spec.md                  # 6 user stories (NL creation, operations, summarization...)
│   ├── plan.md                  # OpenAI Agents SDK + FastMCP architecture
│   ├── tasks.md                 # 51 tasks (P1 complete ✅)
│   ├── data-model.md            # Agent + message models
│   ├── research.md              # OpenAI Agents SDK evaluation
│   ├── contracts/mcp-tools.json # MCP tool definitions
│   └── contracts/agent-config.json
│
├── 003-cloud-native-k8s/        # Phase IV: Container + Kubernetes Deployment
│   ├── spec.md                  # 6 user stories (containerize, health, Helm deploy...)
│   ├── plan.md                  # Docker + Kubernetes + Helm architecture
│   ├── tasks.md                 # 57 tasks (~30 complete)
│   ├── contracts/helm-values-schema.json
│   └── contracts/health-endpoints.json
│
├── 004-event-driven-kafka/      # Phase V: Event-Driven Architecture
│   ├── spec.md                  # 6 user stories (event publishing, Dapr, Kafka...)
│   ├── plan.md                  # Kafka + Dapr pub/sub architecture
│   ├── tasks.md                 # 62 tasks
│   ├── ARCHITECTURE.md          # Detailed event-driven design
│   ├── SETUP.md                 # Kafka + Dapr local setup
│   └── contracts/events/        # CloudEvents schemas (created, updated, completed...)
│
└── 005-todo-ai-chatbot/         # Phase V: AI Chatbot Frontend
    ├── spec.md                  # 6 user stories (chat tasks, conversation context...)
    ├── plan.md                  # Next.js chatbot + MCP server architecture
    ├── tasks.md                 # T033–T106 task list
    ├── contracts/chat-api.yaml  # Chat API specification
    └── contracts/mcp-tools.yaml # MCP tools for chatbot
```

---

## Claude Code Instructions (`CLAUDE.md`)

`CLAUDE.md` configures Claude Code's behavior for this project. Key directives:

- Uses **Spec-Driven Development** — spec → plan → tasks → implement
- All 13 SDD commands in `.claude/commands/` define the workflow
- PHR (Prompt History Record) created after every substantive change
- ADR suggestions for significant architectural decisions
- SpecKit MCP server auto-loaded via `.mcp.json`

See `AGENTS.md` for the cross-agent authority reference (loaded automatically via `@AGENTS.md`).

---

## Technology Stack

| Layer | Phase | Technology |
|-------|-------|------------|
| **CLI** | I | Python 3.11, in-memory data |
| **Backend API** | II+ | FastAPI, SQLModel, Uvicorn, Alembic |
| **Database** | II+ | PostgreSQL (Neon) / SQLite |
| **Frontend** | II+ | Next.js 14, React 18, Tailwind CSS, TypeScript |
| **AI Agent** | III+ | OpenAI Agents SDK, FastMCP |
| **Chatbot UI** | V | Next.js 14, WebSocket, Server-Sent Events |
| **Containerization** | IV+ | Docker, multi-stage builds |
| **Orchestration** | IV+ | Kubernetes, Helm 3 |
| **Event Bus** | V | Apache Kafka (via Strimzi), Dapr pub/sub |
| **Scheduling** | V | Dapr Jobs API |
| **CI/CD** | V | GitHub Actions |

---

## Environment Variables

**Root** (`.env`):
```bash
# Copy from .env.example
DATABASE_URL=postgresql://user:password@host/db?sslmode=require
OPENAI_API_KEY=sk-...
TODO_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`backend/.env`):
```bash
DATABASE_URL=postgresql://user:password@host/db?sslmode=require
# Leave empty to use SQLite (local dev)
```

**Agent** (`agent/.env`):
```bash
OPENAI_API_KEY=sk-your-key-here
TODO_API_BASE_URL=http://localhost:8000
```

**Frontend** (`frontend/.env`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Local Development

```bash
# Terminal 1: Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install && npm run dev

# Terminal 3: AI Agent CLI
cd agent
pip install -r requirements.txt
python -m cli
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

---

## Deployment

### Phase II Deployment

**Frontend → Vercel**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from frontend/
cd frontend
vercel

# Set environment variable in Vercel dashboard:
# NEXT_PUBLIC_API_URL = <your backend URL>
```

After deployment, Vercel provides a URL like `https://your-project.vercel.app`.

**Backend API → Railway (recommended)**

1. Push repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select `backend/` as root directory
4. Set `DATABASE_URL` environment variable (use Neon PostgreSQL)
5. Railway provides a URL like `https://your-project.up.railway.app`

**Backend API → Render (alternative)**

```bash
# render.yaml already included — connect repo at render.com
# Set DATABASE_URL in Render dashboard environment variables
```

> Once deployed, update `NEXT_PUBLIC_API_URL` in Vercel to point to your backend URL.

---

### Phase III–V Chatbot Deployment

**Docker Compose (local)**

```bash
# Full stack including chatbot
docker compose up -d

# Access chatbot at:
# http://localhost:3001
```

**Kubernetes (chatbot only)**

```bash
# Quick deploy
./scripts/deploy-chatbot-minikube.sh

# Manual Helm deploy
helm install chatbot charts/chatbot-frontend \
  --set backend.url=http://backend:8000 \
  --namespace todo --create-namespace
```

---

### Phase IV: Minikube (Local Kubernetes)

**Prerequisites:** Docker, Minikube, Helm 3, kubectl

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g
minikube addons enable ingress

# 2. Build images in Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t todo-backend:latest backend/
docker build -t todo-frontend:latest frontend/
docker build -t todo-mcp:latest agent/

# 3. Create secrets file (never commit this)
cat > charts/todo-platform/values-secrets.yaml <<EOF
backend:
  env:
    DATABASE_URL: "your-database-url"
agent:
  env:
    OPENAI_API_KEY: "sk-your-key"
EOF

# 4. Deploy with Helm
helm install todo-platform charts/todo-platform \
  -f charts/todo-platform/values-secrets.yaml \
  --namespace todo --create-namespace

# 5. Access the app (choose one)
minikube tunnel                          # Then visit http://localhost
kubectl port-forward svc/frontend 3000:3000 -n todo   # Then visit http://localhost:3000
minikube service frontend -n todo        # Opens browser automatically
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full Minikube instructions including troubleshooting.

**Verify deployment:**
```bash
kubectl get pods -n todo
# All pods should show STATUS=Running

curl http://localhost:8000/api/health
# {"status":"healthy"}
```

---

### Phase V: DigitalOcean Deployment

**Prerequisites:** [doctl CLI](https://docs.digitalocean.com/reference/doctl/how-to/install/), Docker, Helm, kubectl

```bash
# 1. Authenticate
doctl auth init
# Paste your DigitalOcean API token

# 2. Run the automated deploy script
./scripts/doks-deploy.sh
# This will:
#   - Create a DOKS cluster (2 nodes, s-2vcpu-4gb, nyc3 region)
#   - Create a DigitalOcean Container Registry
#   - Build and push all Docker images
#   - Install NGINX Ingress Controller
#   - Deploy all services via Helm
#   - Output the external IP / URL

# 3. Get external URL after deploy
kubectl get svc ingress-nginx-controller -n ingress-nginx
# Note the EXTERNAL-IP — this is your DigitalOcean deployment URL

# 4. (Optional) Install Dapr on DOKS for Phase V event-driven features
dapr init -k
kubectl apply -f dapr/components/ -n todo
```

**Estimated cost:** ~$24/month (2 × s-2vcpu-4gb nodes)

See [DEPLOYMENT.md](DEPLOYMENT.md) for the complete DigitalOcean guide including SSL setup, image registry, and CI/CD.

---

## AI Agent Usage

**Interactive CLI (Phase III):**
```bash
cd agent && python -m cli

> add buy groceries with high priority
✓ Created "buy groceries" [high priority]

> show urgent tasks
Tasks (urgent):
1. [ ] Fix production bug (urgent)

> complete buy groceries
✓ "buy groceries" marked as complete.

> set task 1 due Friday
✓ Due date set: Fri Feb 21
```

**Chatbot UI (Phase V):**
```
You: Add a task to prepare the presentation
AI: ✓ Created "Prepare the presentation" — Task #12

You: Show me everything due this week
AI: You have 3 tasks due this week:
    • [high] Prepare the presentation — due Feb 21
    • [medium] Review PR #45 — due Feb 19
    • [low] Update docs — due Feb 22

You: Mark task 12 as urgent
AI: ✓ Priority updated to [urgent] for "Prepare the presentation"
```

**MCP Tools available (14 tools):**
`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`, `set_priority`, `add_tags`, `remove_tag`, `search_tasks`, `set_due_date`, `set_reminder`, `list_overdue`, `set_recurring`, `cancel_recurring`

---

## API Reference

Base URL: `http://localhost:8000` (local) or your deployed backend URL

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos` | List todos (with filter/sort/search params) |
| POST | `/api/todos` | Create todo |
| GET | `/api/todos/{id}` | Get single todo |
| PATCH | `/api/todos/{id}` | Update todo |
| DELETE | `/api/todos/{id}` | Delete todo |
| POST | `/api/todos/{id}/complete` | Toggle completion |
| GET | `/api/todos?priority=high` | Filter by priority |
| GET | `/api/todos?tags=work` | Filter by tag |
| GET | `/api/todos?search=groceries` | Search by keyword |
| GET | `/api/health` | Health check |
| POST | `/api/chat` | AI chat message |
| WS | `/ws` | WebSocket real-time sync |

Interactive docs: `http://localhost:8000/docs`

---

## Todo Data Model

```typescript
interface Todo {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: "low" | "medium" | "high" | "urgent" | null;
  tags: string[] | null;
  due_date: string | null;       // ISO 8601
  remind_at: string | null;      // ISO 8601
  recurrence_rule: string | null; // "daily" | "weekly" | "monthly"
  created_at: string;
}
```

---

## SpecKit MCP Server

All 13 SDD commands are available as MCP prompts via the SpecKit server:

```bash
# Install dependencies
pip install mcp[cli]>=1.0.0

# Start (Claude Code loads this automatically via .mcp.json)
python scripts/speckit_mcp/server.py
```

| Prompt | When to Use |
|--------|-------------|
| `sp-specify` | Define a new feature |
| `sp-plan` | Architect the implementation |
| `sp-tasks` | Break plan into testable tasks |
| `sp-implement` | Execute tasks |
| `sp-phr` | Record the exchange |
| `sp-adr` | Document an architectural decision |
| `sp-constitution` | Amend project principles |

---

## Development Status

### Phase I — Console App ✅
- Single `todo.py` module
- In-memory list with console menu
- CRUD via numbered menu choices

### Phase II — Fullstack Web ✅ (60/61 tasks)
- FastAPI REST API with SQLModel
- Next.js 14 App Router frontend
- PostgreSQL via Neon (SQLite for local dev)
- Priority, tags, due dates, recurrence
- Full CRUD with real-time UI updates

### Phase III — AI Agent ✅ P1 Complete
- OpenAI Agents SDK with 14 MCP tools
- Natural language → structured API calls
- Interactive CLI + single-command mode
- System prompt for task management vocabulary

### Phase IV — Cloud Native ✅ Containerized
- Docker multi-stage builds for all services
- Kubernetes deployment via Helm umbrella chart
- Health check endpoints (`/health`, `/ready`)
- Minikube local cluster verified

### Phase V — Event-Driven 🔄 In Progress
- Kafka event streaming (CloudEvents format)
- Dapr pub/sub, state store, secrets, Jobs API
- WebSocket real-time task sync
- Next.js AI chatbot frontend
- GitHub Actions CI/CD for DOKS
- Oracle Cloud OKE + DigitalOcean DOKS deployment

---

## Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # Must be 3.11+

# Verify database
cat backend/.env  # DATABASE_URL must be set or empty for SQLite
```

**Frontend build fails:**
```bash
cd frontend
npm run build 2>&1 | head -50  # Check TypeScript errors
```

**Pods stuck in Pending (Minikube):**
```bash
kubectl describe pod <pod-name> -n todo  # Check events section
kubectl get events -n todo --sort-by='.lastTimestamp'
```

**Dapr sidecar not injecting:**
```bash
kubectl get pods -n todo -o jsonpath='{.items[*].spec.containers[*].name}'
# Should include "daprd" container
```

**OpenAI agent not responding:**
```bash
curl http://localhost:8000/api/health
cd agent && python -c "from config import get_settings; print('Key:', bool(get_settings().openai_api_key))"
```

---

## Project Governance

This project uses **Spec-Driven Development (SDD)**:

1. Feature spec written in `specs/<feature>/spec.md`
2. Architecture plan in `specs/<feature>/plan.md`
3. Task list in `specs/<feature>/tasks.md`
4. Implementation references task IDs
5. PHR created after every exchange (`history/prompts/`)
6. ADRs for significant decisions (`history/adr/`)

**Constitution:** `.specify/memory/constitution.md` v2.1.0
**Commands:** 13 SDD commands in `.claude/commands/`
**MCP Server:** `scripts/speckit_mcp/server.py`

---

**Built with:** FastAPI · Next.js 14 · OpenAI Agents SDK · Kubernetes · Kafka · Dapr
**SDD:** Spec-Driven Development via SpecKit Plus
