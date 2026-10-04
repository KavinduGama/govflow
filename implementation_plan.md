# Scrape & Sync Pipeline + Real Data Ingestion

Build a "Scrape & Sync" workflow: admin presses a button → scraper runs → detects changes → re-embeds only new/changed content → vector DB is up-to-date.

## Proposed Changes

### 1. Backend — Data Ingestion Service (NEW)

#### [NEW] [`backend/app/services/ingestion.py`](file:///d:/GovFlow/backend/app/services/ingestion.py)

Central ingestion service that handles the full pipeline:

```
Scraped JSON → Extract text sections → Chunk → Hash each chunk → 
Compare with DB → Embed only NEW/CHANGED chunks → Save to DB
```

Key logic:
- **`ingest_scraped_data(site_key)`** — Takes raw scraped JSON, extracts meaningful text sections (FAQs as individual Q&A pairs, procedure sections, contact info), creates `SourceDocument` records, chunks text (~800 chars with overlap), and embeds via OpenAI
- **Change detection** — SHA-256 hash stored per chunk. On re-scrape, hash comparison identifies what's new/changed. Only re-embed changed content (saves OpenAI API costs)
- **Handles both `nic_raw.json` format** (structured: FAQs, procedures, forms) **and `crawler.py` format** (flat pages with text_content)

---

### 2. Backend — Scrape & Sync Endpoint

#### [MODIFY] [`backend/app/routers/admin.py`](file:///d:/GovFlow/backend/app/routers/admin.py)

Add these endpoints:

- **`POST /api/v1/admin/scrape-sync`** — Triggers the full workflow:
  1. Runs the scraper (NIC scraper + crawler)
  2. Ingests the scraped data into source_documents + document_chunks  
  3. Returns a summary of what changed (new pages, updated chunks, unchanged)

- **`GET /api/v1/admin/knowledge-base/stats`** — Returns current KB stats (total docs, chunks, last sync time)

The endpoint runs **synchronously** for now (scraping takes ~10-30 seconds). We use a `status` field so the frontend can show progress.

---

### 3. Database — Add content_hash column

#### [NEW] [`backend/migrations/versions/xxxx_add_content_hash.py`](file:///d:/GovFlow/backend/migrations/versions/)

Add `content_hash` (String) to `document_chunks` table for change detection. Add `last_scraped_at` to `source_documents`.

#### [MODIFY] [`backend/app/models/chunk.py`](file:///d:/GovFlow/backend/app/models/chunk.py)
Add `content_hash: Mapped[str | None]` column.

#### [MODIFY] [`backend/app/models/source_document.py`](file:///d:/GovFlow/backend/app/models/source_document.py)
Add `last_scraped_at` and `content_hash` columns.

---

### 4. Fix Embed Script — Use Real Content

#### [MODIFY] [`backend/scripts/embed_documents.py`](file:///d:/GovFlow/backend/scripts/embed_documents.py)

Replace the mock content (`"This is the official procedure for {title}. " * 20`) with actual text from source documents. This script becomes a fallback — the main ingestion path will be through the new service.

---

### 5. Frontend — Admin "Scrape & Sync" Button

#### [MODIFY] [`frontend/src/app/admin/page.js`](file:///d:/GovFlow/frontend/src/app/admin/page.js)

Add a "Knowledge Base" section to the admin dashboard with:
- **"🔄 Scrape & Sync" button** — triggers `POST /api/v1/admin/scrape-sync`
- **Stats display** — total source documents, chunks, last sync timestamp
- **Sync results** — shows what changed after scraping (e.g., "3 new pages, 12 new chunks, 2 updated chunks")
- **Loading/progress state** — spinner while scraping is in progress

#### [MODIFY] [`frontend/src/app/admin/admin.css`](file:///d:/GovFlow/frontend/src/app/admin/admin.css)

Add styles for the knowledge base section and sync button.

---

## Flow Diagram

```
Admin clicks "Scrape & Sync"
         │
         ▼
POST /api/v1/admin/scrape-sync
         │
    ┌────┴────┐
    ▼         ▼
NIC Scraper  Site Crawler
(drp.gov.lk) (configurable)
    │         │
    └────┬────┘
         ▼
   Raw JSON saved to /data/
         │
         ▼
   Ingestion Service
    ├── Extract text sections
    ├── Chunk text (~800 chars)
    ├── SHA-256 hash each chunk
    ├── Compare hashes with DB
    ├── Embed ONLY new/changed (OpenAI)
    └── Upsert to source_documents + document_chunks
         │
         ▼
   Return sync summary:
   {new_docs: 3, new_chunks: 15, 
    updated_chunks: 2, unchanged: 8,
    embedding_cost_saved: "80%"}
```

## Verification Plan

### Manual Verification
1. Open admin page → click "Scrape & Sync" → verify it scrapes and ingests
2. Check DB has real content in chunks (not mock text)
3. Go to chat → ask a general question like "What are the DRP office hours?" → verify it returns real scraped data
4. Click "Scrape & Sync" again → verify it detects no changes (or only actual changes)
