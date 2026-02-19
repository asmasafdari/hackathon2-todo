# Quickstart: Event-Driven Todo Platform

**Feature**: 004-event-driven-kafka
**Date**: 2026-01-23

This guide covers setting up the event-driven architecture locally with Dapr, Kafka, and the activity logger service.

---

## Prerequisites

Before starting, ensure you have:

- [ ] Docker Desktop running
- [ ] Minikube installed and running (`minikube start --memory 8192 --cpus 4`)
- [ ] Helm v3 installed
- [ ] Dapr CLI installed (`winget install Dapr.CLI` or `brew install dapr/tap/dapr-cli`)
- [ ] kubectl configured for Minikube

## 1. Install Dapr on Kubernetes

```bash
# Initialize Dapr in the cluster
dapr init -k

# Verify installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   VERSION
# dapr-dashboard         dapr-system  True     Running  ...
# dapr-sidecar-injector  dapr-system  True     Running  ...
# dapr-operator          dapr-system  True     Running  ...
# dapr-placement-server  dapr-system  True     Running  ...
# dapr-sentry            dapr-system  True     Running  ...
```

## 2. Deploy Kafka

Use the Bitnami Kafka Helm chart for local development:

```bash
# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka (single-node for dev) with topics for each event type
helm install kafka bitnami/kafka \
  --set listeners.client.protocol=PLAINTEXT \
  --set controller.replicaCount=1 \
  --set provisioning.enabled=true \
  --set provisioning.topics[0].name=todo.created \
  --set provisioning.topics[0].partitions=3 \
  --set provisioning.topics[0].replicationFactor=1 \
  --set provisioning.topics[1].name=todo.updated \
  --set provisioning.topics[1].partitions=3 \
  --set provisioning.topics[1].replicationFactor=1 \
  --set provisioning.topics[2].name=todo.completed \
  --set provisioning.topics[2].partitions=3 \
  --set provisioning.topics[2].replicationFactor=1 \
  --set provisioning.topics[3].name=todo.deleted \
  --set provisioning.topics[3].partitions=3 \
  --set provisioning.topics[3].replicationFactor=1 \
  --set provisioning.topics[4].name=agent.action \
  --set provisioning.topics[4].partitions=3 \
  --set provisioning.topics[4].replicationFactor=1 \
  --wait

# Verify Kafka is running
kubectl get pods -l app.kubernetes.io/name=kafka
```

## 3. Deploy Dapr Components

Create the Kafka pub/sub component:

```bash
# Apply Dapr Kafka component
kubectl apply -f - <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.default.svc.cluster.local:9092"
    - name: authType
      value: "none"
    - name: consumerGroup
      value: "todo-platform"
  scopes:
    - todo-backend
    - activity-logger
    - mcp-server
EOF

# Verify component
dapr components -k
```

## 4. Deploy the Platform

```bash
# Update Helm dependencies (if subchart)
cd charts/todo-platform
helm dependency update

# Install/upgrade the platform
helm upgrade --install todo-platform . \
  --set global.dapr.enabled=true \
  --set kafka.enabled=false \  # Using external Kafka from step 2
  --set activityLogger.enabled=true \
  --wait

# Verify all pods have Dapr sidecars
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

## 5. Verify Event Flow

### Publish a Test Event

```bash
# Port-forward the backend
kubectl port-forward svc/todo-backend 8000:80 &

# Create a todo (should emit event)
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test event publishing", "description": "Verify Kafka receives event"}'
```

### Check Activity Logger

```bash
# Port-forward the activity logger
kubectl port-forward svc/activity-logger 8001:80 &

# Query logs (should show the create event)
curl http://localhost:8001/logs
```

### Check Kafka Topic (Optional)

```bash
# Exec into Kafka pod to read messages
kubectl exec -it kafka-controller-0 -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic todo-events \
  --from-beginning \
  --max-messages 5
```

## 6. Local Development (Without Kubernetes)

For faster iteration during development:

```bash
# Start Dapr standalone mode
dapr init

# Run Kafka locally (Docker Compose)
cat > docker-compose.kafka.yml <<EOF
version: '3'
services:
  kafka:
    image: bitnami/kafka:latest
    ports:
      - "9092:9092"
    environment:
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
EOF

docker-compose -f docker-compose.kafka.yml up -d

# Create Dapr component for local development
mkdir -p ~/.dapr/components
cat > ~/.dapr/components/kafka-pubsub.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "localhost:9092"
    - name: authType
      value: "none"
EOF

# Run backend with Dapr sidecar
cd backend
dapr run --app-id todo-backend --app-port 8000 -- uvicorn main:app --host 0.0.0.0 --port 8000

# Run activity logger with Dapr sidecar (in another terminal)
cd activity-logger
dapr run --app-id activity-logger --app-port 8001 -- uvicorn main:app --host 0.0.0.0 --port 8001
```

## Troubleshooting

### Events Not Appearing in Activity Logger

1. Check Dapr sidecar logs:
   ```bash
   kubectl logs -l app=todo-backend -c daprd
   ```

2. Verify subscription is registered:
   ```bash
   curl http://localhost:3500/v1.0/subscribe
   ```

3. Check for consumer group offsets:
   ```bash
   kubectl exec kafka-controller-0 -- kafka-consumer-groups.sh \
     --bootstrap-server localhost:9092 \
     --group todo-platform \
     --describe
   ```

### Dapr Sidecar Not Starting

1. Check Dapr operator logs:
   ```bash
   kubectl logs -n dapr-system -l app=dapr-sidecar-injector
   ```

2. Verify annotations:
   ```bash
   kubectl get deployment todo-backend -o jsonpath='{.spec.template.metadata.annotations}'
   ```

### Kafka Connection Issues

1. Check broker accessibility from pods:
   ```bash
   kubectl run -it --rm debug --image=busybox --restart=Never -- \
     nc -zv kafka.default.svc.cluster.local 9092
   ```

2. Verify topic exists:
   ```bash
   kubectl exec kafka-controller-0 -- kafka-topics.sh \
     --bootstrap-server localhost:9092 \
     --list
   ```

---

## Automated Deployment (Recommended)

Use the provided deployment script for one-command setup:

```bash
# Deploy everything (Dapr, Kafka, and the platform)
./scripts/deploy-kafka-dapr.sh

# Run E2E validation to verify event flow
./scripts/validate-e2e.sh
```

## What's Included

After successful deployment, you'll have:

✅ **Dapr** running in the cluster with sidecar injection enabled  
✅ **Kafka** with auto-created topics for all event types:
- `todo-created`, `todo-updated`, `todo-completed`, `todo-deleted`
- `agent-action-executed`, `agent-action-failed`  
✅ **Backend** with Dapr sidecar publishing events on all CRUD operations  
✅ **Activity Logger** consuming and persisting all events  
✅ **MCP Server** (AI Agent) publishing agent action events  
✅ **Frontend** for user interactions  

## Event Flow Verification

```bash
# Check all pods are running with Dapr sidecars
kubectl get pods -n todo

# View event publishing logs
kubectl logs -n todo -l app=backend -c backend -f

# View event consumption logs  
kubectl logs -n todo -l app=activity-logger -c activity-logger -f

# Query activity logs API
kubectl port-forward svc/activity-logger -n todo 8081:8081
curl http://localhost:8081/logs
curl http://localhost:8081/logs/stats
```

## Next Steps

1. Review the [spec.md](spec.md) for full requirements
2. Review the [data-model.md](data-model.md) for event schemas
3. Review the [ARCHITECTURE.md](ARCHITECTURE.md) for design details
4. Check [SETUP.md](SETUP.md) for detailed deployment instructions
