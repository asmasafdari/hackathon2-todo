# Research: Todo AI Chatbot

**Date**: 2026-02-16
**Feature**: 005-todo-ai-chatbot

## R1: Existing Implementation Gap Analysis

**Decision**: Most backend and agent code already exists. Focus implementation on Docker containerization and chatbot-frontend completion.

**Findings**:

| Component | Status | Gap |
|-----------|--------|-----|
| Backend FastAPI | Built | CORS needs chatbot-frontend origin added |
| Database models (Todo, User, Conversation, Message) | Built | No schema changes needed |
| Chat router (POST /{user_id}/chat) | Built | Already matches spec |
| Conversation service | Built | Already persists messages |
| Chat service (OpenAI Agents SDK) | Built | Already integrates with agent |
| MCP server (5 tools) | Built | Matches spec exactly |
| Agent (system prompt + Runner) | Built | Comprehensive behavioral rules |
| Chatbot frontend | Partially built | Has ChatInterface, api.ts, page.tsx. Missing: package-lock, env setup |
| Docker | Not started | No Dockerfile, docker-compose, .dockerignore |
| Tests | Partial | Backend tests exist. No chatbot-frontend tests, no Docker integration tests |

**Rationale**: Avoid rebuilding what exists. Docker is the primary new deliverable. Chatbot frontend needs minor completion.

## R2: Docker Containerization Strategy

**Decision**: Multi-stage Docker builds with docker-compose for local development orchestration.

**Rationale**: Multi-stage builds keep images small. Docker Compose provides single-command startup per FR-014 and SC-006.

**Alternatives considered**:

| Option | Pros | Cons |
|--------|------|------|
| Single monolithic container | Simple | Can't scale services independently, large image |
| Docker Compose (multi-service) | Matches prod topology, scalable, standard | Slightly more config |
| Kubernetes only | Production-ready | Too complex for local dev |

**Design**:
- Backend Dockerfile: Python 3.11-slim, multi-stage (build + runtime)
- Chatbot-frontend Dockerfile: Node 20-alpine, multi-stage (deps + build + runtime)
- Agent: Runs as subprocess spawned by backend (MCP stdio), no separate container needed
- Database: PostgreSQL 16 container for local dev (Neon for production)
- docker-compose.yml: Orchestrates all services with health checks

## R3: MCP Server Architecture in Docker

**Decision**: Agent runs as a subprocess of the backend, NOT as a separate container.

**Rationale**: The MCP server communicates via stdio (stdin/stdout) with the OpenAI Agents SDK. The `MCPServerStdio` class spawns the MCP server as a child process. This is a fundamental design requirement of the MCP protocol for stdio transport - both must share the same process space.

**Alternatives considered**:

| Option | Pros | Cons |
|--------|------|------|
| Agent as subprocess (current) | Works with MCPServerStdio, simple | Agent code in backend container |
| Agent as separate container + HTTP | Independent scaling | Requires rewriting MCP transport from stdio to HTTP SSE, breaking change |
| Agent sidecar | Co-located | Still needs shared process for stdio |

**Implication**: The backend Dockerfile must include the agent directory and its dependencies.

## R4: Authentication Strategy for Docker

**Decision**: Keep Clerk authentication. For local Docker development, provide a bypass mode option.

**Rationale**: Clerk is already integrated in both backend and chatbot-frontend. Docker env vars inject Clerk keys. For pure local testing without Clerk, the chat endpoint already accepts `user_id` in the URL path.

**Alternatives considered**:

| Option | Pros | Cons |
|--------|------|------|
| Clerk (keep current) | Already built, production-ready | Requires Clerk account for any testing |
| Better Auth (spec says) | Open source, self-hosted | Would require rewriting auth layer |
| Auth bypass for Docker | Simplifies local dev | Less realistic testing |

**Decision**: Keep Clerk but document env var setup clearly in quickstart.

## R5: Frontend Technology Choice

**Decision**: Keep custom React chat interface (already built) instead of migrating to OpenAI ChatKit.

**Rationale**: The chatbot-frontend already has a working ChatInterface component with message rendering, tool call display, loading states, and auto-scroll. OpenAI ChatKit would be an additional dependency with uncertain maintenance and would require rewriting the existing UI. The current implementation fulfills all spec requirements (FR-009, SC-007).

**Alternatives considered**:

| Option | Pros | Cons |
|--------|------|------|
| Custom React (current) | Already built, full control, no external deps | Custom maintenance |
| OpenAI ChatKit | Official SDK, built-in features | Domain allowlist complexity, dependency risk, rewrite needed |

## R6: Database Strategy for Docker

**Decision**: Use PostgreSQL 16 container for local development. Neon for production (per constitution).

**Rationale**: Constitution mandates "PostgreSQL via Neon (external, no in-cluster database)" for production. For Docker local dev, a PostgreSQL container avoids requiring a Neon account for quick-start testing.

**Configuration**:
- Docker: `postgres:16-alpine` with health check
- Backend auto-detects `DATABASE_URL` format (existing code handles postgres:// → postgresql+asyncpg://)
- SQLite fallback still works when no DATABASE_URL set
