"""Main FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import uvicorn

from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.api.v1 import router as api_v1_router
from backend.services.monitoring import monitoring_service
from backend.services.sanctions import sanctions_service

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Blockchain Compliance Monitor")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize services
    await monitoring_service.start()
    await sanctions_service.initialize()
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down services...")
    await monitoring_service.stop()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Institutional Blockchain Compliance Monitoring System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )

# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Blockchain Compliance Monitor",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.API_WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
