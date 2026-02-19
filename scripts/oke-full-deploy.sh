#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Oracle OKE Full Deploy Script
# Manual alternative to GitHub Actions CI/CD.
# Deploys: Dapr, Monitoring (Prometheus + Grafana + OTel), and Todo Platform.
#
# Usage:
#   export OCI_REGION=<region>          # e.g. ap-sydney-1
#   export OCI_TENANCY=<tenancy>        # e.g. mytenancy
#   export OKE_CLUSTER_ID=<cluster-id> # from OCI console
#   ./scripts/oke-full-deploy.sh
#
# Required env vars (or sourced from .env):
#   OCI_REGION, OCI_TENANCY, OKE_CLUSTER_ID,
#   DATABASE_URL, OPENAI_API_KEY,
#   KAFKA_BROKERS, KAFKA_API_KEY, KAFKA_API_SECRET,
#   REDIS_URL, REDIS_PASSWORD,
#   CLERK_SECRET_KEY, ALLOWED_ORIGINS,
#   GRAFANA_ADMIN_PASSWORD, BACKEND_URL
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $*"; }
info() { echo -e "${BLUE}→${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
fail() { echo -e "${RED}✗${NC} $*"; exit 1; }
hr()   { echo -e "${CYAN}──────────────────────────────────────────────────────────${NC}"; }

# ── Load .env if present ─────────────────────────────────────────────────────
if [[ -f ".env" ]]; then
  info "Loading .env file..."
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
  ok ".env loaded"
fi

# ── Config (with defaults) ───────────────────────────────────────────────────
OCI_REGION="${OCI_REGION:-}"
OCI_TENANCY="${OCI_TENANCY:-}"
OKE_CLUSTER_ID="${OKE_CLUSTER_ID:-}"
OCIR_REGISTRY="${OCI_REGION}.ocir.io"
OCIR_NAMESPACE="${OCI_TENANCY}"

DAPR_VERSION="1.12.0"
HELM_TIMEOUT="10m"
NAMESPACE_APP="todo"
NAMESPACE_MONITORING="monitoring"
SECRET_NAME="todo-secrets"

# ── Step counter ─────────────────────────────────────────────────────────────
STEP=0
step() {
  STEP=$((STEP + 1))
  hr
  echo -e "${CYAN}[Step ${STEP}]${NC} $*"
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Prerequisites
# ─────────────────────────────────────────────────────────────────────────────
step "Checking prerequisites"

MISSING=()
for cmd in oci kubectl helm docker dapr; do
  if command -v "$cmd" &>/dev/null; then
    ok "$cmd found ($(command -v "$cmd"))"
  else
    warn "$cmd NOT found"
    MISSING+=("$cmd")
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  fail "Missing tools: ${MISSING[*]}. Install them and re-run."
fi

# Verify required env vars
REQUIRED_VARS=(OCI_REGION OCI_TENANCY OKE_CLUSTER_ID DATABASE_URL
               OPENAI_API_KEY KAFKA_BROKERS KAFKA_API_KEY KAFKA_API_SECRET
               CLERK_SECRET_KEY ALLOWED_ORIGINS GRAFANA_ADMIN_PASSWORD BACKEND_URL)
MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    MISSING_VARS+=("$var")
  fi
done

if [[ ${#MISSING_VARS[@]} -gt 0 ]]; then
  fail "Missing required env vars: ${MISSING_VARS[*]}\nSet them in .env or export before running."
fi
ok "All prerequisites satisfied"

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Configure kubectl for OKE
# ─────────────────────────────────────────────────────────────────────────────
step "Configuring kubectl for OKE cluster"
info "Cluster ID: ${OKE_CLUSTER_ID}"
info "Region:     ${OCI_REGION}"

oci ce cluster create-kubeconfig \
  --cluster-id "${OKE_CLUSTER_ID}" \
  --region "${OCI_REGION}" \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Verify connectivity
kubectl cluster-info --request-timeout=10s
ok "kubectl configured and connected to OKE"

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Create namespaces
# ─────────────────────────────────────────────────────────────────────────────
step "Creating namespaces: ${NAMESPACE_APP}, ${NAMESPACE_MONITORING}"

kubectl create namespace "${NAMESPACE_APP}" --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace "${NAMESPACE_MONITORING}" --dry-run=client -o yaml | kubectl apply -f -
ok "Namespaces ready"

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Install Dapr on the cluster
# ─────────────────────────────────────────────────────────────────────────────
step "Installing Dapr ${DAPR_VERSION} on OKE"

helm repo add dapr https://dapr.github.io/helm-charts/ 2>/dev/null || true
helm repo update

DAPR_INSTALLED_VERSION=$(helm list -n dapr-system -o json 2>/dev/null \
  | python3 -c "import sys,json; apps=json.load(sys.stdin); \
    print(next((a['chart'] for a in apps if 'dapr' in a['name']),''))" 2>/dev/null || echo "")

if echo "$DAPR_INSTALLED_VERSION" | grep -q "${DAPR_VERSION}"; then
  warn "Dapr ${DAPR_VERSION} already installed — skipping"
else
  helm upgrade --install dapr dapr/dapr \
    --version="${DAPR_VERSION}" \
    --namespace dapr-system \
    --create-namespace \
    --set global.mtls.enabled=true \
    --wait --timeout=5m
  ok "Dapr ${DAPR_VERSION} installed"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Install Monitoring (Prometheus + Grafana + AlertManager)
# ─────────────────────────────────────────────────────────────────────────────
step "Installing kube-prometheus-stack in namespace: ${NAMESPACE_MONITORING}"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo update

helm upgrade --install kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack \
  --namespace "${NAMESPACE_MONITORING}" \
  --values k8s/monitoring/prometheus-stack-values.yaml \
  --set grafana.adminPassword="${GRAFANA_ADMIN_PASSWORD}" \
  --timeout "${HELM_TIMEOUT}" \
  --wait

ok "kube-prometheus-stack installed"

# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Deploy OpenTelemetry Collector + ServiceMonitors
# ─────────────────────────────────────────────────────────────────────────────
step "Deploying OTel Collector and Prometheus ServiceMonitors"

kubectl apply -f k8s/monitoring/otel-collector.yaml
kubectl apply -f k8s/monitoring/dapr-servicemonitor.yaml
kubectl apply -f k8s/monitoring/backend-servicemonitor.yaml

ok "OTel Collector and ServiceMonitors applied"

# ─────────────────────────────────────────────────────────────────────────────
# Step 7: Create application Kubernetes secret
# ─────────────────────────────────────────────────────────────────────────────
step "Creating K8s secret '${SECRET_NAME}' in namespace '${NAMESPACE_APP}'"

# Optional: Redis vars may be empty if not using Redis fallback
REDIS_URL="${REDIS_URL:-}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

kubectl create secret generic "${SECRET_NAME}" \
  --from-literal=DATABASE_URL="${DATABASE_URL}" \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --from-literal=KAFKA_BROKERS="${KAFKA_BROKERS}" \
  --from-literal=KAFKA_API_KEY="${KAFKA_API_KEY}" \
  --from-literal=KAFKA_API_SECRET="${KAFKA_API_SECRET}" \
  --from-literal=REDIS_URL="${REDIS_URL}" \
  --from-literal=REDIS_PASSWORD="${REDIS_PASSWORD}" \
  --from-literal=CLERK_SECRET_KEY="${CLERK_SECRET_KEY}" \
  --from-literal=ALLOWED_ORIGINS="${ALLOWED_ORIGINS}" \
  --namespace "${NAMESPACE_APP}" \
  --dry-run=client -o yaml | kubectl apply -f -

ok "Secret '${SECRET_NAME}' created/updated"

# ─────────────────────────────────────────────────────────────────────────────
# Step 8: Apply Dapr OKE components
# ─────────────────────────────────────────────────────────────────────────────
step "Applying Dapr components for OKE"

# Secret store first (other components reference it for secret resolution)
kubectl apply -f dapr/components/oke/secretstore-kubernetes.yaml -n "${NAMESPACE_APP}"
kubectl apply -f dapr/components/oke/config.yaml                 -n "${NAMESPACE_APP}"
kubectl apply -f dapr/components/oke/resiliency.yaml             -n "${NAMESPACE_APP}"
kubectl apply -f dapr/components/oke/statestore-postgresql.yaml  -n "${NAMESPACE_APP}"
kubectl apply -f dapr/components/oke/bindings-cron.yaml          -n "${NAMESPACE_APP}"

# Pub/Sub: Redpanda Cloud by default; Redis Streams if USE_REDIS_FALLBACK=true
USE_REDIS_FALLBACK="${USE_REDIS_FALLBACK:-false}"
if [[ "${USE_REDIS_FALLBACK}" == "true" ]]; then
  warn "Activating Redis Streams fallback pub/sub"
  kubectl apply -f dapr/components/oke/pubsub-redis-fallback.yaml -n "${NAMESPACE_APP}"
  kubectl delete -f dapr/components/oke/pubsub-redpanda.yaml -n "${NAMESPACE_APP}" 2>/dev/null || true
else
  info "Activating Redpanda Cloud pub/sub (SCRAM)"
  kubectl apply -f dapr/components/oke/pubsub-redpanda.yaml -n "${NAMESPACE_APP}"
  kubectl delete -f dapr/components/oke/pubsub-redis-fallback.yaml -n "${NAMESPACE_APP}" 2>/dev/null || true
fi

echo ""
info "Dapr components in namespace '${NAMESPACE_APP}':"
kubectl get components.dapr.io -n "${NAMESPACE_APP}" 2>/dev/null \
  || kubectl get configmap -n "${NAMESPACE_APP}" -l app.kubernetes.io/part-of=dapr
ok "All Dapr components applied"

# ─────────────────────────────────────────────────────────────────────────────
# Step 9: Helm deploy todo-platform
# ─────────────────────────────────────────────────────────────────────────────
step "Deploying todo-platform via Helm"

# Determine image tag (use git SHA if available, else 'latest')
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo "latest")}"
info "Image tag: ${IMAGE_TAG}"

helm upgrade --install todo-platform charts/todo-platform \
  --namespace "${NAMESPACE_APP}" \
  --values charts/todo-platform/values-oke.yaml \
  --set global.imageTag="${IMAGE_TAG}" \
  --set backend.image.repository="${OCIR_REGISTRY}/${OCIR_NAMESPACE}/todo-backend" \
  --set backend.image.tag="${IMAGE_TAG}" \
  --set frontend.image.repository="${OCIR_REGISTRY}/${OCIR_NAMESPACE}/todo-frontend" \
  --set frontend.image.tag="${IMAGE_TAG}" \
  --set activityLogger.image.repository="${OCIR_REGISTRY}/${OCIR_NAMESPACE}/todo-activity-logger" \
  --set activityLogger.image.tag="${IMAGE_TAG}" \
  --set kafka.brokers="${KAFKA_BROKERS}" \
  --set config.corsOrigins="${ALLOWED_ORIGINS}" \
  --set config.backendUrl="http://todo-platform-backend.${NAMESPACE_APP}.svc.cluster.local:8000" \
  --timeout "${HELM_TIMEOUT}" \
  --wait

ok "Helm deployment complete"

# ─────────────────────────────────────────────────────────────────────────────
# Step 10: Wait for rollout + print status
# ─────────────────────────────────────────────────────────────────────────────
step "Waiting for backend rollout"

kubectl rollout status deployment/backend -n "${NAMESPACE_APP}" --timeout=300s
ok "Backend rollout complete"

hr
echo ""
echo "=== Pods (with Dapr sidecars) ==="
kubectl get pods -n "${NAMESPACE_APP}" -o wide

echo ""
echo "=== Services ==="
kubectl get svc -n "${NAMESPACE_APP}"

echo ""
echo "=== Ingress ==="
kubectl get ingress -n "${NAMESPACE_APP}" 2>/dev/null || echo "No ingress configured"

echo ""
echo "=== Dapr sidecar count ==="
DAPR_COUNT=$(kubectl get pods -n "${NAMESPACE_APP}" \
  -o jsonpath='{range .items[*]}{range .spec.containers[*]}{.name}{"\n"}{end}{end}' \
  | grep -c "daprd" || echo 0)
echo "Pods with Dapr sidecar injected: ${DAPR_COUNT}"

echo ""
echo "=== Monitoring pods ==="
kubectl get pods -n "${NAMESPACE_MONITORING}" --no-headers \
  | awk '{print $1, $3}' | column -t

# ─────────────────────────────────────────────────────────────────────────────
# Step 11: Smoke Tests
# ─────────────────────────────────────────────────────────────────────────────
step "Running smoke tests against ${BACKEND_URL}"

echo ""
info "Health check (/health)..."
if curl -sf --retry 5 --retry-delay 10 --retry-connrefused "${BACKEND_URL}/health" >/dev/null; then
  ok "Liveness check passed"
else
  warn "Liveness check failed — backend may still be starting"
fi

info "Readiness check (/ready)..."
if curl -sf --retry 3 --retry-delay 5 "${BACKEND_URL}/ready" >/dev/null; then
  ok "Readiness check passed"
else
  warn "Readiness check failed — DB connection may not be ready"
fi

info "Dapr subscription discovery (/dapr/subscribe)..."
SUBS=$(curl -sf "${BACKEND_URL}/dapr/subscribe" 2>/dev/null || echo "[]")
echo "  Subscriptions: ${SUBS}"
if echo "${SUBS}" | grep -q "kafka-pubsub"; then
  ok "Pub/Sub subscription registered"
else
  warn "Pub/Sub subscription not visible (Dapr sidecar may need a moment)"
fi

info "API smoke test — create todo..."
CREATE_RESULT=$(curl -sf -X POST "${BACKEND_URL}/api/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"OKE smoke test - safe to delete"}' 2>/dev/null || echo "")
if echo "${CREATE_RESULT}" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(f'Created todo id={d[\"id\"]} ✓')" 2>/dev/null; then
  ok "API smoke test passed"
else
  warn "API smoke test skipped (auth may be required)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
hr
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Oracle OKE Full Deployment Complete             ║"
echo "╠══════════════════════════════════════════════════════════╣"
printf "║  %-20s %-34s ║\n" "Image tag:"     "${IMAGE_TAG}"
printf "║  %-20s %-34s ║\n" "Pub/Sub:"       "$([ "${USE_REDIS_FALLBACK}" = "true" ] && echo "Redis Streams (fallback)" || echo "Redpanda Cloud (SCRAM)")"
printf "║  %-20s %-34s ║\n" "Dapr:"          "v${DAPR_VERSION}"
printf "║  %-20s %-34s ║\n" "Monitoring:"    "Prometheus + Grafana + OTel"
printf "║  %-20s %-34s ║\n" "Namespace app:" "${NAMESPACE_APP}"
printf "║  %-20s %-34s ║\n" "Dapr sidecars:" "${DAPR_COUNT}"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Port-forward Grafana:                                   ║"
echo "║  kubectl port-forward svc/kube-prometheus-stack-grafana  ║"
echo "║    3000:80 -n monitoring                                 ║"
echo "║  Open: http://localhost:3000                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
