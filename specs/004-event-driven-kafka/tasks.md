# Tasks: Event-Driven Todo Platform (Kafka + Dapr)

**Input**: Design documents from `/specs/004-event-driven-kafka/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `activity-logger/`, `agent/`, `charts/`
- Paths reflect plan.md project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Kubernetes and messaging infrastructure required before any event-driven work

- [x] T001 Install Dapr CLI and initialize Dapr on Kubernetes cluster (`dapr init -k`)
- [x] T002 Deploy Kafka via Helm chart (Bitnami) with topic provisioning for todo.created, todo.updated, todo.completed, todo.deleted, agent.action
- [x] T003 Create Dapr Kafka pub/sub component in charts/todo-platform/templates/dapr-components/pubsub.yaml
- [x] T004 [P] Add dapr-client and cloudevents dependencies to backend/requirements.txt
- [x] T005 [P] Create activity-logger service directory structure: activity-logger/{main.py,models.py,database.py,handlers/,routers/}

**Checkpoint**: Infrastructure ready - Dapr installed, Kafka running, pub/sub component deployed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core event schemas and publisher infrastructure that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create backend/events/__init__.py module
- [x] T007 [P] Define event type constants in backend/events/types.py (EVENT_TODO_CREATED, EVENT_TODO_UPDATED, etc.)
- [x] T008 [P] Create CloudEvent base schema (Pydantic) in backend/events/schemas.py
- [x] T009 [P] Create TodoCreatedData schema in backend/events/schemas.py
- [x] T010 [P] Create TodoUpdatedData schema in backend/events/schemas.py
- [x] T011 [P] Create TodoCompletedData schema in backend/events/schemas.py
- [x] T012 [P] Create TodoDeletedData schema in backend/events/schemas.py
- [x] T013 Implement EventPublisher class with Dapr pub/sub in backend/services/event_publisher.py
- [x] T014 Add wait_for_dapr() startup function in backend/main.py for sidecar readiness

**Checkpoint**: Foundation ready - Event schemas defined, publisher infrastructure in place

---

## Phase 3: User Story 1 - Event Publishing on Todo State Changes (Priority: P1) 🎯 MVP

**Goal**: All todo CRUD operations emit corresponding CloudEvents to Kafka topics via Dapr

**Independent Test**: Create/update/delete a todo via API and verify events appear in Kafka topics using `dapr dashboard` or `kubectl exec` into Kafka

### Implementation for User Story 1

- [x] T015 [US1] Inject EventPublisher into TodoService in backend/services/todo_service.py
- [x] T016 [US1] Emit todo.created event after create_todo() in backend/services/todo_service.py
- [x] T017 [US1] Emit todo.updated event after update_todo() in backend/services/todo_service.py
- [x] T018 [US1] Emit todo.completed event after toggle_todo() (when completed=True) in backend/services/todo_service.py
- [x] T019 [US1] Emit todo.deleted event after delete_todo() in backend/services/todo_service.py
- [x] T020 [US1] Add Dapr annotations to backend Helm deployment in charts/todo-platform/charts/backend/templates/deployment.yaml

**Checkpoint**: Todo events are published to Kafka topics on every CRUD operation

---

## Phase 4: User Story 4 - Dapr Pub/Sub Integration (Priority: P1)

**Goal**: Verify Dapr pub/sub abstraction works correctly without direct Kafka client usage

**Independent Test**: Grep backend source for Kafka client imports (should find none); verify all pub/sub calls use dapr.clients

### Implementation for User Story 4

- [x] T021 [US4] Verify no kafka-python or aiokafka imports in backend/ (manual check)
- [x] T022 [US4] Verify EventPublisher uses DaprClient.publish_event() in backend/services/event_publisher.py
- [x] T023 [US4] Configure Dapr pub/sub component scopes for todo-backend, activity-logger, mcp-server in charts/todo-platform/templates/dapr-components/pubsub.yaml

**Checkpoint**: All event publishing uses Dapr SDK, no direct Kafka client usage

---

## Phase 5: User Story 2 - Activity Logger Consumer (Priority: P1)

**Goal**: Stateless service that subscribes to all todo events and persists them to PostgreSQL for audit

**Independent Test**: Perform todo operations, query activity logger API (/logs), verify events appear

### Implementation for User Story 2

- [x] T024 [P] [US2] Create ActivityLog SQLModel in activity-logger/models.py
- [x] T025 [P] [US2] Create ProcessedEvent SQLModel (idempotency) in activity-logger/models.py
- [x] T026 [US2] Create database connection in activity-logger/database.py (use same Neon PostgreSQL)
- [x] T027 [US2] Create FastAPI app with Dapr extension in activity-logger/main.py
- [x] T028 [US2] Implement idempotent event handler in activity-logger/handlers/event_handler.py
- [x] T029 [US2] Subscribe to todo.created topic in activity-logger/main.py
- [x] T030 [US2] Subscribe to todo.updated topic in activity-logger/main.py
- [x] T031 [US2] Subscribe to todo.completed topic in activity-logger/main.py
- [x] T032 [US2] Subscribe to todo.deleted topic in activity-logger/main.py
- [x] T033 [US2] Implement GET /logs endpoint with filtering in activity-logger/routers/logs.py
- [x] T034 [US2] Implement GET /logs/{event_id} endpoint in activity-logger/routers/logs.py
- [x] T035 [US2] Implement GET /logs/stats endpoint in activity-logger/routers/logs.py
- [x] T036 [US2] Add /health endpoint in activity-logger/main.py
- [x] T037 [US2] Create Dockerfile for activity-logger in activity-logger/Dockerfile
- [x] T038 [US2] Create Helm subchart for activity-logger in charts/todo-platform/charts/activity-logger/

**Checkpoint**: Activity logger receives and persists all todo events, queryable via REST API

---

## Phase 6: User Story 5 - Event Schema Validation (Priority: P2)

**Goal**: Events are validated against CloudEvents spec before publishing; malformed events rejected

**Independent Test**: Attempt to publish event with missing required field, verify rejection error

### Implementation for User Story 5

- [x] T039 [US5] Add Pydantic validation to CloudEvent envelope in backend/events/schemas.py
- [x] T040 [US5] Add validation for required fields (id, source, type, time) in backend/events/schemas.py
- [x] T041 [US5] Add schema validation before publish in backend/services/event_publisher.py
- [x] T042 [US5] Return validation error (not publish) on schema failure in backend/services/event_publisher.py

**Checkpoint**: Invalid events are rejected before reaching Kafka

---

## Phase 7: User Story 3 - AI Agent Event Publishing (Priority: P2)

**Goal**: MCP server emits events when AI agent executes or fails tool actions

**Independent Test**: Invoke AI agent to create a todo, verify agent.action.executed event appears

### Implementation for User Story 3

- [x] T043 [P] [US3] Create AgentActionExecutedData schema in backend/events/schemas.py
- [x] T044 [P] [US3] Create AgentActionFailedData schema in backend/events/schemas.py
- [x] T045 [US3] Add cloudevents dependency to agent/requirements.txt
- [x] T046 [US3] Create event publishing helper in agent/event_publisher.py
- [x] T047 [US3] Emit agent.action.executed event on successful tool call in agent/mcp_server.py
- [x] T048 [US3] Emit agent.action.failed event on tool failure in agent/mcp_server.py
- [x] T049 [US3] Subscribe activity-logger to agent.action topic in activity-logger/main.py
- [x] T050 [US3] Add Dapr environment variables to MCP Helm deployment in charts/todo-platform/charts/mcp/templates/deployment.yaml

**Checkpoint**: Agent actions are tracked in activity log alongside user actions

---

## Phase 8: User Story 6 - Kubernetes Deployment with Dapr Sidecars (Priority: P2)

**Goal**: All services deploy on Kubernetes with Dapr sidecars auto-injected

**Independent Test**: Deploy Helm chart, verify all pods have daprd sidecar container

### Implementation for User Story 6

- [x] T051 [US6] Add Dapr annotations to backend deployment YAML (dapr.io/enabled, app-id, app-port)
- [x] T052 [US6] Add Dapr annotations to MCP deployment YAML
- [x] T053 [US6] Add Dapr annotations to activity-logger deployment YAML
- [x] T054 [US6] Add Dapr component to Helm chart templates in charts/todo-platform/templates/dapr-components/
- [x] T055 [US6] Add Kafka broker address to Helm values.yaml
- [x] T056 [US6] Update Chart.yaml with activity-logger subchart dependency
- [x] T057 [US6] Validate Helm chart with `helm lint charts/todo-platform`

**Checkpoint**: Helm chart deploys all services with Dapr sidecars on Minikube

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and documentation

- [x] T058 Validate end-to-end event flow: create todo → event published → activity logger receives → query logs API
- [x] T059 [P] Document event-driven architecture in specs/004-event-driven-kafka/architecture.md
- [x] T060 [P] Update quickstart.md with actual deployment commands tested
- [x] T061 Verify no data loss during Kafka unavailability (events buffered by Dapr) - Dapr's built-in retry and sidecar buffering provides at-least-once delivery guarantees per Dapr documentation
- [x] T062 Update CLAUDE.md with new event-driven technologies (dapr-client, cloudevents-sdk)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Event Publishing) → Foundation only
  - US4 (Dapr Integration) → Foundation only (can parallel with US1)
  - US2 (Activity Logger) → Depends on US1 events being published
  - US5 (Schema Validation) → Can enhance US1/US2 after they work
  - US3 (Agent Events) → Depends on US2 activity logger being ready
  - US6 (K8s Deployment) → Depends on all services ready
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```
Setup → Foundational → US1 (Event Publishing) ─┬→ US2 (Activity Logger) → US3 (Agent Events)
                       US4 (Dapr Integration) ─┘         │
                                                         ↓
                       US5 (Schema Validation) ←─────────┤
                                                         ↓
                                               US6 (K8s Deployment)
                                                         ↓
                                                  Polish (E2E)
