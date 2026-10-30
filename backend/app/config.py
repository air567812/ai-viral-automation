import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Autonomous AI Reels & Shorts Automation Engine"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    SECRET_KEY: str = "change-in-production-secret-key"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/automation.db"

    # Storage & Zero-Waste Lifecycle Policy
    STORAGE_PROVIDER: str = "local"  # "local", "gcs", "s3"
    GCS_BUCKET_NAME: str = "viral-reels-prod-bucket"
    LOCAL_STORAGE_DIR: str = "./data/media"
    AUTO_CLEANUP_AFTER_UPLOAD: bool = True
    FINAL_VIDEO_RETENTION_DAYS: int = 0

    # AI Models
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Video Gen: Google Flow / Veo
    VEO_SIMULATION_MODE: bool = True
    GOOGLE_GENAI_API_KEY: Optional[str] = None
    VEO_MODEL: str = "veo-2.0-generate-001"
    VEO_PROJECT_ID: Optional[str] = None
    VEO_LOCATION: str = "us-central1"
    GOOGLE_FLOW_ENDPOINT: Optional[str] = None
    GOOGLE_FLOW_API_KEY: Optional[str] = None

    # TTS Engine
    TTS_PROVIDER: str = "edge-tts"
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: Optional[str] = None

    # Instagram Graph API
    INSTAGRAM_ACCOUNT_ID: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None

    # YouTube Data API
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_REFRESH_TOKEN: Optional[str] = None
    YOUTUBE_CHANNEL_ID: Optional[str] = None

    # Quality & Automation Controls
    REQUIRE_MANUAL_APPROVAL: bool = True
    DEFAULT_VIDEO_DURATION_SECONDS: int = 45
    TARGET_ASPECT_RATIO: str = "9:16"
    TARGET_RESOLUTION_WIDTH: int = 1080
    TARGET_RESOLUTION_HEIGHT: int = 1920

    # Scheduled intervals
    TREND_RESEARCH_INTERVAL_HOURS: int = 6
    CONTENT_PLANNING_CRON: str = "0 8 * * *"
    PUBLISHING_CRON: str = "0 18 * * *"
    ANALYTICS_CRON: str = "0 23 * * *"
    WEEKLY_REPORT_CRON: str = "0 10 * * 0"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
