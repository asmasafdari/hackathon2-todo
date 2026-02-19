# Implementation Plan: Todo AI Chatbot

**Branch**: `005-todo-ai-chatbot` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-todo-ai-chatbot/spec.md`

## Summary

AI-powered chatbot for managing todos through natural language. The backend (FastAPI + OpenAI Agents SDK + MCP server), chat API, database models, conversation service, and chatbot frontend are **already implemented**. Phase V implements advanced features (recurring tasks, due dates, reminders, priorities, tags, search/filter/sort), event-driven architecture with Kafka and Dapr, local deployment on Minikube, and **production-grade cloud deployment on Oracle Cloud (OKE)**.

## Technical Context

**Language/Version**: Python 3.11+ (backend/agent), TypeScript/Node 20+ (frontend)
**Primary Dependencies**: FastAPI 0.109+, OpenAI Agents SDK 0.1+, MCP SDK 1.0+, Next.js 15, React 19, Clerk Auth
**Storage**: PostgreSQL via Neon (production), PostgreSQL 16 container (Docker dev), SQLite (local dev fallback)
**Testing**: pytest (backend/agent), manual E2E (frontend)
**Target Platform**: Docker Compose for local dev, Minikube for local K8s, Oracle Cloud OKE for production
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <3s response time for chat operations (SC-002)
**Constraints**: Stateless server (FR-008), MCP stdio transport requires agent as subprocess
**Scale/Scope**: Single-user local development, multi-user production

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Storage Strategy | PASS | PostgreSQL via Neon (production), PG container (Docker dev) |
| II. Architecture Evolution | PASS | Phase III AI agent + Phase IV containerization |
| III. Dataclass-Driven Models | PASS | SQLModel + Pydantic schemas (existing) |
| IV. Interface Strategy | PASS | REST API primary, chat UI for interaction |
| V. Input Validation | PASS | Pydantic validation on all endpoints (existing) |
| VI. Simplicity Over Features | PASS | Docker adds minimal complexity for significant onboarding value |
| VII. Event-Driven Principles | PASS | Dapr pub/sub events already integrated (optional, graceful degradation) |

**Constraints Check**:
- Python 3.11+: PASS (backend Dockerfile uses 3.11)
- Node.js 20+: PASS (frontend Dockerfile uses 20)
- PostgreSQL via Neon: PASS (production); Docker dev uses PG container
- Generated via Claude Code: PASS

**Post-Design Re-check**: All gates still pass. No violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/005-todo-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── chat-api.yaml    # OpenAPI contract for chat endpoints
│   └── mcp-tools.yaml   # MCP tools contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py                    # FastAPI app entry (existing)
├── database.py                # DB connection (existing)
├── Dockerfile                 # NEW: Multi-stage Python build
├── .dockerignore              # NEW: Docker ignore rules
├── requirements.txt           # Dependencies (existing)
├── models/                    # SQLModel models (existing)
│   ├── __init__.py
│   ├── todo.py
│   ├── user.py
│   ├── conversation.py
│   └── message.py
├── routers/                   # API routes (existing)
│   ├── todos.py
│   ├── chat.py
│   └── auth.py
├── services/                  # Business logic (existing)
│   ├── todo_service.py
│   ├── chat_service.py
│   ├── conversation_service.py
│   └── event_publisher.py
├── events/                    # CloudEvents schemas (existing)
├── migrations/                # Alembic migrations (existing)
├── dependencies/              # Auth dependencies (existing)
└── tests/                     # Pytest tests (existing)

agent/
├── agent.py                   # OpenAI Agents SDK setup (existing)
├── mcp_server.py              # MCP tools (existing)
├── config.py                  # Agent config (existing)
├── event_publisher.py         # Agent events (existing)
├── requirements.txt           # Agent dependencies (existing)
└── tests/                     # Agent tests (existing)

chatbot-frontend/
├── Dockerfile                 # NEW: Multi-stage Node build
├── .dockerignore              # NEW: Docker ignore rules
├── package.json               # Dependencies (existing)
├── app/
│   ├── layout.tsx             # Root layout (existing)
│   └── page.tsx               # Main page with ChatInterface (existing)
├── components/
│   └── ChatInterface.tsx      # Chat UI component (existing)
├── lib/
│   └── api.ts                 # API client (existing)
└── .env.example               # Environment template (existing)

# Root-level Docker files
docker-compose.yml             # NEW: Orchestrates all services
.dockerignore                  # NEW: Root-level ignore
```

