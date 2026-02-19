# Deployment Guide - Minikube

This guide walks you through deploying the complete Todo Platform to a local Minikube cluster.

## Prerequisites

### Required Tools
- **Docker** - For building container images
- **Minikube** - Local Kubernetes cluster
- **Helm** - Kubernetes package manager
- **kubectl** - Kubernetes CLI

### Install Commands

**macOS (Homebrew):**
```bash
brew install docker minikube helm kubectl
```

**Windows (Chocolatey):**
```bash
choco install docker-desktop minikube kubernetes-helm kubernetes-cli
```

**Linux:**
```bash
# Docker
curl -fsSL https://get.docker.com | sh

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl
curl -LO "https://dl.k8s/release/$(curl -L -s https://dl.k8s/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

## Step 1: Configure Environment Variables

Ensure your `.env` files are properly configured:

**backend/.env:**
```bash
DATABASE_URL=postgresql://user:password@your-neon-host.neon.tech/neondb?sslmode=require
# Or use SQLite for local testing:
# DATABASE_URL=sqlite+aiosqlite:///./todos.db
```

**agent/.env:**
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
TODO_API_BASE_URL=http://backend:8000
```

## Step 2: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --disk-size=20g

# Enable ingress addon
minikube addons enable ingress

# Verify cluster is ready
kubectl get nodes
```

## Step 3: Build Container Images

Configure your shell to use Minikube's Docker daemon:

```bash
# macOS/Linux
eval $(minikube docker-env)

# Windows PowerShell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Windows CMD
@FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i
```

Build all three images:

```bash
# Build backend
docker build -t todo-backend:latest backend/

# Build frontend
docker build -t todo-frontend:latest frontend/

# Build MCP server
docker build -t todo-mcp:latest agent/
```

Verify images were built:
```bash
docker images | grep todo-
```

## Step 4: Create Secrets

Create a `values-secrets.yaml` file (do NOT commit this to git):

```bash
cat > charts/todo-platform/values-secrets.yaml <<EOF
secrets:
  databaseUrl: "postgresql://user:password@your-neon-host.neon.tech/neondb?sslmode=require"
  openaiApiKey: "sk-your-openai-api-key-here"
EOF
```

## Step 5: Deploy with Helm

### Option A: Deploy with Secrets File
```bash
helm install todo-platform charts/todo-platform \
  -f charts/todo-platform/values.yaml \
  -f charts/todo-platform/values-secrets.yaml \
  --namespace todo \
  --create-namespace
```

### Option B: Deploy with Inline Secrets
```bash
helm install todo-platform charts/todo-platform \
  --namespace todo \
  --create-namespace \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.openaiApiKey="sk-..."
```

## Step 6: Verify Deployment

Check pod status:
```bash
kubectl get pods -n todo
```

Expected output (all pods should be `Running`):
```
NAME                                  READY   STATUS    RESTARTS   AGE
todo-platform-backend-xxx             2/2     Running   0          2m
todo-platform-frontend-xxx            1/1     Running   0          2m
todo-platform-mcp-xxx                 2/2     Running   0          2m
```

Check services:
```bash
kubectl get svc -n todo
```

View logs if pods aren't ready:
```bash
# Backend logs
kubectl logs -n todo deployment/todo-platform-backend -c backend

# MCP server logs
kubectl logs -n todo deployment/todo-platform-mcp -c mcp
```

## Step 7: Access the Application

### Option A: Using Minikube Tunnel (Recommended)
```bash
# Start tunnel (keeps running)
minikube tunnel

# In another terminal, get the URL
kubectl get ingress -n todo
```

Access at: `http://localhost`

### Option B: Using Port Forward
```bash
# Forward frontend port
kubectl port-forward -n todo svc/frontend 3000:3000

# Forward backend port (in another terminal)
kubectl port-forward -n todo svc/backend 8000:8000
```

Access at: `http://localhost:3000`

### Option C: Using Minikube Service
```bash
minikube service frontend -n todo
```

