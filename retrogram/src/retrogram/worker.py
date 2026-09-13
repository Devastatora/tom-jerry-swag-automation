from __future__ import annotations

import logging
import signal

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import load_settings
from .db import QueueDB
from .service import run_once, seed_queue


def parse_time(value: str) -> tuple[int, int]:
    hour, minute = value.split(":", 1)
    hour_i, minute_i = int(hour), int(minute)
    if not (0 <= hour_i <= 23 and 0 <= minute_i <= 59):
        raise ValueError(f"Invalid time: {value}")
    return hour_i, minute_i


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = load_settings()
    db = QueueDB(settings.database_path)
    added = seed_queue(db, settings.queue_dir)
    logging.info("Queue ready: %s new, totals=%s", added, db.counts())

    scheduler = BlockingScheduler(timezone=settings.timezone)
    for index, value in enumerate(settings.post_times, start=1):
        hour, minute = parse_time(value)
        scheduler.add_job(
            run_once,
            CronTrigger(hour=hour, minute=minute, timezone=settings.timezone),
            args=[settings],
            id=f"daily-post-{index}",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=3600,
        )
    logging.info("Posting at %s in %s (dry_run=%s)", settings.post_times, settings.timezone, settings.dry_run)
    signal.signal(signal.SIGTERM, lambda *_: scheduler.shutdown(wait=False))
    scheduler.start()


if __name__ == "__main__":
    main()

