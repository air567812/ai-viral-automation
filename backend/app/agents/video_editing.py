import os
from typing import Dict, Any, List
from sqlalchemy import select
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.tts_service import tts_service
from backend.app.services.video_composer import video_composer
from backend.app.services.storage_service import storage_service
from backend.app.models.series import Episode, Series, CharacterBible
from backend.app.models.scene import Scene
from backend.app.database import AsyncSessionLocal

class VideoEditingAgent(BaseAgent):
    """
    Agent 6: Video Editing Engine
    Synthesizes AI voiceover with character voice mappings, generates synchronized subtitles,
    and composites the scene clips into a finalized vertical 9:16 (1080x1920) master video.
    """
    def __init__(self):
        super().__init__("VideoEditingAgent")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        episode_id = context.get("episode_id")
        if not episode_id:
            raise ValueError("Episode ID is required for VideoEditingAgent")

        async with AsyncSessionLocal() as session:
            episode = await session.get(Episode, episode_id)
            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            series = await session.get(Series, episode.series_id)
            stmt_c = select(CharacterBible).where(CharacterBible.series_id == series.id)
            characters = (await session.execute(stmt_c)).scalars().all()
            primary_char = characters[0] if characters else None
            voice_name = primary_char.voice_name if primary_char else "en-US-ChristopherNeural"

            stmt = select(Scene).where(Scene.episode_id == episode.id).order_by(Scene.scene_number)
            scenes = (await session.execute(stmt)).scalars().all()
            clip_paths = [s.clip_path for s in scenes if s.clip_path and os.path.exists(s.clip_path)]

            if not clip_paths:
                raise ValueError(f"No valid video clips found for Episode {episode.id}")

            episode.status = "editing"
            await session.commit()

            # 1. Synthesize Voiceover & Synchronized Subtitles
            audio_path = storage_service.get_episode_audio_path(episode.id)
            srt_path = os.path.join(storage_service.subtitles_dir, f"episode_{episode.id}.srt")
            
            script_text = episode.full_script or episode.hook_3s or "The anomaly unfolds in silence."
            self.logger.info(f"Synthesizing voiceover with voice '{voice_name}'...")
            
            await tts_service.synthesize_speech(
                text=script_text,
                output_audio_path=audio_path,
                output_subtitles_path=srt_path,
                voice=voice_name
            )
            
            # 2. Composite Final Master Video
            master_render_path = storage_service.get_episode_render_path(episode.id)
            self.logger.info(f"Compositing {len(clip_paths)} clips into master video: {master_render_path}...")
            
            render_result = await video_composer.composite_episode(
                scene_clip_paths=clip_paths,
                audio_voice_path=audio_path,
                subtitles_srt_path=srt_path,
                output_master_path=master_render_path
            )

            episode.video_path = master_render_path
            episode.audio_path = audio_path
            episode.subtitles_path = srt_path
            episode.actual_duration_sec = int(sum([s.duration_seconds for s in scenes]))
            episode.status = "edited"
            
            await session.commit()

        self.logger.info(f"Video editing and compositing complete for Episode {episode_id}.")
        return {
            "status": "success",
            "episode_id": episode_id,
            "master_video_path": master_render_path,
            "duration": episode.actual_duration_sec
        }

video_editing_agent = VideoEditingAgent()
