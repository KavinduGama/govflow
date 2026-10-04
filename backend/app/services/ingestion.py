"""
GovFlow Data Ingestion & Sync Service
Handles:
- Scraping government sources (live with fallback to cached data)
- Chunking documents (~800 characters with semantic boundaries)
- SHA-256 hash-based change detection (avoids redundant OpenAI API embedding calls)
- Pgvector embeddings storage in DocumentChunk
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Department, Service, SourceDocument, DocumentChunk
from app.chat.retriever import _get_client

logger = logging.getLogger("govflow.ingestion")
logger.setLevel(logging.INFO)

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def compute_hash(text: str) -> str:
    """Generate SHA-256 hash for chunk or document content to detect changes."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Split text into chunks of roughly `chunk_size` characters,
    preferring paragraph breaks and sentence boundaries.
    """
    cleaned = text.replace("\r\n", "\n").strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    # Split by double newline (paragraphs) first
    paragraphs = cleaned.split("\n\n")
    chunks: List[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # If paragraph itself is larger than chunk_size, split by sentences or words
                if len(para) > chunk_size:
                    words = para.split()
                    temp = ""
                    for word in words:
                        if len(temp) + len(word) + 1 <= chunk_size:
                            temp = f"{temp} {word}" if temp else word
                        else:
                            if temp:
                                chunks.append(temp.strip())
                            temp = word
                    current_chunk = temp
                else:
                    # Keep overlap from the end of the previous chunk if applicable
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                    current_chunk = f"...{overlap_text}\n{para}" if overlap_text else para
            else:
                # Single massive paragraph
                words = para.split()
                temp = ""
                for word in words:
                    if len(temp) + len(word) + 1 <= chunk_size:
                        temp = f"{temp} {word}" if temp else word
                    else:
                        if temp:
                            chunks.append(temp.strip())
                        temp = word
                current_chunk = temp

    if current_chunk and current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate OpenAI embeddings for a list of text strings in batches.
    Uses text-embedding-3-small (1536 dims).
    """
    if not texts:
        return []

    client = _get_client()
    batch_size = 50
    all_embeddings: List[List[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # Clean newlines for optimal embedding quality as per OpenAI recommendation
        sanitized_batch = [t.replace("\n", " ").strip() for t in batch]
        response = client.embeddings.create(
            input=sanitized_batch,
            model="text-embedding-3-small",
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def sync_document_chunks(
    db: Session,
    doc: SourceDocument,
    chunk_items: List[Dict[str, str]],
) -> Dict[str, int]:
    """
    Synchronizes chunks for a single SourceDocument using SHA-256 hash change detection.
    - If chunk hash already exists in DB for this document: keep it, 0 API calls.
    - If chunk is new or altered: call OpenAI to embed only this chunk.
    - If previous chunks are no longer present: delete them.
    - Updates doc.content_hash and doc.last_scraped_at.
    """
    # Combine all chunk contents to calculate document overall hash
    all_text = "".join(item["content"] for item in chunk_items)
    doc_hash = compute_hash(all_text)

    # Fetch existing chunks for this document
    existing_chunks = db.query(DocumentChunk).filter(
        DocumentChunk.source_document_id == doc.id
    ).all()

    existing_by_hash: Dict[str, DocumentChunk] = {}
    for c in existing_chunks:
        if c.content_hash:
            existing_by_hash[c.content_hash] = c

    new_chunk_records: List[DocumentChunk] = []
    chunks_to_embed: List[Tuple[Dict[str, str], str]] = []
    retained_chunk_ids: set[int] = set()

    unchanged_count = 0
    new_count = 0
    deleted_count = 0

    for item in chunk_items:
        c_hash = compute_hash(item["content"])
        if c_hash in existing_by_hash:
            # Chunk is identical — reuse existing embedding without calling OpenAI
            unchanged_count += 1
            retained_chunk_ids.add(existing_by_hash[c_hash].id)
        else:
            chunks_to_embed.append((item, c_hash))

    # Batch embed only new or modified chunks
    if chunks_to_embed:
        texts_to_embed = [c[0]["content"] for c in chunks_to_embed]
        embeddings = get_embeddings_batch(texts_to_embed)

        for (item, c_hash), emb in zip(chunks_to_embed, embeddings):
            new_chunk = DocumentChunk(
                source_document_id=doc.id,
                section_title=item.get("section_title"),
                content=item["content"],
                embedding=emb,
                content_hash=c_hash,
            )
            db.add(new_chunk)
            new_count += 1

    # Remove stale chunks (chunks whose id is not retained, including old mock chunks with no hash)
    for c in existing_chunks:
        if c.id not in retained_chunk_ids:
            db.delete(c)
            deleted_count += 1

    # Update document metadata
    doc.content_hash = doc_hash
    doc.last_scraped_at = datetime.now(timezone.utc).isoformat()
    db.flush()

    return {
        "new_chunks": new_count,
        "unchanged_chunks": unchanged_count,
        "deleted_chunks": deleted_count,
    }


def ingest_nic_data(db: Session, raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingests parsed data from the NIC scraper / nic_raw.json into SourceDocuments & DocumentChunks.
    Handles:
    - FAQs (as individual Q&A pairs)
    - Procedures (first time, lost, amendment, dual citizen, one-day service)
    - Downloads (official PDF forms)
    """
    dept_drp = db.query(Department).filter(
        (Department.code == "drp") | (Department.name_en.ilike("%Registration of Persons%"))
    ).first()
    dept_id = dept_drp.id if dept_drp else None

    # Load service mappings
    service_first_time = db.query(Service).filter(Service.service_code == "nic_first_time").first()
    service_lost = db.query(Service).filter(Service.service_code == "nic_lost").first()

    data = raw_data.get("data", {})
    summary = {
        "documents_processed": 0,
        "new_documents": 0,
        "updated_documents": 0,
        "new_chunks": 0,
        "unchanged_chunks": 0,
        "deleted_chunks": 0,
    }

    # ── 1. Ingest FAQs ──────────────────────────────────────────────────────────
    faqs = data.get("faqs", [])
    if faqs:
        faq_url = "https://drp.gov.lk/en/faq.php"
        doc = db.query(SourceDocument).filter(
            (SourceDocument.url == faq_url) | (SourceDocument.title.ilike("%FAQ%"))
        ).first()

        is_new_doc = False
        if not doc:
            doc = SourceDocument(
                department_id=dept_id,
                title="NIC Frequently Asked Questions (DRP)",
                url=faq_url,
                source_type="faq",
            )
            db.add(doc)
            db.flush()
            is_new_doc = True
            summary["new_documents"] += 1
        else:
            summary["updated_documents"] += 1

        faq_chunk_items = []
        for faq in faqs:
            q = faq.get("question", "").strip()
            a = faq.get("answer", "").strip()
            if not q or not a:
                continue
            faq_text = f"Question: {q}\n\nAnswer: {a}"
            # If FAQ answer is very large, chunk it; otherwise single chunk
            if len(faq_text) <= 1200:
                faq_chunk_items.append({
                    "content": faq_text,
                    "section_title": f"FAQ: {q[:70]}",
                })
            else:
                for sub_chunk in chunk_text(faq_text, chunk_size=800):
                    faq_chunk_items.append({
                        "content": sub_chunk,
                        "section_title": f"FAQ: {q[:70]}",
                    })

        res = sync_document_chunks(db, doc, faq_chunk_items)
        summary["documents_processed"] += 1
        summary["new_chunks"] += res["new_chunks"]
        summary["unchanged_chunks"] += res["unchanged_chunks"]
        summary["deleted_chunks"] += res["deleted_chunks"]

    # ── 2. Ingest Procedures ───────────────────────────────────────────────────
    procedures = data.get("procedures", [])
    procedure_service_map = {
        "nic_first_time": {
            "title": "Obtaining National Identity Card for the first time",
            "service": service_first_time,
        },
        "nic_lost": {
            "title": "Lost or Damaged National Identity Cards",
            "service": service_lost,
        },
        "nic_amendment": {
            "title": "Amending National Identity Card Details",
            "service": None,
        },
        "nic_dual_citizen": {
            "title": "Issuance of National Identity Cards for Dual Citizens",
            "service": None,
        },
        "nic_one_day_service": {
            "title": "National Identity Card One Day Urgent Service",
            "service": None,
        },
    }

    for proc in procedures:
        stype = proc.get("service_type", "")
        mapping = procedure_service_map.get(stype, {
            "title": f"NIC Procedure - {stype.replace('_', ' ').title()}",
            "service": None,
        })
        title = mapping["title"]
        service = mapping["service"]
        service_id = service.id if service else None
        proc_url = proc.get("source_url", "https://drp.gov.lk/en/normal.php")

        doc = db.query(SourceDocument).filter(
            (SourceDocument.url == proc_url) | (SourceDocument.title == title)
        ).first()

        if not doc:
            doc = SourceDocument(
                department_id=dept_id,
                service_id=service_id,
                title=title,
                url=proc_url,
                source_type="webpage",
            )
            db.add(doc)
            db.flush()
            summary["new_documents"] += 1
        else:
            if service_id and not doc.service_id:
                doc.service_id = service_id
            summary["updated_documents"] += 1

        # Build comprehensive procedure text from content + list items
        content = proc.get("content", "")
        list_items = proc.get("list_items", [])
        if list_items:
            list_text = "\n- " + "\n- ".join(list_items)
            full_procedure_text = f"{content}\n\nRequired Documents & Key Items:\n{list_text}"
        else:
            full_procedure_text = content

        chunks = chunk_text(full_procedure_text, chunk_size=800, overlap=100)
        chunk_items = [
            {"content": c, "section_title": f"{title} (Part {i+1})"}
            for i, c in enumerate(chunks)
        ]

        res = sync_document_chunks(db, doc, chunk_items)
        summary["documents_processed"] += 1
        summary["new_chunks"] += res["new_chunks"]
        summary["unchanged_chunks"] += res["unchanged_chunks"]
        summary["deleted_chunks"] += res["deleted_chunks"]

    # ── 3. Ingest Downloads / Forms ─────────────────────────────────────────────
    downloads = data.get("downloads", [])
    if downloads:
        downloads_url = "https://drp.gov.lk/en/downloads.php"
        doc = db.query(SourceDocument).filter(
            (SourceDocument.url == downloads_url) | (SourceDocument.title.ilike("%Download%") | SourceDocument.title.ilike("%Application Form%"))
        ).first()

        if not doc:
            doc = SourceDocument(
                department_id=dept_id,
                title="NIC Application Forms & Downloads",
                url=downloads_url,
                source_type="form",
            )
            db.add(doc)
            db.flush()
            summary["new_documents"] += 1
        else:
            summary["updated_documents"] += 1

        # Format downloadable items
        lines = ["Official Downloadable Forms from Department for Registration of Persons (DRP):"]
        for d in downloads:
            name = d.get("name", "").strip()
            url = d.get("url", "").strip()
            if url:
                lines.append(f"- Form: {name or 'Official PDF Form'} | Link: {url}")

        download_text = "\n".join(lines)
        chunks = chunk_text(download_text, chunk_size=800)
        chunk_items = [
            {"content": c, "section_title": "Official Forms & Applications"}
            for c in chunks
        ]

        res = sync_document_chunks(db, doc, chunk_items)
        summary["documents_processed"] += 1
        summary["new_chunks"] += res["new_chunks"]
        summary["unchanged_chunks"] += res["unchanged_chunks"]
        summary["deleted_chunks"] += res["deleted_chunks"]

    return summary


def ingest_dl_data(db: Session) -> Dict[str, Any]:
    """Ingests DMT (Department of Motor Traffic) manual/scraped data if available."""
    dl_file = DATA_DIR / "dl_manual.json"
    if not dl_file.exists():
        return {}

    with open(dl_file, "r", encoding="utf-8") as f:
        dl_data = json.load(f)

    dept_dmt = db.query(Department).filter(
        (Department.code == "dmt") | (Department.name_en.ilike("%Motor Traffic%"))
    ).first()
    dept_id = dept_dmt.id if dept_dmt else None

    sub_services = dl_data.get("data", {}).get("sub_services", {})
    summary = {
        "documents_processed": 0,
        "new_documents": 0,
        "updated_documents": 0,
        "new_chunks": 0,
        "unchanged_chunks": 0,
        "deleted_chunks": 0,
    }

    service_map = {
        "dl_new": ("Driving Licence – New Application", "dl_new"),
        "dl_renewal": ("Driving Licence – Renewal", "dl_renewal"),
    }

    for svc_key, (doc_title, svc_code) in service_map.items():
        svc_info = sub_services.get(svc_key)
        if not svc_info:
            continue

        svc_model = db.query(Service).filter(Service.service_code == svc_code).first()
        svc_id = svc_model.id if svc_model else None
        doc_url = "https://www.gov.lk/government/eservices"

        doc = db.query(SourceDocument).filter(
            (SourceDocument.title.ilike(f"%{doc_title}%")) |
            ((SourceDocument.service_id == svc_id) & (SourceDocument.service_id.isnot(None)))
        ).first()

        if not doc:
            doc = SourceDocument(
                department_id=dept_id,
                service_id=svc_id,
                title=doc_title,
                url=doc_url,
                source_type="webpage",
            )
            db.add(doc)
            db.flush()
            summary["new_documents"] += 1
        else:
            if svc_id and not doc.service_id:
                doc.service_id = svc_id
            summary["updated_documents"] += 1

        # Format content from structured DMT data
        lines = [f"Service: {svc_info.get('name', doc_title)}"]
        eligibility = svc_info.get("eligibility", {})
        if eligibility:
            lines.append("Eligibility Requirements:")
            for k, v in eligibility.items():
                lines.append(f"  - {k.replace('_', ' ').title()}: {v}")

        req_docs = svc_info.get("required_documents", [])
        if req_docs:
            lines.append("Required Documents:")
            for rd in req_docs:
                lines.append(f"  - {rd.get('name')} ({rd.get('requirement_type')}): {rd.get('notes', '')}")

        procedure = svc_info.get("procedure_steps", [])
        if procedure:
            lines.append("Procedure Steps:")
            for step in procedure:
                lines.append(f"  - Step: {step}")

        fees = svc_info.get("fees", {})
        if fees:
            lines.append(f"Fees: {fees}")

        full_text = "\n".join(lines)
        chunks = chunk_text(full_text, chunk_size=800)
        chunk_items = [
            {"content": c, "section_title": f"{doc_title} (Overview)"}
            for c in chunks
        ]

        res = sync_document_chunks(db, doc, chunk_items)
        summary["documents_processed"] += 1
        summary["new_chunks"] += res["new_chunks"]
        summary["unchanged_chunks"] += res["unchanged_chunks"]
        summary["deleted_chunks"] += res["deleted_chunks"]

    return summary


def run_scrape_and_sync(
    db: Session,
    site_key: str = "nic",
    force_live: bool = True,
) -> Dict[str, Any]:
    """
    Main orchestration pipeline:
    1. Optionally run the live scraper (nic_scraper.run)
    2. Fall back to cached JSON if network fails or live scraping is skipped
    3. Ingest scraped data into SourceDocument and DocumentChunk records
    4. Compute change detection statistics and cost savings
    """
    scraped_live = False
    live_scrape_error: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    if force_live:
        try:
            from scraper import nic_scraper
            logger.info("Triggering live scraper...")
            nic_scraper.run()
            scraped_live = True
        except Exception as e:
            # Includes nic_scraper.IncompleteScrapeError: a broken scrape never replaces the cache
            live_scrape_error = str(e)
            logger.warning("Live scraping failed: %s. Falling back to cached data.", e)

    # Read the scraped JSON
    nic_json_path = DATA_DIR / "nic_raw.json"
    if nic_json_path.exists():
        with open(nic_json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

    if not raw_data:
        raise ValueError("No scraped data available in backend/data/nic_raw.json and live scraper failed.")

    # Ingest NIC data
    nic_summary = ingest_nic_data(db, raw_data)

    # Ingest DL data if available
    dl_summary = ingest_dl_data(db)

    # Aggregate summaries
    total_docs = nic_summary["documents_processed"] + dl_summary.get("documents_processed", 0)
    total_new_docs = nic_summary["new_documents"] + dl_summary.get("new_documents", 0)
    total_updated_docs = nic_summary["updated_documents"] + dl_summary.get("updated_documents", 0)
    total_new_chunks = nic_summary["new_chunks"] + dl_summary.get("new_chunks", 0)
    total_unchanged_chunks = nic_summary["unchanged_chunks"] + dl_summary.get("unchanged_chunks", 0)
    total_deleted_chunks = nic_summary["deleted_chunks"] + dl_summary.get("deleted_chunks", 0)
    total_chunks_in_batch = total_new_chunks + total_unchanged_chunks

    cost_saved = (
        round((total_unchanged_chunks / total_chunks_in_batch) * 100, 1)
        if total_chunks_in_batch > 0
        else 0.0
    )

    db.commit()

    return {
        "status": "success",
        "scraped_live": scraped_live,
        "live_scrape_error": live_scrape_error,
        "documents_processed": total_docs,
        "new_documents": total_new_docs,
        "updated_documents": total_updated_docs,
        "new_chunks": total_new_chunks,
        "unchanged_chunks": total_unchanged_chunks,
        "deleted_chunks": total_deleted_chunks,
        "total_active_chunks": db.query(DocumentChunk).count(),
        "cost_saved_percent": cost_saved,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def get_knowledge_base_stats(db: Session) -> Dict[str, Any]:
    """Retrieve summary statistics for the Knowledge Base admin view."""
    total_docs = db.query(SourceDocument).count()
    total_chunks = db.query(DocumentChunk).count()

    # Find latest scraped timestamp across documents
    latest_doc = (
        db.query(SourceDocument)
        .filter(SourceDocument.last_scraped_at.isnot(None))
        .order_by(SourceDocument.last_scraped_at.desc())
        .first()
    )
    last_sync = latest_doc.last_scraped_at if latest_doc else None

    # Fetch document summaries with chunk counts
    docs = db.query(SourceDocument).all()
    doc_list = []
    for d in docs:
        c_count = db.query(DocumentChunk).filter(DocumentChunk.source_document_id == d.id).count()
        doc_list.append({
            "id": d.id,
            "title": d.title,
            "url": d.url,
            "source_type": d.source_type,
            "chunk_count": c_count,
            "last_scraped_at": d.last_scraped_at,
            "department_id": d.department_id,
            "service_id": d.service_id,
        })

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "last_sync": last_sync,
        "documents": doc_list,
    }
