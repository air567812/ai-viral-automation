from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from backend.app.database import get_db
from backend.app.models.trend import ViralTrend
from backend.app.schemas.trend import ViralTrendResponse
from backend.app.agents import trend_research_agent

router = APIRouter(prefix="/api/trends", tags=["Trends"])

@router.get("", response_model=List[ViralTrendResponse])
async def list_trends(limit: int = 50, db: AsyncSession = Depends(get_db)):
    stmt = select(ViralTrend).order_by(desc(ViralTrend.virality_score)).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/research")
async def trigger_trend_research(niche: str = "sci-fi and mystery"):
    result = await trend_research_agent.execute({"niche": niche})
    return result
