from fastapi import APIRouter
from backend.app.orchestration.pipeline import pipeline_orchestrator
from backend.app.orchestration.scheduler import automation_scheduler

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])

@router.post("/run")
async def trigger_full_pipeline(niche: str = "sci-fi and mystery", auto_publish: bool = False):
    """Triggers an immediate end-to-end autonomous content generation run."""
    result = await pipeline_orchestrator.run_full_cycle(niche=niche, auto_publish=auto_publish)
    return result

@router.get("/status")
async def get_pipeline_status():
    return {
        "scheduler_running": automation_scheduler.is_running,
        "jobs": [
            {"id": j.id, "name": j.name, "next_run_time": str(j.next_run_time)}
            for j in automation_scheduler.scheduler.get_jobs()
        ] if automation_scheduler.is_running else []
    }

@router.post("/pause")
async def pause_scheduler():
    automation_scheduler.pause()
    return {"status": "paused"}

@router.post("/resume")
async def resume_scheduler():
    automation_scheduler.resume()
    return {"status": "resumed"}
