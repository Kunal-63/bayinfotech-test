"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import settings
from app.utils.logger import setup_logging, get_logger
from app.api import chat, tickets, metrics

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Help Desk API",
    description="Backend API for BayInfotech AI Help Desk Platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(tickets.router, prefix="/api", tags=["tickets"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("application_startup", environment=settings.environment)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("application_shutdown")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "healthy",
        "service": "AI Help Desk API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
