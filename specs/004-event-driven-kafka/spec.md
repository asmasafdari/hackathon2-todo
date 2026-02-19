# Feature Specification: Event-Driven Todo Platform

**Feature Branch**: `004-event-driven-kafka`
**Created**: 2026-01-23
**Status**: Draft
**Quality Checklist**: [checklists/requirements.md](checklists/requirements.md)
**Input**: User description: "Phase V – Event-Driven Todo Platform (Kafka + Dapr)"

## Overview

Transform the Todo platform into an event-driven system where state changes emit domain events that can be consumed asynchronously by multiple services. This enables decoupled services, extensibility without changing core services, asynchronous processing, and prepares the system for future analytics, automation, and AI workflows.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Event Publishing on Todo State Changes (Priority: P1)

As a platform operator, I want all todo state changes to be published as events so that downstream services can react to changes without coupling to the backend service.

**Why this priority**: Event publishing is the foundation of the event-driven architecture. Without events being published, no downstream processing can occur.

**Independent Test**: Can be fully tested by creating/updating/deleting a todo and verifying events appear in Kafka topic via Dapr dashboard or CLI.

**Acceptance Scenarios**:

1. **Given** a user creates a new todo via the API, **When** the todo is persisted, **Then** a `todo.created` event is published to Kafka within 1 second
2. **Given** a user updates an existing todo, **When** the update is persisted, **Then** a `todo.updated` event is published containing the changed fields
3. **Given** a user marks a todo as complete, **When** the completion is persisted, **Then** a `todo.completed` event is published with the completion timestamp
4. **Given** a user deletes a todo, **When** the deletion is persisted, **Then** a `todo.deleted` event is published with the todo ID

---

### User Story 2 - Activity Logger Consumer (Priority: P1)

As a platform operator, I want all todo events to be logged to a persistent activity log so that I have an audit trail of all changes in the system.

**Why this priority**: The activity logger demonstrates the consumer pattern and provides immediate value as an audit trail. It's the simplest consumer to implement and verify.

**Independent Test**: Can be fully tested by performing todo operations and verifying entries appear in the activity log (queryable via API endpoint).

**Acceptance Scenarios**:

1. **Given** the activity logger is subscribed to todo events, **When** any todo event is published, **Then** a log entry is created with event type, timestamp, and payload
2. **Given** multiple events occur rapidly, **When** the logger processes them, **Then** events are logged in order with no duplicates (idempotent handling)
3. **Given** the activity log contains entries, **When** an operator queries the log API, **Then** entries can be filtered by event type, date range, and todo ID

---

### User Story 3 - AI Agent Event Publishing (Priority: P2)

As a platform operator, I want AI agent actions to emit events so that agent activity can be monitored and audited alongside user actions.

**Why this priority**: Extends event sourcing to the AI agent subsystem, enabling visibility into automated actions.

**Independent Test**: Can be fully tested by invoking the AI agent to perform a todo action and verifying the `agent.action.executed` event appears.

**Acceptance Scenarios**:

1. **Given** the AI agent executes a tool (create/update/delete todo), **When** the tool completes, **Then** an `agent.action.executed` event is published
2. **Given** an agent action event is published, **When** the activity logger receives it, **Then** the log entry includes agent ID, action type, and outcome
3. **Given** an agent action fails, **When** the failure is recorded, **Then** an `agent.action.failed` event is published with error details

---

### User Story 4 - Dapr Pub/Sub Integration (Priority: P1)

As a developer, I want to publish and subscribe to events using Dapr pub/sub so that application code is decoupled from the underlying message broker (Kafka).

**Why this priority**: Dapr abstraction is a core constraint. All event operations must go through Dapr, not direct Kafka clients.

**Independent Test**: Can be fully tested by verifying no Kafka client libraries are imported in application code and all pub/sub calls use Dapr SDK.

**Acceptance Scenarios**:

