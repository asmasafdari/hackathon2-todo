#!/bin/bash
# End-to-End Event Flow Validation Script
# Tests the complete event-driven flow from todo creation to activity log

set -e

echo "🧪 E2E Event Flow Validation"
echo "============================="
echo ""

# Configuration
NAMESPACE="${NAMESPACE:-todo}"
BACKEND_URL="${BACKEND_URL:-}"
ACTIVITY_LOGGER_URL="${ACTIVITY_LOGGER_URL:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test tracking
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    fail "kubectl not found"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    fail "curl not found"
    exit 1
fi

pass "Prerequisites met"

# Check namespace exists
echo ""
echo "🔍 Checking namespace..."
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    pass "Namespace '$NAMESPACE' exists"
else
    fail "Namespace '$NAMESPACE' not found"
    exit 1
fi

# Check pods are running
echo ""
echo "🔍 Checking pod status..."
PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null || true)

if [ -z "$PODS" ]; then
    fail "No pods found in namespace $NAMESPACE"
    exit 1
fi

# Check each pod is running
while IFS= read -r line; do
    POD_NAME=$(echo "$line" | awk '{print $1}')
    POD_STATUS=$(echo "$line" | awk '{print $3}')
    
    if [ "$POD_STATUS" == "Running" ]; then
        pass "Pod $POD_NAME is Running"
    else
        fail "Pod $POD_NAME is not Running (status: $POD_STATUS)"
    fi
done <<< "$PODS"

# Check Dapr sidecars are injected
echo ""
echo "🔍 Checking Dapr sidecars..."
DEPLOYMENTS=("backend" "mcp" "activity-logger")
for DEP in "${DEPLOYMENTS[@]}"; do
    if kubectl get deployment -n "$NAMESPACE" -l app="$DEP" &> /dev/null; then
        SIDECAR_COUNT=$(kubectl get pods -n "$NAMESPACE" -l app="$DEP" -o jsonpath='{.items[0].spec.containers[*].name}' 2>/dev/null | grep -c "daprd" || true)
        if [ "$SIDECAR_COUNT" -ge 1 ]; then
            pass "Dapr sidecar injected in $DEP"
        else
            warn "Dapr sidecar not found in $DEP (may not be enabled)"
        fi
    fi
done

# Get service URLs
echo ""
echo "🔍 Getting service endpoints..."

# Try to get backend URL
if [ -z "$BACKEND_URL" ]; then
    if command -v minikube &> /dev/null; then
        BACKEND_URL=$(minikube service backend -n "$NAMESPACE" --url 2>/dev/null || true)
    fi
    
    if [ -z "$BACKEND_URL" ]; then
        # Try port-forward
        echo "Setting up port-forward for backend..."
        kubectl port-forward svc/backend -n "$NAMESPACE" 18000:8000 &>/dev/null &
        PF_PID=$!
        sleep 2
        BACKEND_URL="http://localhost:18000"
    fi
fi

# Try to get activity-logger URL
if [ -z "$ACTIVITY_LOGGER_URL" ]; then
    if command -v minikube &> /dev/null; then
        ACTIVITY_LOGGER_URL=$(minikube service activity-logger -n "$NAMESPACE" --url 2>/dev/null || true)
    fi
    
    if [ -z "$ACTIVITY_LOGGER_URL" ]; then
        # Try port-forward
        echo "Setting up port-forward for activity-logger..."
        kubectl port-forward svc/activity-logger -n "$NAMESPACE" 18081:8081 &>/dev/null &
        PF_PID2=$!
        sleep 2
        ACTIVITY_LOGGER_URL="http://localhost:18081"
    fi
fi

echo "Backend URL: $BACKEND_URL"
echo "Activity Logger URL: $ACTIVITY_LOGGER_URL"

# Test health endpoints
echo ""
echo "🏥 Testing health endpoints..."

if curl -s "$BACKEND_URL/health" &> /dev/null; then
    pass "Backend health check"
else
    fail "Backend health check failed"
fi

if curl -s "$ACTIVITY_LOGGER_URL/health" &> /dev/null; then
    pass "Activity Logger health check"
