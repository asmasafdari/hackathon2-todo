# Research: Phase II - Fullstack Todo Application

**Feature**: 001-fullstack-todo
**Date**: 2026-01-21
**Status**: Complete

---

## Technology Stack Decisions

### 1. Backend Framework: FastAPI

**Decision**: Use FastAPI as the backend framework

**Rationale**:
- Native async support for database operations
- Automatic OpenAPI documentation generation
- Pydantic integration for request/response validation
- Excellent performance characteristics
- Native support for SQLModel ORM

**Alternatives Considered**:
- Flask: More mature but lacks native async, requires extensions for validation
- Django REST Framework: Heavier, includes features not needed (admin, auth)

---

### 2. ORM: SQLModel

**Decision**: Use SQLModel for database operations

**Rationale**:
- Created by FastAPI author, seamless integration
- Combines SQLAlchemy ORM with Pydantic validation
- Single model definition serves both database and API schema
- Type hints throughout
- Supports async operations with asyncpg

**Alternatives Considered**:
- SQLAlchemy alone: Requires separate Pydantic models for API
- Tortoise ORM: Less mature, smaller ecosystem

---

### 3. Database: Neon Serverless Postgres

**Decision**: Use Neon as the PostgreSQL provider

**Rationale**:
- Serverless architecture (scale to zero)
- Standard PostgreSQL compatibility
- Connection pooling built-in
- Free tier available for development
- Branching support for development workflows

**Connection Strategy**:
- Use `asyncpg` driver for async operations
- Connection string from environment variable `DATABASE_URL`
- Connection pooling via Neon's proxy

**Alternatives Considered**:
- Local PostgreSQL: Requires installation, not serverless
- Supabase: More features than needed, adds complexity

---

### 4. Frontend Framework: Next.js (App Router)

**Decision**: Use Next.js 14+ with App Router

**Rationale**:
- Modern React patterns (Server Components, Server Actions)
- Built-in API route support (though using separate FastAPI backend)
- File-based routing simplifies structure
- TypeScript support out of the box
- Good developer experience

**Alternatives Considered**:
- Vite + React: Requires more setup for routing, SSR
- Create React App: Deprecated, no SSR

---

### 5. Styling: Tailwind CSS (Minimal)

**Decision**: Use Tailwind CSS with minimal styling

**Rationale**:
- Utility-first approach speeds development
- No component library lock-in
- Small bundle size with purging
- Good defaults for spacing, colors

**Styling Scope**:
- Basic layout (flexbox, grid)
- Simple form styling
- Status indicators (completed vs pending)
- Error/success states

**Alternatives Considered**:
- Plain CSS: More verbose, harder to maintain consistency
- CSS Modules: Good but slower for rapid prototyping

---

### 6. API Communication Pattern

**Decision**: REST API with JSON payloads

**Rationale**:
- Simple and well-understood
- Matches FastAPI's strengths
- No additional dependencies (vs GraphQL)
- Cacheable responses

**Endpoints Design**:
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/todos | List all todos |
| POST | /api/todos | Create new todo |
| PUT | /api/todos/{id} | Update todo |
| DELETE | /api/todos/{id} | Delete todo |
| PATCH | /api/todos/{id}/toggle | Toggle completion |

**Alternatives Considered**:
- GraphQL: Overkill for simple CRUD
- tRPC: Requires both ends in TypeScript

---

### 7. UUID Generation

**Decision**: Generate UUIDs server-side using Python's `uuid4()`

**Rationale**:
- Globally unique without coordination
- No sequential ID guessing
- PostgreSQL native UUID support
- SQLModel/SQLAlchemy handles UUID type

**Alternatives Considered**:
- Auto-increment integers: Sequential, predictable
- Client-generated UUIDs: Trust issues, validation needed

---

### 8. Error Handling Strategy

**Decision**: Structured error responses with HTTP status codes

**Response Format**:
```json
{
  "detail": "Human-readable error message"
}
```

**Status Codes**:
- 200: Success (GET, PUT, PATCH)
- 201: Created (POST)
- 204: No Content (DELETE)
- 400: Bad Request (validation errors)
- 404: Not Found (invalid ID)
- 500: Internal Server Error

---

### 9. Frontend State Management

**Decision**: React useState + fetch API (no external state library)

**Rationale**:
- Simple todo list doesn't require complex state
- Server is source of truth
- Refetch after mutations ensures consistency
- Reduces dependencies

**Alternatives Considered**:
- React Query/TanStack Query: Good but adds dependency for simple case
- Redux: Overkill for this scope
- Zustand: Good but unnecessary

---

### 10. Development Environment

**Decision**: Separate dev servers with CORS configuration

**Backend**: `uvicorn main:app --reload --port 8000`
**Frontend**: `npm run dev` (port 3000)

**CORS Configuration**:
- Allow origin: `http://localhost:3000`
- Allow methods: GET, POST, PUT, PATCH, DELETE
- Allow headers: Content-Type

---

## Unresolved Items

None - all technical decisions documented.

---

## References

- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLModel Documentation: https://sqlmodel.tiangolo.com
- Neon Documentation: https://neon.tech/docs
- Next.js App Router: https://nextjs.org/docs/app
- Tailwind CSS: https://tailwindcss.com/docs
