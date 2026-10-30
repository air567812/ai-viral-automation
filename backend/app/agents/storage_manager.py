from typing import Dict, Any
from sqlalchemy import select
from backend.app.agents.base_agent import BaseAgent
from backend.app.services.storage_service import storage_service
from backend.app.models.series import Episode
from backend.app.models.publish_job import PublishJob
from backend.app.database import AsyncSessionLocal

class StorageManagementAgent(BaseAgent):
    """
    Agent 10: Zero-Waste Cloud Storage Lifecycle Engine
    Guarantees strict storage optimization:
    1. Checks if all required uploads for an episode are verified.
    2. Purges temporary scene clips and intermediate stems.
    3. Deletes master render files according to retention policy.
    4. Never deletes files if any required upload failed or remains unverified.
    """
    def __init__(self):
        super().__init__("StorageManagementAgent")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        episode_id = context.get("episode_id")
        if not episode_id:
            raise ValueError("Episode ID is required for StorageManagementAgent")

        async with AsyncSessionLocal() as session:
            episode = await session.get(Episode, episode_id)
            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            # Check publish jobs
            stmt = select(PublishJob).where(PublishJob.episode_id == episode.id)
            jobs = (await session.execute(stmt)).scalars().all()
            
            ig_verified = any([j.is_verified_published for j in jobs if j.platform == "instagram"])
            yt_verified = any([j.is_verified_published for j in jobs if j.platform == "youtube"])

            self.logger.info(f"Auditing storage for Episode {episode_id}. IG Verified: {ig_verified}, YT Verified: {yt_verified}")

            # Execute zero-waste purge protocol
            purged = storage_service.purge_after_verified_publishing(
                episode_id=episode.id,
                ig_verified=ig_verified,
                yt_verified=yt_verified
            )

        return {
            "status": "success",
            "episode_id": episode_id,
            "purged": purged,
            "ig_verified": ig_verified,
            "yt_verified": yt_verified
        }

storage_management_agent = StorageManagementAgent()
