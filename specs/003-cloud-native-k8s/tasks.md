# Tasks: Cloud-Native Deployment

**Input**: Design documents from `/specs/003-cloud-native-k8s/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Dockerfiles**: `backend/Dockerfile`, `frontend/Dockerfile`, `agent/Dockerfile`, `activity-logger/Dockerfile`
- **Helm Charts**: `charts/todo-platform/`
- **Subcharts**: `charts/todo-platform/charts/{backend,frontend,mcp,activity-logger}/`
- **Dapr Components**: `charts/todo-platform/templates/dapr-components/` (Phase V)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Helm chart skeleton

- [x] T001 Create charts directory structure per plan.md at charts/todo-platform/
- [x] T002 Create umbrella chart Chart.yaml at charts/todo-platform/Chart.yaml
- [x] T003 [P] Create .helmignore file at charts/todo-platform/.helmignore
- [x] T004 [P] Add values-secrets.yaml to .gitignore to prevent secret commits
- [x] T005 [P] Create backend subchart skeleton at charts/todo-platform/charts/backend/Chart.yaml
- [x] T006 [P] Create frontend subchart skeleton at charts/todo-platform/charts/frontend/Chart.yaml
- [x] T007 [P] Create mcp subchart skeleton at charts/todo-platform/charts/mcp/Chart.yaml
- [x] T007a [P] Create activity-logger subchart skeleton at charts/todo-platform/charts/activity-logger/Chart.yaml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure backend health endpoint exists (required for K8s probes) and install Dapr infrastructure

**⚠️ CRITICAL**: Health endpoints and Dapr must exist before container images can be properly built

- [x] T008 Add /health endpoint to FastAPI backend in backend/main.py (if not present)
- [x] T008a [P] Add /health endpoint to activity-logger in activity-logger/main.py (if not present)
- [x] T009 [P] Add /health endpoint to MCP server in agent/mcp_server.py (if not present)
- [x] T009a Install Dapr CLI locally (dapr init)
- [x] T009b Install Dapr on Kubernetes cluster (dapr init -k)

**Checkpoint**: Health endpoints ready - container images can now be built with proper health checks

---

## Phase 3: User Story 2 - Container Image Building (Priority: P1)

**Goal**: Build Docker images for each application component using multi-stage builds

**Independent Test**: Run `docker build` for each component and verify images start with `docker run`

### Implementation for User Story 2

- [x] T010 [P] [US2] Create multi-stage Dockerfile for backend in backend/Dockerfile
- [x] T011 [P] [US2] Create multi-stage Dockerfile for frontend in frontend/Dockerfile
- [x] T012 [P] [US2] Create multi-stage Dockerfile for MCP server in agent/Dockerfile
- [x] T012a [P] [US2] Create multi-stage Dockerfile for activity-logger in activity-logger/Dockerfile
- [x] T013 [US2] Create .dockerignore for backend in backend/.dockerignore
- [x] T014 [P] [US2] Create .dockerignore for frontend in frontend/.dockerignore
- [x] T015 [P] [US2] Create .dockerignore for agent in agent/.dockerignore
- [x] T015a [P] [US2] Create .dockerignore for activity-logger in activity-logger/.dockerignore
- [x] T016 [US2] Verify backend image builds and starts with docker build/run
- [x] T017 [P] [US2] Verify frontend image builds and starts with docker build/run
- [x] T018 [P] [US2] Verify MCP image builds and starts with docker build/run
- [x] T018a [P] [US2] Verify activity-logger image builds and starts with docker build/run

**Checkpoint**: All 4 container images build successfully and can start independently

---

## Phase 4: User Story 5 - Helm Chart Deployment (Priority: P2)

**Goal**: Create Helm chart that deploys all application components

**Independent Test**: Run `helm lint` and `helm template` to verify chart validity

### Implementation for User Story 5

- [x] T019 [US5] Create parent values.yaml with defaults at charts/todo-platform/values.yaml
- [x] T020 [P] [US5] Create backend subchart values.yaml at charts/todo-platform/charts/backend/values.yaml
- [x] T021 [P] [US5] Create frontend subchart values.yaml at charts/todo-platform/charts/frontend/values.yaml
- [x] T022 [P] [US5] Create mcp subchart values.yaml at charts/todo-platform/charts/mcp/values.yaml
- [x] T022a [P] [US5] Create activity-logger subchart values.yaml at charts/todo-platform/charts/activity-logger/values.yaml
- [x] T023 [P] [US5] Create backend deployment template at charts/todo-platform/charts/backend/templates/deployment.yaml
- [x] T024 [P] [US5] Create backend service template at charts/todo-platform/charts/backend/templates/service.yaml
- [x] T025 [P] [US5] Create frontend deployment template at charts/todo-platform/charts/frontend/templates/deployment.yaml
- [x] T026 [P] [US5] Create frontend service template at charts/todo-platform/charts/frontend/templates/service.yaml
- [x] T027 [P] [US5] Create mcp deployment template at charts/todo-platform/charts/mcp/templates/deployment.yaml
- [x] T028 [P] [US5] Create mcp service template at charts/todo-platform/charts/mcp/templates/service.yaml
- [x] T028a [P] [US5] Create activity-logger deployment template at charts/todo-platform/charts/activity-logger/templates/deployment.yaml
- [x] T028b [P] [US5] Create activity-logger service template at charts/todo-platform/charts/activity-logger/templates/service.yaml
- [x] T029 [US5] Run helm lint to validate chart at charts/todo-platform/

**Checkpoint**: Helm chart passes linting and can be templated

---

## Phase 5: User Story 3 - Configuration Management (Priority: P2)

**Goal**: Externalize all configuration into ConfigMaps and Secrets

**Independent Test**: Deploy app, change ConfigMap, restart pod, verify new config applies

### Implementation for User Story 3

- [x] T030 [US3] Create ConfigMap template at charts/todo-platform/templates/configmap.yaml
- [x] T031 [US3] Create Secret template at charts/todo-platform/templates/secrets.yaml
- [x] T032 [US3] Create values-secrets.yaml.example template at charts/todo-platform/values-secrets.yaml.example
- [x] T033 [US3] Update backend deployment to reference ConfigMap and Secret envFrom
- [x] T034 [P] [US3] Update frontend deployment to reference ConfigMap for API URL
- [x] T035 [P] [US3] Update mcp deployment to reference ConfigMap and Secret envFrom
- [x] T035a [P] [US3] Update activity-logger deployment to reference ConfigMap and Secret envFrom

**Checkpoint**: All services read configuration from ConfigMaps and Secrets

---

## Phase 6: User Story 4 - Service Health Monitoring (Priority: P2)

**Goal**: Add liveness and readiness probes to all deployments

**Independent Test**: Deploy app, kill a pod's health endpoint, verify K8s restarts it

### Implementation for User Story 4

- [x] T036 [US4] Add liveness and readiness probes to backend deployment template
- [x] T037 [P] [US4] Add liveness and readiness probes to frontend deployment template
- [x] T038 [P] [US4] Add liveness and readiness probes to mcp deployment template
- [x] T038a [P] [US4] Add liveness and readiness probes to activity-logger deployment template
- [x] T039 [US4] Configure probe timing (initialDelaySeconds, periodSeconds) in values.yaml

**Checkpoint**: All deployments have health probes configured

---

## Phase 7: User Story 6 - Inter-Service Communication (Priority: P3)

**Goal**: Configure Kubernetes networking for service-to-service communication

**Independent Test**: Deploy all services, verify frontend can reach backend via service DNS

### Implementation for User Story 6

- [x] T040 [US6] Create namespace template at charts/todo-platform/templates/namespace.yaml
- [x] T041 [US6] Create Ingress template at charts/todo-platform/templates/ingress.yaml
- [x] T042 [US6] Configure ingress paths: / → frontend, /api/* → backend
- [x] T043 [US6] Update frontend ConfigMap with backend service DNS URL (http://backend:8000)
- [x] T044 [US6] Update mcp ConfigMap with backend service DNS URL
- [x] T044a [US6] Update activity-logger ConfigMap with backend service DNS URL

**Checkpoint**: All services can communicate via Kubernetes service DNS

---

## Phase 8: User Story 1 - Local Development Deployment (Priority: P1)

**Goal**: Deploy entire application stack to Minikube with single command

**Independent Test**: Fresh Minikube, run helm install, verify all pods healthy within 5 minutes

### Implementation for User Story 1

- [x] T045 [US1] Start Minikube and enable ingress addon
- [x] T046 [US1] Build all images in Minikube's Docker daemon with eval $(minikube docker-env)
- [x] T047 [US1] Create local values-secrets.yaml with test credentials
- [x] T048 [US1] Run helm install and verify all pods reach Running state
- [x] T049 [US1] Run minikube tunnel and verify frontend accessible at localhost
- [x] T050 [US1] Verify API requests from frontend reach backend
- [x] T051 [US1] Verify health endpoints respond correctly for all services

**Checkpoint**: Full stack deployed and functional on Minikube

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final validation

- [x] T052 [P] Update quickstart.md with actual deployment commands
- [x] T053 [P] Create DEPLOYMENT.md with architecture diagram and troubleshooting
- [x] T054 Run helm upgrade to verify upgrade path works
- [x] T055 Run helm rollback to verify rollback works
- [x] T056 Verify image sizes are under 500MB with docker images
- [x] T057 Final validation against all success criteria in spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - adds health endpoints
- **US2 (Phase 3)**: Depends on Foundational - builds container images
- **US5 (Phase 4)**: Depends on Setup - creates Helm templates
- **US3 (Phase 5)**: Depends on US5 - adds ConfigMaps/Secrets to templates
- **US4 (Phase 6)**: Depends on US5 - adds probes to deployment templates
- **US6 (Phase 7)**: Depends on US5 - adds Ingress and namespace
- **US1 (Phase 8)**: Depends on ALL above - integration verification
- **Polish (Phase 9)**: Depends on US1 - documentation and final validation

### User Story Dependencies

```
Setup → Foundational → US2 (Images) ─┐
                         ↓           │
                    US5 (Helm) ──────┤
                    ↓    ↓    ↓      │
                  US3  US4  US6      │
                    ↓    ↓    ↓      │
                    └────┴────┴──────┴→ US1 (Integration) → Polish
