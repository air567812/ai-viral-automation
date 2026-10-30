from pydantic import BaseModel
from typing import Optional, List
import datetime

class ViralTrendBase(BaseModel):
    topic: str
    niche: str
    source_platform: str = "mixed"
    hook_3s: str
    storytelling_technique: Optional[str] = None
    estimated_duration_sec: int = 45
    editing_style: str = "fast-paced, dynamic subtitles"
    audio_trend: str = "trending suspense ambient"
    engagement_indicators: str = "high-share-rate"
    reasons_successful: Optional[str] = None

class ViralTrendCreate(ViralTrendBase):
    pass

class ViralTrendResponse(ViralTrendBase):
    id: int
    growth_rate: float
    engagement_score: float
    relevance_score: float
    competition_score: float
    reusability_score: float
    virality_score: float
    status: str
    discovered_at: datetime.datetime

    class Config:
        from_attributes = True
