# Implementation Plan: Phase II - Fullstack Todo Application

**Branch**: `001-fullstack-todo` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fullstack-todo/spec.md`

---

## Summary

Evolve the Phase I in-memory CLI todo app into a persistent full-stack web application. The system will consist of a FastAPI backend with SQLModel ORM connected to Neon Serverless PostgreSQL, and a Next.js frontend with App Router. All CRUD operations (create, read, update, delete, toggle) will be exposed via REST API and consumed by the React-based web UI.

---

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript/Node 18+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, asyncpg (backend); Next.js 14+, React 18+ (frontend)
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (separate frontend + backend)
**Performance Goals**: Page load < 3s, API response < 2s, 10 concurrent users
**Constraints**: No authentication, no containerization, local development only
**Scale/Scope**: Single-user context, ~100 todos maximum

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Phase I Status | Phase II Change | Justification |
|-----------|----------------|-----------------|---------------|
| I. In-Memory Only | Compliant | **SUPERSEDED** | Phase II explicitly requires database persistence |
| II. Single Module | Compliant | **SUPERSEDED** | Full-stack requires separate backend/frontend |
| III. Dataclass-Driven | Compliant | **EVOLVED** | SQLModel uses Pydantic models (similar pattern) |
| IV. CLI-First | Compliant | **SUPERSEDED** | Web UI is Phase II requirement |
| V. Input Validation | Compliant | **MAINTAINED** | Pydantic/SQLModel validation + frontend validation |
| VI. Simplicity Over Features | Compliant | **MAINTAINED** | Minimal styling, no extra features |

**Gate Status**: PASS with justified evolution

**Note**: Phase II intentionally evolves beyond Phase I constitution. The constitution represents Phase I constraints. Phase II introduces new architectural requirements (persistence, web UI) that supersede Phase I principles I, II, and IV while maintaining the spirit of validation (V) and simplicity (VI).

---

## Project Structure

### Documentation (this feature)

```text
specs/001-fullstack-todo/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup guide
├── contracts/
│   └── openapi.yaml     # API contract
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI application entry point
├── database.py          # Database connection and session management
├── models.py            # SQLModel definitions (Todo, TodoCreate, etc.)
├── routers/
│   └── todos.py         # Todo API endpoints
├── services/
│   └── todo_service.py  # Business logic layer
├── .env                 # Environment variables (DATABASE_URL)
└── requirements.txt     # Python dependencies

frontend/
├── app/
│   ├── layout.tsx       # Root layout with metadata
│   ├── page.tsx         # Home page (todo list view)
│   └── globals.css      # Global styles (Tailwind)
├── components/
│   ├── TodoList.tsx     # Todo list container
│   ├── TodoItem.tsx     # Single todo with toggle/edit/delete
│   └── TodoForm.tsx     # Create and edit form
├── lib/
│   └── api.ts           # API client (fetch wrapper)
├── types/
│   └── todo.ts          # TypeScript interfaces
├── .env.local           # Environment variables (API URL)
├── package.json         # Node dependencies
├── tailwind.config.js   # Tailwind configuration
└── tsconfig.json        # TypeScript configuration

tests/
├── backend/
│   ├── test_api.py      # API endpoint tests
│   └── test_service.py  # Service layer tests
└── frontend/
    └── components/      # Component tests
```

**Structure Decision**: Web application pattern selected (Option 2) because the feature explicitly requires separate frontend and backend with API-driven communication.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Next.js Frontend                        │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │  │
│  │  │ TodoList│  │TodoItem │  │TodoForm │  │   api.ts    │   │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘   │  │
│  │       └────────────┴────────────┴───────────────┘          │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (:8000)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Router Layer                            │  │
│  │  GET /api/todos    POST /api/todos    PUT /api/todos/{id}  │  │
│  │  DELETE /api/todos/{id}    PATCH /api/todos/{id}/toggle    │  │
│  └────────────────────────────┬──────────────────────────────┘  │
│                               │                                  │
│  ┌────────────────────────────▼──────────────────────────────┐  │
│  │                   Service Layer                            │  │
│  │  TodoService: create, get_all, get, update, delete, toggle │  │
│  └────────────────────────────┬──────────────────────────────┘  │
│                               │                                  │
│  ┌────────────────────────────▼──────────────────────────────┐  │
│  │                   SQLModel ORM                             │  │
│  │  Todo model ↔ PostgreSQL todos table                       │  │
│  └────────────────────────────┬──────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │ asyncpg + SSL
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Neon Serverless PostgreSQL                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  todos table: id, title, description, completed, created_at│  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Summary

| Method | Endpoint | Request Body | Response | Status |
|--------|----------|--------------|----------|--------|
| GET | /api/todos | - | Todo[] | 200 |
| POST | /api/todos | TodoCreate | Todo | 201 |
| GET | /api/todos/{id} | - | Todo | 200/404 |
| PUT | /api/todos/{id} | TodoUpdate | Todo | 200/404 |
| DELETE | /api/todos/{id} | - | - | 204/404 |
| PATCH | /api/todos/{id}/toggle | - | Todo | 200/404 |

Full contract: [contracts/openapi.yaml](./contracts/openapi.yaml)

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Database | Neon Serverless Postgres | User requirement, serverless scaling |
| ORM | SQLModel | FastAPI integration, Pydantic validation |
| Frontend framework | Next.js App Router | Modern React patterns, file routing |
| State management | useState + fetch | Simple CRUD, server as source of truth |
| Styling | Tailwind CSS | Utility-first, minimal overhead |
| ID format | UUID | Globally unique, no sequence guessing |
| Error handling | HTTP status codes + detail message | RESTful convention |

Full research: [research.md](./research.md)

---

## Complexity Tracking

> No violations requiring justification. Architecture follows minimal viable design for requirements.

---

## Related Artifacts

- [spec.md](./spec.md) - Feature specification
- [research.md](./research.md) - Technology research and decisions
- [data-model.md](./data-model.md) - Entity definitions and schemas
- [quickstart.md](./quickstart.md) - Development setup guide
- [contracts/openapi.yaml](./contracts/openapi.yaml) - OpenAPI specification

---

## Next Steps

Run `/sp.tasks` to generate implementation tasks based on this plan.