**Structure Decision**: Web application with existing backend + chatbot-frontend. Agent runs as subprocess within backend container (MCP stdio transport requirement). Docker Compose at root level orchestrates backend, frontend, and database containers.

## Key Technical Decisions

### D1: Agent as Backend Subprocess (not separate container)

The MCP server uses stdio transport (`MCPServerStdio`). The OpenAI Agents SDK spawns the MCP server as a child process. This means the agent directory must be co-located with the backend in the same Docker image.

**Implementation**: Backend Dockerfile copies both `backend/` and `agent/` into the image. The `chat_service.py` already handles path resolution for both Docker and local environments (lines 11-14).

### D2: PostgreSQL Container for Local Dev

Docker Compose includes a PostgreSQL 16 container for local development. This avoids requiring a Neon account for quick-start testing while maintaining the same database engine.

**Implementation**: `docker-compose.yml` defines a `db` service with health check. Backend `DATABASE_URL` points to `db:5432`.

### D3: Multi-Stage Docker Builds

Both Dockerfiles use multi-stage builds to minimize image size:
- Backend: `python:3.11-slim` with pip install → copy to runtime
- Frontend: `node:20-alpine` with npm build → copy to runtime with standalone output

### D4: Keep Clerk Authentication

Clerk is already integrated in both backend (JWT verification) and frontend (@clerk/nextjs). Migrating to Better Auth (per original spec) would require significant rewriting with no functional benefit for this phase.

## Services Architecture

### Local (Docker Compose)

