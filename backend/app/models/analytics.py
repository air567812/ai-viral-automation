import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base

class AnalyticsRecord(Base):
    __tablename__ = "analytics_records"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    platform = Column(String(50), nullable=False) # "instagram", "youtube"
    
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    
    avg_watch_time_sec = Column(Float, default=0.0)
    retention_rate_pct = Column(Float, default=0.0)
    completion_rate_pct = Column(Float, default=0.0)
    engagement_rate_pct = Column(Float, default=0.0)
    
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

    episode = relationship("Episode", back_populates="analytics")

class StrategyFeedback(Base):
    __tablename__ = "strategy_feedback"

    id = Column(Integer, primary_key=True, index=True)
    niche = Column(String(100), nullable=False, index=True)
    winning_hook_formats = Column(Text, nullable=True) # e.g. "Question + Visual Incongruity"
    optimal_duration_sec = Column(Integer, default=42)
    top_performing_styles = Column(Text, nullable=True)
    summary_learnings = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
