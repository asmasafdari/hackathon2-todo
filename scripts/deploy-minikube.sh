#!/usr/bin/env bash
set -euo pipefail

# Deploy Todo AI Chatbot to Minikube
# Usage: ./scripts/deploy-minikube.sh
#
# Required environment variables:
#   OPENAI_API_KEY          - OpenAI API key for the chatbot
#   CLERK_SECRET_KEY        - Clerk secret key for authentication
#   CLERK_PUBLISHABLE_KEY   - Clerk publishable key for frontend auth
#
# Optional environment variables:
#   CLERK_DOMAIN            - Clerk domain (default: "")
#   MINIKUBE_CPUS           - CPUs for Minikube (default: 4)
#   MINIKUBE_MEMORY         - Memory for Minikube in MB (default: 4096)

NAMESPACE="todo-chatbot"
RELEASE_NAME="chatbot"
CHART_PATH="charts/chatbot"
VALUES_FILE="charts/chatbot/values-minikube.yaml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Check prerequisites ---
info "Checking prerequisites..."

for cmd in minikube helm kubectl docker; do
  if ! command -v "$cmd" &>/dev/null; then
    error "'$cmd' is not installed. Please install it first."
  fi
done

info "All prerequisites found."

# --- Validate required env vars ---
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY environment variable}"
: "${CLERK_SECRET_KEY:?Set CLERK_SECRET_KEY environment variable}"
: "${CLERK_PUBLISHABLE_KEY:?Set CLERK_PUBLISHABLE_KEY environment variable}"

CLERK_DOMAIN="${CLERK_DOMAIN:-}"
MINIKUBE_CPUS="${MINIKUBE_CPUS:-4}"
MINIKUBE_MEMORY="${MINIKUBE_MEMORY:-4096}"

# --- Start Minikube if not running ---
if minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
  info "Minikube is already running."
else
  info "Starting Minikube (cpus=$MINIKUBE_CPUS, memory=${MINIKUBE_MEMORY}MB)..."
  minikube start --cpus="$MINIKUBE_CPUS" --memory="$MINIKUBE_MEMORY"
fi

# --- Enable ingress addon ---
info "Enabling ingress addon..."
minikube addons enable ingress

# --- Switch to Minikube's Docker daemon ---
info "Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)

# --- Build images ---
info "Building backend image..."
docker build -t todo-chatbot-backend:latest -f backend/Dockerfile .

info "Building frontend image..."
docker build -t todo-chatbot-frontend:latest ./chatbot-frontend

# --- Deploy with Helm ---
info "Deploying with Helm..."

# Uninstall previous release if it exists
if helm status "$RELEASE_NAME" -n "$NAMESPACE" &>/dev/null; then
  warn "Existing release found. Upgrading..."
  HELM_CMD="upgrade"
else
  HELM_CMD="install"
fi

helm $HELM_CMD "$RELEASE_NAME" "$CHART_PATH" \
  -f "$VALUES_FILE" \
  --namespace "$NAMESPACE" \
  --create-namespace \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set secrets.clerkSecretKey="$CLERK_SECRET_KEY" \
  --set secrets.clerkPublishableKey="$CLERK_PUBLISHABLE_KEY" \
  --set secrets.clerkDomain="$CLERK_DOMAIN"

# --- Wait for pods ---
info "Waiting for pods to be ready (timeout: 120s)..."
kubectl wait --for=condition=Ready pod \
  -l app=backend \
  -n "$NAMESPACE" \
  --timeout=120s || warn "Backend pods not ready within timeout."

kubectl wait --for=condition=Ready pod \
  -l app=frontend \
  -n "$NAMESPACE" \
  --timeout=120s || warn "Frontend pods not ready within timeout."

# --- Print status ---
echo ""
info "Deployment complete!"
echo ""
kubectl get pods -n "$NAMESPACE"
echo ""

echo "========================================="
echo "  Access the Todo AI Chatbot"
echo "========================================="
echo ""
echo "Option 1: Minikube Tunnel (recommended)"
echo "  minikube tunnel"
echo "  Then open: http://localhost"
echo ""
echo "Option 2: Port Forward"
echo "  kubectl port-forward -n $NAMESPACE svc/frontend 3000:3000"
echo "  kubectl port-forward -n $NAMESPACE svc/backend 8000:8000"
echo "  Then open: http://localhost:3000"
echo ""
echo "Option 3: Minikube Service"
echo "  minikube service frontend -n $NAMESPACE"
echo ""
