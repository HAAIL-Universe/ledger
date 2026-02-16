"""
FastAPI application entry point with health endpoint and CORS configuration.

This module creates and configures the FastAPI application instance, sets up
CORS middleware based on application settings, and registers the health check
endpoint. All routers are mounted here as they are implemented.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Configure logging based on settings
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler for startup and shutdown events.

    Startup: Log configuration summary and verify critical settings.
    Shutdown: Clean up resources (database connections, etc.) as needed.
    """
    logger.info(
        "Ledger API starting up (environment=%s, log_level=%s)",
        settings.environment,
        settings.log_level,
    )
    yield
    logger.info("Ledger API shutting down")


def create_app() -> FastAPI:
    """
    Application factory that creates and configures the FastAPI instance.

    Returns:
        FastAPI: Fully configured application ready to serve requests.
    """
    app = FastAPI(
        title="Ledger",
        description="Receipt and expense tracking system with OCR and NLP extraction",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    # -------------------------------------------------------------------------
    # CORS Middleware
    # -------------------------------------------------------------------------
    # Allow the configured frontend origin, plus localhost variants for dev.
    allowed_origins = [settings.frontend_url]
    if settings.is_dev:
        allowed_origins.extend(
            [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        )
    # Deduplicate while preserving order
    seen = set()
    unique_origins = []
    for origin in allowed_origins:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=unique_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Health Endpoint
    # -------------------------------------------------------------------------
    @app.get(
        "/health",
        tags=["system"],
        summary="Health check",
        response_model=dict,
    )
    async def health() -> dict:
        """
        Health check endpoint.

        Returns a simple status object indicating the API is operational.
        Used by deployment platforms (Render) for liveness probes and
        by monitoring systems for uptime checks.
        """
        return {"status": "ok"}

    # -------------------------------------------------------------------------
    # Router Registration
    # -------------------------------------------------------------------------
    # Routers will be registered here as they are implemented:
    # from app.api.routers import auth, receipts, expenses
    # app.include_router(auth.router, prefix="/auth", tags=["auth"])
    # app.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
    # app.include_router(expenses.router, prefix="/expenses", tags=["expenses"])

    return app


app: FastAPI = create_app()
