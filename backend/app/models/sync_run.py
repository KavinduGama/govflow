from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base

# Lifecycle: queued -> running -> succeeded | failed
SYNC_QUEUED = "queued"
SYNC_RUNNING = "running"
SYNC_SUCCEEDED = "succeeded"
SYNC_FAILED = "failed"
ACTIVE_STATUSES = (SYNC_QUEUED, SYNC_RUNNING)


class SyncRun(Base):
    """One Scrape & Sync job. The admin UI polls this row to follow progress."""

    __tablename__ = "sync_runs"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String(50), nullable=False)
    force_live = Column(Boolean, nullable=False, default=True)
    status = Column(String(20), nullable=False, default=SYNC_QUEUED, index=True)
    triggered_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    result = Column(JSON, nullable=True)  # summary from run_scrape_and_sync on success
    error = Column(Text, nullable=True)   # short, admin-facing message on failure

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "site": self.site,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "result": self.result,
            "error": self.error,
        }

    def __repr__(self) -> str:
        return f"<SyncRun {self.id} {self.site} {self.status}>"
