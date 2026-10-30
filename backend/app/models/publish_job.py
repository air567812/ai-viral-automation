import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base

class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    platform = Column(String(50), nullable=False) # "instagram", "youtube"
    
    title = Column(String(255), nullable=False)
    caption = Column(Text, nullable=False)
    hashtags = Column(Text, nullable=True)
    
    # State tracking
    status = Column(String(50), default="queued") # queued, processing, uploaded, verified, failed
    platform_post_id = Column(String(255), nullable=True)
    platform_url = Column(String(512), nullable=True)
    
    attempt_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    is_verified_published = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    episode = relationship("Episode", back_populates="publish_jobs")
