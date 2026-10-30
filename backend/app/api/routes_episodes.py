from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List
from backend.app.database import get_db
from backend.app.models.series import Episode
from backend.app.schemas.episode import EpisodeResponse
from backend.app.orchestration.pipeline import pipeline_orchestrator

router = APIRouter(prefix="/api/episodes", tags=["Episodes"])

@router.get("", response_model=List[EpisodeResponse])
async def list_episodes(db: AsyncSession = Depends(get_db)):
    stmt = select(Episode).options(selectinload(Episode.scenes)).order_by(desc(Episode.id))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(episode_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Episode).options(selectinload(Episode.scenes)).where(Episode.id == episode_id)
    episode = (await db.execute(stmt)).scalars().first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode

@router.post("/{episode_id}/approve")
async def approve_episode(episode_id: int):
    """Approve a gated episode and trigger publishing across Instagram & YouTube."""
    result = await pipeline_orchestrator.approve_and_publish_episode(episode_id)
    return result

@router.post("/{episode_id}/reject")
async def reject_episode(episode_id: int, reason: str = "Rejected by human reviewer", db: AsyncSession = Depends(get_db)):
    episode = await db.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    episode.status = "rejected"
    episode.rejection_reason = reason
    await db.commit()
    return {"status": "success", "message": f"Episode {episode_id} rejected."}