1. **Given** the backend service needs to publish an event, **When** the publish call is made, **Then** it uses the Dapr pub/sub building block, not a Kafka client
2. **Given** a consumer service needs to subscribe to events, **When** the subscription is configured, **Then** it uses Dapr subscription configuration (declarative or programmatic)
3. **Given** Dapr is configured with Kafka component, **When** events are published, **Then** they appear in the configured Kafka topic

---

### User Story 5 - Event Schema Validation (Priority: P2)

As a developer, I want all events to follow the CloudEvents specification with validated schemas so that consumers can reliably parse events and handle schema evolution.

**Why this priority**: Schema validation prevents malformed events from entering the system and enables safe schema evolution.

**Independent Test**: Can be fully tested by publishing an event with missing required fields and verifying it is rejected before reaching Kafka.

**Acceptance Scenarios**:

1. **Given** an event is being published, **When** required CloudEvents fields (id, source, type, time) are missing, **Then** the publish is rejected with validation error
2. **Given** an event has a valid CloudEvents envelope, **When** the data payload is malformed, **Then** the publish is rejected with schema validation error
3. **Given** a new optional field is added to an event schema, **When** old consumers receive the event, **Then** they process it successfully (ignoring unknown fields)

---

### User Story 6 - Kubernetes Deployment with Dapr Sidecars (Priority: P2)

As an operator, I want the event-driven services deployed on Kubernetes with Dapr sidecars so that the pub/sub infrastructure is managed declaratively.

**Why this priority**: Builds on Phase IV Kubernetes foundation. Dapr sidecars are required for the event architecture to function.

**Independent Test**: Can be fully tested by deploying the Helm chart and verifying Dapr sidecars are injected into all annotated pods.

**Acceptance Scenarios**:

1. **Given** the Helm chart includes Dapr annotations, **When** pods are deployed, **Then** Dapr sidecar containers are automatically injected
2. **Given** Dapr components (Kafka pub/sub) are defined, **When** the chart is installed, **Then** the components are created in the Kubernetes namespace
3. **Given** services are running with Dapr sidecars, **When** a pod restarts, **Then** the sidecar reconnects to Kafka automatically

---

### Edge Cases

- What happens when Kafka is unavailable? → Events are buffered locally by Dapr (configurable); service remains operational but events delayed
- What happens when a consumer crashes mid-processing? → Event redelivered (at-least-once); consumer must be idempotent
- How does the system handle poison messages (malformed events)? → Dead letter topic configured; malformed events routed there after N retries
- What happens when event schema is invalid? → Publisher-side validation rejects event; never reaches Kafka
- How does the system handle out-of-order events? → Consumers use event timestamp and todo version for ordering; idempotent handling prevents issues

## Requirements *(mandatory)*

### Functional Requirements

#### Event Publishing
- **FR-001**: System MUST publish a `todo.created` event when a new todo is persisted
- **FR-002**: System MUST publish a `todo.updated` event when an existing todo is modified
- **FR-003**: System MUST publish a `todo.completed` event when a todo is marked complete
- **FR-004**: System MUST publish a `todo.deleted` event when a todo is deleted
- **FR-005**: System MUST publish an `agent.action.executed` event when an AI agent completes an action
- **FR-006**: System MUST publish an `agent.action.failed` event when an AI agent action fails

#### Event Format
- **FR-007**: All events MUST conform to CloudEvents v1.0 specification
- **FR-008**: Event `type` field MUST follow pattern `com.desktoptodo.<domain>.<action>` (e.g., `com.desktoptodo.todo.created`)
- **FR-009**: Event `source` field MUST identify the publishing service (e.g., `/backend/todos`)
- **FR-010**: Event `data` field MUST contain the domain payload as JSON
- **FR-011**: Events MUST include a `dataversion` field for schema versioning

#### Dapr Integration
- **FR-012**: All event publishing MUST use Dapr pub/sub building block
- **FR-013**: All event subscription MUST use Dapr subscription configuration
- **FR-014**: No direct Kafka client libraries in application code
- **FR-015**: Dapr pub/sub component MUST be configured for Kafka broker

