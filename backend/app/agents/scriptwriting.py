from typing import Dict, Any
from sqlalchemy import select
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.gemini_llm import gemini_service
from backend.app.models.series import Episode, Series, CharacterBible
from backend.app.database import AsyncSessionLocal

class ScriptwritingAgent(BaseAgent):
    """
    Agent 3: Scriptwriting Engine
    Authors high-retention 30-60s vertical episodic scripts structured specifically for Reels & Shorts:
    - 0-3s: Irresistible hook
    - 3-15s: High-stakes mystery introduction
    - 15-35s: Rapid narrative acceleration
    - 35-45s: Mind-bending cliffhanger
    """
    def __init__(self):
        super().__init__("ScriptwritingAgent")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        episode_id = context.get("episode_id")
        if not episode_id:
            raise ValueError("Episode ID is required for ScriptwritingAgent")

        async with AsyncSessionLocal() as session:
            episode = await session.get(Episode, episode_id)
            if not episode:
                raise ValueError(f"Episode {episode_id} not found")
            
            series = await session.get(Series, episode.series_id)
            stmt_c = select(CharacterBible).where(CharacterBible.series_id == series.id)
            characters = (await session.execute(stmt_c)).scalars().all()
            char_desc = "\n".join([f"- {c.name} ({c.role}): {c.visual_description}" for c in characters])

            self.logger.info(f"Generating script for Episode #{episode.episode_number} of '{series.title}'...")
            
            prompt = f"""
            Write a viral 30-45 second script for Episode {episode.episode_number} of the series '{series.title}'.
            Theme: {series.theme}
            Characters:
            {char_desc}
            
            Formatting requirements:
            - hook_3s: Opening 1-3 seconds hook designed to prevent scrolling.
            - synopsis: 1-2 sentence overview.
            - full_script: The complete spoken voiceover text (approx 75-100 words, paced for 35-45 seconds).
            - cliffhanger: Shocking final revelation leaving viewers desperate for next episode.
            - caption: Compelling social media caption with engagement question.
            - hashtags: 5-8 trending viral hashtags.
            """
            
            script_data = await gemini_service.generate_json(
                prompt,
                "You are an award-winning micro-cinema screenwriter specializing in viral high-retention vertical video series."
            )
            
            episode.title = script_data.get("title", episode.title)
            episode.synopsis = script_data.get("synopsis", episode.synopsis)
            episode.hook_3s = script_data.get("hook_3s", episode.hook_3s)
            episode.full_script = script_data.get("full_script", episode.full_script)
            episode.cliffhanger = script_data.get("cliffhanger", episode.cliffhanger)
            episode.status = "scripted"
            
            await session.commit()
            await session.refresh(episode)

        self.logger.info(f"Scriptwriting complete for Episode #{episode.episode_number}.")
        return {
            "status": "success",
            "episode_id": episode.id,
            "title": episode.title,
            "script_length": len(episode.full_script) if episode.full_script else 0
        }

scriptwriting_agent = ScriptwritingAgent()
