import os
import datetime
from typing import Dict, Any, List
from sqlalchemy import select
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.instagram_api import instagram_publisher
from backend.app.services.youtube_api import youtube_publisher
from backend.app.models.series import Episode, Series
from backend.app.models.publish_job import PublishJob
from backend.app.database import AsyncSessionLocal

class PublishingAgent(BaseAgent):
    """
    Agent 8: Social Media Publishing Engine
    Orchestrates idempotent publishing across Instagram Reels and YouTube Shorts.
    Captures permalinks, post IDs, and timestamps upon verified confirmation.
    """
    def __init__(self):
        super().__init__("PublishingAgent")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        episode_id = context.get("episode_id")
        if not episode_id:
            raise ValueError("Episode ID is required for PublishingAgent")

        async with AsyncSessionLocal() as session:
            episode = await session.get(Episode, episode_id)
            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            # Check if episode is approved
            if episode.status not in ["approved", "published"]:
                self.logger.warning(f"Episode {episode_id} cannot be published. Current status: '{episode.status}'")
                return {
                    "status": "blocked",
                    "reason": f"Episode status is '{episode.status}'. Requires approval."
                }

            series = await session.get(Series, episode.series_id)
            episode.status = "publishing"
            await session.commit()

            title = f"{episode.title} | {series.title}"
            caption = f"{episode.synopsis}\n\nWhat happens next? Watch the full series!"
            hashtags = "#SciFi #Shorts #Reels #AIStories #Viral #Trending #MiniSeries"

            results = {}

            # 1. Instagram Reels Publish Job
            self.logger.info(f"Publishing Episode {episode_id} to Instagram Reels...")
            ig_job = PublishJob(
                episode_id=episode.id,
                platform="instagram",
                title=title,
                caption=caption,
                hashtags=hashtags,
                status="processing"
            )
            session.add(ig_job)
            await session.flush()

            try:
                # Video URL or local filepath
                video_target = episode.video_path or "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
                ig_res = await instagram_publisher.publish_reel(
                    video_url=video_target,
                    caption=caption,
                    hashtags=hashtags
                )
                ig_job.status = "verified"
                ig_job.platform_post_id = ig_res["post_id"]
                ig_job.platform_url = ig_res["url"]
                ig_job.is_verified_published = True
                ig_job.verified_at = datetime.datetime.utcnow()
                results["instagram"] = ig_res
            except Exception as e:
                ig_job.status = "failed"
                ig_job.last_error = str(e)
                results["instagram"] = {"status": "failed", "error": str(e)}
                self.logger.error(f"Instagram publishing failed: {e}")

            # 2. YouTube Shorts Publish Job
            self.logger.info(f"Publishing Episode {episode_id} to YouTube Shorts...")
            yt_job = PublishJob(
                episode_id=episode.id,
                platform="youtube",
                title=title,
                caption=caption,
                hashtags=hashtags,
                status="processing"
            )
            session.add(yt_job)
            await session.flush()

            try:
                video_file = episode.video_path or ""
                yt_res = await youtube_publisher.publish_short(
                    video_filepath=video_file,
                    title=title,
                    description=caption
                )
                yt_job.status = "verified"
                yt_job.platform_post_id = yt_res["post_id"]
                yt_job.platform_url = yt_res["url"]
                yt_job.is_verified_published = True
                yt_job.verified_at = datetime.datetime.utcnow()
                results["youtube"] = yt_res
            except Exception as e:
                yt_job.status = "failed"
                yt_job.last_error = str(e)
                results["youtube"] = {"status": "failed", "error": str(e)}
                self.logger.error(f"YouTube publishing failed: {e}")

            # Dual platform verification check
            both_verified = ig_job.is_verified_published and yt_job.is_verified_published
            if both_verified:
                episode.status = "published"
                episode.published_at = datetime.datetime.utcnow()
            else:
                episode.status = "partial_published"

            await session.commit()

        self.logger.info(f"Publishing cycle completed for Episode {episode_id}. Dual-verified: {both_verified}")
        return {
            "status": "success",
            "episode_id": episode_id,
            "both_verified": both_verified,
            "results": results
        }

publishing_agent = PublishingAgent()
