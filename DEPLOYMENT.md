# Chatbot Deployment Guide

This guide covers deploying the Todo Platform (with AI chatbot capabilities) locally on Kubernetes and to DigitalOcean Kubernetes Service (DOKS).

## ✅ Local Deployment Status: COMPLETE

The application has been successfully deployed to Docker Desktop Kubernetes cluster:

### What's Working:
- **Frontend**: Running and accessible ✅
- **Backend API**: Running and responding to requests ✅
- **MCP (AI Agent)**: Deployed (requires OpenAI API key for full functionality)
- **Database**: SQLite with async support configured ✅

### Access URLs:
```bash
# Frontend (via port-forward)
kubectl port-forward -n todo svc/frontend 3000:3000
# Access: http://localhost:3000

# Backend API (via port-forward)
kubectl port-forward -n todo svc/backend 8000:8000
# Access: http://localhost:8000/api/docs
```

### Quick Test:
```bash
# Port forward backend
kubectl port-forward -n todo svc/backend 8000:8000 &

# Test the API
curl http://localhost:8000/api/todos

# Create a todo
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test from Kubernetes"}'
```

---

## ☁️ DigitalOcean Kubernetes (DOKS) Deployment

### Prerequisites

1. **DigitalOcean Account**: Sign up at https://cloud.digitalocean.com
2. **doctl CLI**: Install the DigitalOcean CLI
3. **Docker**: For building container images
4. **kubectl**: Kubernetes CLI
5. **Helm**: Kubernetes package manager

### Install doctl

**macOS:**
```bash
brew install doctl
```

**Linux:**
```bash
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.125.1/doctl-1.125.1-linux-amd64.tar.gz | tar -xzv
sudo mv doctl /usr/local/bin
```

**Windows:**
```powershell
# Using Chocolatey
choco install doctl
```

### Authenticate with DigitalOcean

```bash
# Run interactive authentication
doctl auth init
# Enter your API token when prompted

# Verify authentication
doctl account get
```

### Deployment Steps

#### 1. Set Environment Variables (Optional)

```bash
export CLUSTER_NAME=todo-cluster
export REGION=nyc3
export NODE_SIZE=s-2vcpu-4gb
export NODE_COUNT=2
```

#### 2. Create Kubernetes Cluster

```bash
# Create the cluster (takes 5-10 minutes)
doctl kubernetes cluster create $CLUSTER_NAME \
  --region $REGION \
  --size $NODE_SIZE \
  --count $NODE_COUNT \
  --wait

# Save kubeconfig
doctl kubernetes cluster kubeconfig save $CLUSTER_NAME

# Verify cluster
kubectl get nodes
```

#### 3. Create Container Registry

```bash
# Create registry
doctl registry create todo-registry

# Login to registry
doctl registry login

# Get registry endpoint
export REGISTRY_ENDPOINT=$(doctl registry get --format Endpoint | tail -n1)
echo "Registry: $REGISTRY_ENDPOINT"
```

#### 4. Build and Push Images

```bash
# Build and push backend
docker build -t $REGISTRY_ENDPOINT/todo-backend:latest backend/
docker push $REGISTRY_ENDPOINT/todo-backend:latest

# Build and push frontend
docker build -t $REGISTRY_ENDPOINT/todo-frontend:latest frontend/
docker push $REGISTRY_ENDPOINT/todo-frontend:latest

# Build and push MCP
docker build -t $REGISTRY_ENDPOINT/todo-mcp:latest agent/
docker push $REGISTRY_ENDPOINT/todo-mcp:latest

# Optional: Build and push activity-logger
docker build -t $REGISTRY_ENDPOINT/todo-activity-logger:latest activity_logger/
docker push $REGISTRY_ENDPOINT/todo-activity-logger:latest
```

#### 5. Configure Secrets

Create the secrets file with your production credentials:

```bash
cat > charts/todo-platform/values-secrets.yaml << 'EOF'
secrets:
  # Use PostgreSQL for production (recommended)
  databaseUrl: "postgresql+asyncpg://user:password@your-db-host:5432/todo_db"
  # OR use SQLite (not recommended for production)
  # databaseUrl: "sqlite+aiosqlite:///app/data/todos.db"
  
  # OpenAI API key for AI chatbot features (optional)
  openaiApiKey: "sk-your-openai-api-key"
EOF
```

**Note**: For production, use a managed PostgreSQL database from DigitalOcean or Neon.

#### 6. Install NGINX Ingress Controller

```bash
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --wait
```

#### 7. Deploy Application

```bash
# Create namespace
kubectl create namespace todo

# Deploy with Helm
helm upgrade --install todo-platform charts/todo-platform \
  -f charts/todo-platform/values.yaml \
  -f charts/todo-platform/values-doks.yaml \
  -f charts/todo-platform/values-secrets.yaml \
  --namespace todo \
  --wait \
  --timeout 10m
```

#### 8. Get External IP

