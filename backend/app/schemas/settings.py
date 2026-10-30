from pydantic import BaseModel
from typing import Optional

class SystemSettingsSchema(BaseModel):
    require_manual_approval: bool
    default_video_duration_seconds: int
    target_aspect_ratio: str
    target_resolution_width: int
    target_resolution_height: int
    trend_research_interval_hours: int
    auto_cleanup_after_upload: bool
    veo_simulation_mode: bool
    tts_provider: str
