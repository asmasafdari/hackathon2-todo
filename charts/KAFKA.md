# Kafka Configuration for Todo Platform

## Overview

Apache Kafka is used as the message broker for event-driven architecture.
Events are published by the backend and agent, consumed by activity-logger.

## Deployment

### Option 1: Deploy Kafka with Helm (Recommended for local dev)

```bash
# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka in the todo namespace
helm install kafka bitnami/kafka \
  --namespace todo \
  --set replicaCount=1 \
  --set persistence.enabled=false \
  --set zookeeper.persistence.enabled=false \
  --set listeners.client.protocol=PLAINTEXT
```

### Option 2: External Kafka

If using an external Kafka cluster, update the Dapr component:

```yaml
# values.yaml
kafka:
  brokers: "your-kafka-broker:9092"
  authType: "password"  # or sasl, tls
```

## Topics

The following topics are used:

| Topic | Publisher | Subscriber | Description |
|-------|-----------|------------|-------------|
| `todo-created` | backend, mcp | activity-logger | Todo creation events |
| `todo-updated` | backend, mcp | activity-logger | Todo update events |
| `todo-completed` | backend, mcp | activity-logger | Todo completion events |
| `todo-deleted` | backend, mcp | activity-logger | Todo deletion events |
| `agent-action-executed` | mcp | activity-logger | Agent action success |
| `agent-action-failed` | mcp | activity-logger | Agent action failure |

## Testing Kafka

```bash
# List topics
kubectl exec -it -n todo kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092

# Create a topic
kubectl exec -it -n todo kafka-0 -- kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Produce messages
kubectl exec -it -n todo kafka-0 -- kafka-console-producer.sh --topic test-topic --bootstrap-server localhost:9092

# Consume messages
kubectl exec -it -n todo kafka-0 -- kafka-console-consumer.sh --topic test-topic --from-beginning --bootstrap-server localhost:9092
```

## Troubleshooting

### Connection refused
```bash
# Check if Kafka pods are running
kubectl get pods -n todo -l app.kubernetes.io/name=kafka

# Check Kafka logs
kubectl logs -n todo -l app.kubernetes.io/name=kafka
```

### Topic not found
Topics are auto-created by Dapr. If disabled, create manually:
```bash
kubectl exec -it -n todo kafka-0 -- kafka-topics.sh --create --topic todo-created --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```
