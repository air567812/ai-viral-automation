import logging
from typing import Dict, Any, Optional
from backend.app.agents import (
    trend_research_agent,
    content_strategy_agent,
    scriptwriting_agent,
    storyboard_agent,
    video_generation_agent,
    video_editing_agent,
    quality_control_agent,
    publishing_agent,
    analytics_agent,
    storage_management_agent,
)

logger = logging.getLogger("PipelineOrchestrator")

class AutonomousContentPipeline:
    """
    Central Orchestration Pipeline coordinating all 10 autonomous agents
    into a production-grade automated media factory.
    """
    async def run_full_cycle(self, niche: str = "sci-fi and mystery", auto_publish: bool = False) -> Dict[str, Any]:
        """Runs the entire content creation and publishing workflow from trend to publish."""
        logger.info("================ STARTING AUTONOMOUS PIPELINE CYCLE ================")
        pipeline_log = {}

        # 1. Trend Research
        trend_res = await trend_research_agent.execute({"niche": niche})
        pipeline_log["1_trend_research"] = trend_res

        # 2. Content Strategy
        strategy_res = await content_strategy_agent.execute({"niche": niche})
        pipeline_log["2_content_strategy"] = strategy_res
        episode_id = strategy_res.get("episode_id")

        if not episode_id:
            logger.error("Content strategy failed to plan an episode.")
            return {"status": "failed", "step": "content_strategy", "log": pipeline_log}

        # 3. Scriptwriting
        script_res = await scriptwriting_agent.execute({"episode_id": episode_id})
        pipeline_log["3_scriptwriting"] = script_res

        # 4. Storyboard & Prompt Engineering
        storyboard_res = await storyboard_agent.execute({"episode_id": episode_id})
        pipeline_log["4_storyboard"] = storyboard_res

        # 5. Video Generation (Google Veo / Flow)
        video_gen_res = await video_generation_agent.execute({"episode_id": episode_id})
        pipeline_log["5_video_generation"] = video_gen_res

        # 6. Video Editing, Audio, Subtitles
        editing_res = await video_editing_agent.execute({"episode_id": episode_id})
        pipeline_log["6_video_editing"] = editing_res

        # 7. Quality Control & Human-in-the-Loop Gating
        qc_res = await quality_control_agent.execute({"episode_id": episode_id})
        pipeline_log["7_quality_control"] = qc_res

        # 8. Publishing (If approved or auto_publish is forced)
        if qc_res.get("episode_status") == "approved" or auto_publish:
            if auto_publish:
                from backend.app.database import AsyncSessionLocal
                from backend.app.models.series import Episode
                async with AsyncSessionLocal() as session:
                    ep = await session.get(Episode, episode_id)
                    if ep:
                        ep.status = "approved"
                        ep.is_approved = True
                        await session.commit()

            publish_res = await publishing_agent.execute({"episode_id": episode_id})
            pipeline_log["8_publishing"] = publish_res

            # 9. Storage Lifecycle (Zero-waste cleanup)
            storage_res = await storage_management_agent.execute({"episode_id": episode_id})
            pipeline_log["9_storage_management"] = storage_res

            # 10. Analytics & Self-Learning
            analytics_res = await analytics_agent.execute({"episode_id": episode_id})
            pipeline_log["10_analytics"] = analytics_res
        else:
            logger.info(f"Pipeline paused at Human Approval Gate for Episode {episode_id}.")
            pipeline_log["8_publishing"] = {"status": "gated_pending_approval"}

        logger.info("================ PIPELINE CYCLE EXECUTION COMPLETED ================")
        return {
            "status": "success",
            "episode_id": episode_id,
            "pipeline_log": pipeline_log
        }

    async def approve_and_publish_episode(self, episode_id: int) -> Dict[str, Any]:
        """Manually approve a gated episode and trigger publishing, storage cleanup, and analytics."""
        logger.info(f"Manual approval received for Episode {episode_id}. Initiating publishing sequence...")
        
        from backend.app.database import AsyncSessionLocal
        from backend.app.models.series import Episode

        async with AsyncSessionLocal() as session:
            ep = await session.get(Episode, episode_id)
            if not ep:
                raise ValueError(f"Episode {episode_id} not found")
            ep.status = "approved"
            ep.is_approved = True
            await session.commit()

        publish_res = await publishing_agent.execute({"episode_id": episode_id})
        storage_res = await storage_management_agent.execute({"episode_id": episode_id})
        analytics_res = await analytics_agent.execute({"episode_id": episode_id})

        return {
            "status": "success",
            "episode_id": episode_id,
            "publishing": publish_res,
            "storage": storage_res,
            "analytics": analytics_res
        }

pipeline_orchestrator = AutonomousContentPipeline()
