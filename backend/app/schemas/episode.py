from pydantic import BaseModel
from typing import Optional, List
import datetime

class SceneSchema(BaseModel):
    id: Optional[int] = None
    scene_number: int
    scene_description: str
    camera_angle: str
    character_name: Optional[str] = None
    character_actions: Optional[str] = None
    dialogue: Optional[str] = None
    environment: Optional[str] = None
    lighting: str
    visual_style: str
    sound_effects: Optional[str] = None
    duration_seconds: float
    veo_prompt: str
    clip_path: Optional[str] = None
    status: str = "pending"

    class Config:
        from_attributes = True

class EpisodeResponse(BaseModel):
    id: int
    series_id: int
    episode_number: int
    title: str
    synopsis: str
    hook_3s: str
    cliffhanger: Optional[str] = None
    full_script: Optional[str] = None
    target_duration_sec: int
    actual_duration_sec: Optional[int] = None
    aspect_ratio: str
    resolution: str
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    status: str
    requires_approval: bool
    is_approved: bool
    rejection_reason: Optional[str] = None
    scheduled_publish_time: Optional[datetime.datetime] = None
    published_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    scenes: List[SceneSchema] = []

    class Config:
        from_attributes = True

class SeriesResponse(BaseModel):
    id: int
    title: str
    niche: str
    theme: str
    target_audience: str
    total_episodes_planned: int
    current_episode_count: int
    created_at: datetime.datetime
    episodes: List[EpisodeResponse] = []

    class Config:
        from_attributes = True