```

### Parallel Opportunities

**Within Phase 1 (Setup)**:
- T003, T004, T005, T006, T007, T007a can run in parallel

**Within Phase 2 (Foundational)**:
- T008, T008a, T009 can run in parallel (different services)
- T009a, T009b (Dapr setup) are sequential but independent of other tasks

**Within Phase 3 (US2 - Images)**:
- T010, T011, T012, T012a can run in parallel (different Dockerfiles)
- T014, T015, T015a, T017, T018, T018a can run in parallel after their image is built

**Within Phase 4 (US5 - Helm)**:
- T020, T021, T022 can run in parallel (different subcharts)
- T023, T024 can run in parallel with T025, T026 and T027, T028

**Within Phase 5 (US3 - Config)**:
- T034, T035 can run in parallel after T033

**Within Phase 6 (US4 - Health)**:
- T037, T038 can run in parallel after T036

---

## Parallel Example: US2 Container Images

```bash
# Build all 4 images in parallel:
docker build -t todo-backend:dev backend/ &
docker build -t todo-frontend:dev frontend/ &
docker build -t todo-mcp:dev agent/ &
docker build -t todo-activity-logger:dev activity-logger/ &
wait
```

---

## Implementation Strategy

### MVP First (Minimum Viable Deployment)

1. Complete Phase 1: Setup (chart skeleton)
2. Complete Phase 2: Foundational (health endpoints)
3. Complete Phase 3: US2 (container images)
4. Complete Phase 4: US5 (basic Helm templates)
5. **STOP and VALIDATE**: Can deploy to Minikube with basic functionality
6. Continue with US3, US4, US6 for production-readiness

### Incremental Delivery

1. Setup + Foundational + US2 → Images buildable
2. Add US5 → Helm deployable (basic)
3. Add US3 → Config externalized
4. Add US4 → Health monitoring
5. Add US6 → Full networking
6. US1 → Full integration verified
7. Polish → Documentation complete

---

## Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| 1 Setup | - | 8 | 6 |
| 2 Foundational | - | 5 | 2 |
| 3 US2 Images | P1 | 12 | 8 |
| 4 US5 Helm | P2 | 14 | 10 |
| 5 US3 Config | P2 | 7 | 3 |
| 6 US4 Health | P2 | 5 | 3 |
| 7 US6 Network | P3 | 6 | 0 |
| 8 US1 Deploy | P1 | 7 | 0 |
| 9 Polish | - | 6 | 2 |
| **Total** | | **70** | **34** |
| **Complete** | | **70/70** | **100%** |

---

## Notes

- **[COMPLETE]** All 70 tasks finished - Phase IV (Cloud-Native K8s) is ready for deployment
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Health endpoints and Dapr installation in Phase 2 are blocking prerequisites
- **Activity Logger**: Fourth service added to match plan.md architecture (was missing from original tasks)
- **Dapr**: Installed in Phase 2, sidecars auto-injected via annotations in deployment templates
- **Ingress**: Template created (T041-T042) with paths / → frontend, /api/* → backend
- US2 (Images) and US5 (Helm) can partially overlap after images are building
- US3, US4, US6 all modify Helm templates - coordinate if running in parallel
- US1 is integration verification - run after all other stories complete
- **Kafka**: Belongs to Phase V (Event-Driven), not included in Phase IV tasks
