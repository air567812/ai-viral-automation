import os
import shutil
import logging
from typing import Optional, List
from backend.app.config import settings

logger = logging.getLogger("StorageService")

class StorageService:
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER
        self.base_dir = os.path.abspath(settings.LOCAL_STORAGE_DIR)
        os.makedirs(self.base_dir, exist_ok=True)
        self.scenes_dir = os.path.join(self.base_dir, "scenes")
        self.renders_dir = os.path.join(self.base_dir, "renders")
        self.audio_dir = os.path.join(self.base_dir, "audio")
        self.subtitles_dir = os.path.join(self.base_dir, "subtitles")
        
        for d in [self.scenes_dir, self.renders_dir, self.audio_dir, self.subtitles_dir]:
            os.makedirs(d, exist_ok=True)

    def get_episode_scene_dir(self, episode_id: int) -> str:
        path = os.path.join(self.scenes_dir, f"episode_{episode_id}")
        os.makedirs(path, exist_ok=True)
        return path

    def get_episode_render_path(self, episode_id: int) -> str:
        return os.path.join(self.renders_dir, f"episode_{episode_id}_master.mp4")

    def get_episode_audio_path(self, episode_id: int) -> str:
        return os.path.join(self.audio_dir, f"episode_{episode_id}_voice.mp3")

    def get_episode_subtitles_path(self, episode_id: int) -> str:
        return os.path.join(self.subtitles_dir, f"episode_{episode_id}_subtitles.ass")

    def cleanup_intermediate_scenes(self, episode_id: int):
        """Purges raw scene clips after rendering master video."""
        scene_dir = os.path.join(self.scenes_dir, f"episode_{episode_id}")
        if os.path.exists(scene_dir):
            try:
                shutil.rmtree(scene_dir)
                logger.info(f"Cleaned up intermediate scene clips for episode {episode_id} at {scene_dir}")
            except Exception as e:
                logger.error(f"Error purging intermediate scenes for episode {episode_id}: {e}")

    def purge_after_verified_publishing(self, episode_id: int, ig_verified: bool, yt_verified: bool) -> bool:
        """
        Zero-waste storage lifecycle rule:
        Never delete a video until all required uploads are verified as successful!
        If one platform fails, retain the final file and retry the failed upload.
        """
        if not (ig_verified and yt_verified):
            logger.warning(
                f"Episode {episode_id} upload verification incomplete (IG: {ig_verified}, YT: {yt_verified}). "
                f"Retaining master render for upload retry."
            )
            return False

        if not settings.AUTO_CLEANUP_AFTER_UPLOAD:
            logger.info(f"Auto-cleanup disabled in config. Retaining render for episode {episode_id}.")
            return False

        render_path = self.get_episode_render_path(episode_id)
        audio_path = self.get_episode_audio_path(episode_id)
        sub_path = self.get_episode_subtitles_path(episode_id)
        self.cleanup_intermediate_scenes(episode_id)

        for p in [render_path, audio_path, sub_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                    logger.info(f"Successfully purged temporary media file: {p}")
                except Exception as e:
                    logger.error(f"Failed to purge {p}: {e}")

        logger.info(f"Zero-waste cleanup complete for episode {episode_id}. All published URLs preserved in DB.")
        return True

storage_service = StorageService()
