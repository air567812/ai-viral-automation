from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    
    scene_description = Column(Text, nullable=False)
    camera_angle = Column(String(100), default="Eye-level medium shot, cinematic depth of field")
    character_name = Column(String(100), nullable=True)
    character_actions = Column(Text, nullable=True)
    dialogue = Column(Text, nullable=True)
    environment = Column(Text, nullable=True)
    lighting = Column(String(255), default="Moody, dramatic rim lighting")
    visual_style = Column(String(255), default="Hyper-realistic 8k cinematic vertical video")
    sound_effects = Column(String(255), nullable=True)
    duration_seconds = Column(Float, default=5.0)
    
    # Veo / Flow prompt specification
    veo_prompt = Column(Text, nullable=False)
    veo_negative_prompt = Column(Text, default="blurry, distorted faces, low quality, horizontal, borders, watermark")
    veo_job_id = Column(String(100), nullable=True)
    
    clip_path = Column(String(512), nullable=True)
    status = Column(String(50), default="pending") # pending, generating, ready, failed

    episode = relationship("Episode", back_populates="scenes")
