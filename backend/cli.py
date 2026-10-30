import os
import sys
import asyncio
import argparse
import logging
from backend.app.database import init_db
from backend.app.orchestration.pipeline import pipeline_orchestrator
from backend.app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AutonomousReelsCLI")

async def run_cli():
    parser = argparse.ArgumentParser(description="Autonomous AI Viral Reels & YouTube Shorts CLI")
    parser.add_argument("--niche", type=str, default="sci-fi and mystery", help="Target content niche")
    parser.add_argument("--auto-publish", action="store_true", help="Automatically publish without holding for manual approval")
    parser.add_argument("--simulation", action="store_true", help="Force Google Veo simulation mode for testing")
    parser.add_argument("--duration", type=int, default=45, help="Target video duration in seconds")
    
    args = parser.parse_args()

    if args.simulation:
        settings.VEO_SIMULATION_MODE = True
    if args.duration:
        settings.DEFAULT_VIDEO_DURATION_SECONDS = args.duration

    logger.info("Initializing database tables...")
    await init_db()

    logger.info(f"Triggering autonomous pipeline for niche: '{args.niche}' | Auto-Publish: {args.auto_publish}")
    result = await pipeline_orchestrator.run_full_cycle(
        niche=args.niche,
        auto_publish=args.auto_publish
    )

    print("==================================================")
    print(f"PIPELINE STATUS: {result.get('status').upper()}")
    print(f"GENERATED EPISODE ID: {result.get('episode_id')}")
    print("==================================================")

    # Write GitHub Actions Step Summary if running inside GitHub Actions
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path and os.path.exists(os.path.dirname(summary_path)):
        try:
            log = result.get("pipeline_log", {})
            pub = log.get("8_publishing", {})
            ig_url = pub.get("results", {}).get("instagram", {}).get("url", "N/A")
            yt_url = pub.get("results", {}).get("youtube", {}).get("url", "N/A")

            md = f"""
## 🎬 Autonomous AI Reels & Shorts Generation Report

- **Status:** `{result.get('status').upper()}`
- **Episode ID:** `#{result.get('episode_id')}`
- **Niche:** `{args.niche}`
- **Auto-Publish:** `{args.auto_publish}`

### 🚀 Publishing Status
- **Instagram Reel:** {ig_url}
- **YouTube Short:** {yt_url}

### 🤖 Agent Execution Breakdown
1. **Trend Research:** `{log.get('1_trend_research', {}).get('status', 'N/A')}`
2. **Content Strategy:** `{log.get('2_content_strategy', {}).get('status', 'N/A')}`
3. **Scriptwriting:** `{log.get('3_scriptwriting', {}).get('status', 'N/A')}`
4. **Storyboard (9:16 Veo):** `{log.get('4_storyboard', {}).get('status', 'N/A')}`
5. **Video Generation:** `{log.get('5_video_generation', {}).get('status', 'N/A')}`
6. **Video Editing & Voice:** `{log.get('6_video_editing', {}).get('status', 'N/A')}`
7. **Quality Control:** `{log.get('7_quality_control', {}).get('status', 'N/A')}`
8. **Social Publishing:** `{pub.get('status', 'N/A')}`
9. **Zero-Waste Storage Purge:** `{log.get('9_storage_management', {}).get('status', 'N/A')}`
10. **Self-Learning Analytics:** `{log.get('10_analytics', {}).get('status', 'N/A')}`
"""
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(md)
        except Exception as e:
            logger.warning(f"Could not write to GITHUB_STEP_SUMMARY: {e}")

    if result.get("status") != "success":
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_cli())
