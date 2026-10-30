import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.orchestration.scheduler import automation_scheduler
from backend.app.api.routes_trends import router as trends_router
from backend.app.api.routes_series import router as series_router
from backend.app.api.routes_episodes import router as episodes_router
from backend.app.api.routes_pipeline import router as pipeline_router
from backend.app.api.routes_analytics import router as analytics_router
from backend.app.api.routes_settings import router as settings_router

# Configure root logger
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AutonomousReelsApp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    await init_db()
    logger.info("Starting automation background scheduler...")
    automation_scheduler.start()
    yield
    logger.info("Shutting down automation background scheduler...")
    automation_scheduler.shutdown()

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous AI Viral Reels & YouTube Shorts Content Factory",
    version="1.0.0",
    lifespan=lifespan
)

# Ensure local storage media directory exists
os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)
renders_dir = os.path.join(settings.LOCAL_STORAGE_DIR, "renders")
os.makedirs(renders_dir, exist_ok=True)

# Mount local media directory for in-dashboard video preview
app.mount("/media", StaticFiles(directory=settings.LOCAL_STORAGE_DIR), name="media")

# Setup templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Include API Routers
app.include_router(trends_router)
app.include_router(series_router)
app.include_router(episodes_router)
app.include_router(pipeline_router)
app.include_router(analytics_router)
app.include_router(settings_router)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the primary Autonomous AI Reels & Shorts Studio dashboard."""
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "scheduler_active": automation_scheduler.is_running
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
