#!/bin/bash
# Deploy Kafka and Dapr for the Todo Platform event-driven architecture

set -e

echo "🚀 Deploying Event-Driven Infrastructure (Kafka + Dapr)"
echo "========================================================"

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ Helm not found. Please install Helm first."
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    echo "❌ Dapr CLI not found. Installing..."
    # Install Dapr CLI
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "Please install Dapr CLI manually on Windows:"
        echo "powershell -Command \"Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1' -OutFile 'install-dapr.ps1'; .\\install-dapr.ps1\""
        exit 1
    else
        wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
    fi
fi

echo "✅ All prerequisites met"

# Step 1: Install Dapr on Kubernetes
echo ""
echo "📦 Step 1: Installing Dapr on Kubernetes..."
if kubectl get pods -n dapr-system 2>/dev/null | grep -q dapr; then
    echo "✅ Dapr already installed on Kubernetes"
else
    dapr init -k
    echo "✅ Dapr initialized on Kubernetes"
fi

# Wait for Dapr to be ready
echo ""
echo "⏳ Waiting for Dapr to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=dapr -n dapr-system --timeout=120s 2>/dev/null || true
kubectl get pods -n dapr-system

# Step 2: Create todo namespace
echo ""
echo "📦 Step 2: Creating todo namespace..."
kubectl create namespace todo --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Namespace 'todo' ready"

# Step 3: Deploy Kafka via Helm
echo ""
echo "📦 Step 3: Deploying Kafka via Helm..."

# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update

# Check if Kafka is already installed
if helm list -n todo | grep -q kafka; then
    echo "✅ Kafka already installed, upgrading..."
    helm upgrade kafka bitnami/kafka \
        --namespace todo \
        --set replicaCount=1 \
        --set persistence.enabled=false \
        --set zookeeper.persistence.enabled=false \
        --set listeners.client.protocol=PLAINTEXT \
        --wait
else
    echo "🆕 Installing Kafka..."
    helm install kafka bitnami/kafka \
        --namespace todo \
        --set replicaCount=1 \
        --set persistence.enabled=false \
        --set zookeeper.persistence.enabled=false \
        --set listeners.client.protocol=PLAINTEXT \
        --wait
fi

echo "✅ Kafka deployed successfully"

# Wait for Kafka to be ready
echo ""
echo "⏳ Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n todo --timeout=300s 2>/dev/null || true
kubectl get pods -n todo -l app.kubernetes.io/name=kafka

# Step 4: Verify installation
echo ""
echo "📋 Step 4: Verifying installation..."
echo ""
echo "Dapr pods:"
kubectl get pods -n dapr-system
echo ""
echo "Kafka pods:"
kubectl get pods -n todo -l app.kubernetes.io/name=kafka
echo ""
echo "Dapr components:"
kubectl get components -n todo 2>/dev/null || echo "No components yet (will be created by Helm chart)"

echo ""
echo "========================================================"
echo "✅ Event-Driven Infrastructure Ready!"
echo "========================================================"
echo ""
echo "Next steps:"
echo "1. Deploy the Todo Platform: helm install todo-platform charts/todo-platform -n todo"
echo "2. Test events: Create a todo via API and check activity logs"
echo "3. View Dapr dashboard: dapr dashboard -k"
echo ""
echo "Useful commands:"
echo "  - kubectl get pods -n todo"
echo "  - kubectl logs -n todo -l app.kubernetes.io/name=kafka"
echo "  - kubectl exec -it -n todo kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092"
echo ""
