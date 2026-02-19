# Quickstart: Todo AI Chatbot

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (for AI agent)
- Clerk account with API keys (for authentication)

## 1. Environment Setup

Copy the example environment files:

```bash
cp backend/.env.example backend/.env
cp chatbot-frontend/.env.example chatbot-frontend/.env
cp agent/.env.example agent/.env
```

Fill in the required values:

**backend/.env**:
```
DATABASE_URL=postgresql://todouser:todopass@db:5432/tododb
CLERK_SECRET_KEY=sk_test_your-key
```

**agent/.env**:
```
OPENAI_API_KEY=sk-your-openai-key
TODO_API_BASE_URL=http://backend:8000
```

**chatbot-frontend/.env**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your-key
CLERK_SECRET_KEY=sk_test_your-key
```

## 2. Start with Docker Compose

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on port 5432 (internal)
- **Backend (FastAPI)** on port 8000
- **Chatbot Frontend (Next.js)** on port 3001

## 3. Access the Application

- **Chatbot UI**: http://localhost:3001
- **Backend API docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## 4. Try It Out

1. Sign in via Clerk on the chatbot UI
2. Type: "Add a task to buy groceries"
3. Type: "Show my tasks"
4. Type: "Mark task 1 as complete"

## 5. Development (without Docker)

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd chatbot-frontend
npm install
npm run dev

# Environment: Set DATABASE_URL and OPENAI_API_KEY
```

## 6. Running Tests

```bash
# Backend tests
cd backend && pytest

# Agent tests
cd agent && pytest
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend can't connect to DB | Check DATABASE_URL in .env; ensure postgres container is healthy |
| AI agent errors | Verify OPENAI_API_KEY is set and valid |
| Auth failures | Check Clerk keys in both backend and frontend .env |
| Frontend can't reach backend | Verify NEXT_PUBLIC_API_URL matches backend port |
