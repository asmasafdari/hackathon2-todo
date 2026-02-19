#!/bin/bash
# Minikube Deployment Script (Phase V)
# Deploys Todo Platform with Dapr, Strimzi Kafka, and all microservices

set -e

echo "Todo Platform - Minikube Deployment (Phase V)"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check prerequisites
check_prerequisites() {
    echo ""
    echo "Checking prerequisites..."

    for cmd in minikube kubectl helm docker; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}$cmd not found. Please install it first.${NC}"
            exit 1
        fi
        echo -e "${GREEN}  $cmd installed${NC}"
    done

    if command -v dapr &> /dev/null; then
        echo -e "${GREEN}  dapr CLI installed${NC}"
    else
        echo -e "${YELLOW}  dapr CLI not found - will install Dapr via kubectl${NC}"
    fi
}

# Start Minikube
start_minikube() {
    echo ""
    echo "[1/8] Starting Minikube..."

    if minikube status 2>/dev/null | grep -q "Running"; then
        echo -e "${YELLOW}  Minikube is already running${NC}"
    else
        minikube start --cpus=4 --memory=8192 --disk-size=20g
        echo -e "${GREEN}  Minikube started${NC}"
    fi

    minikube addons enable ingress
    kubectl get nodes
}

# Configure Docker to use Minikube's daemon
configure_docker() {
    echo ""
    echo "[2/8] Configuring Docker environment..."

    case "$OSTYPE" in
        linux*|darwin*)
            eval $(minikube docker-env)
            ;;
        msys*|cygwin*|win*)
            eval $(minikube docker-env --shell bash)
            ;;
    esac

    echo -e "${GREEN}  Docker configured for Minikube${NC}"
}

# Build images
build_images() {
    echo ""
    echo "[3/8] Building container images..."

    echo "  Building backend..."
    docker build -t todo-backend:latest backend/

    echo "  Building chatbot-frontend..."
    docker build -t todo-frontend:latest chatbot-frontend/

    echo -e "${GREEN}  All images built${NC}"
}

# Install Dapr
install_dapr() {
    echo ""
    echo "[4/8] Installing Dapr on Kubernetes..."

    if command -v dapr &> /dev/null; then
        if dapr status -k 2>/dev/null | grep -q "Running"; then
            echo -e "${YELLOW}  Dapr already installed${NC}"
        else
            dapr init -k --wait
            echo -e "${GREEN}  Dapr installed${NC}"
        fi
    else
        # Install Dapr via Helm if CLI not available
        helm repo add dapr https://dapr.github.io/helm-charts/ 2>/dev/null || true
        helm repo update
        kubectl create namespace dapr-system --dry-run=client -o yaml | kubectl apply -f -
        helm upgrade --install dapr dapr/dapr --namespace dapr-system --wait
        echo -e "${GREEN}  Dapr installed via Helm${NC}"
    fi
}

# Install Kafka (Strimzi)
install_kafka() {
    echo ""
    echo "[5/8] Installing Kafka (Strimzi operator)..."

    kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

    # Install Strimzi operator
    kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka 2>/dev/null || true

    echo "  Waiting for Strimzi operator to be ready..."
    kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=180s 2>/dev/null || \
        echo -e "${YELLOW}  Strimzi operator may still be starting${NC}"

    # Deploy Kafka cluster
    kubectl apply -f k8s/kafka/kafka-cluster.yaml
    echo "  Waiting for Kafka cluster..."
    kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=300s -n kafka 2>/dev/null || \
        echo -e "${YELLOW}  Kafka cluster may still be starting${NC}"

    # Create topics
    kubectl apply -f k8s/kafka/topics.yaml
    echo -e "${GREEN}  Kafka and topics deployed${NC}"
}

# Deploy Dapr components
deploy_dapr_components() {
    echo ""
    echo "[6/8] Deploying Dapr components..."

    kubectl create namespace todo --dry-run=client -o yaml | kubectl apply -f -
    kubectl apply -f dapr/components/ -n todo
    echo -e "${GREEN}  Dapr components deployed${NC}"
}

# Deploy with Helm
deploy_helm() {
    echo ""
    echo "[7/8] Deploying application with Helm..."

    # Check if secrets file exists
    if [ ! -f "charts/todo-platform/values-secrets.yaml" ]; then
        echo -e "${YELLOW}  Creating sample secrets file...${NC}"
        cat > charts/todo-platform/values-secrets.yaml <<EOF
secrets:
  databaseUrl: "sqlite:///app/data/todos.db"
  openaiApiKey: ""
EOF
        echo -e "${YELLOW}  Edit charts/todo-platform/values-secrets.yaml with your actual secrets${NC}"
    fi

    # Update Helm dependencies
    cd charts/todo-platform
    helm dependency update 2>/dev/null || true
    cd ../..

    # Deploy
    helm upgrade --install todo-platform charts/todo-platform \
        -f charts/todo-platform/values.yaml \
        -f charts/todo-platform/values-minikube.yaml \
        -f charts/todo-platform/values-secrets.yaml \
        --namespace todo \
        --set backend.image.repository=todo-backend \
        --set backend.image.tag=latest \
        --set frontend.image.repository=todo-frontend \
        --set frontend.image.tag=latest \
        --set kafka.enabled=true \
        --set dapr.pubsub.enabled=true \
        --set dapr.stateStore.enabled=true \
        --set dapr.secrets.enabled=true \
        --wait \
        --timeout 5m 2>/dev/null || echo -e "${YELLOW}  Some pods may still be starting${NC}"

    echo -e "${GREEN}  Helm deployment complete${NC}"
}

# Show status
show_status() {
    echo ""
    echo "[8/8] Verifying deployment..."
    echo ""

    echo "=== Pod Status (todo namespace) ==="
    kubectl get pods -n todo 2>/dev/null || true

    echo ""
    echo "=== Pod Status (kafka namespace) ==="
    kubectl get pods -n kafka 2>/dev/null || true

    echo ""
    echo "=== Dapr Status ==="
    dapr status -k 2>/dev/null || kubectl get pods -n dapr-system 2>/dev/null || true

    echo ""
    echo "=== Services ==="
    kubectl get svc -n todo 2>/dev/null || true

    echo ""
    echo -e "${BLUE}Access the application:${NC}"
    echo "   Option 1: minikube tunnel (recommended)"
    echo "      Run: minikube tunnel"
    echo "      Then access: http://localhost"
    echo ""
    echo "   Option 2: Port forward"
    echo "      kubectl port-forward -n todo svc/todo-platform-frontend 3000:3000"
    echo "      kubectl port-forward -n todo svc/todo-platform-backend 8000:8000"
    echo ""
    echo "   Option 3: Minikube service"
    echo "      minikube service todo-platform-frontend -n todo"
}

# Main
main() {
    check_prerequisites
    start_minikube
    configure_docker
    build_images
    install_dapr
    install_kafka
    deploy_dapr_components
    deploy_helm
    show_status

    echo ""
    echo -e "${GREEN}Deployment complete!${NC}"
    echo ""
    echo "Useful commands:"
    echo "   View logs:    kubectl logs -n todo -l app=backend"
    echo "   Dapr dash:    dapr dashboard -k"
    echo "   Scale:        kubectl scale deployment -n todo todo-platform-backend --replicas=3"
    echo "   Teardown:     helm uninstall todo-platform -n todo"
    echo "   Stop:         minikube stop"
}

main
