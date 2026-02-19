# Tasks: Todo AI Chatbot (Phase V)

**Input**: Design documents from `/specs/005-todo-ai-chatbot/`
**Prerequisites**: plan.md (loaded), spec.md (loaded), research.md (loaded), data-model.md (loaded), contracts/ (loaded)

**Development Approach**: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code.

**Organization**: Tasks grouped by plan parts (A, B, C). Earlier Docker/verification tasks from prior phases are completed. New tasks cover advanced features, Minikube, and Oracle Cloud OKE deployment.

## Format: `[ID] [P?] [Part] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Part]**: Which plan part this task belongs to (A, B, C)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (FastAPI, Python)
- **Agent**: `agent/` (OpenAI Agents SDK, MCP server)
- **Frontend**: `chatbot-frontend/` (Next.js, TypeScript)
- **Helm Charts**: `charts/` (Kubernetes deployment)
- **Dapr Components**: `dapr/` (Dapr YAML configurations)
- **K8s Manifests**: `k8s/` (Kubernetes resources)
- **CI/CD**: `.github/workflows/` (GitHub Actions)

---

## Previously Completed (Docker & Verification)

> Tasks T001–T032 from the prior Docker containerization phase are complete. Docker Compose stack is operational. All user stories (US1–US7) verified. See git history for details.

---

## Part A: Advanced Features

### A1: Intermediate Features — Priorities, Tags, Search, Filter, Sort

**Purpose**: Extend the todo model and MCP tools with intermediate-level functionality

- [x] T033 [A1] Add `priority` field (enum: low, medium, high, urgent) and `tags` field (JSON array of strings) to the todo model in `backend/models/todo.py`
- [x] T034 [A1] Create and run Alembic migration for new `priority` and `tags` columns in `backend/migrations/`
- [x] T035 [A1] Update `backend/services/todo_service.py` to support filtering by priority, tags, and search by title/description
- [x] T036 [A1] Update `backend/routers/todos.py` with query parameters for priority filter, tag filter, search term, and sort order (created_at, priority, due_date)
- [x] T037 [A1] Add MCP tools `set_priority`, `add_tags`, `remove_tag`, `search_tasks` in `agent/mcp_server.py`
- [x] T038 [A1] Update agent system prompt in `agent/agent.py` to map natural language (e.g., "set task 3 to high priority", "tag task 1 with work") to new tools
- [x] T039 [P] [A1] Update chatbot-frontend to display priority badges and tags in task lists in `chatbot-frontend/components/ChatInterface.tsx`

**Checkpoint**: "Set task 1 to high priority" and "Tag task 2 with shopping" work via chat; "Show urgent tasks" filters correctly

---

### A2: Advanced Features — Due Dates & Reminders

**Purpose**: Add time-based task management with scheduled reminders

- [x] T040 [A2] Add `due_date` (datetime, nullable) and `remind_at` (datetime, nullable) fields to todo model in `backend/models/todo.py`
- [x] T041 [A2] Create and run Alembic migration for `due_date` and `remind_at` columns in `backend/migrations/`
- [x] T042 [A2] Update `backend/services/todo_service.py` with methods for setting due dates, querying overdue tasks, and filtering by due date range
- [x] T043 [A2] Update `backend/routers/todos.py` with endpoints/parameters for due date operations and overdue task listing
- [x] T044 [A2] Add MCP tools `set_due_date`, `set_reminder`, `list_overdue` in `agent/mcp_server.py`
- [x] T045 [A2] Update agent system prompt in `agent/agent.py` to map "remind me about task 1 tomorrow at 9am", "what's overdue?" to new tools

**Checkpoint**: "Set task 1 due Friday" sets due date; "What's overdue?" lists past-due tasks

---

### A3: Advanced Features — Recurring Tasks

**Purpose**: Implement auto-recurring tasks that regenerate on completion

- [x] T046 [A3] Add `recurrence_rule` (string, nullable — e.g., "daily", "weekly", "monthly") and `recurrence_parent_id` (FK, nullable) fields to todo model in `backend/models/todo.py`
- [x] T047 [A3] Create and run Alembic migration for recurrence fields in `backend/migrations/`
- [x] T048 [A3] Implement recurring task service in `backend/services/recurring_task_service.py` — on task completion, auto-create next occurrence based on recurrence_rule
- [x] T049 [A3] Add MCP tools `set_recurring`, `cancel_recurring` in `agent/mcp_server.py`
- [x] T050 [A3] Update agent system prompt in `agent/agent.py` to handle "Make task 1 repeat weekly", "Stop recurring for task 3"

