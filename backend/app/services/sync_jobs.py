"""
Background Scrape & Sync jobs.

The HTTP request only *creates* a SyncRun row and returns immediately (202 Accepted).
The slow part (scraping + embedding) runs afterwards via FastAPI BackgroundTasks, and the
admin UI polls GET /admin/sync-runs/{id} to follow it.

BackgroundTasks run inside the API process, which is fine at our scale. If syncs get longer or
we run several API servers, move execute_sync_run to a real worker queue (Phase 3: Arq/Celery).
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from sqlalchemy.orm import Session

from app.models.sync_run import (
    ACTIVE_STATUSES,
    SYNC_FAILED,
    SYNC_QUEUED,
    SYNC_RUNNING,
    SYNC_SUCCEEDED,
    SyncRun,
)
from app.services.ingestion import run_scrape_and_sync

logger = logging.getLogger(__name__)

# A run still "active" after this long almost certainly died with a server restart
STALE_AFTER = timedelta(minutes=30)


class SyncAlreadyRunningError(Exception):
    def __init__(self, run: SyncRun):
        super().__init__(f"Sync run {run.id} is already {run.status}")
        self.run = run


def _as_utc(value: datetime) -> datetime:
    # SQLite (used in tests) drops tzinfo; Postgres keeps it
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def create_sync_run(db: Session, site: str, force_live: bool, user_id: Optional[int]) -> SyncRun:
    """
    Queue a new run, unless one is already active for this site.

    Two syncs at once would race on the same rows and pay for the same embeddings twice.
    """
    active = (
        db.query(SyncRun)
        .filter(SyncRun.site == site, SyncRun.status.in_(ACTIVE_STATUSES))
        .order_by(SyncRun.created_at.desc())
        .first()
    )
    if active:
        if datetime.now(timezone.utc) - _as_utc(active.created_at) > STALE_AFTER:
            active.status = SYNC_FAILED
            active.error = "Interrupted (server restarted or crashed before the run finished)."
            active.finished_at = datetime.now(timezone.utc)
        else:
            raise SyncAlreadyRunningError(active)

    run = SyncRun(site=site, force_live=force_live, status=SYNC_QUEUED, triggered_by_user_id=user_id)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def execute_sync_run(run_id: int, session_factory: Callable[[], Session]) -> None:
    """
    Do the actual scrape & sync for a queued run.

    Opens its own DB session: the request's session is already closed by the time this runs.
    Never raises, because there is nobody left to receive the error; the outcome is stored on the row.
    """
    with session_factory() as db:
        run = db.get(SyncRun, run_id)
        if run is None:
            logger.error("Sync run %s disappeared before it started", run_id)
            return

        run.status = SYNC_RUNNING
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        try:
            result = run_scrape_and_sync(db=db, site_key=run.site, force_live=run.force_live)
        except Exception:
            logger.exception("Sync run %s failed", run_id)
            db.rollback()  # discard half-written chunks from this run
            run = db.get(SyncRun, run_id)
            run.status = SYNC_FAILED
            run.error = "Scrape & sync failed. Check the server logs for details."
        else:
            run.status = SYNC_SUCCEEDED
            run.result = result
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
