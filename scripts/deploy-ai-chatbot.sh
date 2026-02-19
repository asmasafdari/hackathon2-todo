#!/bin/bash
# AI-Powered Deployment Script for Todo Chatbot
# Uses: kubectl-ai, kagent, and Docker AI (Gordon)

set -e

echo "========================================"
echo "  AI-Powered Todo Chatbot Deployment"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
MINIKUBE_PROFILE="todo-chatbot"
NAMESPACE="todo-chatbot"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

# Helper functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if AI tools are available
check_ai_tools() {
    log_info "Checking AI-DevOps tools..."
    
    KUBECTL_AI_AVAILABLE=false
    KAGENT_AVAILABLE=false
    GORDON_AVAILABLE=false
    
    if command -v kubectl-ai &> /dev/null; then
        KUBECTL_AI_AVAILABLE=true
        log_success "kubectl-ai is available"
    else
        log_warn "kubectl-ai not found. Will use standard kubectl commands."
    fi
    
    if command -v kagent &> /dev/null; then
        KAGENT_AVAILABLE=true
        log_success "kagent is available"
    else
        log_warn "kagent not found. Will use standard kubectl commands."
    fi
    
    if docker ai --help &> /dev/null; then
        GORDON_AVAILABLE=true
        log_success "Gordon (Docker AI) is available"
    else
        log_warn "Gordon (Docker AI) not available. Will use standard Docker commands."
    fi
    
    echo ""
}

# Start Minikube with AI assistance
start_minikube_ai() {
    log_info "Starting Minikube cluster..."
    
    if [ "$KAGENT_AVAILABLE" = true ]; then
        log_info "Using kagent to check cluster health..."
        kagent "analyze the cluster health for profile $MINIKUBE_PROFILE" || true
    fi
    
    if minikube status -p "$MINIKUBE_PROFILE" &> /dev/null; then
        log_success "Minikube profile '$MINIKUBE_PROFILE' is already running"
    else
        log_info "Creating Minikube cluster..."
        minikube start -p "$MINIKUBE_PROFILE" \
            --memory=6144 \
            --cpus=4 \
            --driver=docker \
            --addons=ingress
        log_success "Minikube cluster started"
    fi
    
    if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
        log_info "Using kubectl-ai to verify cluster..."
        kubectl-ai "check if the cluster is ready" -n "$NAMESPACE" || true
    fi
    
    echo ""
}

# Build images with AI assistance
build_images_ai() {
    log_info "Building Docker images..."
    
    # Set Docker to use Minikube's daemon
    eval $(minikube -p "$MINIKUBE_PROFILE" docker-env)
    
    if [ "$GORDON_AVAILABLE" = true ]; then
        log_info "Using Gordon (Docker AI) to optimize builds..."
        
        # Ask Gordon for optimization tips
        docker ai "How can I optimize the Dockerfile in backend/ for faster builds?" || true
        
        # Build with AI insights
        log_info "Building backend image with Gordon's insights..."
        docker build -t todo-chatbot-backend:latest backend/
        
        log_info "Building frontend image..."
        docker ai "Optimize the build for frontend/Dockerfile" || true
        docker build -t todo-chatbot-frontend:latest chatbot-frontend/
    else
        log_info "Building images with standard Docker commands..."
        
        cd backend
        docker build -t todo-chatbot-backend:latest .
        cd ..
        
        cd chatbot-frontend
        docker build -t todo-chatbot-frontend:latest .
        cd ..
    fi
    
    log_success "Docker images built successfully"
    echo ""
}

# Deploy using AI tools
deploy_with_ai() {
    log_info "Deploying Todo Chatbot to Kubernetes..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        log_warn "OPENAI_API_KEY not set. Please set it for the chatbot to function."
        read -p "Enter your OpenAI API key: " OPENAI_API_KEY
        export OPENAI_API_KEY
    fi
    
    if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
        log_info "Using kubectl-ai for deployment..."
        
        # Create namespace using AI
        kubectl-ai "create namespace $NAMESPACE" || kubectl create namespace "$NAMESPACE"
        
        # Deploy backend with AI assistance
        kubectl-ai "deploy the todo-chatbot-backend image with environment variable OPENAI_API_KEY from secret" \
            -n "$NAMESPACE" || helm_deploy
    else
        log_info "Using Helm for deployment..."
        helm_deploy
    fi
    
    if [ "$KAGENT_AVAILABLE" = true ]; then
        log_info "Using kagent to monitor deployment..."
        kagent "monitor the deployment in namespace $NAMESPACE" || true
    fi
    
    echo ""
}

