# Quickstart: Phase II - Fullstack Todo Application

**Feature**: 001-fullstack-todo
**Date**: 2026-01-21

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or pnpm
- Neon account with database created

---

## Environment Setup

### 1. Get Neon Database Connection String

1. Log into [Neon Console](https://console.neon.tech)
2. Create a new project (or use existing)
3. Copy the connection string from the dashboard
4. Format: `postgresql://user:password@host/database?sslmode=require`

### 2. Create Environment Files

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://user:password@your-neon-host.neon.tech/neondb?sslmode=require
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlmodel asyncpg python-dotenv

# Run database migrations (creates tables)
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"

# Start development server
uvicorn main:app --reload --port 8000
```

**Verify**: Open http://localhost:8000/docs to see Swagger UI

---

## Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev
# or
pnpm dev
```

**Verify**: Open http://localhost:3000 to see the app

---

## Project Structure

```
desktop-todo/
├── backend/
│   ├── main.py              # FastAPI application entry
│   ├── database.py          # Database connection & session
│   ├── models.py            # SQLModel definitions
│   ├── routers/
│   │   └── todos.py         # Todo API endpoints
│   ├── services/
│   │   └── todo_service.py  # Business logic
│   ├── .env                 # Environment variables
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page (todo list)
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── TodoList.tsx     # Todo list component
│   │   ├── TodoItem.tsx     # Single todo item
│   │   └── TodoForm.tsx     # Create/edit form
│   ├── lib/
│   │   └── api.ts           # API client functions
│   ├── types/
│   │   └── todo.ts          # TypeScript interfaces
│   ├── .env.local           # Environment variables
│   └── package.json         # Node dependencies
│
└── specs/
    └── 001-fullstack-todo/  # This feature's docs
```

---

## Quick Verification

### Test Backend API

```bash
# List todos (should return empty array)
curl http://localhost:8000/api/todos

# Create a todo
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test todo", "description": "Testing the API"}'

# List todos again (should return the created todo)
curl http://localhost:8000/api/todos
```

### Test Frontend

1. Open http://localhost:3000
2. You should see the todo list (empty initially)
3. Create a new todo using the form
4. Verify it appears in the list
5. Toggle completion by clicking the checkbox
6. Refresh the page - todo should persist

---

## Common Issues

### CORS Errors
Ensure backend has CORS configured for `http://localhost:3000`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Database Connection Failed
- Verify `DATABASE_URL` is correct in `.env`
- Check Neon dashboard for connection limits
- Ensure `?sslmode=require` is in the connection string

### Frontend Can't Reach Backend
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Look for network errors in browser console

---

## Development Commands

| Task | Backend | Frontend |
|------|---------|----------|
| Start dev server | `uvicorn main:app --reload` | `npm run dev` |
| Run tests | `pytest` | `npm test` |
| Format code | `black .` | `npm run lint` |
| Type check | `mypy .` | `npm run type-check` |

---

## Next Steps

After setup is verified:

1. Run `/sp.tasks` to generate implementation tasks
2. Follow task order for systematic implementation
3. Test each feature as you build it
