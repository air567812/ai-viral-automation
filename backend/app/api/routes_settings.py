from fastapi import APIRouter
from backend.app.config import settings
from backend.app.schemas.settings import SystemSettingsSchema

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=SystemSettingsSchema)
async def get_settings():
    return SystemSettingsSchema(
        require_manual_approval=settings.REQUIRE_MANUAL_APPROVAL,
        default_video_duration_seconds=settings.DEFAULT_VIDEO_DURATION_SECONDS,
        target_aspect_ratio=settings.TARGET_ASPECT_RATIO,
        target_resolution_width=settings.TARGET_RESOLUTION_WIDTH,
        target_resolution_height=settings.TARGET_RESOLUTION_HEIGHT,
        trend_research_interval_hours=settings.TREND_RESEARCH_INTERVAL_HOURS,
        auto_cleanup_after_upload=settings.AUTO_CLEANUP_AFTER_UPLOAD,
        veo_simulation_mode=settings.VEO_SIMULATION_MODE,
        tts_provider=settings.TTS_PROVIDER
    )

@router.post("")
async def update_settings(new_settings: SystemSettingsSchema):
    settings.REQUIRE_MANUAL_APPROVAL = new_settings.require_manual_approval
    settings.DEFAULT_VIDEO_DURATION_SECONDS = new_settings.default_video_duration_seconds
    settings.AUTO_CLEANUP_AFTER_UPLOAD = new_settings.auto_cleanup_after_upload
    settings.VEO_SIMULATION_MODE = new_settings.veo_simulation_mode
    settings.TTS_PROVIDER = new_settings.tts_provider
    return {"status": "success", "message": "Settings updated successfully"}
