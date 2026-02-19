#!/bin/bash
set -e

# =============================================================================
# Todo Chatbot Minikube Deployment Script
# =============================================================================
# This script deploys the Todo AI Chatbot to Minikube with:
# - Backend (FastAPI + OpenAI Agents + MCP)
# - Frontend (Next.js + ChatKit)
# - NGINX Ingress Controller
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MINIKUBE_PROFILE="${MINIKUBE_PROFILE:-todo-chatbot}"
NAMESPACE="${NAMESPACE:-todo-chatbot}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
CLERK_SECRET_KEY="${CLERK_SECRET_KEY:-}"
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:-}"
CLERK_DOMAIN="${CLERK_DOMAIN:-}"

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
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        echo ""
        echo "Please install:"
        echo "  - minikube: https://minikube.sigs.k8s.io/docs/start/"
        echo "  - kubectl: https://kubernetes.io/docs/tasks/tools/"
        echo "  - helm: https://helm.sh/docs/intro/install/"
        echo "  - docker: https://docs.docker.com/get-docker/"
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
    
# Start Minikube with adequate resources
    # Note: Memory reduced to 6144MB (6GB) to work with Docker Desktop default limits
    # If you have more memory available, you can increase this to 8192 or higher
    minikube start \\
        --profile="$MINIKUBE_PROFILE" \\
        --driver=docker \\
        --kubernetes-version=stable \\
        --cpus=4 \\
        --memory=6144 \\
        --disk-size=30g \\
        --addons=ingress
    
    log_success "Minikube started successfully"
}

build_images() {
    log_info "Building Docker images..."

    # Set Docker to use Minikube's Docker daemon
    eval $(minikube -p "$MINIKUBE_PROFILE" docker-env)

    # Build backend image from project root (Dockerfile copies both backend/ and agent/)
    log_info "Building backend image..."
    docker build -t todo-chatbot-backend:latest -f backend/Dockerfile .

    # Build frontend image
    log_info "Building frontend image..."
    docker build -t todo-chatbot-frontend:latest chatbot-frontend/

    log_success "Docker images built successfully"
}

check_openai_key() {
    if [ -z "$OPENAI_API_KEY" ]; then
        log_warning "OPENAI_API_KEY not set"
        echo ""
        read -p "Enter your OpenAI API key (or press Enter to skip): " OPENAI_API_KEY
        if [ -z "$OPENAI_API_KEY" ]; then
            log_error "OpenAI API key is required for the chatbot to function"
            exit 1
        fi
    fi
}

deploy_with_helm() {
    log_info "Deploying Todo Chatbot with Helm..."
    
    # Build helm set flags for secrets
    local helm_secrets=(
        --set "secrets.openaiApiKey=$OPENAI_API_KEY"
    )
    [ -n "$CLERK_SECRET_KEY" ] && helm_secrets+=(--set "secrets.clerkSecretKey=$CLERK_SECRET_KEY")
    [ -n "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" ] && helm_secrets+=(--set "secrets.clerkPublishableKey=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
    [ -n "$CLERK_DOMAIN" ] && helm_secrets+=(--set "secrets.clerkDomain=$CLERK_DOMAIN")

    # Check if release exists
    if helm list -n "$NAMESPACE" | grep -q "chatbot"; then
        log_warning "Chatbot release already exists, upgrading..."
        helm upgrade chatbot ./charts/chatbot \
            --namespace "$NAMESPACE" \
            --values ./charts/chatbot/values-minikube.yaml \
            "${helm_secrets[@]}" \
            --wait \
            --timeout 5m
    else
        # Create namespace
        kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

        # Install release
        helm install chatbot ./charts/chatbot \
            --namespace "$NAMESPACE" \
            --values ./charts/chatbot/values-minikube.yaml \
            "${helm_secrets[@]}" \
            --wait \
            --timeout 5m
    fi
    
    log_success "Todo Chatbot deployed successfully"
}

wait_for_pods() {
    log_info "Waiting for all pods to be ready..."
    
    kubectl wait --for=condition=ready pod \
        --all \
        --namespace "$NAMESPACE" \
        --timeout=300s
    
    log_success "All pods are ready"
}

print_status() {
    echo ""
    echo "=========================================="
    echo "  Todo Chatbot Deployment Status"
    echo "=========================================="
    echo ""
    
    echo "Minikube Profile: $MINIKUBE_PROFILE"
    echo "Namespace: $NAMESPACE"
    echo ""
    
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""
    
    echo "Services:"
    kubectl get svc -n "$NAMESPACE"
    echo ""
    
    # Get Minikube IP
    MINIKUBE_IP=$(minikube ip --profile="$MINIKUBE_PROFILE")
    echo "Access URLs:"
    echo "  Frontend: http://$MINIKUBE_IP"
    echo "  Backend API: http://$MINIKUBE_IP/api"
    echo ""
    
    echo "Useful Commands:"
    echo "  View logs: kubectl logs -n $NAMESPACE -l app=backend"
    echo "  Shell into backend: kubectl exec -it -n $NAMESPACE deployment/backend -- /bin/sh"
    echo "  Port forward backend: kubectl port-forward -n $NAMESPACE svc/backend 8000:8000"
    echo "  Port forward frontend: kubectl port-forward -n $NAMESPACE svc/frontend 3000:3000"
    echo ""
}

cleanup() {
    log_warning "Cleaning up resources..."
    
    # Remove Helm release
    helm uninstall chatbot -n "$NAMESPACE" 2>/dev/null || true
    
    # Delete namespace
    kubectl delete namespace "$NAMESPACE" 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "  Todo Chatbot - Minikube Deployment"
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
    check_openai_key
    start_minikube
    build_images
    deploy_with_helm
    wait_for_pods
    print_status
    
    log_success "Deployment completed successfully!"
    echo ""
    echo "Open your browser and navigate to the Frontend URL above to start chatting!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

main "$@"
