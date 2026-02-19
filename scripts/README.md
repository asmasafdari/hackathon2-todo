# Complete Deployment Guide

This guide covers deploying the Todo Platform across multiple platforms: **Docker**, **Minikube**, **DigitalOcean Kubernetes (DOKS)**, **kubectl**, and **AI Agent (kagent)** deployment.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Options](#deployment-options)
  - [Docker (Local)](#1-docker-local)
  - [Minikube (Local Kubernetes)](#2-minikube-local-kubernetes)
  - [DigitalOcean Kubernetes (DOKS)](#3-digitalocean-kubernetes-doks)
  - [kubectl (Any Kubernetes)](#4-kubectl-any-kubernetes)
  - [Event-Driven (Kafka + Dapr)](#5-event-driven-kafka--dapr)
  - [AI Agent (kagent)](#6-ai-agent-kagent)
- [Environment Setup](#environment-setup)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Common Tools

| Tool | Purpose | Install Command (macOS) |
|------|---------|-------------------------|
| Docker | Container runtime | `brew install docker` |
| kubectl | Kubernetes CLI | `brew install kubectl` |
| Helm | Kubernetes package manager | `brew install helm` |
| doctl | DigitalOcean CLI (for DOKS) | `brew install doctl` |
| minikube | Local Kubernetes | `brew install minikube` |
| dapr | Dapr CLI (for event-driven) | `brew install dapr/tap/dapr-cli` |

### Windows Installation
```powershell
# Using Chocolatey
choco install docker-desktop kubernetes-cli kubernetes-helm minikube

# DigitalOcean CLI
choco install doctl

# Dapr
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### Linux Installation
```bash
# Docker
curl -fsSL https://get.docker.com | sh

# kubectl
curl -LO "https://dl.k8s/release/$(curl -L -s https://dl.k8s/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

## ⚙️ Environment Setup

Before deploying, configure your environment variables:

### Backend (`backend/.env`)
```bash
# For local development (SQLite)
DATABASE_URL=sqlite:///app/data/todos.db

# For production (PostgreSQL via Neon)
# DATABASE_URL=postgresql://user:password@host.neon.tech/db?sslmode=require
```

### AI Agent (`agent/.env`)
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
TODO_API_BASE_URL=http://backend:8000
```

### Frontend (`frontend/.env`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Quick Start

### Option A: Docker (Simplest)
```bash
./scripts/docker-deploy.sh
```
Access: http://localhost:3000

### Option B: Minikube (Local Kubernetes)
```bash
./scripts/minikube-deploy.sh
```
Access: http://localhost (via `minikube tunnel`)

### Option C: DigitalOcean (Production)
```bash
export DIGITALOCEAN_ACCESS_TOKEN=your-token
./scripts/doks-deploy.sh
```
Access: External IP provided after deployment

## 📦 Deployment Options

### 1. Docker (Local)

**Best for:** Local development, quick testing

```bash
# Deploy with Docker
./scripts/docker-deploy.sh

# Or use Docker Compose for more control
cd scripts
docker-compose -f docker-compose.yml up -d

# With AI Agent
docker-compose -f docker-compose.yml --profile with-agent up -d

# With Kafka (event-driven)
docker-compose -f docker-compose.yml --profile with-kafka up -d
```

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Cleanup:**
```bash
./scripts/docker-cleanup.sh
```

---

### 2. Minikube (Local Kubernetes)

**Best for:** Testing Kubernetes locally, learning K8s

```bash
# Deploy everything
./scripts/minikube-deploy.sh

# With Kafka for event-driven mode
./scripts/minikube-deploy.sh
# Then when prompted: y

# Or manually add Kafka after
./scripts/kafka-deploy.sh
```

**Access the App:**
```bash
# Option 1: Tunnel (recommended)
minikube tunnel
# Access: http://localhost

# Option 2: Port forward
kubectl port-forward -n todo svc/frontend 3000:3000
# Access: http://localhost:3000

# Option 3: Minikube service
minikube service frontend -n todo
```

**Cleanup:**
```bash
./scripts/minikube-cleanup.sh
```

---

### 3. DigitalOcean Kubernetes (DOKS)

**Best for:** Production, scalable cloud deployment

**Prerequisites:**
```bash
# Authenticate with DigitalOcean
doctl auth init

# Set environment variables (optional)
export CLUSTER_NAME=todo-cluster
export REGION=nyc3
export NODE_SIZE=s-2vcpu-4gb
export NODE_COUNT=2
```

**Deploy:**
```bash
./scripts/doks-deploy.sh
```

This script will:
1. Create a Kubernetes cluster on DigitalOcean
2. Create a Container Registry
3. Build and push images
4. Install NGINX Ingress Controller
5. Deploy the application with Helm

**Access:**
The script will output the external IP address. Access via:
- http://<EXTERNAL_IP>
- http://<EXTERNAL_IP>/api/docs (API documentation)

**Cleanup:**
```bash
./scripts/doks-cleanup.sh
```

**Manual Steps (if needed):**
```bash
# Get kubeconfig
doctl kubernetes cluster kubeconfig save <cluster-name>

# Check cluster
kubectl get nodes

# Deploy manually
helm install todo-platform charts/todo-platform \
  -f charts/todo-platform/values.yaml \
  --namespace todo --create-namespace
```

---

### 4. kubectl (Any Kubernetes)

**Best for:** Custom Kubernetes clusters, existing infrastructure

```bash
# Ensure you have kubeconfig set up for your cluster
kubectl config current-context

# Deploy with kubectl
./scripts/kubectl-deploy.sh
```

**What it does:**
- Applies ConfigMap for configuration
- Creates Secrets from environment
- Deploys all services
- Sets up Services and Ingress

**Access:**
```bash
kubectl port-forward -n todo svc/frontend 3000:3000
# Access: http://localhost:3000
```

**Manual kubectl commands:**
```bash
# Create namespace
kubectl create namespace todo

# Apply manifests
kubectl apply -f scripts/kubectl-manifests/ -n todo

# Check status
kubectl get all -n todo
```

---

### 5. Event-Driven (Kafka + Dapr)

**Best for:** Production with async processing, audit trails

**Prerequisites:**
- Running Kubernetes cluster (Minikube or DOKS)
- Dapr CLI installed

**Deploy:**
```bash
# Deploy to existing cluster with Kafka
cd scripts
./kafka-deploy.sh
```

This will:
1. Install Dapr runtime in the cluster
2. Deploy Kafka (via Bitnami Helm chart)
3. Create Dapr Pub/Sub component
4. Create Kafka topics
5. Deploy app with Dapr sidecars
6. Configure event subscriptions

**Event Topics:**
- `todo-created` - New todo created
- `todo-updated` - Todo updated
- `todo-completed` - Todo marked complete
- `todo-deleted` - Todo deleted
- `agent-action-executed` - AI agent performed action
- `agent-action-failed` - AI agent action failed

**Test Events:**
```bash
# List topics
kubectl exec -n todo kafka-0 -- \
  kafka-topics.sh --list --bootstrap-server localhost:9092

# Produce test message
kubectl exec -n todo kafka-0 -- \
  kafka-console-producer.sh --topic todo-created --bootstrap-server localhost:9092

# Consume messages
kubectl exec -n todo kafka-0 -- \
  kafka-console-consumer.sh --topic todo-created --from-beginning --bootstrap-server localhost:9092

# View Dapr dashboard
dapr dashboard -k
```

---

### 6. AI Agent (kagent)

**Best for:** Deploying the AI-powered todo assistant

**Prerequisites:**
- OpenAI API key
- Running backend service

**Deploy:**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key

# Or have it in agent/.env file

# Deploy AI Agent
cd scripts
./kagent-deploy.sh
```

**Usage:**
```bash
# Port forward to interact locally
kubectl port-forward -n todo svc/kagent 8080:8080

# Or use with Claude Desktop
# Configure Claude Desktop to use the MCP server
```

**Features:**
- Natural language todo creation
- Intelligent task queries
- Conversational task completion
- Event publishing for audit trail

---

## 🔍 Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Find and kill process on port 3000 or 8000
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Or use different ports
docker run -p 3001:3000 todo-frontend:latest
```

**Image build fails:**
```bash
# Clean build cache
docker build --no-cache -t todo-backend:latest backend/
```

### Kubernetes Issues

**Pods stuck in Pending:**
```bash
# Check events
kubectl get events -n todo --sort-by='.lastTimestamp'

# Common causes:
# - Insufficient resources
# - Image pull errors
```

**ImagePullBackOff:**
```bash
# For Minikube - ensure docker-env is set
eval $(minikube docker-env)

# Rebuild images
docker build -t todo-backend:latest backend/
docker build -t todo-frontend:latest frontend/

# Restart deployment
kubectl rollout restart deployment -n todo
```

**Backend can't connect to database:**
```bash
# Check logs
kubectl logs -n todo deployment/todo-platform-backend

# Verify secrets
kubectl get secret -n todo todo-platform-secrets -o yaml
```

### Kafka Issues

**Kafka not starting:**
```bash
# Check Kafka logs
kubectl logs -n todo -l app.kubernetes.io/name=kafka

# Check resource limits
kubectl describe pod -n todo kafka-0
```

**Events not being published:**
```bash
# Check Dapr sidecar logs
kubectl logs -n todo deployment/todo-platform-backend -c daprd

# Verify Dapr component
kubectl get components -n todo
```

### DigitalOcean Issues

**doctl auth failed:**
```bash
doctl auth init
# Enter your DigitalOcean API token
```

**Cluster creation fails:**
```bash
# Check available regions
doctl kubernetes options regions

# Check account limits
doctl account get
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Ingress Controller                       │
│                    (NGINX / Minikube)                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
┌──────▼──────┐      ┌────────▼─────┐
│  Frontend   │      │   Backend    │
│  (Next.js)  │      │  (FastAPI)   │
│   Port 3000 │      │   Port 8000  │
└─────────────┘      └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
       ┌──────▼────┐ ┌──────▼────┐ ┌─────▼──────┐
       │   Kafka   │ │ Database  │ │   AI Agent │
       │  (Dapr)   │ │(PostgreSQL│ │   (MCP)    │
       └───────────┘ │ /SQLite)  │ └────────────┘
                     └───────────┘
                            │
                     ┌──────▼──────┐
                     │Activity Log │
                     │  (Events)   │
                     └─────────────┘
```

---

## 🔗 Useful Commands

```bash
# View all resources
kubectl get all -n todo

# View logs
kubectl logs -n todo -l app.kubernetes.io/name=backend -f

# Shell into container
kubectl exec -it -n todo deployment/todo-platform-backend -- /bin/sh

# Scale deployment
kubectl scale deployment -n todo todo-platform-backend --replicas=3

# Port forward
kubectl port-forward -n todo svc/backend 8000:8000

# Helm upgrade
helm upgrade todo-platform charts/todo-platform -n todo

# Helm rollback
helm rollback todo-platform -n todo

# Delete everything
helm uninstall todo-platform -n todo
kubectl delete namespace todo
```

---

## 📚 Additional Resources

- [Helm Chart Documentation](../charts/DEPLOYMENT.md)
- [Kafka Configuration](../charts/KAFKA.md)
- [Event-Driven Spec](../specs/004-event-driven-kafka/spec.md)
- [Dapr Documentation](https://docs.dapr.io/)
- [DigitalOcean Kubernetes Docs](https://docs.digitalocean.com/products/kubernetes/)

---

**Need help?** Check the troubleshooting section above or run individual scripts with `--help` flag.
