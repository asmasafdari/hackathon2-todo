#!/bin/bash
# kagent (AI Agent) Deployment Script
# Deploys the AI Agent MCP server to Kubernetes

set -e

echo "🤖 Todo Platform - AI Agent (kagent) Deployment"
echo "================================================"

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
    
    # Check cluster
    if ! kubectl get nodes &> /dev/null; then
        echo -e "${RED}❌ No Kubernetes cluster accessible${NC}"
        exit 1
    fi
    
    # Check OpenAI API key
    if [ -z "$OPENAI_API_KEY" ] && [ ! -f "agent/.env" ]; then
        echo -e "${RED}❌ OPENAI_API_KEY not set and agent/.env not found${NC}"
        echo "   Set OPENAI_API_KEY environment variable or create agent/.env"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites met${NC}"
}

# Load API key
load_api_key() {
    if [ -z "$OPENAI_API_KEY" ] && [ -f "agent/.env" ]; then
        export $(grep -v '^#' agent/.env | xargs)
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}❌ OPENAI_API_KEY not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ OpenAI API key loaded${NC}"
}

# Deploy kagent
deploy_kagent() {
    echo ""
    echo "🚀 Deploying AI Agent (MCP Server)..."
    
    # Create or update secret
    kubectl create secret generic kagent-secrets \
        --from-literal=openai-api-key="$OPENAI_API_KEY" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy MCP server
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kagent
  namespace: $NAMESPACE
  labels:
    app: kagent
    component: ai-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kagent
  template:
    metadata:
      labels:
        app: kagent
        component: ai-agent
    spec:
      containers:
      - name: mcp
        image: todo-mcp:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: kagent-secrets
              key: openai-api-key
        - name: TODO_API_BASE_URL
          value: "http://backend:8000"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: kagent
  namespace: $NAMESPACE
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: 8080
  selector:
    app: kagent
EOF
    
    echo -e "${GREEN}✓ AI Agent deployed${NC}"
}

# Wait for deployment
wait_for_deployment() {
    echo ""
    echo "⏳ Waiting for AI Agent to be ready..."
    kubectl wait --for=condition=available --timeout=120s deployment/kagent -n "$NAMESPACE"
    echo -e "${GREEN}✓ AI Agent ready${NC}"
}

# Test agent
test_agent() {
    echo ""
    echo "🧪 Testing AI Agent..."
    
    KAGENT_POD=$(kubectl get pods -n "$NAMESPACE" -l app=kagent -o jsonpath='{.items[0].metadata.name}')
    
    # Test health endpoint
    echo "Testing health endpoint..."
    kubectl exec -n "$NAMESPACE" "$KAGENT_POD" -- \
        curl -s http://localhost:8080/health || echo "   (Health check failed)"
    
    echo ""
    echo "To interact with the agent:"
    echo "   1. Port forward: kubectl port-forward -n $NAMESPACE svc/kagent 8080:8080"
    echo "   2. The MCP server uses stdio transport - integrate with Claude Desktop or run locally"
}

# Show status
show_status() {
    echo ""
    echo "📊 AI Agent Status:"
    echo "==================="
    
    kubectl get pods -n "$NAMESPACE" -l app=kagent
    
    echo ""
    echo -e "${BLUE}🤖 AI Agent Features:${NC}"
    echo "   • Natural language todo creation"
    echo "   • Intelligent task queries"
    echo "   • Todo completion via conversation"
    echo "   • Event publishing for audit trail"
    
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs: kubectl logs -n $NAMESPACE -l app=kagent -f"
    echo "   Shell access: kubectl exec -it -n $NAMESPACE deployment/kagent -- /bin/sh"
    echo "   Port forward: kubectl port-forward -n $NAMESPACE svc/kagent 8080:8080"
}

# Main
main() {
    check_prerequisites
    load_api_key
    deploy_kagent
    wait_for_deployment
    test_agent
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 AI Agent (kagent) deployment complete!${NC}"
}

# Run
main
