---
id: 002
title: Refine Topic Per Event Architecture Design
stage: plan
date: 2026-01-23
surface: agent
model: claude-opus-4-5-20251101
feature: 004-event-driven-kafka
branch: 003-cloud-native-k8s
user: Amena
command: /sp.plan
labels: ["event-driven", "kafka", "dapr", "topics", "refinement"]
links:
  spec: specs/004-event-driven-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-event-driven-kafka/plan.md
  - specs/004-event-driven-kafka/data-model.md
  - specs/004-event-driven-kafka/research.md
  - specs/004-event-driven-kafka/quickstart.md
tests:
  - N/A (planning phase)
---

## Prompt

```text
# Phase V Technical Plan

## Architecture Overview

User / AI Agent
 → Frontend / MCP
   → FastAPI Backend
     → Dapr Sidecar
       → Kafka Pub/Sub
         → Event Consumers

## Dapr Design

### Building Blocks Used
- Pub/Sub (Kafka)
- Service Invocation (optional future)
- Observability

### Pub/Sub Component
- Kafka-based pub/sub component
- Topic per domain event type

## Event Design

### Event Envelope
- event_id
- event_type
- source
- timestamp
- payload

### Topics
- todo.created
- todo.updated
- todo.completed
- todo.deleted
- agent.action

## Consumer Design

### Initial Consumer
- Activity Logger Service
- Writes structured logs
- Stateless

## Failure Handling
- Retry via Dapr
- Dead-letter topics (optional)
- Idempotent consumers

## Deployment
- Kafka deployed via Helm
- Dapr installed via Helm
- All services run with Dapr sidecars
```

## Response snapshot

Updated Phase V plan artifacts to incorporate user's technical guidance:

1. **Topic Strategy**: Changed from single `todo-events` topic to **topic-per-event-type**:
   - `todo.created`
   - `todo.updated`
   - `todo.completed`
   - `todo.deleted`
   - `agent.action`

2. **Updated Artifacts**:
   - `plan.md`: Added Architecture Overview section, Topics table, Consumer Design (stateless), Failure Handling details
   - `data-model.md`: Added Topic Mapping section, updated Entity Relationships diagram
   - `research.md`: Added Section 6 (Topic Strategy) with decision rationale
   - `quickstart.md`: Updated Kafka provisioning to create all 5 topics

3. **Key Decisions Confirmed**:
   - Stateless Activity Logger (no local state)
   - Dead-letter topics optional for Phase V
   - Dapr handles retries
   - Idempotent consumers required

## Outcome

- ✅ Impact: Aligned plan with user's architecture vision; topic-per-event enables better scaling
- 🧪 Tests: N/A (planning phase)
- 📁 Files: 4 files modified (plan.md, data-model.md, research.md, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks
- 🧠 Reflection: User input clarified topic strategy preference; topic-per-type is better for future extensibility

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All artifacts consistent with user guidance
- Prompt variant (if applicable): User-provided technical plan as input
- Next experiment (smallest change to try): Verify Kafka topic auto-creation behavior with Dapr
