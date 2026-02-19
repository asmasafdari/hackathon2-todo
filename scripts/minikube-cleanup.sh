#!/bin/bash
# Minikube Cleanup Script

echo "🧹 Minikube Cleanup"
echo "=================="

echo ""
echo "Removing Helm release..."
helm uninstall todo-platform -n todo 2>/dev/null || echo "No Helm release found"

echo ""
echo "Removing Kafka..."
helm uninstall kafka -n todo 2>/dev/null || echo "No Kafka found"

echo ""
read -p "Delete namespace 'todo'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl delete namespace todo
    echo "✓ Namespace deleted"
fi

echo ""
read -p "Stop Minikube? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    minikube stop
    echo "✓ Minikube stopped"
fi

echo ""
read -p "Delete Minikube cluster (all data will be lost)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    minikube delete
    echo "✓ Minikube cluster deleted"
fi

echo ""
echo "✓ Cleanup complete"
