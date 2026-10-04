"""
GovFlow — Vector Document Embedding Script
Embeds official government service documents into pgvector using OpenAI text-embedding-3-small.
Integrates with app.services.ingestion for real scraped data and SHA-256 change detection.
"""

import argparse
import os
import sys

# Configure UTF-8 for Windows console if supported
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal
from app.models import SourceDocument, DocumentChunk
from app.services.ingestion import run_scrape_and_sync, get_knowledge_base_stats


def main():
    parser = argparse.ArgumentParser(description="GovFlow Vector Document Embedder")
    parser.add_argument("--reset", action="store_true", help="Delete all existing chunks and re-embed")
    parser.add_argument("--live", action="store_true", help="Attempt live scraping before embedding")
    parser.add_argument("--site", default="nic", help="Site key to scrape/sync (default: nic)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.reset:
            print("[RESET] Clearing existing document chunks...")
            db.query(DocumentChunk).delete()
            # Also clear content_hash from source_documents
            for doc in db.query(SourceDocument).all():
                doc.content_hash = None
            db.commit()
            print("[OK] Document chunks cleared.")

        print(f"[SYNC] Starting Scrape & Sync pipeline (live={args.live}, site={args.site})...")
        summary = run_scrape_and_sync(db=db, site_key=args.site, force_live=args.live)

        print("\n" + "=" * 50)
        print("INGESTION & EMBEDDING SUMMARY")
        print("=" * 50)
        print(f"Status              : {summary['status']}")
        print(f"Scraped Live        : {summary['scraped_live']}")
        print(f"Documents Processed : {summary['documents_processed']}")
        print(f"New Documents       : {summary['new_documents']}")
        print(f"Updated Documents   : {summary['updated_documents']}")
        print(f"New Chunks Embedded : {summary['new_chunks']}")
        print(f"Unchanged (Skipped) : {summary['unchanged_chunks']}")
        print(f"Deleted Chunks      : {summary['deleted_chunks']}")
        print(f"Total Active Chunks : {summary['total_active_chunks']}")
        print(f"Cost Saved (Skipped): {summary['cost_saved_percent']}%")
        print(f"Timestamp           : {summary['timestamp']}")
        print("=" * 50)

    except Exception as e:
        print(f"[ERROR] Error during embedding process: {e}")
        db.rollback()
        raise e
    finally:
        db.close()



if __name__ == "__main__":
    main()