```bash
# Wait for external IP
kubectl get svc ingress-nginx-controller -n ingress-nginx -w

# Or get it immediately
export EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"
```

#### 9. Configure DNS (Optional)

If you have a custom domain:

```bash
# Create A record pointing to EXTERNAL_IP
# Example: todo.yourdomain.com -> $EXTERNAL_IP

# Update ingress host
kubectl patch ingress todo-platform-ingress -n todo \
  --type merge \
  -p '{"spec":{"rules":[{"host":"todo.yourdomain.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"frontend","port":{"number":3000}}}}]}}]}}'
```

#### 10. Verify Deployment

```bash
# Check all pods
kubectl get pods -n todo

# Check services
kubectl get svc -n todo

# Test API
curl http://$EXTERNAL_IP/api/health

# Check logs
kubectl logs -n todo -l app.kubernetes.io/name=backend
```

---

## 🔧 Automated Deployment Scripts

### Option 1: Use the Existing Scripts

```bash
# For local deployment (Docker Desktop Kubernetes)
./scripts/minikube-deploy.sh

# For DigitalOcean (requires doctl auth)
export DIGITALOCEAN_ACCESS_TOKEN=your-token
./scripts/doks-deploy.sh
```

### Option 2: One-Command Deployment

```bash
# Local deployment
make deploy-local

# DigitalOcean deployment
make deploy-doks
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Backend logs
kubectl logs -n todo -l app.kubernetes.io/name=backend -f

# Frontend logs
kubectl logs -n todo -l app.kubernetes.io/name=frontend -f

# MCP logs
kubectl logs -n todo -l app.kubernetes.io/name=mcp -f
```

### Scale Deployments

```bash
# Scale backend to 3 replicas
kubectl scale deployment -n todo todo-platform-backend --replicas=3

# Scale frontend to 3 replicas
kubectl scale deployment -n todo todo-platform-frontend --replicas=3
```

### Shell into Containers

```bash
# Backend shell
kubectl exec -it -n todo deployment/todo-platform-backend -- /bin/sh

# Database inspection (SQLite)
kubectl exec -it -n todo deployment/todo-platform-backend -- sqlite3 /app/data/todos.db "SELECT * FROM todo;"
```

---

## 🧹 Cleanup

### Local Cleanup

```bash
# Remove deployment
helm uninstall todo-platform -n todo
kubectl delete namespace todo

# Stop Docker Desktop Kubernetes (via Docker Desktop UI)
```

### DigitalOcean Cleanup

```bash
# Remove deployment
helm uninstall todo-platform -n todo
kubectl delete namespace todo

# Delete cluster (costs money!)
doctl kubernetes cluster delete $CLUSTER_NAME

# Delete registry
doctl registry delete
```

---

## 🔍 Troubleshooting

### Common Issues

**1. ImagePullBackOff**
- Check if images are built and pushed to registry
- Verify registry authentication: `doctl registry login`

**2. CrashLoopBackOff**
- Check logs: `kubectl logs -n todo deployment/todo-platform-backend`
- Verify secrets are configured correctly
- Check database URL format (must use `sqlite+aiosqlite://` or `postgresql+asyncpg://`)

**3. Pending Pods**
- Check resource limits: `kubectl describe pod -n todo <pod-name>`
- May need to increase cluster node size or count

**4. Ingress Not Working**
- Verify ingress controller is installed: `kubectl get pods -n ingress-nginx`
- Check ingress resource: `kubectl get ingress -n todo`
- Get external IP: `kubectl get svc -n ingress-nginx`

**5. Database Connection Issues**
- Verify DATABASE_URL format
- For SQLite: Use `sqlite+aiosqlite:///app/data/todos.db`
- For PostgreSQL: Use `postgresql+asyncpg://user:pass@host/db`

---

## 📚 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Ingress Controller                       │
│                    (NGINX / Load Balancer)                   │
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
               ┌────────────┴─────────────┐
               │                          │
        ┌──────▼──────┐          ┌───────▼────────┐
        │  Database   │          │   AI Agent     │
        │  (SQLite/   │          │   (MCP Server) │
        │ PostgreSQL) │          └────────────────┘
        └─────────────┘
```

---

## 🚀 Next Steps

1. **Production Database**: Set up a managed PostgreSQL database
2. **SSL/TLS**: Configure HTTPS with Let's Encrypt
3. **Monitoring**: Add Prometheus/Grafana for observability
4. **CI/CD**: Set up GitHub Actions for automated deployments
5. **Scaling**: Configure Horizontal Pod Autoscaling (HPA)
6. **Backup**: Set up database backup strategies

---

## 📖 Additional Resources

- [Helm Documentation](https://helm.sh/docs/)
- [DigitalOcean Kubernetes Docs](https://docs.digitalocean.com/products/kubernetes/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the logs: `kubectl logs -n todo <pod-name>`
3. Check the [scripts/README.md](../scripts/README.md) for more details
