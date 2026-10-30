from typing import Dict, Any, List
from sqlalchemy import select
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.gemini_llm import gemini_service
from backend.app.models.series import Episode, Series, CharacterBible
from backend.app.models.scene import Scene
from backend.app.database import AsyncSessionLocal

class StoryboardAgent(BaseAgent):
    """
    Agent 4: Storyboard Engine
    Translates the episodic script into individual scenes with precise Google Veo 2 / Flow prompts:
    - Camera angle & motion
    - 9:16 vertical composition
    - Character visual continuity
    - Environmental lighting
    - Sound design cues
    """
    def __init__(self):
        super().__init__("StoryboardAgent")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        episode_id = context.get("episode_id")
        if not episode_id:
            raise ValueError("Episode ID is required for StoryboardAgent")

        async with AsyncSessionLocal() as session:
            episode = await session.get(Episode, episode_id)
            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            series = await session.get(Series, episode.series_id)
            stmt_c = select(CharacterBible).where(CharacterBible.series_id == series.id)
            characters = (await session.execute(stmt_c)).scalars().all()
            char_continuity = "\n".join([f"{c.name}: {c.visual_description}" for c in characters])

            self.logger.info(f"Generating scene storyboard for Episode #{episode.episode_number}...")
            
            prompt = f"""
            Break down the following script for Episode {episode.episode_number} into 3 to 4 sequential visual scenes for video generation.
            Script:
            {episode.full_script}
            
            Character Continuity Guide:
            {char_continuity}
            
            For each scene, provide:
            - scene_number: 1, 2, 3...
            - scene_description: What happens visually
            - camera_angle: e.g. Macro extreme close-up, Dutch angle low shot, slow push-in
            - character_name: Name of character in scene (if any)
            - character_actions: Exact physical action
            - dialogue: Spoken words during this scene
            - environment: Detailed setting description
            - lighting: Exact lighting mood (e.g. moody volumetric cyan rim light, amber shadows)
            - visual_style: Hyper-realistic 8k cinematic vertical video, 9:16 aspect ratio
            - sound_effects: Atmospheric SFX
            - duration_seconds: 5.0 to 7.0 seconds
            - veo_prompt: The exact comprehensive generation prompt optimized for Google Veo 2 (explicitly stating vertical 9:16 composition and character details).
            """

            storyboard_data = await gemini_service.generate_json(
                prompt,
                "You are an expert AI video director and prompt engineer specializing in Google Veo 2 cinematic video synthesis."
            )
            raw_scenes = storyboard_data.get("scenes", [])
            
            # Delete any existing scenes for this episode to prevent stale duplicates
            stmt_old = select(Scene).where(Scene.episode_id == episode.id)
            old_scenes = (await session.execute(stmt_old)).scalars().all()
            for old in old_scenes:
                await session.delete(old)
            await session.flush()

            created_scene_ids = []
            for item in raw_scenes:
                scene = Scene(
                    episode_id=episode.id,
                    scene_number=int(item.get("scene_number", len(created_scene_ids) + 1)),
                    scene_description=item.get("scene_description", "Cinematic scene"),
                    camera_angle=item.get("camera_angle", "Cinematic eye-level"),
                    character_name=item.get("character_name"),
                    character_actions=item.get("character_actions"),
                    dialogue=item.get("dialogue"),
                    environment=item.get("environment"),
                    lighting=item.get("lighting", "Moody cinematic lighting"),
                    visual_style=item.get("visual_style", "8k hyper-realistic vertical 9:16"),
                    sound_effects=item.get("sound_effects"),
                    duration_seconds=float(item.get("duration_seconds", 6.0)),
                    veo_prompt=item.get("veo_prompt", "Vertical 9:16 cinematic video"),
                    status="pending"
                )
                session.add(scene)
                await session.flush()
                created_scene_ids.append(scene.id)

            await session.commit()

        self.logger.info(f"Storyboard generated {len(created_scene_ids)} scenes for Episode #{episode.episode_number}.")
        return {
            "status": "success",
            "episode_id": episode.id,
            "scene_count": len(created_scene_ids),
            "scene_ids": created_scene_ids
        }

storyboard_agent = StoryboardAgent()