## Step 8: Test the Deployment

1. **Test Frontend**: Open browser to the URL
   - Should see the Todo web interface
   - Try creating a todo

2. **Test Backend API**:
   ```bash
   curl http://localhost/api/todos
   ```

3. **Test Health Endpoints**:
   ```bash
   curl http://localhost/api/health
   ```

## Troubleshooting

### Pods stuck in Pending
```bash
# Check events
kubectl get events -n todo --sort-by='.lastTimestamp'

# Common causes:
# - Insufficient resources: Increase minikube memory
# - Image pull errors: Verify images built in minikube's docker
```

### ImagePullBackOff
```bash
# Verify docker-env is set
eval $(minikube docker-env)

# Rebuild images
docker build -t todo-backend:latest backend/
docker build -t todo-frontend:latest frontend/
docker build -t todo-mcp:latest agent/

# Restart deployment
kubectl rollout restart deployment -n todo
```

### Backend can't connect to database
```bash
# Check backend logs
kubectl logs -n todo deployment/todo-platform-backend

# Verify DATABASE_URL secret
kubectl get secret -n todo todo-platform-secrets -o yaml
```

### MCP server can't reach backend
```bash
# Check if backend service is accessible
kubectl exec -n todo deployment/todo-platform-mcp -- \
  curl http://backend:8000/health
```

## Useful Commands

```bash
# Scale deployments
kubectl scale deployment -n todo todo-platform-backend --replicas=3

# View all resources
kubectl get all -n todo

# Describe a pod for debugging
kubectl describe pod -n todo <pod-name>

# Shell into a container
kubectl exec -it -n todo deployment/todo-platform-backend -c backend -- /bin/sh

# Upgrade deployment
helm upgrade todo-platform charts/todo-platform -n todo

# Rollback deployment
helm rollback todo-platform -n todo

# Delete everything
helm uninstall todo-platform -n todo
kubectl delete namespace todo
```

## Cleanup

```bash
# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete

# Or delete just the deployment
helm uninstall todo-platform -n todo
kubectl delete namespace todo
```

---

## Chatbot Deployment (Phase III)

The Todo AI Chatbot has its own Helm chart at `charts/chatbot/` with a dedicated deploy script.

### Quick Start

```bash
# Set required environment variables
export OPENAI_API_KEY="sk-..."
export CLERK_SECRET_KEY="sk_..."
export CLERK_PUBLISHABLE_KEY="pk_..."

# Run the automated deploy script
./scripts/deploy-minikube.sh
```

The script handles: Minikube startup, ingress addon, Docker image builds, and Helm deployment.

### Manual Deployment

```bash
# 1. Start Minikube and configure Docker
minikube start --cpus=4 --memory=4096
minikube addons enable ingress
eval $(minikube docker-env)

# 2. Build images
docker build -t todo-chatbot-backend:latest -f backend/Dockerfile .
docker build -t todo-chatbot-frontend:latest ./chatbot-frontend

# 3. Deploy
helm install chatbot charts/chatbot \
  -f charts/chatbot/values-minikube.yaml \
  --namespace todo-chatbot \
  --create-namespace \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set secrets.clerkSecretKey="$CLERK_SECRET_KEY" \
  --set secrets.clerkPublishableKey="$CLERK_PUBLISHABLE_KEY" \
  --set secrets.clerkDomain=""

# 4. Verify
kubectl get pods -n todo-chatbot

# 5. Access
kubectl port-forward -n todo-chatbot svc/frontend 3000:3000
kubectl port-forward -n todo-chatbot svc/backend 8000:8000
```

### Chatbot Cleanup

```bash
helm uninstall chatbot -n todo-chatbot
kubectl delete namespace todo-chatbot
```

---

## Next Steps

- Set up CI/CD pipeline for automated deployments
- Configure monitoring with Prometheus/Grafana
- Set up log aggregation
- Configure TLS certificates
- Deploy to cloud Kubernetes (EKS, GKE, AKS)
