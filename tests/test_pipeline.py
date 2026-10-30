import os
import pytest
import asyncio
from backend.app.database import init_db, AsyncSessionLocal
from backend.app.orchestration.pipeline import pipeline_orchestrator
from backend.app.agents import (
    trend_research_agent,
    content_strategy_agent,
    scriptwriting_agent,
    storyboard_agent,
    video_generation_agent,
    video_editing_agent,
    quality_control_agent,
    publishing_agent,
    storage_management_agent,
    analytics_agent
)

@pytest.mark.asyncio
async def test_full_pipeline_end_to_end():
    """Validates the entire autonomous media factory cycle end-to-end."""
    # 1. Initialize DB
    await init_db()

    # 2. Run full autonomous cycle with auto_publish=True
    result = await pipeline_orchestrator.run_full_cycle(
        niche="sci-fi and mystery",
        auto_publish=True
    )

    assert result["status"] == "success"
    assert "episode_id" in result
    episode_id = result["episode_id"]

    # Verify agent logs
    log = result["pipeline_log"]
    assert log["1_trend_research"]["status"] == "success"
    assert log["2_content_strategy"]["status"] == "success"
    assert log["3_scriptwriting"]["status"] == "success"
    assert log["4_storyboard"]["status"] == "success"
    assert log["5_video_generation"]["status"] == "success"
    assert log["6_video_editing"]["status"] == "success"
    assert log["7_quality_control"]["status"] == "qc_passed"
    assert log["8_publishing"]["status"] == "success"
    assert log["8_publishing"]["both_verified"] is True
    assert log["9_storage_management"]["status"] == "success"
    assert log["10_analytics"]["status"] == "success"

@pytest.mark.asyncio
async def test_zero_waste_storage_guard():
    """Guarantees that video files are never prematurely deleted if publishing is not verified."""
    from backend.app.services.storage_service import storage_service
    
    # Negative test: unverified publishing must NOT delete master render
    purged = storage_service.purge_after_verified_publishing(
        episode_id=99999,
        ig_verified=False,
        yt_verified=True
    )
    assert purged is False, "Storage manager must NOT purge if any platform is unverified!"