```
┌─────────────────────────────────────────────────────────┐
│                    docker-compose.yml                      │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   frontend    │  │   backend    │  │      db      │   │
│  │  (Next.js)   │  │  (FastAPI)   │  │ (PostgreSQL) │   │
│  │  Port 3001   │──│  Port 8000   │──│  Port 5432   │   │
│  │              │  │              │  │              │   │
│  └──────────────┘  │  ┌────────┐ │  └──────────────┘   │
│                     │  │ Agent  │ │                      │
│                     │  │ (MCP)  │ │                      │
│                     │  │subprocess│                      │
│                     │  └────────┘ │                      │
│                     └──────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### Production (Oracle Cloud OKE)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                         ORACLE CLOUD OKE CLUSTER                                      │
│                                                                                       │
│  ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐        │
│  │    Frontend Pod     │   │    Backend Pod      │   │  Notification Pod   │        │
│  │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │        │
│  │ │ Next  │ │ Dapr  │ │   │ │FastAPI│ │ Dapr  │ │   │ │Notif  │ │ Dapr  │ │        │
│  │ │  App  │◀┼▶Sidecar│ │   │ │+ MCP  │◀┼▶Sidecar│ │   │ │Service│◀┼▶Sidecar│ │        │
│  │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │        │
│  └──────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘        │
│             │                         │                         │                    │
│             └─────────────────────────┼─────────────────────────┘                    │
│                                       │                                              │
│                          ┌────────────▼────────────┐                                 │
│                          │    DAPR COMPONENTS      │                                 │
│                          │  ┌──────────────────┐   │                                 │
│                          │  │ pubsub.kafka     │───┼────▶ Strimzi Kafka (in-cluster) │
│                          │  ├──────────────────┤   │                                 │
│                          │  │ state.postgresql │───┼────▶ Neon DB                    │
│                          │  ├──────────────────┤   │                                 │
│                          │  │ scheduler        │   │  (Dapr Jobs API)                │
│                          │  ├──────────────────┤   │                                 │
│                          │  │ secretstores.k8s │   │  (API keys, credentials)        │
│                          │  └──────────────────┘   │                                 │
│                          └─────────────────────────┘                                 │
│                                                                                       │
│  CI/CD: GitHub Actions → OCIR (Oracle Container Registry) → Helm deploy to OKE      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Part A: Advanced Features

1. **Recurring Tasks, Due Dates & Reminders**
   - Implement all Advanced Level features (Recurring Tasks, Due Dates & Reminders)
   - Implement Intermediate Level features (Priorities, Tags, Search, Filter, Sort)

2. **Event-Driven Architecture with Kafka**
   - Add Kafka topics: `task-events`, `reminders`, `task-updates`
   - Implement event producers in Chat API / MCP Tools
   - Implement consumers: Recurring Task Service, Notification Service, Audit Service
   - Real-time sync across clients via WebSocket Service

3. **Dapr Integration**
   - Implement Dapr for distributed application runtime
   - Configure Dapr components: Pub/Sub (Kafka), State (PostgreSQL), Secrets (K8s)
   - Use Dapr Jobs API for scheduled reminders (exact-time triggers, no polling)
   - Service invocation for frontend → backend communication with built-in retries

### Part B: Local Deployment (Minikube)

4. **Deploy to Minikube**
   - Containerize all services (backend, chatbot-frontend, notification, recurring task)
   - Deploy using Helm charts
   - Deploy Kafka in-cluster using Strimzi operator or Redpanda

5. **Deploy Dapr on Minikube**
   - Install Dapr on Kubernetes (`dapr init -k`)
   - Configure Full Dapr: Pub/Sub, State, Bindings (cron), Secrets, Service Invocation
   - Apply Dapr component YAML configurations
   - Verify sidecar injection and inter-service communication

### Part C: Cloud Deployment (Oracle Cloud - OKE)

6. **Oracle Cloud Setup (Always Free Tier)**
   - Sign up at https://www.oracle.com/cloud/free/
   - Create OKE (Oracle Kubernetes Engine) cluster (4 OCPUs, 24GB RAM - always free)
   - Configure `kubectl` to connect with OKE cluster
   - No credit card charge after trial — best for learning without time pressure

7. **Deploy to OKE**
   - Deploy using Helm charts from Part B (Minikube)
   - Deploy Dapr on OKE with Full Dapr: Pub/Sub, State, Bindings (cron), Secrets, Service Invocation
   - Deploy Kafka using Strimzi operator on OKE (self-hosted in-cluster)
   - If Kafka access issues arise, swap to any other Dapr PubSub component (Dapr makes this a config change)

8. **CI/CD Pipeline**
   - Set up CI/CD pipeline using GitHub Actions
   - Automate Docker image builds and pushes to container registry (OCIR - Oracle Cloud Infrastructure Registry)
   - Automate Helm deployments to OKE on merge to main

9. **Monitoring & Logging**
   - Configure monitoring and logging on OKE
   - Set up Dapr observability (distributed tracing, metrics)
   - Health check endpoints for all services

10. **Verification & Documentation**
    - End-to-end smoke test: chat flow through OKE-deployed stack
    - README update with OKE deployment instructions and live URL
    - Document OKE cluster setup steps for reproducibility

## Complexity Tracking

No constitution violations. All changes are additive (new Docker files). Existing code requires only minor CORS configuration updates.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MCP stdio fails in Docker/K8s | Low | High | Agent path resolution already handles Docker (chat_service.py:11-14) |
| OpenAI API key not set | Medium | High | Clear env template, health check endpoint, K8s secrets |
| OKE free tier resource limits | Low | Medium | 4 OCPUs + 24GB RAM is sufficient; monitor resource usage |
| Kafka (Strimzi) resource overhead on OKE | Medium | Medium | Use single-replica ephemeral Kafka; Dapr allows PubSub swap if needed |
| Oracle Cloud account setup delays | Low | Low | Always-free tier has no credit card charge; straightforward signup |
| CI/CD pipeline failures | Medium | Medium | GitHub Actions with OCIR auth; test pipeline on Minikube first |
| Dapr sidecar injection issues on OKE | Low | Medium | Test on Minikube first; Dapr K8s docs well-documented |
