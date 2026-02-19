#!/bin/bash
# Kafka Event-Driven Deployment Script
# Deploys Todo Platform with Kafka for event-driven architecture

set -e

echo "📨 Todo Platform - Event-Driven Deployment (Kafka + Dapr)"
echo "========================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="${NAMESPACE:-todo}"

# Check prerequisites
check_prerequisites() {
    echo ""
    echo "🔍 Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found${NC}"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}❌ Helm not found${NC}"
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl get nodes &> /dev/null; then
        echo -e "${RED}❌ No Kubernetes cluster accessible${NC}"
        echo "   Run one of:"
        echo "      ./scripts/minikube-deploy.sh (for local)"
        echo "      ./scripts/doks-deploy.sh (for DigitalOcean)"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Kubernetes cluster accessible${NC}"
}

# Install Dapr
install_dapr() {
    echo ""
    echo "🔌 Installing Dapr..."
    
    # Check if Dapr CLI is installed
    if ! command -v dapr &> /dev/null; then
        echo -e "${YELLOW}⚠️  Dapr CLI not found. Installing...${NC}"
        wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
    fi
    
    # Check if Dapr is already installed in cluster
    if helm list -n dapr-system 2>/dev/null | grep -q dapr; then
        echo -e "${GREEN}✓ Dapr already installed in cluster${NC}"
    else
        echo "Installing Dapr runtime..."
        helm repo add dapr https://dapr.github.io/helm-charts/
        helm repo update
        helm upgrade --install dapr dapr/dapr \
            --namespace dapr-system \
            --create-namespace \
            --wait
        echo -e "${GREEN}✓ Dapr installed${NC}"
    fi
}

# Deploy Kafka
deploy_kafka() {
    echo ""
    echo "🚀 Deploying Kafka..."
    
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    # Check if Kafka already exists
    if helm list -n "$NAMESPACE" 2>/dev/null | grep -q kafka; then
        echo -e "${YELLOW}⚠️  Kafka already deployed${NC}"
    else
        helm upgrade --install kafka bitnami/kafka \
            --namespace "$NAMESPACE" \
            --create-namespace \
            --set replicaCount=1 \
            --set persistence.enabled=false \
            --set zookeeper.persistence.enabled=false \
            --set listeners.client.protocol=PLAINTEXT \
            --wait \
            --timeout 5m
        
        echo -e "${GREEN}✓ Kafka deployed${NC}"
    fi
    
    # Get Kafka broker address
    KAFKA_BROKER="kafka.$NAMESPACE.svc.cluster.local:9092"
    echo "   Kafka broker: $KAFKA_BROKER"
}

# Deploy Dapr Pub/Sub Component
deploy_dapr_component() {
    echo ""
    echo "📦 Deploying Dapr Pub/Sub Component..."
    
    kubectl apply -f - <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: $NAMESPACE
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: kafka.$NAMESPACE.svc.cluster.local:9092
  - name: authType
    value: none
  - name: disableTls
    value: "true"
  - name: consumerGroup
    value: todo-consumers
  - name: initialOffset
    value: oldest
  - name: backOffDuration
    value: 5s
  - name: backOffMaxRetries
    value: "3"
EOF
    
    echo -e "${GREEN}✓ Dapr component deployed${NC}"
}

# Create Kafka topics
create_topics() {
    echo ""
    echo "📋 Creating Kafka topics..."
    
    TOPICS=(
        "todo-created"
        "todo-updated"
        "todo-completed"
        "todo-deleted"
        "agent-action-executed"
        "agent-action-failed"
        "dead-letter"
    )
    
    # Wait for Kafka to be ready
    echo "Waiting for Kafka to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n "$NAMESPACE" --timeout=120s
    
    for topic in "${TOPICS[@]}"; do
        echo "   Creating topic: $topic"
        kubectl exec -n "$NAMESPACE" kafka-0 -- \
            kafka-topics.sh --create \
            --topic "$topic" \
            --bootstrap-server localhost:9092 \
            --partitions 3 \
            --replication-factor 1 \
            2>/dev/null || echo "     (Topic may already exist)"
    done
    
    echo -e "${GREEN}✓ Topics created${NC}"
}

# Deploy app with event-driven enabled
deploy_app() {
    echo ""
    echo "🎯 Deploying application with event-driven mode..."
    
    # Create values file for event-driven mode
    cat > charts/todo-platform/values-kafka.yaml <<EOF
# Event-driven specific values
dapr:
  enabled: true
  logLevel: info
  pubsub:
    enabled: true

backend:
  dapr:
    appPort: 8000
    appId: backend
    enabled: true

activityLogger:
  dapr:
    appPort: 8081
    appId: activity-logger
    enabled: true
    subscriptions:
      - pubsubname: kafka-pubsub
        topic: todo-created
        route: /events/todo-created
      - pubsubname: kafka-pubsub
        topic: todo-updated
        route: /events/todo-updated
      - pubsubname: kafka-pubsub
        topic: todo-completed
        route: /events/todo-completed
      - pubsubname: kafka-pubsub
        topic: todo-deleted
        route: /events/todo-deleted
      - pubsubname: kafka-pubsub
        topic: agent-action-executed
        route: /events/agent-action-executed
      - pubsubname: kafka-pubsub
        topic: agent-action-failed
        route: /events/agent-action-failed
EOF
    
    # Deploy with event-driven values
    helm upgrade --install todo-platform charts/todo-platform \
        -f charts/todo-platform/values.yaml \
        -f charts/todo-platform/values-secrets.yaml \
        -f charts/todo-platform/values-kafka.yaml \
        --namespace "$NAMESPACE" \
        --wait \
        --timeout 5m
    
    echo -e "${GREEN}✓ Application deployed${NC}"
}

