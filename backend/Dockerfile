# Backend Dockerfile
# Build context: project root (set in docker-compose.yml)
# This allows copying both backend/ and agent/ directories

# ---- Stage 1: Install dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies for asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from both backend and agent
COPY backend/requirements.txt /build/backend-requirements.txt
COPY agent/requirements.txt /build/agent-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --prefix=/install \
    -r /build/backend-requirements.txt \
    -r /build/agent-requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy backend and agent code
COPY backend/ /app/backend/
COPY agent/ /app/agent/

# Set working directory to backend
WORKDIR /app/backend

# Create data directory for SQLite fallback
RUN mkdir -p /app/backend/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
