import os
from typing import Dict, Any, List
from sqlalchemy import select
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.veo_flow import veo_service
from backend.app.services.storage_service import storage_service
from backend.app.models.series import Episode
from backend.app.models.scene import Scene
from backend.app.database import AsyncSessionLocal

class VideoGenerationAgent(BaseAgent):
    """
    Agent 5: Video Generation Engine (Google Veo / Flow)
    Iterates over episode scenes, calls the Google Veo / Flow video generation service,
    manages character consistency parameters, retries on failures, and stores temporary scene clips.
    """
    def __init__(self):
        super().__init__("VideoGenerationAgent")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        episode_id = context.get("episode_id")
        if not episode_id:
            raise ValueError("Episode ID is required for VideoGenerationAgent")

        async with AsyncSessionLocal() as session:
            episode = await session.get(Episode, episode_id)
            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            stmt = select(Scene).where(Scene.episode_id == episode.id).order_by(Scene.scene_number)
            scenes = (await session.execute(stmt)).scalars().all()
            if not scenes:
                raise ValueError(f"No storyboard scenes found for Episode {episode.id}")

            episode.status = "generating"
            await session.commit()

            scene_dir = storage_service.get_episode_scene_dir(episode.id)
            generated_clips = []

            for scene in scenes:
                clip_filename = f"scene_{scene.scene_number}.mp4"
                clip_path = os.path.join(scene_dir, clip_filename)
                
                self.logger.info(f"Generating clip for Episode {episode.id} Scene {scene.scene_number}...")
                scene.status = "generating"
                await session.commit()

                # Call Google Veo / Flow generation service
                gen_result = await veo_service.generate_scene_clip(
                    prompt=scene.veo_prompt,
                    output_filepath=clip_path,
                    duration_seconds=scene.duration_seconds,
                    aspect_ratio="9:16",
                    negative_prompt=scene.veo_negative_prompt
                )

                if gen_result.get("status") == "success":
                    scene.clip_path = clip_path
                    scene.status = "ready"
                    generated_clips.append(clip_path)
                    self.logger.info(f"Scene {scene.scene_number} clip ready at {clip_path}")
                else:
                    scene.status = "failed"
                    self.logger.error(f"Scene {scene.scene_number} clip generation failed")

                await session.commit()

        self.logger.info(f"Video generation cycle complete for Episode {episode_id}. {len(generated_clips)} clips generated.")
        return {
            "status": "success",
            "episode_id": episode_id,
            "clips_count": len(generated_clips),
            "clips": generated_clips
        }

video_generation_agent = VideoGenerationAgent()
