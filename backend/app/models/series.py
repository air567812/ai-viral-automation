import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, unique=True, index=True)
    niche = Column(String(100), nullable=False, index=True) # sci-fi, horror, suspense, facts, comedy
    theme = Column(Text, nullable=False)
    target_audience = Column(String(255), default="Gen Z & Millennials (18-35)")
    total_episodes_planned = Column(Integer, default=10)
    current_episode_count = Column(Integer, default=0)
    continuity_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    characters = relationship("CharacterBible", back_populates="series", cascade="all, delete-orphan")
    episodes = relationship("Episode", back_populates="series", cascade="all, delete-orphan")

class CharacterBible(Base):
    __tablename__ = "character_bible"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(100), default="protagonist")
    visual_description = Column(Text, nullable=False) # Detailed description for consistent Veo generation
    voice_name = Column(String(100), default="en-US-ChristopherNeural") # Edge-TTS voice identifier
    voice_pitch = Column(String(20), default="+0Hz")
    voice_rate = Column(String(20), default="+0%")
    personality_traits = Column(Text, nullable=True)

    series = relationship("Series", back_populates="characters")

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    synopsis = Column(Text, nullable=False)
    hook_3s = Column(Text, nullable=False)
    cliffhanger = Column(Text, nullable=True)
    full_script = Column(Text, nullable=True)
    
    # Specs & status
    target_duration_sec = Column(Integer, default=45)
    actual_duration_sec = Column(Integer, nullable=True)
    aspect_ratio = Column(String(20), default="9:16")
    resolution = Column(String(20), default="1080x1920")
    
    # Paths & storage tracking
    video_path = Column(String(512), nullable=True)
    audio_path = Column(String(512), nullable=True)
    subtitles_path = Column(String(512), nullable=True)
    thumbnail_path = Column(String(512), nullable=True)
    
    # Workflow status: draft, scripted, generating, editing, qc_passed, pending_approval, approved, publishing, published, failed, rejected
    status = Column(String(50), default="draft", index=True)
    requires_approval = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    
    scheduled_publish_time = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    series = relationship("Series", back_populates="episodes")
    scenes = relationship("Scene", back_populates="episode", cascade="all, delete-orphan", order_by="Scene.scene_number")
    publish_jobs = relationship("PublishJob", back_populates="episode", cascade="all, delete-orphan")
    analytics = relationship("AnalyticsRecord", back_populates="episode", cascade="all, delete-orphan")