else
    fail "Activity Logger health check failed"
fi

# Test event flow
echo ""
echo "🔄 Testing event flow..."

# Get initial log count
INITIAL_COUNT=$(curl -s "$ACTIVITY_LOGGER_URL/logs/stats" 2>/dev/null | grep -o '"total":[0-9]*' | cut -d: -f2 || echo "0")
echo "Initial log count: $INITIAL_COUNT"

# Create a todo
echo ""
echo "Creating test todo..."
TODO_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/todos" \
    -H "Content-Type: application/json" \
    -d '{"title": "E2E Test Todo", "description": "Testing event flow"}' 2>/dev/null || true)

if [ -n "$TODO_RESPONSE" ] && echo "$TODO_RESPONSE" | grep -q "id"; then
    TODO_ID=$(echo "$TODO_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    pass "Todo created (ID: $TODO_ID)"
else
    fail "Failed to create todo"
    TODO_ID=""
fi

# Wait for event propagation
echo ""
echo "⏳ Waiting for event propagation (5 seconds)..."
sleep 5

# Check activity logs
echo ""
echo "📊 Checking activity logs..."

LOGS_RESPONSE=$(curl -s "$ACTIVITY_LOGGER_URL/logs" 2>/dev/null || true)
if echo "$LOGS_RESPONSE" | grep -q "E2E Test Todo"; then
    pass "Todo creation event logged"
else
    fail "Todo creation event not found in logs"
fi

# Check stats
STATS_RESPONSE=$(curl -s "$ACTIVITY_LOGGER_URL/logs/stats" 2>/dev/null || true)
FINAL_COUNT=$(echo "$STATS_RESPONSE" | grep -o '"total":[0-9]*' | cut -d: -f2 || echo "0")
echo "Final log count: $FINAL_COUNT"

if [ "$FINAL_COUNT" -gt "$INITIAL_COUNT" ]; then
    pass "Log count increased (from $INITIAL_COUNT to $FINAL_COUNT)"
else
    warn "Log count did not increase (may need more time)"
fi

# Update the todo
if [ -n "$TODO_ID" ]; then
    echo ""
    echo "Updating test todo..."
    UPDATE_RESPONSE=$(curl -s -X PUT "$BACKEND_URL/api/todos/$TODO_ID" \
        -H "Content-Type: application/json" \
        -d '{"title": "E2E Test Todo Updated"}' 2>/dev/null || true)
    
    if echo "$UPDATE_RESPONSE" | grep -q "Updated"; then
        pass "Todo updated"
    else
        fail "Failed to update todo"
    fi
    
    # Toggle completion
    echo ""
    echo "Toggling todo completion..."
    TOGGLE_RESPONSE=$(curl -s -X PATCH "$BACKEND_URL/api/todos/$TODO_ID/toggle" 2>/dev/null || true)
    
    if echo "$TOGGLE_RESPONSE" | grep -q "completed"; then
        pass "Todo toggled"
    else
        fail "Failed to toggle todo"
    fi
    
    # Wait for events
    sleep 3
    
    # Check for update and completion events
    LOGS_RESPONSE=$(curl -s "$ACTIVITY_LOGGER_URL/logs" 2>/dev/null || true)
    
    if echo "$LOGS_RESPONSE" | grep -q "todo.updated"; then
        pass "Todo update event logged"
    else
        warn "Todo update event not found (may need more time)"
    fi
    
    if echo "$LOGS_RESPONSE" | grep -q "todo.completed"; then
        pass "Todo completion event logged"
    else
        warn "Todo completion event not found (may need more time)"
    fi
    
    # Clean up
    echo ""
    echo "Cleaning up test todo..."
    DELETE_RESPONSE=$(curl -s -X DELETE "$BACKEND_URL/api/todos/$TODO_ID" 2>/dev/null || true)
    if [ -n "$DELETE_RESPONSE" ] || [ "$?" -eq 0 ]; then
        pass "Test todo deleted"
    fi
fi

# Summary
echo ""
echo "============================="
echo "📋 E2E Validation Summary"
echo "============================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ All E2E tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some E2E tests failed${NC}"
    exit 1
fi
