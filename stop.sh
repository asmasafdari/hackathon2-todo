#!/bin/bash
# Stop Todo Platform

echo "🛑 Stopping Todo Platform"
echo "========================="
echo ""

# Function to kill process on port
kill_port() {
    local port=$1
    local name=$2
    local pid=$(netstat -ano | grep ":$port" | grep "LISTENING" | awk '{print $5}' | head -1)
    if [ -n "$pid" ]; then
        echo "   Stopping $name on port $port (PID: $pid)..."
        taskkill //F //PID $pid 2>/dev/null && echo "   ✓ Stopped" || echo "   ✗ Failed to stop"
    else
        echo "   $name not running on port $port"
    fi
}

# Kill processes
kill_port 8000 "Backend"
kill_port 3000 "Frontend"

echo ""
echo "✅ All services stopped"
echo ""
