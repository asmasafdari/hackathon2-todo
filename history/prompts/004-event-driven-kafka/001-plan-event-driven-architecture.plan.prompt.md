---
id: 001
title: Plan Event-Driven Architecture with Kafka and Dapr
stage: plan
date: 2026-01-23
surface: agent
model: claude-opus-4-5-20251101
feature: 004-event-driven-kafka
branch: 003-cloud-native-k8s
user: Amena
command: /sp.plan
labels: ["event-driven", "kafka", "dapr", "architecture", "phase-v"]
links:
  spec: specs/004-event-driven-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - specs/004-event-driven-kafka/spec.md
  - specs/004-event-driven-kafka/plan.md
  - specs/004-event-driven-kafka/research.md
  - specs/004-event-driven-kafka/data-model.md
  - specs/004-event-driven-kafka/quickstart.md
  - specs/004-event-driven-kafka/contracts/events/cloudevent-envelope.json
  - specs/004-event-driven-kafka/contracts/events/todo-created.json
  - specs/004-event-driven-kafka/contracts/events/todo-updated.json
  - specs/004-event-driven-kafka/contracts/events/todo-completed.json
  - specs/004-event-driven-kafka/contracts/events/todo-deleted.json
  - specs/004-event-driven-kafka/contracts/events/agent-action-executed.json
  - specs/004-event-driven-kafka/contracts/events/agent-action-failed.json
  - specs/004-event-driven-kafka/contracts/api/activity-logger-openapi.yaml
tests:
  - N/A (planning phase)
---

## Prompt

```text
# Phase V – Event-Driven Todo Platform (Kafka + Dapr)

## Goal
Transform the Todo platform into an event-driven system where state changes
emit domain events that can be consumed asynchronously by multiple services.

## Event-Driven Objectives
- Decouple services using events
- Enable extensibility without changing core services
- Support asynchronous processing
- Prepare system for future analytics, automation, and AI workflows

## Event Sources
- Todo created
- Todo updated
- Todo completed
- Todo deleted
- AI agent action executed

## Event Consumers
- Activity logger
- Notification service (future)
- Analytics pipeline (future)
- Audit trail

## Tooling
- Apache Kafka (event broker)
- Dapr (sidecar + building blocks)
- Kubernetes-native deployment

## Constraints
- No direct Kafka client usage in application code
- All event publishing via Dapr pub/sub
- At-least-once delivery semantics
- No exactly-once guarantees required
```

## Response snapshot

Executed `/sp.plan` command for Phase V Event-Driven Todo Platform. Key outputs:

1. **Constitution Amendment**: Updated constitution from v1.0.0 to v2.0.0 to support event-driven architecture, adding principles for storage strategy evolution, architecture phases, and event-driven patterns (Dapr abstraction, idempotent handlers, schema versioning).

2. **Feature Spec Created**: Generated comprehensive spec at `specs/004-event-driven-kafka/spec.md` with 6 user stories covering event publishing, activity logger, AI agent events, Dapr integration, schema validation, and Kubernetes deployment.

3. **Implementation Plan**: Created `plan.md` with technical context (Python 3.11, Dapr SDK 1.12+, CloudEvents), constitution check (all gates PASS), and project structure extending existing backend with new `events/` module and `activity-logger` service.

4. **Phase 0 Research**: Generated `research.md` documenting Dapr pub/sub patterns, CloudEvents specification, idempotent handler patterns (inbox table), Kubernetes sidecar annotations, and activity log schema design.

5. **Phase 1 Artifacts**:
   - `data-model.md`: Event schemas for todo and agent domain events
   - `contracts/events/`: JSON Schema files for all CloudEvents
   - `contracts/api/activity-logger-openapi.yaml`: REST API for querying logs
   - `quickstart.md`: Local development setup guide

## Outcome

- ✅ Impact: Planned complete event-driven architecture transformation for Phase V
- 🧪 Tests: N/A (planning phase, no implementation yet)
- 📁 Files: 14 files created/modified (constitution, spec, plan, research, data-model, quickstart, 7 JSON schemas, 1 OpenAPI spec)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks, then create branch `004-event-driven-kafka`
- 🧠 Reflection: Constitution required amendment before planning could proceed; this was the correct workflow since Phase V fundamentally changes the architecture from the original CLI-only design.

## Evaluation notes (flywheel)

- Failure modes observed: Initial constitution check failed due to v1.0.0 constraints (single module, in-memory only). Resolved by amending constitution with user approval.
- Graders run and results (PASS/FAIL): Constitution Check PASS (post-amendment), Technical Context complete (no NEEDS CLARIFICATION remaining)
- Prompt variant (if applicable): Standard /sp.plan command
- Next experiment (smallest change to try): Validate Dapr component configuration by deploying to local Minikube cluster before implementation
