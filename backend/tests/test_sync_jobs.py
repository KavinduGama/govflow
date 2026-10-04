import json
from datetime import datetime, timedelta, timezone

import pytest

from app.models import SyncRun
from app.services import sync_jobs
from scraper import nic_scraper
from tests.conftest import auth_header

GOOD_SCRAPE = {
    "scraped_at": "2026-10-01T00:00:00+00:00",
    "data": {"faqs": [{}] * 10, "procedures": [{}] * 5, "downloads": [{}] * 30},
}


def scrape_with(faqs, procedures, downloads):
    return {"data": {"faqs": [{}] * faqs, "procedures": [{}] * procedures, "downloads": [{}] * downloads}}


# ---------- Scraper validation ----------

def test_valid_scrape_passes():
    nic_scraper.validate_scrape(scrape_with(10, 5, 30), GOOD_SCRAPE)


def test_empty_section_is_rejected():
    # What a site outage looks like: fetch_page() returns None, so sections come back empty
    with pytest.raises(nic_scraper.IncompleteScrapeError, match="faqs: nothing scraped"):
        nic_scraper.validate_scrape(scrape_with(0, 5, 30), GOOD_SCRAPE)


def test_large_shrink_is_rejected():
    # 2 FAQs where we previously had 10: probably a partial page load or a layout change
    with pytest.raises(nic_scraper.IncompleteScrapeError, match="only 2 items"):
        nic_scraper.validate_scrape(scrape_with(2, 5, 30), GOOD_SCRAPE)


def test_first_ever_scrape_only_needs_non_empty_sections():
    nic_scraper.validate_scrape(scrape_with(1, 1, 1), previous=None)


def test_broken_scrape_never_overwrites_cache(tmp_path, monkeypatch):
    cache = tmp_path / "nic_raw.json"
    cache.write_text(json.dumps(GOOD_SCRAPE), encoding="utf-8")
    monkeypatch.setattr(nic_scraper, "OUTPUT_PATH", cache)
    monkeypatch.setattr(nic_scraper, "scrape", lambda: scrape_with(0, 0, 0))

    with pytest.raises(nic_scraper.IncompleteScrapeError):
        nic_scraper.run()

    assert json.loads(cache.read_text(encoding="utf-8")) == GOOD_SCRAPE


def test_good_scrape_replaces_cache(tmp_path, monkeypatch):
    cache = tmp_path / "nic_raw.json"
    cache.write_text(json.dumps(GOOD_SCRAPE), encoding="utf-8")
    fresh = {"scraped_at": "2026-10-04T00:00:00+00:00", **scrape_with(11, 5, 33)}
    monkeypatch.setattr(nic_scraper, "OUTPUT_PATH", cache)
    monkeypatch.setattr(nic_scraper, "scrape", lambda: fresh)

    nic_scraper.run()

    assert json.loads(cache.read_text(encoding="utf-8")) == fresh
    assert not cache.with_suffix(".json.tmp").exists()


# ---------- Background sync runs ----------
# The real pipeline scrapes the web and calls OpenAI, so tests swap it for a stub.

@pytest.fixture
def admin(make_user):
    return make_user("admin@example.com", role="admin")


def test_sync_is_queued_then_succeeds(client, admin, monkeypatch):
    monkeypatch.setattr(sync_jobs, "run_scrape_and_sync",
                        lambda db, site_key, force_live: {"status": "success", "new_chunks": 3})

    res = client.post("/api/v1/admin/scrape-sync?force_live=false", headers=auth_header(admin))
    assert res.status_code == 202
    run_id = res.json()["id"]

    # TestClient runs background tasks before returning, so the run has finished by now
    run = client.get(f"/api/v1/admin/sync-runs/{run_id}", headers=auth_header(admin)).json()
    assert run["status"] == "succeeded"
    assert run["result"]["new_chunks"] == 3
    assert run["started_at"] and run["finished_at"]


def test_failed_sync_records_safe_error(client, admin, monkeypatch):
    def explode(db, site_key, force_live):
        raise RuntimeError("password=hunter2 leaked in a stack trace")
    monkeypatch.setattr(sync_jobs, "run_scrape_and_sync", explode)

    run_id = client.post("/api/v1/admin/scrape-sync", headers=auth_header(admin)).json()["id"]
    run = client.get(f"/api/v1/admin/sync-runs/{run_id}", headers=auth_header(admin)).json()

    assert run["status"] == "failed"
    assert "hunter2" not in run["error"]


def test_second_sync_is_rejected_while_one_is_running(client, db_session, admin):
    db_session.add(SyncRun(site="nic", status="running", created_at=datetime.now(timezone.utc)))
    db_session.commit()

    res = client.post("/api/v1/admin/scrape-sync", headers=auth_header(admin))
    assert res.status_code == 409


def test_stale_run_does_not_block_new_sync(client, db_session, admin, monkeypatch):
    monkeypatch.setattr(sync_jobs, "run_scrape_and_sync", lambda db, site_key, force_live: {"status": "success"})
    stale = SyncRun(site="nic", status="running", created_at=datetime.now(timezone.utc) - timedelta(hours=2))
    db_session.add(stale)
    db_session.commit()

    res = client.post("/api/v1/admin/scrape-sync", headers=auth_header(admin))

    assert res.status_code == 202
    db_session.refresh(stale)
    assert stale.status == "failed"


def test_unknown_site_is_rejected(client, admin):
    res = client.post("/api/v1/admin/scrape-sync?site=passport", headers=auth_header(admin))
    assert res.status_code == 422


def test_sync_runs_are_listed_newest_first(client, db_session, admin):
    for status in ("succeeded", "failed"):
        db_session.add(SyncRun(site="nic", status=status))
    db_session.commit()

    runs = client.get("/api/v1/admin/sync-runs", headers=auth_header(admin)).json()
    assert [r["status"] for r in runs] == ["failed", "succeeded"]
