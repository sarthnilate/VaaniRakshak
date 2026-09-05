import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.database import init_db
from backend.db.redis import session_manager
from backend.api.router import api_router
from backend.websocket.call_stream import router as ws_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("vaanirakshak.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown event handler."""
    logger.info("Initializing VAANIRAKSHAK AI Threat Engine...")
    # Initialize SQLite / PostgreSQL tables
    await init_db()
    # Initialize Redis session manager with in-memory fallback
    await session_manager.initialize()
    logger.info("VAANIRAKSHAK AI Threat Engine initialized successfully.")
    yield
    logger.info("Shutting down VAANIRAKSHAK AI Threat Engine...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-Time AI-Powered Voice Cloning Impersonation Detection & Prevention Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API & WebSocket Routers
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to VAANIRAKSHAK AI Threat Engine API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
