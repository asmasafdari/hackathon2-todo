import asyncio
import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import init_db
from routers.todos import router as todos_router
from routers.chat import router as chat_router
from routers.auth import router as auth_router
from routers.internal import router as internal_router
from routers.websocket import router as ws_router
from routers.dapr_subscriptions import router as dapr_router

# Honour LOG_LEVEL injected by Kubernetes ConfigMap (or default to INFO)
_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, _log_level, logging.INFO))

logger = logging.getLogger(__name__)


async def wait_for_dapr(max_retries: int = 30, delay: float = 1.0) -> bool:
    """
    Wait for Dapr sidecar to be ready before processing requests.

    This function should be called during application startup to ensure
    the Dapr sidecar is available for pub/sub operations.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries

    Returns:
        True if Dapr is ready, False if timed out
    """
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    health_url = f"http://localhost:{dapr_port}/v1.0/healthz"

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(health_url, timeout=2.0)
                if resp.status_code == 204:
                    logger.info(f"Dapr sidecar ready after {attempt + 1} attempts")
                    return True
        except Exception as e:
            logger.debug(f"Dapr not ready (attempt {attempt + 1}/{max_retries}): {e}")

        await asyncio.sleep(delay)

    logger.warning(f"Dapr sidecar not ready after {max_retries} attempts")
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and wait for Dapr on startup."""
    # Initialize database
    await init_db()

    # Wait for Dapr sidecar if running in Kubernetes
    if os.getenv("DAPR_HTTP_PORT"):
        dapr_ready = await wait_for_dapr()
        if not dapr_ready:
            logger.warning("Proceeding without Dapr - event publishing may fail")

    yield


app = FastAPI(
    title="Todo API",
    description="RESTful API for Phase II Fullstack Todo Application",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS — configurable via ALLOWED_ORIGINS env var (comma-separated)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(chat_router)
app.include_router(internal_router)
app.include_router(ws_router)
app.include_router(dapr_router)


@app.get("/")
async def root():
    return {"message": "Todo API is running"}


@app.get("/health")
async def health():
    """Liveness probe for Kubernetes."""
    return {"status": "healthy", "service": "backend", "version": "1.0.0"}


@app.get("/ready")
async def ready():
    """Readiness probe for Kubernetes — checks DB connectivity."""
    try:
        from database import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "service": "backend"}
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)},
        )