# Annotate pods for Dapr
annotate_pods() {
    echo ""
    echo "🏷️  Annotating pods for Dapr sidecar injection..."
    
    kubectl patch deployment todo-platform-backend -n "$NAMESPACE" --type=json -p='[{"op": "add", "path": "/spec/template/metadata/annotations/dapr.io~1enabled", "value": "true"}, {"op": "add", "path": "/spec/template/metadata/annotations/dapr.io~1app-id", "value": "backend"}, {"op": "add", "path": "/spec/template/metadata/annotations/dapr.io~1app-port", "value": "8000"}]'
    
    kubectl patch deployment todo-platform-activity-logger -n "$NAMESPACE" --type=json -p='[{"op": "add", "path": "/spec/template/metadata/annotations/dapr.io~1enabled", "value": "true"}, {"op": "add", "path": "/spec/template/metadata/annotations/dapr.io~1app-id", "value": "activity-logger"}, {"op": "add", "path": "/spec/template/metadata/annotations/dapr.io~1app-port", "value": "8081"}]'
    
    echo -e "${GREEN}✓ Pods annotated${NC}"
    
    # Wait for rollout
    echo "Waiting for pods to restart with Dapr sidecars..."
    kubectl rollout status deployment/todo-platform-backend -n "$NAMESPACE" --timeout=120s
    kubectl rollout status deployment/todo-platform-activity-logger -n "$NAMESPACE" --timeout=120s
}

# Test event flow
test_events() {
    echo ""
    echo "🧪 Testing event flow..."
    
    echo ""
    echo "Creating a test todo via API..."
    BACKEND_POD=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}')
    
    kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- \
        curl -s -X POST http://localhost:8000/api/todos \
        -H "Content-Type: application/json" \
        -d '{"title":"Test Event Todo","description":"Testing event-driven flow"}' || true
    
    echo ""
    echo "Checking activity logger..."
    sleep 2
    
    ACTIVITY_POD=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=activity-logger -o jsonpath='{.items[0].metadata.name}')
    kubectl logs -n "$NAMESPACE" "$ACTIVITY_POD" --tail=20 | grep -i "todo-created" || echo "   (Check logs manually: kubectl logs -n $NAMESPACE $ACTIVITY_POD)"
    
    echo ""
    echo "Checking Kafka topics..."
    kubectl exec -n "$NAMESPACE" kafka-0 -- \
        kafka-topics.sh --list --bootstrap-server localhost:9092
}

# Show status
show_status() {
    echo ""
    echo "📊 Event-Driven Status:"
    echo "======================="
    
    echo ""
    echo "Kafka Pods:"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka
    
    echo ""
    echo "Dapr Components:"
    kubectl get components -n "$NAMESPACE"
    
    echo ""
    echo "Application Pods (with Dapr sidecars):"
    kubectl get pods -n "$NAMESPACE" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{range .spec.containers[*]}{.name}{" "}{end}{"\n"}{end}'
    
    echo ""
    echo -e "${BLUE}📚 Event Topics:${NC}"
    echo "   todo-created - Emitted when a todo is created"
    echo "   todo-updated - Emitted when a todo is updated"
    echo "   todo-completed - Emitted when a todo is marked complete"
    echo "   todo-deleted - Emitted when a todo is deleted"
    echo "   agent-action-executed - Emitted when AI agent performs action"
    echo "   agent-action-failed - Emitted when AI agent action fails"
    
    echo ""
    echo "🔧 Useful commands:"
    echo "   View Kafka topics: kubectl exec -n $NAMESPACE kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092"
    echo "   Produce test message: kubectl exec -n $NAMESPACE kafka-0 -- kafka-console-producer.sh --topic todo-created --bootstrap-server localhost:9092"
    echo "   Consume messages: kubectl exec -n $NAMESPACE kafka-0 -- kafka-console-consumer.sh --topic todo-created --from-beginning --bootstrap-server localhost:9092"
    echo "   Dapr dashboard: dapr dashboard -k"
}

# Main
main() {
    check_prerequisites
    install_dapr
    deploy_kafka
    deploy_dapr_component
    create_topics
    deploy_app
    annotate_pods
    test_events
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 Event-driven deployment complete!${NC}"
}

# Run
main
