#!/bin/bash
# DigitalOcean Kubernetes (DOKS) Deployment Script
# This script automates the deployment to DigitalOcean Kubernetes Service

set -e

echo "☁️  DigitalOcean Kubernetes Deployment Script"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-todo-cluster}"
REGION="${REGION:-nyc3}"
NODE_SIZE="${NODE_SIZE:-s-2vcpu-4gb}"
NODE_COUNT="${NODE_COUNT:-2}"

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    if ! command -v doctl &> /dev/null; then
        echo -e "${RED}❌ doctl not found. Please install it first:${NC}"
        echo "   Option 1 - Windows (Chocolatey): choco install doctl"
        echo "   Option 2 - Download from: https://github.com/digitalocean/doctl/releases"
        echo "   Option 3 - Use the web interface at https://cloud.digitalocean.com/kubernetes"
        exit 1
    fi
    echo -e "${GREEN}✓ doctl installed${NC}"
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ kubectl installed${NC}"
    
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}❌ Helm not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Helm installed${NC}"
    
    # Check doctl auth
    if ! doctl account get &> /dev/null; then
        echo -e "${RED}❌ Not authenticated with DigitalOcean${NC}"
        echo "   Run: doctl auth init"
        echo "   Get a token from: https://cloud.digitalocean.com/account/api/tokens"
        exit 1
    fi
    echo -e "${GREEN}✓ Authenticated with DigitalOcean${NC}"
}

# Create cluster
create_cluster() {
    echo ""
    echo "🔧 Creating Kubernetes cluster..."
    echo "   Name: $CLUSTER_NAME"
    echo "   Region: $REGION"
    echo "   Node size: $NODE_SIZE"
    echo "   Node count: $NODE_COUNT"
    
    # Check if cluster exists
    if doctl kubernetes cluster get "$CLUSTER_NAME" &> /dev/null; then
        echo -e "${YELLOW}⚠️  Cluster '$CLUSTER_NAME' already exists${NC}"
    else
        echo "Creating cluster (this may take 5-10 minutes)..."
        doctl kubernetes cluster create "$CLUSTER_NAME" \
            --region "$REGION" \
            --size "$NODE_SIZE" \
            --count "$NODE_COUNT" \
            --auto-upgrade=false \
            --wait
        echo -e "${GREEN}✓ Cluster created${NC}"
    fi
    
    # Save kubeconfig
    echo "Saving kubeconfig..."
    doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"
    echo -e "${GREEN}✓ Kubeconfig saved${NC}"
    
    # Verify
    kubectl get nodes
}

# Create Container Registry
create_registry() {
    echo ""
    echo "📦 Setting up Container Registry..."
    
    REGISTRY_NAME="todo-registry"
    
    # Check if registry exists
    if ! doctl registry get &> /dev/null; then
        echo "Creating registry..."
        doctl registry create "$REGISTRY_NAME"
        echo -e "${GREEN}✓ Registry created${NC}"
    else
        echo -e "${GREEN}✓ Registry exists${NC}"
    fi
    
    # Login to registry
    echo "Logging into registry..."
    doctl registry login
    
    # Get registry endpoint
    REGISTRY_ENDPOINT=$(doctl registry get --format Endpoint | tail -n1)
    echo -e "${GREEN}✓ Registry endpoint: $REGISTRY_ENDPOINT${NC}"
    
    export REGISTRY_ENDPOINT
}

# Build and push images
build_and_push() {
    echo ""
    echo "🔨 Building and pushing images..."
    
    REGISTRY_ENDPOINT=$(doctl registry get --format Endpoint | tail -n1)
    
    # Build and push backend
    echo "Building backend..."
    docker build -t "$REGISTRY_ENDPOINT/todo-backend:latest" backend/
    docker push "$REGISTRY_ENDPOINT/todo-backend:latest"
    
    # Build and push frontend
    echo "Building frontend..."
    docker build -t "$REGISTRY_ENDPOINT/todo-frontend:latest" frontend/
    docker push "$REGISTRY_ENDPOINT/todo-frontend:latest"
    
    echo -e "${GREEN}✓ All images pushed${NC}"
}

# Setup ingress controller
setup_ingress() {
    echo ""
    echo "🌐 Setting up NGINX Ingress Controller..."
    
    helm upgrade --install ingress-nginx ingress-nginx \
        --repo https://kubernetes.github.io/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --wait
    
    echo -e "${GREEN}✓ Ingress controller installed${NC}"
    
    # Wait for external IP
    echo "Waiting for external IP..."
    while true; do
        EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
        if [ -n "$EXTERNAL_IP" ]; then
            break
        fi
        echo -n "."
        sleep 5
    done
    
    echo ""
    echo -e "${GREEN}✓ External IP: $EXTERNAL_IP${NC}"
    export EXTERNAL_IP
}

# Create secrets
create_secrets() {
    echo ""
    echo "🔐 Creating secrets..."
    
    # Check if secrets file exists
    if [ ! -f "charts/todo-platform/values-secrets.yaml" ]; then
        echo -e "${YELLOW}⚠️  Creating sample secrets file...${NC}"
        cat > charts/todo-platform/values-secrets.yaml <<EOF
secrets:
  databaseUrl: "sqlite+aiosqlite:////tmp/todos.db"
  openaiApiKey: ""
EOF
        echo -e "${YELLOW}⚠️  Please edit charts/todo-platform/values-secrets.yaml with your actual secrets${NC}"
    fi
}

# Deploy application
deploy_app() {
    echo ""
    echo "🚀 Deploying application..."
    
    REGISTRY_ENDPOINT=$(doctl registry get --format Endpoint | tail -n1)
    
    kubectl create namespace todo --dry-run=client -o yaml | kubectl apply -f -
    
    helm upgrade --install todo-platform charts/todo-platform \
        -f charts/todo-platform/values.yaml \
        -f charts/todo-platform/values-secrets.yaml \
        --namespace todo \
        --set global.imageTag=latest \
        --set backend.image.repository="$REGISTRY_ENDPOINT/todo-backend" \
        --set frontend.image.repository="$REGISTRY_ENDPOINT/todo-frontend" \
        --set global.imagePullPolicy=Always \
        --set dapr.enabled=false \
        --set activityLogger.enabled=false \
        --set mcp.enabled=false \
        --set ingress.enabled=true \
        --wait \
        --timeout 10m
    
    echo -e "${GREEN}✓ Application deployed${NC}"
}

# Show status
show_status() {
    echo ""
    echo "📊 Deployment Status:"
    echo "===================="
    
    kubectl get pods -n todo
    
    echo ""
    EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    
    if [ -n "$EXTERNAL_IP" ]; then
        echo -e "${BLUE}🌐 Access URLs:${NC}"
        echo "   http://$EXTERNAL_IP"
        echo "   http://$EXTERNAL_IP/api/docs (API docs)"
    fi
    
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs: kubectl logs -n todo -l app.kubernetes.io/name=backend"
    echo "   Scale: kubectl scale deployment -n todo todo-platform-backend --replicas=3"
}

# Main
main() {
    check_prerequisites
    create_cluster
    create_registry
    build_and_push
    setup_ingress
    create_secrets
    deploy_app
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 Deployment to DigitalOcean complete!${NC}"
}

# Run main if script is executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main
fi