**Checkpoint**: Complete a recurring task → next occurrence auto-created with correct due date

---

### A4: Event-Driven Architecture — Kafka Integration

**Purpose**: Add Kafka-based event streaming for decoupled microservices communication

- [x] T051 [A4] Create Kafka event schemas (CloudEvents format) for `task-events`, `reminders`, `task-updates` topics in `backend/events/kafka_schemas.py`
- [x] T052 [A4] Implement Kafka event producer in `backend/services/event_publisher.py` — publish events on task create, update, complete, delete
- [x] T053 [A4] Create notification service consumer in `backend/services/notification_service.py` — consume from `reminders` topic, log/send notifications
- [x] T054 [A4] Create recurring task consumer in `backend/services/recurring_task_consumer.py` — consume from `task-events` topic, auto-create next occurrence on completion
- [x] T055 [A4] Create audit/activity log consumer in `activity_logger/` — consume from `task-events`, store complete operation history
- [x] T056 [P] [A4] Add WebSocket endpoint in `backend/routers/` for real-time task sync — consume from `task-updates` topic, broadcast to connected clients

**Checkpoint**: Creating a task publishes to `task-events` topic; completing a recurring task triggers the recurring task consumer

---

### A5: Dapr Integration

**Purpose**: Abstract infrastructure (Kafka, DB, Secrets) behind Dapr HTTP APIs

- [x] T057 [A5] Create Dapr Pub/Sub component config for Kafka in `dapr/components/kafka-pubsub.yaml`
- [x] T058 [A5] Create Dapr State Store component config for PostgreSQL in `dapr/components/statestore.yaml`
- [x] T059 [A5] Create Dapr Secrets component config for Kubernetes secrets in `dapr/components/kubernetes-secrets.yaml`
- [x] T060 [A5] Refactor `backend/services/event_publisher.py` to publish via Dapr sidecar HTTP API (`http://localhost:3500/v1.0/publish/kafka-pubsub/...`) instead of direct Kafka client
- [x] T061 [A5] Implement Dapr Jobs API integration in `backend/services/reminder_scheduler.py` for exact-time reminder scheduling (replaces cron polling)
- [x] T062 [A5] Add Dapr subscription endpoint in `backend/routers/` to receive events from Dapr Pub/Sub
- [x] T063 [A5] Create Dapr service invocation config for frontend → backend communication with built-in retries

**Checkpoint**: Dapr sidecar runs alongside backend; events publish via Dapr HTTP API; secrets retrieved via Dapr secrets API

---

## Part B: Local Deployment (Minikube)

### B1: Containerize & Deploy to Minikube

**Purpose**: Deploy all services to local Kubernetes via Minikube with Helm charts

- [x] T064 [B1] Create/update Helm chart for backend service in `charts/backend/` — deployment, service, configmap, secrets, Dapr annotations
- [x] T065 [P] [B1] Create/update Helm chart for chatbot-frontend in `charts/chatbot-frontend/` — deployment, service, ingress, Dapr annotations
- [x] T066 [P] [B1] Create Helm chart for notification service in `charts/notification-service/` — deployment, Dapr annotations for Pub/Sub subscription
- [x] T067 [P] [B1] Create Helm chart for recurring task service in `charts/recurring-task-service/` — deployment, Dapr annotations for Pub/Sub subscription
- [x] T068 [B1] Deploy Kafka in Minikube using Strimzi operator — install Strimzi, create `kafka-cluster.yaml` (single replica, ephemeral) in `k8s/kafka/`
- [x] T069 [B1] Create Kafka topic manifests (`task-events`, `reminders`, `task-updates`) in `k8s/kafka/topics.yaml`
- [x] T070 [B1] Create Minikube deployment script in `scripts/minikube-deploy.sh` — start Minikube, build images, install Helm charts, apply Dapr components
- [ ] T071 [B1] Verify all pods running on Minikube: backend, frontend, notification, recurring task, Kafka, Dapr sidecars

**Checkpoint**: `minikube-deploy.sh` brings up full stack; `kubectl get pods` shows all healthy

---

### B2: Dapr on Minikube

**Purpose**: Full Dapr runtime on local Kubernetes

