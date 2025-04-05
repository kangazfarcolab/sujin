import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api import api_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Fra-Gent API server")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Fra-Gent API server")

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "name": "Fra-Gent",
        "version": "0.1.0",
        "status": "ok",
    }

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)
