# Desktop Todo Constitution

## Core Principles

### I. Storage Strategy
**Phase I (CLI)**: In-memory only. Data ephemeral.
**Phase II+ (Fullstack)**: PostgreSQL via external provider (Neon). No in-cluster database.
**Phase V+ (Event-Driven)**: Event sourcing via Dapr pub/sub to Kafka. At-least-once delivery.

### II. Architecture Evolution
**Phase I**: Single Python module (`todo.py`).
**Phase II**: Multi-tier fullstack (FastAPI backend, Next.js frontend).
**Phase III**: AI agent integration via MCP server.
**Phase IV**: Containerized microservices (Docker, Kubernetes, Helm).
**Phase V**: Event-driven architecture (Kafka broker, Dapr sidecars).

### III. Dataclass-Driven Models
All data models implemented as Python dataclasses or Pydantic models. Immutable where possible, with clear field definitions and type hints. Event schemas follow CloudEvents specification.

### IV. Interface Strategy
**Phase I**: CLI-first (console menu system).
**Phase II+**: REST API primary interface. Web UI for user interaction.
**Phase V+**: Event publishing via Dapr pub/sub. Synchronous API for commands, asynchronous events for state changes.

### V. Input Validation
All user input validated before processing. Empty inputs rejected. Invalid IDs handled gracefully. API requests validated via Pydantic. Events validated against schema.

### VI. Simplicity Over Features
YAGNI principles enforced. No premature abstractions. Features added only when explicitly required by specification. Complexity justified in plan.md Complexity Tracking section.

### VII. Event-Driven Principles (Phase V+)
- **Decoupling**: Services communicate via events, not direct calls where possible.
- **Idempotency**: Event handlers must be idempotent (at-least-once delivery).
- **Schema Evolution**: Events versioned; consumers handle unknown fields gracefully.
- **No Direct Broker Access**: Application code uses Dapr pub/sub, never Kafka client directly.

## Constraints

- Python 3.11+ for backend services
- Node.js 20+ for frontend
- Kubernetes 1.27+ for orchestration
- Dapr 1.12+ for building blocks (pub/sub, state, service invocation)
- Kafka for event broker (via Dapr, no direct client)
- PostgreSQL via Neon (external, no in-cluster database)
- Generated via Claude Code (no manual coding)

## Development Workflow

1. Specification defined in `specs/<feature>/spec.md`
2. Plan created via `/sp.plan` before implementation
3. Tasks generated via `/sp.tasks`
4. Implementation follows spec exactly
5. Changes require spec update first
6. Event schemas in `contracts/events/`

## Governance

Constitution defines project boundaries. All features must align with core principles. Amendments require explicit user approval. Phase-specific principles apply only to that phase and later.

### VIII. Tooling and Agent Infrastructure
**AGENTS.md**: Project root. Cross-agent authority loaded by Claude Code via `@AGENTS.md` shim in `CLAUDE.md`.
**MCP Server**: `scripts/speckit_mcp/server.py`. Auto-discovers `.claude/commands/`. Registered via `.mcp.json`.
**Commands**: All 13 files in `.claude/commands/` define the SDD workflow. Agents MUST use these rather than ad-hoc implementations.

**Version**: 2.1.0 | **Ratified**: 2026-01-21 | **Last Amended**: 2026-02-18

## Amendment History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-21 | Initial constitution for CLI todo app |
| 2.0.0 | 2026-01-23 | Amended for Phase V event-driven architecture (Kafka + Dapr) |
| 2.1.0 | 2026-02-18 | Added Section VIII (Tooling) — AGENTS.md pattern + MCP server |
