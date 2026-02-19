# Quickstart: Cloud-Native Deployment

**Feature**: 003-cloud-native-k8s

## Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Version | Verify Command |
|------|---------|----------------|
| Docker | 20.10+ | `docker --version` |
| Minikube | 1.30+ | `minikube version` |
| kubectl | 1.27+ | `kubectl version --client` |
| Helm | 3.12+ | `helm version` |

## Quick Deploy (5 minutes)

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --driver=docker --memory=4096 --cpus=2

# Enable ingress addon
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
```

### 2. Build Container Images

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Build all images (from project root)
docker build -t todo-backend:dev -f backend/Dockerfile backend/
docker build -t todo-frontend:dev -f frontend/Dockerfile frontend/
docker build -t todo-mcp:dev -f agent/Dockerfile agent/
```

### 3. Create Secrets File

```bash
# Create values-secrets.yaml (DO NOT COMMIT THIS FILE)
cat > charts/todo-platform/values-secrets.yaml << 'EOF'
secrets:
  databaseUrl: "postgresql://user:pass@your-neon-host/dbname?sslmode=require"
  openaiApiKey: "sk-your-openai-api-key"
EOF
```

### 4. Deploy with Helm

```bash
# Install the application
helm install todo charts/todo-platform \
  -f charts/todo-platform/values-secrets.yaml \
  --set global.imageTag=dev

# Watch pods come up
kubectl get pods -w
```

### 5. Access the Application

```bash
# Get the Minikube IP
minikube ip

# Or use tunnel for localhost access
minikube tunnel

# Access the application
# Frontend: http://localhost/ or http://$(minikube ip)/
# Backend API: http://localhost/api/todos
```

## Verification

### Check Pod Health

```bash
# All pods should be Running
kubectl get pods

# Check logs if issues
kubectl logs -l app=backend
kubectl logs -l app=frontend
kubectl logs -l app=mcp
```

### Test API

```bash
# Health check
curl http://localhost/api/health

# Create a todo
curl -X POST http://localhost/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test from K8s"}'

# List todos
curl http://localhost/api/todos
```

### Test Frontend

Open `http://localhost/` in your browser. You should see the Todo application.

## Common Operations

### Upgrade Deployment

```bash
# After code changes, rebuild images
docker build -t todo-backend:v2 -f backend/Dockerfile backend/

# Upgrade the release
helm upgrade todo charts/todo-platform \
  -f charts/todo-platform/values-secrets.yaml \
  --set global.imageTag=v2
```

### Rollback

```bash
# View release history
helm history todo

# Rollback to previous version
helm rollback todo 1
```

### View Logs

```bash
# Follow logs for a service
kubectl logs -f -l app=backend

# Get all events
kubectl get events --sort-by='.lastTimestamp'
```

### Uninstall

```bash
# Remove the application
helm uninstall todo

# Stop Minikube
minikube stop
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pods stuck in `Pending` | Check resources: `kubectl describe pod <name>` |
| Pods in `CrashLoopBackOff` | Check logs: `kubectl logs <pod-name>` |
| `ImagePullBackOff` | Ensure images are built in Minikube's Docker |
| Can't access via browser | Run `minikube tunnel` in separate terminal |
| Database connection failed | Verify `DATABASE_URL` in secrets and network access |

## File Structure After Setup

```
charts/
└── todo-platform/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-secrets.yaml    # Your secrets (gitignored)
    ├── charts/
    │   ├── backend/
    │   ├── frontend/
    │   └── mcp/
    └── templates/
        ├── namespace.yaml
        ├── configmap.yaml
        ├── secrets.yaml
        └── ingress.yaml
```

## Next Steps

1. **Custom Domain**: Set `ingress.host` in values.yaml
2. **TLS**: Add TLS configuration to ingress
3. **CI/CD**: Automate image builds and deployments
4. **Monitoring**: Add Prometheus/Grafana for observability
