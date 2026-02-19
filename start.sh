#!/bin/bash
# Start Todo Platform - Backend and Frontend
# This script starts both services and verifies they're running

echo "🚀 Starting Todo Platform"
echo "========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    netstat -ano | grep ":$port" | grep -q "LISTENING"
    return $?
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(netstat -ano | grep ":$port" | grep "LISTENING" | awk '{print $5}' | head -1)
    if [ -n "$pid" ]; then
        echo "   Stopping process on port $port (PID: $pid)..."
        taskkill //F //PID $pid 2>/dev/null || true
        sleep 2
    fi
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
kill_port 8000
kill_port 3000
echo -e "${GREEN}✓ Ports cleared${NC}"
echo ""

# Start Backend
echo "🔧 Starting Backend (FastAPI)..."
cd backend

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "   Installing backend dependencies..."
    pip install -r requirements.txt -q
fi

# Start backend in background
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "   Backend starting with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "   Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "   ${GREEN}✓ Backend is ready${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "   ${RED}❌ Backend failed to start${NC}"
        echo "   Check backend/backend.log for errors"
        exit 1
    fi
done

echo ""

# Start Frontend
echo "🎨 Starting Frontend (Next.js)..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "   Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "   Frontend starting with PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo "   Waiting for frontend to be ready..."
for i in {1..30}; do
    # Check if port 3000 is listening
    if netstat -ano | grep ":3000" | grep -q "LISTENING"; then
        # Wait a bit more for Next.js to fully start
        sleep 2
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "   ${GREEN}✓ Frontend is ready${NC}"
            break
        fi
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "   ${YELLOW}⚠️ Frontend may not be fully ready yet${NC}"
        echo "   Check frontend/frontend.log for details"
    fi
done

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Todo Platform is running!${NC}"
echo "=========================================="
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Test API:"
echo "   curl http://localhost:8000/api/todos"
echo ""
echo "🛑 To stop:"
echo "   Run: ./stop.sh"
echo "   Or press Ctrl+C in the terminal windows"
echo ""

# Keep script running
echo "Press Ctrl+C to stop watching..."
echo ""

# Show logs
tail -f backend/backend.log frontend/frontend.log 2>/dev/null || wait
