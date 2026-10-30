from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend.app.database import get_db
from backend.app.models.analytics import AnalyticsRecord, StrategyFeedback
from backend.app.models.series import Episode

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("")
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    # Total aggregates
    views_stmt = select(func.sum(AnalyticsRecord.views))
    total_views = (await db.execute(views_stmt)).scalar() or 0

    likes_stmt = select(func.sum(AnalyticsRecord.likes))
    total_likes = (await db.execute(likes_stmt)).scalar() or 0

    shares_stmt = select(func.sum(AnalyticsRecord.shares))
    total_shares = (await db.execute(shares_stmt)).scalar() or 0

    avg_watch_stmt = select(func.avg(AnalyticsRecord.avg_watch_time_sec))
    avg_watch_time = round((await db.execute(avg_watch_stmt)).scalar() or 0.0, 1)

    avg_completion_stmt = select(func.avg(AnalyticsRecord.completion_rate_pct))
    avg_completion = round((await db.execute(avg_completion_stmt)).scalar() or 0.0, 1)

    # Strategy learnings
    feedbacks_stmt = select(StrategyFeedback).order_by(desc(StrategyFeedback.updated_at)).limit(5)
    feedbacks = (await db.execute(feedbacks_stmt)).scalars().all()

    # Recent records
    recent_stmt = select(AnalyticsRecord).order_by(desc(AnalyticsRecord.recorded_at)).limit(10)
    recent_records = (await db.execute(recent_stmt)).scalars().all()

    return {
        "summary": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_shares": total_shares,
            "avg_watch_time_sec": avg_watch_time,
            "avg_completion_rate_pct": avg_completion
        },
        "strategy_learnings": [
            {
                "niche": f.niche,
                "winning_hooks": f.winning_hook_formats,
                "optimal_duration": f.optimal_duration_sec,
                "learnings": f.summary_learnings
            }
            for f in feedbacks
        ],
        "recent_records": recent_records
    }
