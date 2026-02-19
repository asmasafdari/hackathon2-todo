# Quick Start Guide

Get the Todo Platform running locally in under 5 minutes.

## Prerequisites

- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm`
- **OpenAI API Key** (for AI agent functionality)
- **Neon PostgreSQL** (optional - SQLite works for local dev)

## Quick Start (All Services)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd desktop-todo
```

### 2. Configure Environment

**Backend** (`backend/.env`):
```bash
cd backend
cp .env.example .env
# Edit .env and set DATABASE_URL or leave empty for SQLite
cd ..
```

**Agent** (`agent/.env`):
```bash
cd agent
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
cd ..
```

**Frontend** (`frontend/.env`):
```bash
cd frontend
cp .env.local .env
# Edit .env if backend is not on localhost:8000
cd ..
```

### 3. Start Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

API docs at: `http://localhost:8000/docs`

### 4. Start Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 5. Start AI Agent (New Terminal)

```bash
cd agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run interactive agent
python -m cli

# Or run a single command
python -m cli "add buy groceries"
```

## Usage

### Web Interface

1. Open `http://localhost:3000` in your browser
2. Create todos using the form
3. Toggle completion by clicking checkboxes
4. Edit todos by clicking the edit button
5. Delete todos by clicking the delete button

### AI Agent CLI

**Interactive Mode:**
```
You: add buy milk
Agent: Created "buy milk"!

You: show my tasks
Agent: Your tasks:
1. [ ] Buy milk

You: mark buy milk as done
Agent: Done! "Buy milk" marked as complete.
```

**Single Command Mode:**
```bash
python -m cli "add buy groceries"
python -m cli "show my tasks"
python -m cli "complete buy groceries"
```

## Development Workflow

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Type checking (optional)
pip install mypy
mypy .
```

### Frontend Development

```bash
cd frontend

# Run linter
npm run lint

# Build for production
npm run build

# Start production server
npm run start
```

### Agent Development

```bash
cd agent

# Run tests
pytest

# Test MCP tools directly
python mcp_server.py
```

## Docker Deployment (Local)

Build and run with Docker:

```bash
# Build images
docker build -t todo-backend backend/
docker build -t todo-frontend frontend/
docker build -t todo-mcp agent/

# Run with docker-compose (if available)
docker compose -f scripts/docker-compose.yml --profile with-agent up -d

# Or run individually:
docker run -p 8000:8000 --env-file backend/.env todo-backend
docker run -p 3000:3000 todo-frontend
docker run --env-file agent/.env todo-mcp
```

## Kubernetes Deployment (Minikube)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Minikube deployment instructions.

Quick commands:
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Build images in Minikube's Docker
eval $(minikube docker-env)
docker build -t todo-backend:latest backend/
docker build -t todo-frontend:latest frontend/
docker build -t todo-mcp:latest agent/

# Deploy with Helm
helm install todo-platform charts/todo-platform \
  -f charts/todo-platform/values.yaml \
  -f charts/todo-platform/values-secrets.yaml \
  --namespace todo --create-namespace

# Access the app
minikube service frontend -n todo
```

## Troubleshooting

### Port Already in Use

**Backend port 8000:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uvicorn main:app --reload --port 8001
```

**Frontend port 3000:**
```bash
# Use different port
npm run dev -- --port 3001
```

### Database Connection Issues

**SQLite (Default):**
- No configuration needed
- Database file created automatically: `todos.db`

**PostgreSQL:**
```bash
# Verify DATABASE_URL format
postgresql://user:password@host:5432/dbname?sslmode=require

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Agent Not Responding

**Check OpenAI API Key:**
```bash
cd agent
python -c "from config import get_settings; print('Key set:', bool(get_settings().openai_api_key))"
```

**Check Backend Connectivity:**
```bash
curl http://localhost:8000/health
```

### CORS Errors in Browser

Ensure backend CORS allows frontend origin:
```python
# backend/main.py
allow_origins=["http://localhost:3000"]
```

## Next Steps

- [Read the API documentation](http://localhost:8000/docs)
- [Deploy to Kubernetes](DEPLOYMENT.md)
- [View project specifications](../specs/)
- [Configure event-driven architecture](../specs/004-event-driven-kafka/)

## Getting Help

- **API Issues**: Check backend logs and `/health` endpoint
- **Frontend Issues**: Check browser console and network tab
- **Agent Issues**: Verify OpenAI API key and backend connectivity
- **Deployment Issues**: See [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