- [ ] T072 [B2] Install Dapr on Minikube (`dapr init -k`) and verify Dapr system pods running
- [ ] T073 [B2] Apply all Dapr component YAMLs (`dapr/components/`) to Minikube cluster
- [ ] T074 [B2] Verify Dapr sidecar injection on backend pod — check `daprd` container in pod spec
- [ ] T075 [B2] Verify Dapr Pub/Sub: publish a test event from backend, confirm receipt by notification service
- [ ] T076 [B2] Verify Dapr State Store: save and retrieve conversation state via Dapr HTTP API
- [ ] T077 [B2] Verify Dapr Secrets: retrieve OpenAI API key via Dapr secrets API from K8s secret
- [ ] T078 [B2] End-to-end Minikube smoke test: chat message → task created → event published → consumers process → task listed

**Checkpoint**: Full Dapr integration verified on Minikube; all building blocks operational

---

## Part C: Cloud Deployment (Oracle Cloud — OKE)

### C1: Oracle Cloud Setup

**Purpose**: Provision OKE cluster on Oracle Cloud Always Free tier

- [ ] T079 [C1] Sign up for Oracle Cloud at https://www.oracle.com/cloud/free/ (Always Free — 4 OCPUs, 24GB RAM, no charge after trial)
- [ ] T080 [C1] Create OKE (Oracle Kubernetes Engine) cluster via Oracle Cloud Console — configure node pool with Always Free shape (VM.Standard.A1.Flex)
- [ ] T081 [C1] Install and configure OCI CLI — set up `~/.oci/config` with tenancy, user, key
- [ ] T082 [C1] Configure `kubectl` to connect with OKE cluster — download kubeconfig via `oci ce cluster create-kubeconfig`
- [ ] T083 [C1] Verify cluster access: `kubectl get nodes` shows OKE nodes ready

**Checkpoint**: `kubectl get nodes` returns healthy OKE nodes; cluster is accessible from local machine

---

### C2: Deploy to OKE

**Purpose**: Deploy full application stack to Oracle Cloud OKE

- [ ] T084 [C2] Create OCIR (Oracle Cloud Infrastructure Registry) repositories for backend, chatbot-frontend, notification-service, recurring-task-service
- [ ] T085 [C2] Build and push Docker images to OCIR — tag images with OCIR path (`<region>.ocir.io/<tenancy>/<repo>:<tag>`)
- [ ] T086 [C2] Create Kubernetes namespace and secrets on OKE — OPENAI_API_KEY, DATABASE_URL, Clerk keys, OCIR pull secret
- [ ] T087 [C2] Install Dapr on OKE (`dapr init -k`) and apply all Dapr component YAMLs from `dapr/components/`
- [ ] T088 [C2] Deploy Kafka on OKE using Strimzi operator — apply `k8s/kafka/kafka-cluster.yaml` and topic manifests; if Kafka issues arise, swap to alternative Dapr PubSub component
- [ ] T089 [C2] Deploy all Helm charts to OKE (backend, chatbot-frontend, notification, recurring task) — update image references to OCIR paths
- [ ] T090 [C2] Configure OKE ingress/load balancer for external access to frontend and backend API
- [ ] T091 [C2] Verify all pods running on OKE: `kubectl get pods -A` shows all healthy with Dapr sidecars

**Checkpoint**: All services running on OKE; frontend accessible via public URL; chat flow works end-to-end

---

### C3: CI/CD Pipeline

**Purpose**: Automate build, push, and deploy via GitHub Actions

- [x] T092 [C3] Create GitHub Actions workflow in `.github/workflows/deploy-oke.yml` — trigger on push to main
- [x] T093 [C3] Add workflow steps: checkout, build Docker images, push to OCIR (authenticate via OCI credentials stored in GitHub Secrets)
- [x] T094 [C3] Add workflow steps: configure kubectl for OKE, run `helm upgrade --install` for each service
- [ ] T095 [C3] Add GitHub Secrets: OCI_TENANCY, OCI_USER, OCI_FINGERPRINT, OCI_KEY, OCI_REGION, OKE_CLUSTER_ID
- [ ] T096 [C3] Test CI/CD pipeline end-to-end: push a change, verify automated build → push → deploy on OKE

**Checkpoint**: Push to main triggers automated deployment to OKE; new images built and deployed without manual intervention

---

### C4: Monitoring & Logging

**Purpose**: Production observability on OKE

- [x] T097 [C4] Configure health check endpoints (`/health`, `/ready`) on all services for K8s liveness/readiness probes
- [ ] T098 [C4] Set up Dapr observability — enable distributed tracing and metrics collection via Dapr dashboard or Zipkin
- [ ] T099 [C4] Configure centralized logging — aggregate logs from all pods (use `kubectl logs` or deploy lightweight log collector)
- [ ] T100 [C4] Set up resource monitoring — configure K8s resource quotas and requests/limits for OKE Always Free tier constraints