#### Activity Logger
- **FR-016**: Activity logger service MUST subscribe to all `todo.*` events
- **FR-017**: Activity logger service MUST subscribe to all `agent.*` events
- **FR-018**: Activity logger MUST persist events with timestamp, type, and full payload
- **FR-019**: Activity logger MUST provide REST API for querying logged events
- **FR-020**: Activity logger MUST be idempotent (same event processed at most once)

#### Kubernetes/Helm
- **FR-021**: Helm chart MUST include Dapr component definitions for Kafka pub/sub
- **FR-022**: Helm chart MUST enable Dapr sidecar injection via pod annotations
- **FR-023**: Helm chart MUST include activity logger service deployment
- **FR-024**: Helm values MUST allow configuration of Kafka broker address

### Non-Functional Requirements

- **NFR-001**: Event publishing latency MUST be under 100ms (p95) from API response
- **NFR-002**: Activity logger MUST process events within 500ms of receipt (p95)
- **NFR-003**: System MUST support at-least-once delivery semantics
- **NFR-004**: System MUST NOT require exactly-once delivery guarantees
- **NFR-005**: Dead letter topic MUST capture events that fail processing after 3 retries
- **NFR-006**: Dapr sidecar memory limit MUST be under 256MB per pod

### Technical Constraints

- **TC-001**: Message broker: Apache Kafka
- **TC-002**: Sidecar framework: Dapr 1.12+
- **TC-003**: Event specification: CloudEvents v1.0
- **TC-004**: No direct Kafka client usage in application code
- **TC-005**: Kubernetes-native deployment (builds on Phase IV)
- **TC-006**: At-least-once delivery (no exactly-once required)

### Key Entities

- **Domain Event**: An immutable record of something that happened in the system, following CloudEvents spec
- **Event Publisher**: Component that emits events to Dapr pub/sub after state changes
- **Event Consumer**: Service that subscribes to and processes events asynchronously
- **Activity Log Entry**: Persisted record of an event for audit and query purposes
- **Dapr Component**: Kubernetes CRD defining a Dapr building block (e.g., pub/sub with Kafka)
- **Dead Letter Topic**: Kafka topic for events that failed processing after retry exhaustion

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All todo CRUD operations emit corresponding events within 100ms of API response
- **SC-002**: Activity logger captures 100% of published events (verified via count comparison)
- **SC-003**: No Kafka client imports exist in application source code (verified via grep)
- **SC-004**: Events conform to CloudEvents spec (verified via schema validation tests)
- **SC-005**: System recovers gracefully from Kafka unavailability (events buffered, no data loss)
- **SC-006**: Activity log API returns query results within 200ms (p95)
- **SC-007**: Helm chart deploys successfully with Dapr sidecars on Minikube

## Out of Scope

- Notification service (future consumer)
- Analytics pipeline (future consumer)
- Event replay/sourcing for state reconstruction
- Exactly-once delivery semantics
- Schema registry (Confluent Schema Registry)
- Multi-cluster Kafka replication
- Event-driven sagas or distributed transactions
- CQRS (Command Query Responsibility Segregation) patterns
- Real-time streaming analytics (Kafka Streams, ksqlDB)

## Dependencies

- Phase IV cloud-native deployment (Kubernetes, Helm) must be functional
- Backend service must be containerized and deployable
- Dapr must be installable on the Kubernetes cluster
- Kafka must be accessible (can be in-cluster via Helm chart or external)
- Activity logger requires a persistence store (can use existing Neon PostgreSQL)

## Assumptions

- Developers have Dapr CLI installed for local development
- Minikube or equivalent Kubernetes cluster is available
- Kafka can be deployed via Helm (Bitnami chart) or accessed externally
- At-least-once delivery is acceptable (consumers are idempotent)
- CloudEvents specification provides sufficient schema flexibility
- Activity logger can share the existing Neon PostgreSQL database
