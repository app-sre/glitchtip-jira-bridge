import logging
import socket

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
)
from prometheus_fastapi_instrumentator import Instrumentator

from .api import router
from .config import settings
from .dependencies import api_key_auth

HOSTNAME = socket.gethostname()
default_router = APIRouter()


@default_router.get("/healthz", include_in_schema=False)
async def healthz() -> str:
    """Kubernetes readiness check."""
    return HOSTNAME


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    dependencies = [] if settings.debug else [Depends(api_key_auth)]
    fast_api_app = FastAPI(
        title="Glitchtip Jira Bridge",
        description="Process Glitchtip events and create Jira issues.",
        version="0.1.0",
        debug=settings.debug,
        root_path=settings.root_path,
        openapi_url="/docs/openapi.json",
    )
    # no auth for healthz check
    fast_api_app.include_router(default_router)
    fast_api_app.include_router(router, prefix="/api", dependencies=dependencies)

    instrumentator = Instrumentator(excluded_handlers=["/metrics"]).instrument(
        fast_api_app
    )

    @fast_api_app.on_event("startup")
    async def _startup() -> None:
        instrumentator.expose(fast_api_app, include_in_schema=False)

    return fast_api_app


log = logging.getLogger(__name__)
log.info("Starting Glitchtip Jira Bridge")
app = create_app()