**Checkpoint**: Health endpoints return 200; Dapr tracing shows request flow across services; logs accessible centrally

---

### C5: Verification & Documentation

**Purpose**: Final validation and project documentation

- [ ] T101 [C5] End-to-end smoke test on OKE: Sign in → Send "Add a task to test OKE" → Verify task created → "Set high priority" → "Show urgent tasks" → Verify filtered list
- [ ] T102 [C5] Verify Kafka event flow on OKE: create recurring task → complete it → verify next occurrence auto-created via consumer
- [ ] T103 [C5] Verify Dapr integration on OKE: events via Pub/Sub, state via State Store, secrets via Secrets API, reminders via Jobs API
- [ ] T104 [C5] Update `README.md` with OKE deployment instructions, live deployment URL, and architecture overview
- [ ] T105 [C5] Create `DEPLOYMENT_GUIDE.md` with step-by-step OKE cluster setup, OCIR configuration, and Helm deployment instructions
- [ ] T106 [C5] Update `specs/005-todo-ai-chatbot/` documentation — final spec, plan, tasks reflecting completed Phase V

**Checkpoint**: Live OKE deployment accessible; all documentation complete; GitHub repo submission-ready

---

## Dependencies & Execution Order

### Part Dependencies

- **Part A (Advanced Features)**: Start immediately — extends existing backend/agent code
  - A1 (Priorities/Tags) → A2 (Due Dates) → A3 (Recurring Tasks): Sequential — each builds on model changes
  - A4 (Kafka) + A5 (Dapr): Can start after A3 — event-driven layer on top of features
- **Part B (Minikube)**: Depends on Part A completion — need all services to containerize
  - B1 (Deploy) → B2 (Dapr on Minikube): Sequential
- **Part C (Oracle Cloud OKE)**: Depends on Part B — reuse Helm charts and validated config
  - C1 (Setup) can start in parallel with Part B (account setup while developing locally)
  - C2 (Deploy) → C3 (CI/CD) → C4 (Monitoring) → C5 (Verification): Sequential

### Parallel Opportunities

- T033-T039 (A1): T039 frontend can run in parallel with backend tasks
- T064-T067 (B1): Helm charts for frontend, notification, recurring task can be created in parallel
- T079-T083 (C1): Oracle Cloud setup can begin during Part B development
- T092-T095 (C3): GitHub Actions workflow steps are sequential but CI/CD setup can overlap with C4

### Critical Path

```
A1 → A2 → A3 → A4 → A5 → B1 → B2 → C2 → C3 → C4 → C5
                                  ↑
                            C1 (parallel)
```

---

## Execution Summary

| Part | Tasks | New Code | Key Deliverable |
|------|-------|----------|-----------------|
| A1: Priorities/Tags | T033-T039 | Models, services, MCP tools, frontend | Intermediate features |
| A2: Due Dates | T040-T045 | Models, services, MCP tools | Time-based management |
| A3: Recurring Tasks | T046-T050 | Models, services, MCP tools | Auto-recurring tasks |
| A4: Kafka | T051-T056 | Event schemas, producers, consumers | Event-driven architecture |
| A5: Dapr | T057-T063 | Dapr components, refactored publisher | Infrastructure abstraction |
| B1: Minikube Deploy | T064-T071 | Helm charts, K8s manifests, scripts | Local K8s deployment |
| B2: Dapr on Minikube | T072-T078 | Verification only | Full Dapr on local K8s |
| C1: Oracle Cloud Setup | T079-T083 | OCI config | OKE cluster provisioned |
| C2: Deploy to OKE | T084-T091 | OCIR config, ingress | Production deployment |
| C3: CI/CD | T092-T096 | GitHub Actions workflow | Automated deployments |
| C4: Monitoring | T097-T100 | Health endpoints, observability | Production readiness |
| C5: Verification | T101-T106 | Documentation | Submission-ready |

**Total**: 74 new tasks (T033-T106) across 12 sub-phases

---

## Notes

- [P] tasks = different files, no dependencies — can run in parallel
- [Part] label maps task to plan part for traceability
- Part A is feature development; Part B is local K8s; Part C is cloud production
- If Kafka causes issues on OKE, Dapr PubSub allows swapping to any alternative (RabbitMQ, Redis Streams) with config change only
- Oracle Cloud Always Free tier: 4 OCPUs, 24GB RAM — no expiring credits, best for learning
- Commit after each sub-phase completion
- Stop at any checkpoint to validate independently
