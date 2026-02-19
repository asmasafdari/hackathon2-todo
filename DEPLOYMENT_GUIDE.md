# Todo Chatbot - Kubernetes Deployment Guide

Complete guide for deploying the Todo AI Chatbot on local Kubernetes using Minikube and Helm.

## 📋 Prerequisites

- **minikube** - Local Kubernetes cluster ([Install](https://minikube.sigs.k8s.io/docs/start/))
- **kubectl** - Kubernetes CLI ([Install](https://kubernetes.io/docs/tasks/tools/))
- **helm** - Kubernetes package manager ([Install](https://helm.sh/docs/intro/install/))
- **docker** - Container runtime ([Install](https://docs.docker.com/get-docker/))
- **OpenAI API Key** - Required for AI functionality ([Get Key](https://platform.openai.com/api-keys))

## 🚀 Quick Deploy

### Option 1: Automated Deployment Script (Recommended)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Run the deployment script
./scripts/deploy-chatbot-minikube.sh
```

The script will:
1. Check prerequisites
2. Start Minikube cluster
3. Build Docker images
4. Deploy with Helm
5. Show access URLs

### Option 2: Manual Deployment

```bash
# Step 1: Start Minikube
minikube start --profile=todo-chatbot --cpus=4 --memory=8192 --addons=ingress

# Step 2: Set Docker to use Minikube's daemon
eval $(minikube -p todo-chatbot docker-env)

# Step 3: Build images
docker build -t todo-chatbot-backend:latest backend/
docker build -t todo-chatbot-frontend:latest chatbot-frontend/

# Step 4: Deploy with Helm
kubectl create namespace todo-chatbot
helm install chatbot ./charts/chatbot \
  --namespace todo-chatbot \
  --values ./charts/chatbot/values-minikube.yaml \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"

# Step 5: Get access URL
minikube ip --profile=todo-chatbot
```

## 📁 Deployment Structure

```
charts/chatbot/                 # Helm Chart
├── Chart.yaml                  # Chart metadata
├── values.yaml                 # Default values
├── values-minikube.yaml        # Minikube-specific values
└── templates/
    ├── namespace.yaml          # Namespace creation
    ├── backend.yaml            # Backend deployment & service
    ├── frontend.yaml           # Frontend deployment & service
    └── ingress.yaml            # Ingress configuration

k8s/chatbot/base/               # Raw Kubernetes manifests
├── deployment.yaml             # All-in-one deployment
└── ingress.yaml                # Ingress rules

scripts/
└── deploy-chatbot-minikube.sh  # Automated deployment script
```

## 🔧 Configuration

### Environment Variables

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional:**
- `MINIKUBE_PROFILE` - Minikube profile name (default: todo-chatbot)
- `NAMESPACE` - Kubernetes namespace (default: todo-chatbot)

### Helm Values

**Production (values.yaml):**
```yaml
backend:
  image:
    repository: todo-chatbot-backend
    tag: latest
    pullPolicy: IfNotPresent
  
frontend:
  image:
    repository: todo-chatbot-frontend
    tag: latest
    pullPolicy: IfNotPresent
```

**Minikube (values-minikube.yaml):**
```yaml
backend:
  image:
    pullPolicy: Never  # Use locally built images
  
frontend:
  image:
    pullPolicy: Never  # Use locally built images
```

## 📊 Architecture

```
┌─────────────────┐     ┌──────────────────────────┐     ┌──────────────┐
│   Ingress       │────▶│  Backend Service         │────▶│  Backend Pod │
│   (NGINX)       │     │  (ClusterIP:8000)        │     │  (FastAPI)   │
│                 │     └──────────────────────────┘     └──────────────┘
│  /api/*         │                                           │
│  /*             │                                           ▼
└────────┬────────┘                                      ┌──────────────┐
         │                                               │  OpenAI API  │
         │                                               └──────────────┘
         │
         ▼
┌──────────────────────────┐
│  Frontend Service        │
│  (ClusterIP:3000)        │
└──────────────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Frontend Pod            │
│  (Next.js)               │
└──────────────────────────┘
```

## 🎯 Accessing the Application

After deployment:

```bash
# Get Minikube IP
minikube ip --profile=todo-chatbot
# Output: 192.168.49.2

# Access URLs:
# Frontend: http://192.168.49.2
# Backend API: http://192.168.49.2/api
```

Open your browser and navigate to the Frontend URL.

## 🛠️ Useful Commands

### View Resources

```bash
# List all pods
kubectl get pods -n todo-chatbot

# View services
kubectl get svc -n todo-chatbot

# View ingress
kubectl get ingress -n todo-chatbot

# View logs
kubectl logs -n todo-chatbot -l app=backend
kubectl logs -n todo-chatbot -l app=frontend
```

### Port Forwarding (for local testing)

```bash
# Forward backend
kubectl port-forward -n todo-chatbot svc/backend 8000:8000

# Forward frontend
kubectl port-forward -n todo-chatbot svc/frontend 3000:3000
```

### Shell into Containers

```bash
# Backend shell
kubectl exec -it -n todo-chatbot deployment/backend -- /bin/sh

# Frontend shell
kubectl exec -it -n todo-chatbot deployment/frontend -- /bin/sh
```

### Scale Deployments

```bash
# Scale backend
kubectl scale deployment backend --replicas=3 -n todo-chatbot

# Scale frontend
kubectl scale deployment frontend --replicas=2 -n todo-chatbot
```

## 🧹 Cleanup

### Option 1: Using Script

```bash
./scripts/deploy-chatbot-minikube.sh cleanup
```

### Option 2: Manual

```bash
# Remove Helm release
helm uninstall chatbot -n todo-chatbot

# Delete namespace
kubectl delete namespace todo-chatbot

# Stop Minikube
minikube stop --profile=todo-chatbot

# Delete Minikube cluster
minikube delete --profile=todo-chatbot
```

## 🐛 Troubleshooting

### Issue: "ImagePullBackOff" Error

**Cause**: Docker images not found

**Solution**:
```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube -p todo-chatbot docker-env)

# Rebuild images
docker build -t todo-chatbot-backend:latest backend/
docker build -t todo-chatbot-frontend:latest chatbot-frontend/
```

### Issue: "CrashLoopBackOff" Error

**Cause**: Application crashing on startup

**Solution**:
```bash
# Check logs
kubectl logs -n todo-chatbot deployment/backend

# Common fixes:
# 1. Ensure OPENAI_API_KEY is set
# 2. Check database connection
# 3. Verify environment variables
```

### Issue: "502 Bad Gateway"

**Cause**: Ingress cannot reach services

**Solution**:
```bash
# Verify services are running
kubectl get svc -n todo-chatbot

# Check ingress controller
kubectl get pods -n ingress-nginx

# Restart ingress controller if needed
minikube addons disable ingress
minikube addons enable ingress
```

### Issue: "Service Unavailable"

**Cause**: Pods not ready

**Solution**:
```bash
# Check pod status
kubectl get pods -n todo-chatbot

# Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n todo-chatbot --timeout=300s
```

## 📈 Monitoring

### Resource Usage

```bash
# View resource usage
kubectl top pods -n todo-chatbot

# View node usage
kubectl top nodes
```

### Logs Streaming

```bash
# Stream backend logs
kubectl logs -n todo-chatbot -l app=backend -f

# Stream frontend logs
kubectl logs -n todo-chatbot -l app=frontend -f
```

## 🔐 Security Notes

- **Never commit secrets**: API keys are stored in Kubernetes Secrets
- **Use ConfigMaps**: Non-sensitive configuration in ConfigMaps
- **Network policies**: Services are isolated within namespace
- **Non-root containers**: Dockerfiles run as non-root user

## 🚀 Next Steps

### Production Deployment

1. **Push images to registry**:
```bash
docker tag todo-chatbot-backend:latest your-registry/chatbot-backend:1.0.0
docker push your-registry/chatbot-backend:1.0.0
```

2. **Update values.yaml**:
```yaml
backend:
  image:
    repository: your-registry/chatbot-backend
    tag: 1.0.0
    pullPolicy: Always
```

3. **Configure TLS**:
```yaml
ingress:
  tls:
    - secretName: chatbot-tls
      hosts:
        - chatbot.yourdomain.com
```

### Advanced Features

- **Horizontal Pod Autoscaling (HPA)**
- **Pod Disruption Budgets (PDB)**
- **Network Policies**
- **Service Mesh (Istio/Linkerd)**
- **Prometheus/Grafana Monitoring**

## 📚 Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

## 🆘 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review logs: `kubectl logs -n todo-chatbot <pod-name>`
3. Check [Phase III Implementation Guide](./PHASE_III_IMPLEMENTATION.md)

---

**Status**: Ready for deployment ✅  
**Last Updated**: February 12, 2026