# Standard Helm deployment
helm_deploy() {
    log_info "Deploying with Helm..."
    
    # Create namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy with Helm
    if helm list -n "$NAMESPACE" | grep -q "chatbot"; then
        log_info "Upgrading existing release..."
        helm upgrade chatbot ./charts/chatbot \
            --namespace "$NAMESPACE" \
            --values ./charts/chatbot/values-minikube.yaml \
            --set secrets.openaiApiKey="$OPENAI_API_KEY" \
            --wait
    else
        log_info "Installing new release..."
        helm install chatbot ./charts/chatbot \
            --namespace "$NAMESPACE" \
            --values ./charts/chatbot/values-minikube.yaml \
            --set secrets.openaiApiKey="$OPENAI_API_KEY" \
            --wait
    fi
    
    log_success "Deployment complete"
}

# Verify deployment with AI
verify_deployment_ai() {
    log_info "Verifying deployment..."
    
    if [ "$KAGENT_AVAILABLE" = true ]; then
        log_info "Using kagent to analyze deployment health..."
        kagent "analyze the deployment health in namespace $NAMESPACE"
    elif [ "$KUBECTL_AI_AVAILABLE" = true ]; then
        log_info "Using kubectl-ai to check pod status..."
        kubectl-ai "check if all pods are running" -n "$NAMESPACE"
    else
        # Standard verification
        kubectl get pods -n "$NAMESPACE"
        kubectl wait --for=condition=ready pod --all -n "$NAMESPACE" --timeout=300s
    fi
    
    echo ""
}

# Print access information
print_access_info() {
    log_success "Deployment verified successfully!"
    echo ""
    echo "========================================"
    echo "  Access Information"
    echo "========================================"
    echo ""
    
    # Get Minikube IP
    MINIKUBE_IP=$(minikube ip -p "$MINIKUBE_PROFILE")
    echo "Minikube IP: $MINIKUBE_IP"
    echo ""
    echo "Access URLs:"
    echo "  Frontend: http://$MINIKUBE_IP"
    echo "  Backend API: http://$MINIKUBE_IP/api"
    echo ""
    
    if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
        echo "AI-Assisted Commands Available:"
        echo "  kubectl-ai 'scale the frontend to 2 replicas' -n $NAMESPACE"
        echo "  kubectl-ai 'check logs for backend' -n $NAMESPACE"
    fi
    
    if [ "$KAGENT_AVAILABLE" = true ]; then
        echo "  kagent 'optimize resource allocation'"
        echo "  kagent 'troubleshoot failing pods'"
    fi
    
    echo ""
    echo "Standard Commands:"
    echo "  kubectl get pods -n $NAMESPACE"
    echo "  kubectl logs -n $NAMESPACE -l app=backend"
    echo "  helm list -n $NAMESPACE"
    echo ""
}

# Cleanup function
cleanup() {
    log_warn "Cleaning up deployment..."
    
    if [ "$KUBECTL_AI_AVAILABLE" = true ]; then
        kubectl-ai "delete all resources in namespace $NAMESPACE" || true
    fi
    
    helm uninstall chatbot -n "$NAMESPACE" 2>/dev/null || true
    kubectl delete namespace "$NAMESPACE" 2>/dev/null || true
    
    log_success "Cleanup complete"
}

# Main execution
main() {
    # Check for cleanup command
    if [ "${1:-}" = "cleanup" ]; then
        cleanup
        exit 0
    fi
    
    echo "🤖 AI-Powered Deployment Script"
    echo ""
    
    check_ai_tools
    start_minikube_ai
    build_images_ai
    deploy_with_ai
    verify_deployment_ai
    print_access_info
    
    log_success "All done! Your Todo Chatbot is ready."
}

# Run main function
main "$@"
