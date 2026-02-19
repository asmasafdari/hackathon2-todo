# Research: Cloud-Native Deployment

**Feature**: 003-cloud-native-k8s
**Date**: 2026-01-22

## Research Questions

### 1. Docker Base Image Selection

**Decision**: Use `python:3.11-slim` for backend/MCP and `node:20-alpine` for frontend

**Rationale**:
- `python:3.11-slim` (140MB) provides good balance between size and compatibility
- Debian-based for better package availability if needed
- `node:20-alpine` (~50MB) is the smallest production-ready Node.js image
- Alpine is well-suited for Next.js production builds

**Alternatives Considered**:
| Image | Size | Pros | Cons |
|-------|------|------|------|
| python:3.11-alpine | ~50MB | Smallest | musl libc issues with some packages |
| python:3.11 | ~900MB | Full Debian | Too large for containers |
| node:20-slim | ~200MB | Debian-based | Larger than alpine |
| distroless | ~20MB | Minimal attack surface | No shell for debugging |

### 2. Multi-Stage Build Pattern

**Decision**: Use 3-stage builds (dependencies → build → runtime)

**Rationale**:
- Stage 1: Install dependencies with full toolchain
- Stage 2: Build application (compile TypeScript, bundle)
- Stage 3: Copy only runtime artifacts to minimal image
- Keeps final image small while allowing complex build processes

**Pattern for Python (FastAPI)**:
```dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim as deps
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=deps /root/.local /root/.local
COPY . .
```

**Pattern for Node.js (Next.js)**:
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine as deps
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine as builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
```

### 3. Health Check Endpoint Design

**Decision**: HTTP GET endpoints returning JSON status

**Rationale**:
- Kubernetes probes work with HTTP responses
- JSON format allows adding metadata (version, dependencies)
- Separate liveness (is process alive?) from readiness (can accept traffic?)

**Backend Health Endpoint**:
```json
GET /health → 200 OK
{
  "status": "healthy",
  "service": "backend",
  "version": "1.0.0",
  "database": "connected"
}
```

**Frontend Health Check**:
- Use root path `/` returning 200 OK
- Next.js serves pages even without explicit health endpoint

**MCP Server Health Endpoint**:
```json
GET /health → 200 OK
{
  "status": "healthy",
  "service": "mcp-server"
}
```

### 4. Helm Chart Structure

**Decision**: Umbrella chart with subcharts for each component

**Rationale**:
- Single `helm install` deploys entire stack
- Subcharts allow independent versioning and testing
- Shared values can be passed to all subcharts
- Common pattern for microservices

**Structure**:
```
charts/todo-platform/
├── Chart.yaml           # Umbrella chart
├── values.yaml          # Default values
├── charts/
│   ├── backend/         # Backend subchart
│   ├── frontend/        # Frontend subchart
│   └── mcp/             # MCP server subchart
└── templates/
    ├── namespace.yaml
    ├── configmap.yaml   # Shared config
    └── secrets.yaml     # Shared secrets
```

**Alternatives Considered**:
| Approach | Pros | Cons |
|----------|------|------|
| Monolithic chart | Simpler | Hard to manage at scale |
| Separate charts | Independent releases | Multiple install commands |
| Kustomize | No templating language | Less powerful than Helm |

### 5. Kubernetes Service Networking

**Decision**: ClusterIP services for internal, Ingress for external

**Rationale**:
- ClusterIP (default): Internal cluster communication only
- Ingress: Single entry point, path-based routing
- No LoadBalancer needed for Minikube (uses ingress addon)

**Service Configuration**:
| Service | Type | Port | Access |
|---------|------|------|--------|
| backend | ClusterIP | 8000 | Internal only |
| frontend | ClusterIP | 3000 | Via Ingress |
| mcp | ClusterIP | 8080 | Internal only |

**Ingress Rules**:
- `/` → frontend:3000
- `/api/*` → backend:8000

### 6. Secret Management Strategy

**Decision**: Kubernetes Secrets with base64 encoding, values passed at install time

**Rationale**:
- Standard Kubernetes pattern
- Helm `--set` or `-f values-secrets.yaml` for deployment
- `.gitignore` prevents committing secrets file
- Production can use external secret managers (Vault, AWS Secrets Manager)

**Implementation**:
```yaml
# values-secrets.yaml (NOT committed)
secrets:
  databaseUrl: "postgresql://..."
  openaiApiKey: "sk-..."

# templates/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-secrets
type: Opaque
data:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | b64enc }}
```

### 7. Minikube Configuration

**Decision**: Use Minikube with ingress addon enabled

**Rationale**:
- Built-in ingress controller (nginx)
- No external LoadBalancer required
- `minikube tunnel` for local access
- Docker driver recommended on Windows/Mac

**Setup Commands**:
```bash
minikube start --driver=docker --memory=4096
minikube addons enable ingress
minikube addons enable ingress-dns  # Optional for *.test domains
```

### 8. Container Registry Strategy

**Decision**: Use Minikube's built-in registry for local development

**Rationale**:
- No external registry needed for local testing
- `eval $(minikube docker-env)` shares Docker daemon
- Images built locally are immediately available to Minikube
- Production would use DockerHub, ECR, GCR, etc.

**Local Workflow**:
```bash
eval $(minikube docker-env)
docker build -t todo-backend:dev backend/
# Image is now available in Minikube
```

## Technology Decisions Summary

| Decision | Choice | Spec Reference |
|----------|--------|----------------|
| Python base image | python:3.11-slim | FR-001, FR-004 |
| Node base image | node:20-alpine | FR-002, FR-004 |
| Build strategy | Multi-stage (3 stages) | FR-004, SC-006 |
| Health checks | HTTP GET /health | FR-015, FR-016, FR-017 |
| Chart structure | Umbrella + subcharts | FR-011, FR-012 |
| Service type | ClusterIP + Ingress | FR-007, TC-003 |
| Secrets | K8s Secrets, Helm values | FR-009, FR-018, SC-007 |
| Local cluster | Minikube + ingress addon | NFR-004, TC-001 |
