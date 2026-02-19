# Phase V Setup - Event-Driven Architecture

Complete setup guide for the event-driven architecture with Kafka and Dapr.

## Prerequisites

- Minikube running
- Helm installed
- kubectl configured

## Step-by-Step Deployment

### 1. Install Dapr on Kubernetes

```bash
# Install Dapr CLI if not already installed
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr is running
kubectl get pods -n dapr-system
```

### 2. Deploy Kafka

```bash
# Add Bitnami Helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka (lightweight single-node for dev)
helm install kafka bitnami/kafka \
  --namespace todo \
  --create-namespace \
  --set replicaCount=1 \
  --set persistence.enabled=false \
  --set zookeeper.persistence.enabled=false \
  --set listeners.client.protocol=PLAINTEXT

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n todo --timeout=300s
```

### 3. Build All Images

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend
docker build -t todo-backend:latest backend/

# Build frontend
docker build -t todo-frontend:latest frontend/

# Build MCP server
docker build -t todo-mcp:latest agent/

# Build activity-logger
docker build -t todo-activity-logger:latest activity-logger/
```

### 4. Deploy the Platform

```bash
# Create secrets file
cat > charts/todo-platform/values-secrets.yaml <<EOF
secrets:
  databaseUrl: "postgresql://user:pass@your-neon-host/db?sslmode=require"
  openaiApiKey: "sk-your-openai-api-key"
EOF

# Deploy with Helm
helm install todo-platform charts/todo-platform \
  -f charts/todo-platform/values.yaml \
  -f charts/todo-platform/values-secrets.yaml \
  --namespace todo

# Wait for all pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-platform -n todo --timeout=300s
```

### 5. Verify Event Flow

```bash
# Check all pods are running
kubectl get pods -n todo

# View backend logs (should show Dapr sidecar ready)
kubectl logs -n todo deployment/todo-platform-backend -c backend

# View activity-logger logs
kubectl logs -n todo deployment/todo-platform-activity-logger -c activity-logger

# Access the frontend
minikube service frontend -n todo
```

### 6. Test Events

```bash
# Create a todo via the API
BACKEND_URL=$(minikube service backend -n todo --url)
curl -X POST $BACKEND_URL/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Event", "description": "Testing event flow"}'

# Query activity logs
ACTIVITY_URL=$(minikube service activity-logger -n todo --url)
curl $ACTIVITY_URL/logs

# View stats
curl $ACTIVITY_URL/logs/stats
```

## Architecture Verification

### Check Event Publishing

```bash
# Watch backend logs for event publishing
kubectl logs -n todo deployment/todo-platform-backend -c backend -f

# Watch activity-logger for event consumption
kubectl logs -n todo deployment/todo-platform-activity-logger -c activity-logger -f
```

### Check Kafka Topics

```bash
# List topics
kubectl exec -it -n todo kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092

# Expected topics:
# - agent-action-executed
# - agent-action-failed
```

### Check Dapr Components

```bash
# List Dapr components
kubectl get components -n todo

# Check pub/sub status
kubectl describe component kafka-pubsub -n todo
```

## Troubleshooting

### Dapr sidecar not injecting

```bash
# Check Dapr is installed
kubectl get pods -n dapr-system

# Restart deployment to trigger injection
kubectl rollout restart deployment -n todo
```

### Kafka connection refused

```bash
# Check Kafka is running
kubectl get pods -n todo -l app.kubernetes.io/name=kafka

# Check Kafka logs
kubectl logs -n todo kafka-0

# Test connectivity
kubectl exec -it -n todo kafka-0 -- kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

### Events not being published

```bash
# Check Dapr sidecar logs
kubectl logs -n todo deployment/todo-platform-backend -c daprd

# Verify pub/sub component
kubectl get component kafka-pubsub -n todo -o yaml
```

### Activity logger not receiving events

```bash
# Check Dapr subscription
kubectl logs -n todo deployment/todo-platform-activity-logger -c daprd

# Verify subscription is registered
kubectl exec -it -n todo deployment/todo-platform-activity-logger -c daprd -- curl localhost:3500/v1.0/subscribe
```

## Monitoring

### Dapr Dashboard

```bash
# Port forward Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080

# Access at http://localhost:8080
```

### View Metrics

```bash
# Check Dapr metrics
kubectl exec -it -n todo deployment/todo-platform-backend -c daprd -- curl localhost:9090/metrics
```

## Cleanup

```bash
# Uninstall the platform
helm uninstall todo-platform -n todo

# Uninstall Kafka
helm uninstall kafka -n todo

# Uninstall Dapr
dapr uninstall -k

# Delete namespace
kubectl delete namespace todo
```

## Next Steps

1. **Scale Kafka**: For production, use multi-node Kafka cluster
2. **Add Monitoring**: Prometheus + Grafana for metrics
3. **Configure Persistence**: Enable persistent volumes for Kafka
4. **Secure**: Add TLS/mTLS for Kafka and Dapr
5. **Add More Consumers**: Notifications service, Analytics service

## Architecture Diagram

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend   │────▶│    Kafka     │
└──────────────┘     └──────┬──────┘     │   (Dapr)     │
                            │            └──────┬───────┘
                     ┌──────▼──────┐           │
                     │ Dapr Sidecar│           │
                     └─────────────┘           │
                                               │
┌──────────────┐     ┌─────────────┐          │
│     MCP      │────▶│ Dapr Sidecar│──────────┘
│  (AI Agent)  │     └─────────────┘
└──────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Activity Logger │
                  │  (Event Consumer)│
                  └──────────────────┘
```
