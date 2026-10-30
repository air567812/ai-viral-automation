import datetime
from typing import Dict, Any, List
from sqlalchemy import select
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.gemini_llm import gemini_service
from backend.app.models.trend import ViralTrend
from backend.app.database import AsyncSessionLocal

class TrendResearchAgent(BaseAgent):
    """
    Agent 1: Viral Trend Research Engine
    Periodically identifies viral hooks, pacing styles, audio trends, and storytelling structures
    across Instagram Reels, YouTube Shorts, and Google Trends without copying content.
    Calculates composite Virality Score.
    """
    def __init__(self):
        super().__init__("TrendResearchAgent")

    def _calculate_virality_score(
        self,
        growth: float,
        engagement: float,
        relevance: float,
        competition: float,
        reusability: float
    ) -> float:
        # Algorithmic scoring formula:
        # High growth (25%) + High engagement (25%) + Relevance (20%) + Low competition (15%) + Reusability (15%)
        comp_inverted = max(0.0, 100.0 - competition)
        score = (
            (growth * 0.25) +
            (engagement * 0.25) +
            (relevance * 0.20) +
            (comp_inverted * 0.15) +
            (reusability * 0.15)
        )
        return round(score, 1)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Executing autonomous trend research cycle...")
        target_niche = context.get("niche", "sci-fi and mystery")
        
        prompt = f"""
        Analyze current viral short-form video patterns for 9:16 Instagram Reels and YouTube Shorts in the '{target_niche}' niche.
        Identify 2 high-engagement trend patterns.
        For each, specify:
        - topic: Title/Subject of the pattern
        - niche: Category
        - source_platform: instagram or youtube
        - hook_3s: Exact 3-second opening visual or spoken hook
        - storytelling_technique: e.g. Inverted reveal, cold open question, suspense escalation
        - estimated_duration_sec: between 30 and 60
        - editing_style: pacing, transitions, visual tone
        - audio_trend: sound design / music vibe
        - engagement_indicators: why it triggers shares/saves
        - reasons_successful: psychological driver
        - growth_rate: 0 to 100
        - engagement_score: 0 to 100
        - relevance_score: 0 to 100
        - competition_score: 0 to 100
        - reusability_score: 0 to 100 (how well it translates to an episodic multi-part series)
        """
        
        result = await gemini_service.generate_json(prompt, "You are a senior social media data scientist and viral content algorithm analyst.")
        raw_trends = result.get("trends", [])
        
        saved_trends = []
        async with AsyncSessionLocal() as session:
            for item in raw_trends:
                # Check for duplication
                stmt = select(ViralTrend).where(ViralTrend.topic == item["topic"])
                existing = (await session.execute(stmt)).scalars().first()
                if not existing:
                    v_score = self._calculate_virality_score(
                        float(item.get("growth_rate", 75)),
                        float(item.get("engagement_score", 80)),
                        float(item.get("relevance_score", 85)),
                        float(item.get("competition_score", 40)),
                        float(item.get("reusability_score", 90))
                    )
                    trend_obj = ViralTrend(
                        topic=item["topic"],
                        niche=item.get("niche", target_niche),
                        source_platform=item.get("source_platform", "mixed"),
                        hook_3s=item["hook_3s"],
                        storytelling_technique=item.get("storytelling_technique"),
                        estimated_duration_sec=int(item.get("estimated_duration_sec", 45)),
                        editing_style=item.get("editing_style", "fast-paced"),
                        audio_trend=item.get("audio_trend", "ambient suspense"),
                        engagement_indicators=item.get("engagement_indicators", "high-shares"),
                        reasons_successful=item.get("reasons_successful", "curiosity gap"),
                        growth_rate=float(item.get("growth_rate", 75)),
                        engagement_score=float(item.get("engagement_score", 80)),
                        relevance_score=float(item.get("relevance_score", 85)),
                        competition_score=float(item.get("competition_score", 40)),
                        reusability_score=float(item.get("reusability_score", 90)),
                        virality_score=v_score,
                        status="discovered"
                    )
                    session.add(trend_obj)
                    saved_trends.append(item["topic"])
            
            await session.commit()
            
        self.logger.info(f"Trend research complete. Discovered and indexed {len(saved_trends)} new viral patterns.")
        return {
            "status": "success",
            "discovered_count": len(saved_trends),
            "trends": saved_trends
        }

trend_research_agent = TrendResearchAgent()
