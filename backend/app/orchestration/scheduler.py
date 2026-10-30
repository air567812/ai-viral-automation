import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from backend.app.config import settings
from backend.app.orchestration.pipeline import pipeline_orchestrator
from backend.app.agents import trend_research_agent, analytics_agent

logger = logging.getLogger("SchedulerService")

class AutomationScheduler:
    """
    In-App Automated Recurring Job Executor using APScheduler.
    Manages periodic trend discovery, daily pipeline runs, and analytics collection.
    """
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        if self.is_running:
            return

        logger.info("Initializing automation background scheduler jobs...")

        # 1. Trend Research job (every 6 hours)
        self.scheduler.add_job(
            self._job_trend_research,
            trigger=IntervalTrigger(hours=settings.TREND_RESEARCH_INTERVAL_HOURS),
            id="job_trend_research",
            name="Trend Research Cycle",
            replace_existing=True
        )

        # 2. Daily Pipeline Creation Job (8:00 AM)
        self.scheduler.add_job(
            self._job_daily_pipeline,
            trigger=CronTrigger.from_crontab(settings.CONTENT_PLANNING_CRON),
            id="job_daily_pipeline",
            name="Daily Content Factory Cycle",
            replace_existing=True
        )

        # 3. Nightly Analytics & Self-Learning (11:00 PM)
        self.scheduler.add_job(
            self._job_analytics_learning,
            trigger=CronTrigger.from_crontab(settings.ANALYTICS_CRON),
            id="job_analytics_learning",
            name="Nightly Analytics & Learning",
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Automation scheduler started successfully.")

    def pause(self):
        if self.is_running:
            self.scheduler.pause()
            logger.info("Automation scheduler paused.")

    def resume(self):
        if self.is_running:
            self.scheduler.resume()
            logger.info("Automation scheduler resumed.")

    def shutdown(self):
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Automation scheduler shut down.")

    async def _job_trend_research(self):
        logger.info("Executing scheduled trend research job...")
        await trend_research_agent.execute({"niche": "all"})

    async def _job_daily_pipeline(self):
        logger.info("Executing scheduled daily content generation cycle...")
        await pipeline_orchestrator.run_full_cycle()

    async def _job_analytics_learning(self):
        logger.info("Executing scheduled analytics collection & self-learning...")
        await analytics_agent.execute({})

automation_scheduler = AutomationScheduler()
