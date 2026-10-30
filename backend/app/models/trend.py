import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum
from backend.app.database import Base

class ViralTrend(Base):
    __tablename__ = "viral_trends"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    niche = Column(String(100), nullable=False, index=True)
    source_platform = Column(String(50), default="mixed") # instagram, youtube, google_trends
    hook_3s = Column(Text, nullable=False)
    storytelling_technique = Column(String(255), nullable=True)
    estimated_duration_sec = Column(Integer, default=45)
    editing_style = Column(String(255), default="fast-paced, dynamic subtitles, zoom-ins")
    audio_trend = Column(String(255), default="trending suspense ambient")
    engagement_indicators = Column(String(255), default="high-share-to-like-ratio")
    reasons_successful = Column(Text, nullable=True)
    
    # Calculated Scores (0.0 to 100.0)
    growth_rate = Column(Float, default=75.0)
    engagement_score = Column(Float, default=80.0)
    relevance_score = Column(Float, default=85.0)
    competition_score = Column(Float, default=50.0)
    reusability_score = Column(Float, default=90.0)
    virality_score = Column(Float, default=82.0)
    
    status = Column(String(50), default="discovered") # discovered, selected, converted, archived
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
