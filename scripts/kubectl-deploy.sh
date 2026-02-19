#!/bin/bash
# kubectl Deployment Script
# Deploys Todo Platform using kubectl and YAML manifests

set -e

echo "☸️  Todo Platform - kubectl Deployment"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="${NAMESPACE:-todo}"
MANIFESTS_DIR="scripts/kubectl-manifests"

# Check prerequisites
check_prerequisites() {
    echo ""
    echo "🔍 Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found${NC}"
        exit 1
    fi
    
    if ! kubectl get nodes &> /dev/null; then
        echo -e "${RED}❌ No Kubernetes cluster accessible${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Kubernetes cluster accessible${NC}"
}

# Create namespace
create_namespace() {
    echo ""
    echo "📦 Creating namespace..."
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    echo -e "${GREEN}✓ Namespace '$NAMESPACE' ready${NC}"
}

# Apply manifests
apply_manifests() {
    echo ""
    echo "🚀 Applying Kubernetes manifests..."
    
    # Apply in order: ConfigMap -> Secrets -> Deployments -> Services -> Ingress
    echo "   Applying ConfigMap..."
    kubectl apply -f "$MANIFESTS_DIR/configmap.yaml" -n "$NAMESPACE"
    
    echo "   Applying Secrets..."
    # Create secrets from values file
    kubectl create secret generic todo-secrets \
        --from-literal=database-url="${DATABASE_URL:-sqlite:///app/data/todos.db}" \
        --from-literal=openai-api-key="${OPENAI_API_KEY:-}" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    echo "   Applying Deployments..."
    kubectl apply -f "$MANIFESTS_DIR/backend-deployment.yaml" -n "$NAMESPACE"
    kubectl apply -f "$MANIFESTS_DIR/frontend-deployment.yaml" -n "$NAMESPACE"
    kubectl apply -f "$MANIFESTS_DIR/mcp-deployment.yaml" -n "$NAMESPACE"
    kubectl apply -f "$MANIFESTS_DIR/activity-logger-deployment.yaml" -n "$NAMESPACE"
    
    echo "   Applying Services..."
    kubectl apply -f "$MANIFESTS_DIR/backend-service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$MANIFESTS_DIR/frontend-service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$MANIFESTS_DIR/mcp-service.yaml" -n "$NAMESPACE"
    kubectl apply -f "$MANIFESTS_DIR/activity-logger-service.yaml" -n "$NAMESPACE"
    
    echo "   Applying Ingress..."
    kubectl apply -f "$MANIFESTS_DIR/ingress.yaml" -n "$NAMESPACE"
    
    echo -e "${GREEN}✓ All manifests applied${NC}"
}

# Wait for deployments
wait_for_deployments() {
    echo ""
    echo "⏳ Waiting for deployments to be ready..."
    
    kubectl wait --for=condition=available --timeout=300s deployment/backend -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/mcp -n "$NAMESPACE" || echo "MCP deployment may not be ready yet"
    kubectl wait --for=condition=available --timeout=300s deployment/activity-logger -n "$NAMESPACE" || echo "Activity logger may not be ready yet"
    
    echo -e "${GREEN}✓ Deployments ready${NC}"
}

# Show status
show_status() {
    echo ""
    echo "📊 Deployment Status:"
    echo "===================="
    
    echo ""
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    
    echo ""
    echo "Services:"
    kubectl get svc -n "$NAMESPACE"
    
    echo ""
    echo "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    
    echo ""
    echo -e "${BLUE}🌐 Access the application:${NC}"
    echo "   Use: kubectl port-forward -n $NAMESPACE svc/frontend 3000:3000"
    echo "   Then: http://localhost:3000"
}

# Main
main() {
    check_prerequisites
    create_namespace
    apply_manifests
    wait_for_deployments
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 kubectl deployment complete!${NC}"
}

# Run
main
