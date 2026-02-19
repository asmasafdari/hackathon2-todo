# Implementation Plan: Event-Driven Todo Platform (Kafka + Dapr)

**Branch**: `004-event-driven-kafka` | **Date**: 2026-01-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-event-driven-kafka/spec.md`

## Summary

Transform the existing fullstack Todo platform into an event-driven architecture using Apache Kafka as the message broker and Dapr as the abstraction layer. All todo state changes (create, update, complete, delete) emit domain events via Dapr pub/sub to Kafka topics. An activity logger service consumes events to provide an audit trail. Application code never interacts with Kafka directly—all pub/sub operations go through Dapr sidecars.

## Technical Context

**Language/Version**: Python 3.11 (backend, activity-logger), Node.js 20 (frontend)
**Primary Dependencies**: FastAPI 0.100+, Dapr SDK 1.12+, Pydantic 2.x, SQLModel, cloudevents-sdk
**Storage**: PostgreSQL (Neon) for todos and activity log entries
**Testing**: pytest (backend), pytest-asyncio (async tests), Dapr test containers
**Target Platform**: Kubernetes 1.27+ (Minikube for local dev)
**Project Type**: Multi-service event-driven architecture
**Performance Goals**: Event publishing <100ms p95, event processing <500ms p95
**Constraints**: No direct Kafka client usage, at-least-once delivery, idempotent consumers
**Scale/Scope**: Single replica per service (Phase V); event schema designed for future scaling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Storage Strategy | PASS | PostgreSQL via Neon + Kafka via Dapr (constitution v2.0.0 allows) |
| II. Architecture Evolution | PASS | Phase V permits event-driven architecture per amended constitution |
| III. Dataclass-Driven Models | PASS | Pydantic models for events, CloudEvents spec |
| IV. Interface Strategy | PASS | REST API + async events via Dapr pub/sub |
| V. Input Validation | PASS | Events validated against schema before publishing |
| VI. Simplicity Over Features | PASS | Only activity logger consumer; future consumers out of scope |
| VII. Event-Driven Principles | PASS | Dapr abstraction, idempotent handlers, schema versioning |

**Pre-Phase 0 Gate**: PASS (Constitution v2.0.0 amended for Phase V)

## Project Structure

### Documentation (this feature)

```text
specs/004-event-driven-kafka/
├── plan.md              # This file
├── research.md          # Phase 0: Dapr/Kafka patterns research
├── data-model.md        # Phase 1: Event schemas (CloudEvents)
├── quickstart.md        # Phase 1: Local development setup
├── contracts/           # Phase 1: Event schema definitions
│   └── events/          # CloudEvents JSON schemas
└── tasks.md             # Phase 2: Implementation tasks (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app with Dapr integration
├── models.py            # SQLModel entities (existing)
├── database.py          # Database connection (existing)
├── routers/
│   └── todos.py         # Todo CRUD endpoints (modify to emit events)
├── services/
│   ├── todo_service.py  # Todo business logic (existing)
│   └── event_publisher.py  # NEW: Dapr pub/sub event publishing
├── events/              # NEW: Event definitions
│   ├── __init__.py
│   ├── schemas.py       # CloudEvents Pydantic models
│   └── types.py         # Event type constants
└── tests/
    ├── test_events.py   # Event schema validation tests
    └── test_pubsub.py   # Dapr pub/sub integration tests

activity-logger/         # NEW: Event consumer service
├── main.py              # FastAPI app with Dapr subscription
├── models.py            # ActivityLog SQLModel
├── database.py          # Database connection
├── handlers/
│   └── event_handler.py # Idempotent event processing
├── routers/
│   └── logs.py          # Activity log query API
└── tests/
    └── test_handler.py  # Idempotency tests

agent/                   # Existing MCP agent (modify for events)
├── mcp_server.py        # MCP server (add event publishing)
└── ...

charts/todo-platform/    # Existing Helm chart (extend)
├── Chart.yaml
├── values.yaml          # Add Dapr/Kafka config
├── templates/
│   ├── dapr-components/ # NEW: Dapr component definitions
│   │   ├── pubsub.yaml  # Kafka pub/sub component
│   │   └── statestore.yaml # (optional for future)
│   └── ...
├── charts/
│   ├── backend/         # Existing (add Dapr annotations)
│   ├── frontend/        # Existing (unchanged)
│   ├── mcp/             # Existing (add Dapr annotations)
│   └── activity-logger/ # NEW: Activity logger subchart
└── ...
```

**Structure Decision**: Extend existing web application structure with new `activity-logger` service and `events/` module in backend. Helm chart extended with Dapr components and new subchart.

## Complexity Tracking

> No constitution violations. Phase V architecture explicitly permitted by constitution v2.0.0.

## Research Topics (Phase 0)

1. **Dapr Pub/Sub with Kafka**: Best practices for Python SDK, component configuration
2. **CloudEvents Specification**: Required/optional fields, data versioning strategies
3. **Idempotent Event Handlers**: Deduplication patterns (event ID tracking, upsert)
4. **Dapr on Kubernetes**: Sidecar injection, component deployment order
5. **Activity Log Schema**: Optimal indexing for time-range and type queries

## Architecture Overview

```
User / AI Agent
 → Frontend / MCP
   → FastAPI Backend
     → Dapr Sidecar
       → Kafka Pub/Sub
         → Event Consumers (Activity Logger)
```

## Dapr Design

### Building Blocks Used
- **Pub/Sub** (Kafka) - Primary event transport
- **Service Invocation** - Optional future use
- **Observability** - Metrics, traces via Dapr

### Pub/Sub Component
- Kafka-based pub/sub component
- **Topic per domain event type** (not single topic)

## Design Decisions (Phase 1)

1. **Event Schema Format**: CloudEvents v1.0 with JSON data payload
2. **Topic Structure**: Topic per event type (see Topics below)
3. **Consumer Persistence**: Store activity log in same Neon database (separate table)
4. **Idempotency Strategy**: Track processed event IDs in activity log table
5. **Error Handling**: Dead letter topics optional (Dapr retry handles most cases)

## Topics

| Topic | Event Type | Publisher |
|-------|------------|-----------|
| `todo.created` | `com.desktoptodo.todo.created` | Backend |
| `todo.updated` | `com.desktoptodo.todo.updated` | Backend |
| `todo.completed` | `com.desktoptodo.todo.completed` | Backend |
| `todo.deleted` | `com.desktoptodo.todo.deleted` | Backend |
| `agent.action` | `com.desktoptodo.agent.action.*` | MCP Server |

## Consumer Design

### Activity Logger Service
- **Stateless** - No local state, writes to PostgreSQL
- Subscribes to all topics above
- Writes structured logs with CloudEvents envelope
- Idempotent via processed_events table

## Failure Handling
- **Retry**: Via Dapr pub/sub retry policy
- **Dead-letter**: Optional, not required for Phase V
- **Idempotency**: Consumers must be idempotent (at-least-once delivery)

## Next Steps

After this plan is approved:
1. Run `/sp.plan` Phase 0 to generate `research.md` (resolve unknowns)
2. Run `/sp.plan` Phase 1 to generate `data-model.md`, `contracts/`, `quickstart.md`
3. Run `/sp.tasks` to generate implementation tasks
4. Create new branch `004-event-driven-kafka`
5. Implement tasks iteratively