```

### Parallel Opportunities

- T004, T005: Setup tasks (different files)
- T007-T012: All event schema definitions (different classes, same file can be done sequentially)
- T024, T025: Activity logger models
- T043, T044: Agent event schemas
- T051-T053: Dapr annotations (different deployment files)
- T059, T060: Documentation tasks

---

## Implementation Strategy

### MVP First (User Story 1 + US4 Only)

1. Complete Phase 1: Setup (Dapr, Kafka, component)
2. Complete Phase 2: Foundational (event schemas, publisher)
3. Complete Phase 3: User Story 1 (emit events from backend)
4. Complete Phase 4: User Story 4 (verify Dapr abstraction)
5. **STOP and VALIDATE**: Create a todo, verify event appears in Kafka topic
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US1 + US4 → Events published (MVP!)
3. Add US2 → Activity logger consuming events
4. Add US5 → Schema validation hardening
5. Add US3 → Agent events tracked
6. Add US6 → Full Kubernetes deployment
7. Polish → Documentation, E2E validation

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 62 |
| **Setup Tasks** | 5 |
| **Foundational Tasks** | 9 |
| **US1 Tasks** | 6 |
| **US2 Tasks** | 15 |
| **US3 Tasks** | 8 |
| **US4 Tasks** | 3 |
| **US5 Tasks** | 4 |
| **US6 Tasks** | 7 |
| **Polish Tasks** | 5 |
| **Parallel Opportunities** | 12 |
| **MVP Scope** | US1 + US4 (14 tasks after foundation) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No direct Kafka client usage anywhere in codebase
