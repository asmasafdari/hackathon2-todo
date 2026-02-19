# Data Model: Cloud-Native Deployment

**Feature**: 003-cloud-native-k8s
**Date**: 2026-01-22

## Overview

This document defines the Kubernetes resource models and their relationships for the cloud-native deployment of the Todo application. Unlike typical application data models, these represent infrastructure configuration entities.

## Container Images

### Backend Image

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `todo-backend` |
| tag | string | Version tag (e.g., `1.0.0`, `dev`) |
| base | string | `python:3.11-slim` |
| port | integer | 8000 |
| entrypoint | string | `uvicorn main:app --host 0.0.0.0 --port 8000` |

**Environment Variables**:
- `DATABASE_URL` (secret) - PostgreSQL connection string
- `CORS_ORIGINS` (config) - Allowed CORS origins

### Frontend Image

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `todo-frontend` |
| tag | string | Version tag |
| base | string | `node:20-alpine` |
| port | integer | 3000 |
| entrypoint | string | `node server.js` |

**Environment Variables**:
- `NEXT_PUBLIC_API_URL` (config) - Backend API URL

### MCP Server Image

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `todo-mcp` |
| tag | string | Version tag |
| base | string | `python:3.11-slim` |
| port | integer | 8080 |
| entrypoint | string | `python -m mcp_server` |

**Environment Variables**:
- `TODO_API_BASE_URL` (config) - Backend API URL
- `OPENAI_API_KEY` (secret) - OpenAI API key

## Kubernetes Resources

### Deployment

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | yes | Unique deployment name |
| replicas | integer | no | Number of pod replicas (default: 1) |
| image | string | yes | Container image reference |
| port | integer | yes | Container port |
| resources.requests.cpu | string | no | CPU request (e.g., `100m`) |
| resources.requests.memory | string | no | Memory request (e.g., `128Mi`) |
| resources.limits.cpu | string | no | CPU limit |
| resources.limits.memory | string | no | Memory limit |
| livenessProbe | ProbeSpec | yes | Liveness check configuration |
| readinessProbe | ProbeSpec | yes | Readiness check configuration |
| envFrom | list | no | ConfigMap/Secret references |

### ProbeSpec

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| httpGet.path | string | yes | Health check endpoint path |
| httpGet.port | integer | yes | Port to check |
| initialDelaySeconds | integer | no | Delay before first check (default: 10) |
| periodSeconds | integer | no | Check interval (default: 10) |
| timeoutSeconds | integer | no | Check timeout (default: 5) |
| failureThreshold | integer | no | Failures before unhealthy (default: 3) |

### Service

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | yes | Service name (DNS name) |
| type | enum | no | ClusterIP, NodePort, LoadBalancer |
| port | integer | yes | Service port |
| targetPort | integer | yes | Container port |
| selector | map | yes | Pod label selector |

### ConfigMap

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | yes | ConfigMap name |
| data | map | yes | Key-value configuration data |

**Standard Keys**:
- `API_BASE_URL` - Backend API URL for internal services
- `CORS_ORIGINS` - Allowed CORS origins
- `LOG_LEVEL` - Application log level

### Secret

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | yes | Secret name |
| type | string | no | Secret type (default: Opaque) |
| data | map | yes | Base64-encoded secret data |

**Required Secrets**:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key

### Ingress

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | yes | Ingress name |
| className | string | no | Ingress controller class |
| rules | list | yes | Routing rules |
| tls | list | no | TLS configuration |

**Ingress Rule**:
| Attribute | Type | Description |
|-----------|------|-------------|
| host | string | Hostname (optional for local) |
| paths | list | Path-based routing rules |

**Path Rule**:
| Attribute | Type | Description |
|-----------|------|-------------|
| path | string | URL path prefix |
| pathType | enum | Prefix, Exact, ImplementationSpecific |
| backend.service.name | string | Target service name |
| backend.service.port.number | integer | Target service port |

## Helm Values Schema

### Root Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| global.namespace | string | `todo` | Kubernetes namespace |
| global.imageTag | string | `latest` | Default image tag |

### Backend Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| backend.enabled | boolean | true | Deploy backend |
| backend.replicas | integer | 1 | Pod replicas |
| backend.image.repository | string | `todo-backend` | Image name |
| backend.image.tag | string | `""` | Image tag (uses global if empty) |
| backend.service.port | integer | 8000 | Service port |
| backend.resources.requests.cpu | string | `100m` | CPU request |
| backend.resources.requests.memory | string | `256Mi` | Memory request |

### Frontend Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| frontend.enabled | boolean | true | Deploy frontend |
| frontend.replicas | integer | 1 | Pod replicas |
| frontend.image.repository | string | `todo-frontend` | Image name |
| frontend.image.tag | string | `""` | Image tag |
| frontend.service.port | integer | 3000 | Service port |

### MCP Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| mcp.enabled | boolean | true | Deploy MCP server |
| mcp.replicas | integer | 1 | Pod replicas |
| mcp.image.repository | string | `todo-mcp` | Image name |
| mcp.image.tag | string | `""` | Image tag |
| mcp.service.port | integer | 8080 | Service port |

### Secrets Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| secrets.databaseUrl | string | `""` | Database connection string |
| secrets.openaiApiKey | string | `""` | OpenAI API key |

### Ingress Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| ingress.enabled | boolean | true | Enable ingress |
| ingress.className | string | `nginx` | Ingress class |
| ingress.host | string | `""` | Hostname (empty for any) |

## Resource Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         Namespace: todo                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │  ConfigMap  │     │   Secret    │     │   Ingress   │       │
│  │  (shared)   │     │  (shared)   │     │             │       │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘       │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Deployments                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │  frontend   │  │   backend   │  │     mcp     │     │   │
│  │  │  (1 pod)    │  │  (1 pod)    │  │  (1 pod)    │     │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │   │
│  └─────────┼────────────────┼────────────────┼─────────────┘   │
│            │                │                │                  │
│            ▼                ▼                ▼                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      Services                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │  frontend   │  │   backend   │  │     mcp     │     │   │
│  │  │  :3000      │  │   :8000     │  │   :8080     │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  External: Neon │
                    │   PostgreSQL    │
                    └─────────────────┘
```

## State Transitions

### Pod Lifecycle

```
Pending → ContainerCreating → Running → Terminating → Terminated
                                ↓
                           CrashLoopBackOff (on failure)
```

### Deployment Rollout

```
Desired (new) → Progressing → Available
                    ↓
              Failed (rollback available)
```

### Health Check States

```
Unknown → Healthy (passing probes)
    ↓
Unhealthy → Pod Restart (liveness) or Traffic Removed (readiness)
```
