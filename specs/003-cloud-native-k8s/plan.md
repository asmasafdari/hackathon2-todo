# Implementation Plan: Cloud-Native Deployment

**Branch**: `003-cloud-native-k8s` | **Date**: 2026-01-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-cloud-native-k8s/spec.md`

## Summary

Package and deploy the full-stack Todo application as cloud-native services using Docker containers, Kubernetes orchestration, and Helm charts. This enables reproducible, declarative deployments on Minikube for local development or any Kubernetes-compatible cloud platform.

## Technical Context

**Language/Version**: Python 3.11+ (backend, agent), Node.js 20 (frontend)
**Primary Dependencies**: FastAPI, Next.js, SQLModel, Dapr, Helm 3
**Storage**: PostgreSQL (Neon) - external database, no in-cluster persistence
**Testing**: pytest (backend), Docker build verification, Helm lint
**Target Platform**: Kubernetes 1.27+ (Minikube for local dev)
**Project Type**: Multi-service web application (backend, frontend, agent, activity-logger)
**Performance Goals**: Deploy complete stack in under 10 minutes, services healthy within 5 minutes
**Constraints**: No direct cloud provider resources, single replica per service, external database only
**Scale/Scope**: Single-user local development, Minikube-compatible

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Simplicity | PASS | Single command deployment via Helm |
| No External Deps (App) | N/A | Infrastructure deps (K8s) expected for deployment feature |
| CLI-First | PASS | Helm CLI deployment |
| Configuration Externalized | PASS | ConfigMaps and Secrets for all config |

**Constitution Deviations Justified**: This phase is about deployment infrastructure, not application code. Kubernetes and Helm are the appropriate tools for the requirement.

## Project Structure

### Scope

**Phase IV Focus**: Containerization and Kubernetes deployment infrastructure only
- Docker images for all 4 services
- Helm charts for Kubernetes deployment
- Dapr sidecar setup (Phase V will add Kafka pub/sub components)
- **Phase V (Event-Driven) will add**: Kafka, Dapr pub/sub components, event schemas

### Documentation (this feature)

```text
specs/003-cloud-native-k8s/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: K8s/Helm patterns
├── data-model.md        # N/A (no new entities)
├── quickstart.md        # Phase 1: Deployment guide
├── contracts/           # Phase 1: API contracts
│   ├── health-endpoints.json
│   └── helm-values-schema.json
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── Dockerfile           # Multi-stage Python image
├── main.py              # FastAPI app with /health endpoint
└── ...

frontend/
├── Dockerfile           # Multi-stage Node.js image
└── ...

agent/
├── Dockerfile           # Multi-stage Python image
└── ...

activity-logger/
├── Dockerfile           # Multi-stage Python image
└── ...

charts/
└── todo-platform/
    ├── Chart.yaml           # Helm chart metadata
    ├── values.yaml          # Default configuration values
    ├── .helmignore
    ├── templates/
    │   ├── configmap.yaml       # Non-sensitive configuration
    │   ├── secrets.yaml         # Sensitive data (API keys, DB URL)
    │   └── dapr-components/     # Dapr pub/sub configuration
    └── charts/
        ├── backend/           # Backend subchart
        ├── frontend/          # Frontend subchart
        ├── mcp/               # MCP agent subchart
        └── activity-logger/   # Activity logger subchart
```

**Structure Decision**: Helm umbrella chart with subcharts for each service. This allows independent versioning and deployment of services while maintaining a single deployment command.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Frontend   │  │   Backend    │  │     MCP      │       │
│  │   (Next.js)  │  │  (FastAPI)   │  │   (Agent)    │       │
│  │   :3000      │  │   :8000      │  │   :8080      │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│         └─────────────────┼─────────────────┘                │
│                           │                                  │
│                    ┌──────┴──────┐                          │
│                    │ Dapr Sidecar│                          │
│                    │  (pub/sub)  │                          │
│                    └──────┬──────┘                          │
│                           │                                  │
│              ┌────────────┼────────────────┐               │
│              ▼            ▼                ▼               │
│         ┌────────┐  ┌──────────┐  ┌──────────────┐         │
│         │Activity│  │ PostgreSQL│  │  (Kafka in   │         │
│         │ Logger │  │   (Neon)  │  │   Phase V)   │         │
│         │ :8081  │  │  External │  │              │         │
│         └────────┘  └──────────┘  └──────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Note: Dapr sidecars enable service-to-service communication.
Kafka integration is part of Phase V (Event-Driven Architecture).
```

