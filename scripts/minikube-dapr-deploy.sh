#!/bin/bash
set -e

# =============================================================================
# Minikube + Full Dapr Deployment Script
# =============================================================================
# This script deploys the Todo Platform to Minikube with full Dapr integration:
# - Pub/Sub (Kafka or Redis)
# - State Store (Redis)
# - Bindings (Cron)
# - Secrets (Kubernetes)
# - Service Invocation
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MINIKUBE_PROFILE="${MINIKUBE_PROFILE:-todo-dapr}"
NAMESPACE="${NAMESPACE:-todo}"
DAPR_VERSION="${DAPR_VERSION:-1.12.0}"
HELM_TIMEOUT="${HELM_TIMEOUT:-10m}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_tools=()
    
    if ! command -v minikube &> /dev/null; then
        missing_tools+=("minikube")
    fi
    
    if ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi
    
    if ! command -v helm &> /dev/null; then
        missing_tools+=("helm")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! command -v dapr &> /dev/null; then
        missing_tools+=("dapr")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        echo ""
        echo "Please install the missing tools:"
        echo "  - minikube: https://minikube.sigs.k8s.io/docs/start/"
        echo "  - kubectl: https://kubernetes.io/docs/tasks/tools/"
        echo "  - helm: https://helm.sh/docs/intro/install/"
        echo "  - docker: https://docs.docker.com/get-docker/"
        echo "  - dapr: https://docs.dapr.io/getting-started/install-dapr-cli/"
        exit 1
    fi
    
    log_success "All prerequisites installed"
}

start_minikube() {
    log_info "Starting Minikube cluster..."
    
    if minikube profile list | grep -q "$MINIKUBE_PROFILE"; then
        log_warning "Minikube profile '$MINIKUBE_PROFILE' already exists"
        minikube profile "$MINIKUBE_PROFILE"
        if minikube status | grep -q "Running"; then
            log_success "Minikube is already running"
            return
        fi
    else
        minikube profile "$MINIKUBE_PROFILE"
    fi
    
    # Start Minikube with adequate resources for Dapr
    minikube start \
        --profile="$MINIKUBE_PROFILE" \
        --driver=docker \
        --kubernetes-version=stable \
        --cpus=4 \
        --memory=8192 \
        --disk-size=30g \
        --addons=ingress,dashboard,metrics-server
    
    log_success "Minikube started successfully"
}

enable_minikube_addons() {
    log_info "Enabling Minikube addons..."
    
    minikube addons enable ingress
    minikube addons enable metrics-server
    minikube addons enable dashboard
    
    log_success "Minikube addons enabled"
}

install_dapr() {
    log_info "Installing Dapr runtime on Minikube..."
    
    # Check if Dapr is already installed
    if helm list -n dapr-system | grep -q "dapr"; then
        log_warning "Dapr is already installed"
        read -p "Do you want to upgrade Dapr? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            helm upgrade dapr dapr/dapr \
                --namespace dapr-system \
                --version "$DAPR_VERSION" \
                --set global.ha.enabled=true \
                --wait
            log_success "Dapr upgraded successfully"
        fi
        return
    fi
    
    # Add Dapr Helm repo
    if ! helm repo list | grep -q "dapr"; then
        helm repo add dapr https://dapr.github.io/helm-charts/
        helm repo update
    fi
    
    # Create dapr-system namespace
    kubectl create namespace dapr-system --dry-run=client -o yaml | kubectl apply -f -
    
    # Install Dapr with high availability
    helm install dapr dapr/dapr \
        --namespace dapr-system \
        --version "$DAPR_VERSION" \
        --set global.ha.enabled=true \
        --set global.mtls.enabled=true \
        --wait
    
    log_success "Dapr installed successfully"
}

install_redis() {
    log_info "Installing Redis (for Dapr State Store and Pub/Sub)..."
    
    # Add Bitnami Helm repo
    if ! helm repo list | grep -q "bitnami"; then
        helm repo add bitnami https://charts.bitnami.com/bitnami
        helm repo update
    fi
    
    # Check if Redis is already installed
    if helm list -n "$NAMESPACE" | grep -q "redis"; then
        log_warning "Redis is already installed"
        return
    fi
    
    # Create namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Install Redis
    helm install redis bitnami/redis \
        --namespace "$NAMESPACE" \
        --set auth.enabled=true \
        --set auth.password=redis-password \
        --set architecture=standalone \
        --wait
    
    log_success "Redis installed successfully"
}

install_kafka() {
    log_info "Installing Kafka (for Dapr Pub/Sub)..."
    
    # Add Bitnami Helm repo (if not already added)
    if ! helm repo list | grep -q "bitnami"; then
        helm repo add bitnami https://charts.bitnami.com/bitnami
        helm repo update
    fi
    
    # Check if Kafka is already installed
    if helm list -n "$NAMESPACE" | grep -q "kafka"; then
        log_warning "Kafka is already installed"
        return
    fi
    
    # Install Kafka
    helm install kafka bitnami/kafka \
        --namespace "$NAMESPACE" \
        --set replicaCount=1 \
        --set zookeeper.replicaCount=1 \
        --set persistence.size=8Gi \
        --wait
    
    log_success "Kafka installed successfully"
}

