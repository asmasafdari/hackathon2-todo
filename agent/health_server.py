"""Simple HTTP health server for Kubernetes probes.

The MCP server uses stdio transport (not HTTP), so this provides
a lightweight HTTP endpoint for Kubernetes liveness/readiness probes.
"""

import asyncio
from aiohttp import web

from config import get_settings

settings = get_settings()


async def health_handler(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({
        "status": "healthy",
        "service": "mcp-server",
        "version": "0.1.0"
    })


async def ready_handler(request: web.Request) -> web.Response:
    """Readiness check - verifies backend is reachable."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{settings.todo_api_base_url}/health")
            if response.status_code == 200:
                return web.json_response({
                    "status": "ready",
                    "service": "mcp-server",
                    "backend": "reachable"
                })
    except Exception:
        pass

    return web.json_response(
        {"status": "not_ready", "service": "mcp-server", "backend": "unreachable"},
        status=503
    )


def create_app() -> web.Application:
    """Create the health check web application."""
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/ready", ready_handler)
    return app


def run_health_server(port: int = 8080):
    """Run the health server."""
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_health_server()