## Design Decisions

### 1. Helm Umbrella Chart with Subcharts

**Decision**: Use Helm umbrella chart pattern with service-specific subcharts.

**Rationale**:
- Single command deployment of entire stack
- Independent service versioning possible
- Shared configuration via parent values.yaml
- Standard Kubernetes packaging

### 2. External PostgreSQL (Neon)

**Decision**: Use Neon Serverless PostgreSQL, not in-cluster database.

**Rationale**:
- Spec requirement (TC-005)
- Simplifies K8s deployment (no PVC management)
- Production-like external dependency
- Zero data loss on pod restart

### 3. Multi-Stage Docker Builds

**Decision**: All images use multi-stage builds.

**Rationale**:
- Smaller final image size
- Security (build tools not in runtime image)
- Faster deployments
- Spec requirement (FR-004)

### 4. Dapr Sidecar Pattern

**Decision**: Deploy Dapr sidecars with all services.

**Rationale**:
- Required for Phase V event-driven architecture
- Clean separation of concerns
- Service-to-service communication abstraction
- Built-in observability

## Configuration Strategy

### ConfigMaps (Non-Sensitive)
- API base URLs
- Service ports
- Log levels
- Dapr configuration

### Secrets (Sensitive)
- `DATABASE_URL`: Neon PostgreSQL connection
- `OPENAI_API_KEY`: AI agent API access
- Session database path (if needed)

### Environment-Specific Values
```yaml
# values.yaml structure
backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
  env:
    logLevel: INFO

frontend:
  replicaCount: 1
  # ...

secrets:
  databaseUrl: ""  # Override with --set or external secret
  openaiApiKey: "" # Override with --set or external secret
```

## Health Check Strategy

| Service | Endpoint | Probe Type | Path |
|---------|----------|------------|------|
| Backend | /health | Liveness + Readiness | GET /health |
| Frontend | Root | Liveness | GET / |
| MCP | /health | Liveness | GET /health |
| Activity Logger | /health | Liveness + Readiness | GET /health |

## Services Deployed

| Service | Port | Language | Purpose |
|---------|------|----------|---------|
| Frontend | 3000 | Node.js/Next.js | Web UI |
| Backend | 8000 | Python/FastAPI | REST API |
| MCP | 8080 | Python/FastMCP | AI Agent |
| Activity Logger | 8081 | Python/FastAPI | Audit logging (Phase V: event consumer) |

## Dependencies

### Required Tools
- Docker (with BuildKit)
- Minikube (or Kubernetes cluster)
- Helm 3.12+
- kubectl

### External Services
- Neon PostgreSQL database (must be accessible from cluster)
- OpenAI API (for agent functionality)

## Deployment Flow

### Prerequisites
- Docker with BuildKit
- Minikube installed
- Helm 3.12+ installed
- kubectl configured
- Dapr CLI installed (`dapr init` for local dev)

### Step-by-Step Deployment

```bash
# 1. Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# 2. Install Dapr on Kubernetes cluster
dapr init -k

# 3. Verify Dapr is running
kubectl get pods -n dapr-system

# 4. Configure Docker to use Minikube's daemon
eval $(minikube docker-env)

# 5. Build all service images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
docker build -t todo-mcp:latest ./agent
docker build -t todo-activity-logger:latest ./activity-logger

# 6. Verify images exist
docker images | grep todo-

# 7. Deploy with Helm
helm install todo-platform ./charts/todo-platform \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"

# 8. Verify deployment
kubectl get pods -n todo
helm status todo-platform

# 9. Access the application
minikube service todo-platform-frontend -n todo
```

### Dapr-Specific Verification

```bash
# Check Dapr sidecars are injected
kubectl get pods -n todo -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# View Dapr logs for a service
kubectl logs -n todo deployment/todo-platform-backend -c daprd

# Check Dapr components
dapr components -k
```

## Complexity Tracking

> No constitution violations for deployment phase. Infrastructure tools are appropriate for the scope.

## Next Steps

After this plan is approved:
1. Run `/sp.tasks` to generate implementation tasks
2. Create branch `003-cloud-native-k8s`
3. Implement Dockerfiles for all services
4. Create Helm chart structure
5. Test deployment on Minikube
