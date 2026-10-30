from typing import Dict, Any, Optional
from sqlalchemy import select, desc
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.gemini_llm import gemini_service
from backend.app.models.trend import ViralTrend
from backend.app.models.series import Series, CharacterBible, Episode
from backend.app.database import AsyncSessionLocal

class ContentStrategyAgent(BaseAgent):
    """
    Agent 2: Content Strategy Engine
    Selects high-virality trends, plans episodic storylines, maintains
    the Character Bible for visual and voice continuity, and schedules upcoming episodes.
    """
    def __init__(self):
        super().__init__("ContentStrategyAgent")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Executing content strategy cycle...")
        series_id = context.get("series_id")
        
        async with AsyncSessionLocal() as session:
            # 1. Fetch top discovered trend if no specific topic given
            top_trend = None
            if not series_id:
                stmt = select(ViralTrend).where(ViralTrend.status == "discovered").order_by(desc(ViralTrend.virality_score))
                top_trend = (await session.execute(stmt)).scalars().first()

            # 2. Check if active series exists, or create a new original series
            active_series = None
            if series_id:
                active_series = await session.get(Series, series_id)
            else:
                stmt_s = select(Series).order_by(desc(Series.created_at))
                active_series = (await session.execute(stmt_s)).scalars().first()

            if not active_series:
                # Create a new series based on top trend
                topic = top_trend.topic if top_trend else "The Geneva Anomaly: Stolen Timelines"
                niche = top_trend.niche if top_trend else "sci-fi"
                
                active_series = Series(
                    title=f"Chronicles: {topic[:50]}",
                    niche=niche,
                    theme="Quantum anomalies, lost timelines, and reality distortions in high-tech subterranean research facilities.",
                    target_audience="Sci-Fi & Mystery enthusiasts, Gen Z & Millennials",
                    total_episodes_planned=10,
                    current_episode_count=0,
                    continuity_notes="Dr. Vance possesses the reversed chronometer; time shifts occur on each episode."
                )
                session.add(active_series)
                await session.flush()
                
                # Create default Character Bible for continuity
                hero = CharacterBible(
                    series_id=active_series.id,
                    name="Dr. Aris Vance",
                    role="protagonist",
                    visual_description="Mid-30s theoretical physicist with sharp focused eyes, wearing a dark waterproof tactical laboratory parka and titanium-rimmed glasses.",
                    voice_name="en-US-ChristopherNeural",
                    voice_pitch="+0Hz",
                    voice_rate="+0%",
                    personality_traits="Methodical, observant, calm under existential threat"
                )
                session.add(hero)
                await session.flush()
                self.logger.info(f"Initialized new Series #{active_series.id} '{active_series.title}' with Character Bible.")

            # Plan next episode in series
            next_ep_num = active_series.current_episode_count + 1
            planned_episode = Episode(
                series_id=active_series.id,
                episode_number=next_ep_num,
                title=f"Episode {next_ep_num}: The Anomaly Unfolds",
                synopsis=f"Dr. Vance investigates the escalating temporal distortion triggered by the clock.",
                hook_3s=top_trend.hook_3s if top_trend else "If your watch ticks backwards today, do not look in the mirror.",
                target_duration_sec=45,
                status="draft",
                requires_approval=True
            )
            session.add(planned_episode)
            active_series.current_episode_count = next_ep_num
            
            if top_trend:
                top_trend.status = "selected"
                
            await session.commit()
            await session.refresh(planned_episode)

        self.logger.info(f"Content strategy planned Episode #{planned_episode.episode_number} (ID: {planned_episode.id}) for Series #{active_series.id}.")
        return {
            "status": "success",
            "series_id": active_series.id,
            "episode_id": planned_episode.id,
            "episode_number": planned_episode.episode_number
        }

content_strategy_agent = ContentStrategyAgent()