install_zipkin() {
    log_info "Installing Zipkin (for Dapr distributed tracing)..."
    
    if kubectl get deployment zipkin -n dapr-system &> /dev/null; then
        log_warning "Zipkin is already installed"
        return
    fi
    
    kubectl create deployment zipkin \
        --image openzipkin/zipkin-slim:2 \
        --namespace dapr-system \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl expose deployment zipkin \
        --type ClusterIP \
        --port 9411 \
        --namespace dapr-system \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Zipkin installed successfully"
}

build_images() {
    log_info "Building Docker images..."
    
    # Set Docker to use Minikube's Docker daemon
    eval $(minikube -p "$MINIKUBE_PROFILE" docker-env)
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t todo-backend:latest -f backend/Dockerfile backend/
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -t todo-frontend:latest -f frontend/Dockerfile frontend/
    
    # Build MCP image (optional)
    if [ -d "agent" ] && [ -f "agent/Dockerfile" ]; then
        log_info "Building MCP agent image..."
        docker build -t todo-mcp:latest -f agent/Dockerfile agent/
    fi
    
    # Build Activity Logger image (optional)
    if [ -d "activity_logger" ] && [ -f "activity_logger/Dockerfile" ]; then
        log_info "Building activity-logger image..."
        docker build -t todo-activity-logger:latest -f activity_logger/Dockerfile activity_logger/
    fi
    
    log_success "Docker images built successfully"
}

create_secrets() {
    log_info "Creating Kubernetes secrets..."
    
    # Create Redis secret
    kubectl create secret generic redis \
        --namespace "$NAMESPACE" \
        --from-literal=redis-password=redis-password \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create application secrets
    kubectl create secret generic todo-secrets \
        --namespace "$NAMESPACE" \
        --from-literal=database-url="sqlite+aiosqlite:///tmp/todos.db" \
        --from-literal=openai-api-key="" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Secrets created successfully"
}

deploy_application() {
    log_info "Deploying Todo Platform with Dapr..."
    
    # Create namespace if not exists
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Update Helm dependencies
    helm dependency update charts/todo-platform
    
    # Deploy with Helm
    helm upgrade --install todo-platform charts/todo-platform \
        --namespace "$NAMESPACE" \
        --values charts/todo-platform/values-minikube.yaml \
        --timeout "$HELM_TIMEOUT" \
        --wait
    
    log_success "Application deployed successfully"
}

wait_for_pods() {
    log_info "Waiting for all pods to be ready..."
    
    kubectl wait --for=condition=ready pod \
        --all \
        --namespace "$NAMESPACE" \
        --timeout=300s
    
    log_success "All pods are ready"
}

setup_port_forwarding() {
    log_info "Setting up port forwarding..."
    
    # Kill existing port-forwards
    pkill -f "kubectl port-forward.*$NAMESPACE" 2>/dev/null || true
    
    # Start port forwards in background
    kubectl port-forward -n "$NAMESPACE" svc/frontend 3000:3000 &
    kubectl port-forward -n "$NAMESPACE" svc/backend 8000:8000 &
    kubectl port-forward -n dapr-system svc/zipkin 9411:9411 &
    
    log_success "Port forwarding configured:"
    log_info "  Frontend: http://localhost:3000"
    log_info "  Backend API: http://localhost:8000/api/docs"
    log_info "  Zipkin: http://localhost:9411"
}

print_status() {
    echo ""
    echo "=========================================="
    echo "  Todo Platform + Dapr Deployment Status"
    echo "=========================================="
    echo ""
    
    echo "Minikube Profile: $MINIKUBE_PROFILE"
    echo "Namespace: $NAMESPACE"
    echo ""
    
    echo "Dapr Components:"
    kubectl get components -n "$NAMESPACE" 2>/dev/null || echo "  No components found in namespace"
    echo ""
    
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""
    
    echo "Services:"
    kubectl get svc -n "$NAMESPACE"
    echo ""
    
    echo "Access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000/api/docs"
    echo "  Zipkin Tracing: http://localhost:9411"
    echo "  Minikube Dashboard: minikube dashboard --profile=$MINIKUBE_PROFILE"
    echo ""
    
    echo "Useful Commands:"
    echo "  View Dapr sidecar logs: kubectl logs -n $NAMESPACE -l app=dapr-sidecar"
    echo "  View application logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=backend"
    echo "  Check Dapr status: dapr status -k"
    echo ""
}

cleanup() {
    log_warning "Cleaning up resources..."
    
    # Kill port forwards
    pkill -f "kubectl port-forward" 2>/dev/null || true
    
    # Remove Helm release
    helm uninstall todo-platform -n "$NAMESPACE" 2>/dev/null || true
    
    # Delete namespace
    kubectl delete namespace "$NAMESPACE" 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "  Todo Platform + Full Dapr Deployment"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        cleanup)
            cleanup
            exit 0
            ;;
        status)
            print_status
            exit 0
            ;;
        restart)
            cleanup
            ;;
    esac
    
    # Run deployment steps
    check_prerequisites
    start_minikube
    enable_minikube_addons
    install_dapr
    install_redis
    install_kafka
    install_zipkin
    build_images
    create_secrets
    deploy_application
    wait_for_pods
    setup_port_forwarding
    print_status
    
    log_success "Deployment completed successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

main "$@"
