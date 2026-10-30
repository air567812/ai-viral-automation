from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List
from backend.app.database import get_db
from backend.app.models.series import Series
from backend.app.schemas.episode import SeriesResponse

router = APIRouter(prefix="/api/series", tags=["Series"])

@router.get("", response_model=List[SeriesResponse])
async def list_series(db: AsyncSession = Depends(get_db)):
    stmt = select(Series).options(selectinload(Series.episodes)).order_by(desc(Series.created_at))
    result = await db.execute(stmt)
    return result.scalars().all()
