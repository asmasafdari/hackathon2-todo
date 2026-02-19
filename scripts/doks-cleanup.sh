#!/bin/bash
# DigitalOcean Kubernetes Cleanup Script

echo "🧹 DigitalOcean Kubernetes Cleanup"
echo "==================================="

echo ""
echo "⚠️  This will delete resources from DigitalOcean"

echo ""
read -p "Remove Helm release 'todo-platform'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    helm uninstall todo-platform -n todo 2>/dev/null || echo "No release found"
fi

echo ""
read -p "Remove ingress-nginx? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    helm uninstall ingress-nginx -n ingress-nginx 2>/dev/null || echo "Not found"
    kubectl delete namespace ingress-nginx 2>/dev/null || true
fi

echo ""
read -p "Remove namespace 'todo'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl delete namespace todo 2>/dev/null || echo "Not found"
fi

echo ""
read -p "Delete Kubernetes cluster '${CLUSTER_NAME:-todo-cluster}'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    doctl kubernetes cluster delete ${CLUSTER_NAME:-todo-cluster} --force
fi

echo ""
read -p "Delete Container Registry? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    doctl registry delete --force 2>/dev/null || echo "Not found"
fi

echo ""
echo "✓ Cleanup complete"
