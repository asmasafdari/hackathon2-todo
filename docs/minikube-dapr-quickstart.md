# Todo Platform - Minikube + Full Dapr Quickstart

Complete guide for deploying the Todo Platform on Minikube with all Dapr building blocks enabled.

## 🚀 Quick Start (One Command)

```bash
./scripts/minikube-dapr-deploy.sh
```

## 📋 Prerequisites

- **minikube** - Kubernetes local cluster ([Install](https://minikube.sigs.k8s.io/docs/start/))
- **kubectl** - Kubernetes CLI ([Install](https://kubernetes.io/docs/tasks/tools/))
- **helm** - Kubernetes package manager ([Install](https://helm.sh/docs/intro/install/))
- **docker** - Container runtime ([Install](https://docs.docker.com/get-docker/))
- **dapr** - Dapr CLI ([Install](https://docs.dapr.io/getting-started/install-dapr-cli/))

### Install Prerequisites (macOS/Linux)

```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s/release/$(curl -L -s https://dl.k8s/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

### Install Prerequisites (Windows - PowerShell Admin)

```powershell
# Install minikube
winget install Kubernetes.minikube

# Install kubectl
winget install Kubernetes.kubectl

# Install Helm
winget install Helm.Helm

# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

## 🏗️ What Gets Deployed

### Dapr Building Blocks

| Feature | Component | Description |
|---------|-----------|-------------|
| **Pub/Sub** | Redis Streams | Async messaging between services |
| **State Store** | Redis | Distributed state management |
| **Bindings** | Cron | Scheduled tasks and triggers |
| **Secrets** | Kubernetes | Secure secret management |
| **Service Invocation** | mTLS + Resiliency | Secure service-to-service calls |

### Infrastructure

- **Minikube** - Local Kubernetes cluster (4 CPUs, 8GB RAM)
- **Dapr Runtime** - v1.12.0 with high availability
- **Redis** - State store and pub/sub backend
- **Zipkin** - Distributed tracing
- **NGINX Ingress** - Traffic routing

### Application Services

- **Frontend** (Next.js) - Web UI with Dapr sidecar
- **Backend** (FastAPI) - API with Dapr sidecar
- **MCP** (AI Agent) - Optional AI features
- **Activity Logger** - Event tracking

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Ingress Controller                       │
│                    (NGINX / Load Balancer)                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴───────────┐
        │                      │
┌───────▼──────┐      ┌────────▼─────┐
│  Frontend    │      │   Backend    │
│ (Next.js)    │      │  (FastAPI)   │
│ Dapr Sidecar │      │ Dapr Sidecar │
└──────┬───────┘      └──────┬───────┘
       │                     │
       │      Dapr Runtime   │
       │    ┌─────────────┐  │
       └────┤  mTLS/      ├──┘
            │ Resiliency  │
            └──────┬──────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐   ┌────▼────┐   ┌─────▼──────┐
│  Redis │   │  Cron   │   │ Kubernetes │
│ State  │   │Binding  │   │  Secrets   │
│ Store  │   │         │   │            │
└────────┘   └─────────┘   └────────────┘
    │
    └──── Pub/Sub
```

## 🎯 Deployment Steps

### 1. Quick Deploy (Recommended)

```bash
# Run the deployment script
./scripts/minikube-dapr-deploy.sh

# Check status
./scripts/minikube-dapr-deploy.sh status

# Clean up when done
./scripts/minikube-dapr-deploy.sh cleanup
```

### 2. Manual Deployment

```bash
# Step 1: Start Minikube
minikube start --profile=todo-dapr --cpus=4 --memory=8192 --disk-size=30g

# Step 2: Install Dapr
dapr init --kubernetes --wait

# Step 3: Install Redis (for state store and pub/sub)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis --namespace todo --create-namespace \
  --set auth.enabled=true --set auth.password=redis-password

# Step 4: Build images
minikube -p todo-dapr docker-env | source
docker build -t todo-backend:latest backend/
docker build -t todo-frontend:latest frontend/

# Step 5: Deploy application
helm upgrade --install todo-platform charts/todo-platform \
  --namespace todo \
  --values charts/todo-platform/values-minikube.yaml \
  --wait
```

## 🔍 Verification

### Check Dapr Components

```bash
# List all Dapr components
kubectl get components -n todo

# Expected output:
# NAME                TYPE           VERSION   SCOPES
# todo-state-store    state.redis    v1        todo-backend,activity-logger,mcp-server
# todo-pubsub         pubsub.redis   v1        todo-backend,activity-logger,mcp-server
# todo-cron-binding   bindings.cron  v1        todo-backend
# todo-secrets        secretstores.kubernetes  v1  todo-backend,activity-logger,mcp-server
```

### Check Pods

```bash
kubectl get pods -n todo

# Expected output:
# NAME                                          READY   STATUS    RESTARTS   AGE
# todo-platform-backend-xxx                     2/2     Running   0          5m
# todo-platform-frontend-xxx                    2/2     Running   0          5m
# redis-master-0                                1/1     Running   0          5m
# dapr-operator-xxx                             1/1     Running   0          10m
# dapr-sidecar-injector-xxx                     1/1     Running   0          10m
# dapr-placement-server-0                       1/1     Running   0          10m
```

### Test Service Invocation

```bash
# Port forward to access services
kubectl port-forward -n todo svc/todo-backend 8000:8000 &
kubectl port-forward -n todo svc/todo-frontend 3000:3000 &

# Test backend API
curl http://localhost:8000/api/health

# Create a todo (uses Dapr pub/sub internally)
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test with Dapr", "description": "Using pub/sub!"}'

# List todos
curl http://localhost:8000/api/todos
```

## 📊 Access Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Web UI |
| Backend API | http://localhost:8000/api/docs | API Documentation |
| Zipkin | http://localhost:9411 | Distributed Tracing |
| Minikube Dashboard | `minikube dashboard --profile=todo-dapr` | Kubernetes Dashboard |

## 🔧 Dapr Features in Action

### Pub/Sub (Event Publishing)

The backend automatically publishes events when todos are created:

```python
# Example: Publishing events via Dapr
from dapr.clients import DaprClient

with DaprClient() as d:
    d.publish_event(
        pubsub_name="todo-pubsub",
        topic_name="todo-created",
        data={"id": "123", "title": "New Todo"}
    )
```

### State Store

Store and retrieve state across service restarts:

```python
# Example: Using state store
from dapr.clients import DaprClient

with DaprClient() as d:
    # Save state
    d.save_state("todo-state-store", "key", "value")
    
    # Get state
    state = d.get_state("todo-state-store", "key")
```

### Service Invocation

Call other services securely:

```bash
# Using Dapr sidecar to invoke backend from frontend
curl http://localhost:3500/v1.0/invoke/todo-backend/method/api/todos
```

### Distributed Tracing

View traces in Zipkin at http://localhost:9411

### Secrets Management

```python
# Example: Get secrets from Kubernetes
from dapr.clients import DaprClient

with DaprClient() as d:
    secret = d.get_secret("todo-kubernetes-secrets", "database-url")
```

## 🛠️ Configuration

### Modifying Dapr Components

Edit `charts/todo-platform/values-minikube.yaml`:

```yaml
dapr:
  stateStore:
    enabled: true
    type: "redis"  # or "postgresql"
  
  bindings:
    cron:
      enabled: true
      schedule: "@every 5m"  # Change cron schedule
  
  secrets:
    enabled: true
    type: "kubernetes"  # or "local"
```

### Redeploy After Changes

```bash
helm upgrade --install todo-platform charts/todo-platform \
  --namespace todo \
  --values charts/todo-platform/values-minikube.yaml \
  --wait
```

## 🧪 Testing Dapr Features

### Test Pub/Sub

```bash
# Publish a test event
dapr publish --publish-app-id todo-backend \
  --pubsub todo-pubsub \
  --topic todo-created \
  --data '{"test": "message"}'
```

### Test State Store

```bash
# Save state
dapr invoke --app-id todo-backend \
  --method state/save \
  --data '{"key": "test", "value": "hello"}'

# Get state
dapr invoke --app-id todo-backend \
  --method state/get \
  --data '{"key": "test"}'
```

### Test Service Invocation

```bash
# Invoke backend health check via Dapr
dapr invoke --app-id todo-backend --method /api/health
```

## 📈 Monitoring

### View Dapr Metrics

```bash
# Port forward to Dapr metrics
kubectl port-forward -n dapr-system svc/dapr-operator 9090:9090

# Access Prometheus metrics
curl http://localhost:9090/metrics
```

### View Logs

```bash
# Backend application logs
kubectl logs -n todo -l app.kubernetes.io/name=backend -c backend

# Dapr sidecar logs
kubectl logs -n todo -l app.kubernetes.io/name=backend -c daprd

# Dapr operator logs
kubectl logs -n dapr-system -l app=dapr-operator
```

## 🧹 Cleanup

```bash
# Remove everything
./scripts/minikube-dapr-deploy.sh cleanup

# Or manually:
helm uninstall todo-platform -n todo
helm uninstall redis -n todo
dapr uninstall --kubernetes
minikube delete --profile=todo-dapr
```

## 🐛 Troubleshooting

### Dapr Sidecar Not Starting

```bash
# Check Dapr system pods
kubectl get pods -n dapr-system

# Check Dapr operator logs
kubectl logs -n dapr-system -l app=dapr-operator

# Restart Dapr
dapr uninstall --kubernetes
dapr init --kubernetes --wait
```

### Redis Connection Issues

```bash
# Check Redis pod
kubectl get pods -n todo -l app.kubernetes.io/name=redis

# Verify Redis secret
kubectl get secret redis -n todo -o yaml

# Test Redis connection
kubectl exec -it -n todo redis-master-0 -- redis-cli ping
```

### Port Forwarding Issues

```bash
# Kill existing port forwards
pkill -f "kubectl port-forward"

# Restart port forwards
kubectl port-forward -n todo svc/todo-backend 8000:8000 &
kubectl port-forward -n todo svc/todo-frontend 3000:3000 &
```

### Image Pull Errors

```bash
# Ensure images are built in Minikube's Docker
minikube -p todo-dapr docker-env | source
docker images | grep todo-

# Rebuild if needed
docker build -t todo-backend:latest backend/
docker build -t todo-frontend:latest frontend/
```

## 📚 Additional Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/)
- [Dapr State Store](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
- [Dapr Bindings](https://docs.dapr.io/reference/components-reference/supported-bindings/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

## 🎯 Next Steps

1. **Enable AI Features**: Set `mcp.enabled: true` and provide OpenAI API key
2. **Add Activity Logger**: Set `activityLogger.enabled: true`
3. **Custom Cron Jobs**: Add scheduled tasks in values file
4. **Production Database**: Switch from SQLite to PostgreSQL
5. **Monitoring**: Add Prometheus/Grafana

## 📊 Deployment Summary

| Component | Status | Access |
|-----------|--------|--------|
| Minikube | ✅ Running | `minikube dashboard --profile=todo-dapr` |
| Dapr Runtime | ✅ Installed | `dapr status -k` |
| Redis | ✅ Running | `redis-master:6379` |
| Backend | ✅ Running | http://localhost:8000 |
| Frontend | ✅ Running | http://localhost:3000 |
| Zipkin | ✅ Running | http://localhost:9411 |

---

**Last Updated**: February 12, 2026  
**Dapr Version**: 1.12.0  
**Status**: ✅ Full Dapr Deployment Complete
