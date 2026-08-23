# GovFlow AI — Week 1 Execution Plan
### Theme: "Get the data. Build the bones."
### Dates: Day 1–5 | Goal: Real NIC + DL data in DB, FastAPI running, Rule Engines tested

---

## Project Structure You'll Have By End of Week 1

```
govflow-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  ← FastAPI app entry point
│   │   ├── database.py              ← SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── department.py
│   │   │   ├── service.py
│   │   │   ├── question.py
│   │   │   ├── workflow_step.py
│   │   │   ├── required_document.py
│   │   │   └── source_document.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── question.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── services.py
│   │   └── engines/
│   │       ├── __init__.py
│   │       ├── question_engine.py   ← Day 5
│   │       └── workflow_engine.py   ← Day 5
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── nic_scraper.py           ← Day 1
│   │   └── dl_extractor.py          ← Day 2
│   ├── data/
│   │   ├── nic_raw.json             ← scraped DRP content
│   │   ├── dl_manual.json           ← manually curated DL workflow
│   │   └── seed/
│   │       ├── departments.json
│   │       ├── services.json
│   │       ├── nic_questions.json
│   │       ├── nic_steps.json
│   │       ├── dl_questions.json
│   │       └── dl_steps.json
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── scripts/
│   │   └── seed_db.py               ← Day 4
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_question_engine.py  ← Day 5
│   │   └── test_workflow_engine.py  ← Day 5
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
└── docker-compose.yml               ← PostgreSQL via Docker
```

---

## Pre-Week Setup (Do This First — 15 minutes)

### 1. Install prerequisites
- Python 3.11+ → https://python.org
- Docker Desktop → https://docker.com/products/docker-desktop
- VS Code → already installed
- Git → `git --version` to check

### 2. Create project folder
```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS"
mkdir govflow-ai
cd govflow-ai
git init
```

### 3. Create `.gitignore`
```
.env
__pycache__/
*.pyc
.venv/
data/raw/
*.db
```

---

## DAY 1 — Python Project + NIC Scraper

**Time estimate: 3–4 hours**  
**Goal: Running scraper that saves NIC procedure data to JSON**

### 🧠 What You'll Learn
- `requests` library — the #1 way Python talks to the internet
- `BeautifulSoup` — parsing HTML as a navigable tree
- Why we save raw HTML (reproducibility — website may change later)
- How to extract structured data from accordion/tab-based government pages
- JSON as a data format for scraped content

### Step 1A — Create Python virtual environment

```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\govflow-ai"
mkdir backend
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
```

You should see `(.venv)` in your terminal prompt.

### Step 1B — Create `requirements.txt`

```txt
# HTTP & scraping
requests==2.32.3
beautifulsoup4==4.12.3
lxml==5.2.2
pdfplumber==0.11.0

# Database
sqlalchemy==2.0.32
psycopg2-binary==2.9.9
alembic==1.13.2

# FastAPI
fastapi==0.112.0
uvicorn[standard]==0.30.6
pydantic==2.8.2
pydantic-settings==2.4.0
python-dotenv==1.0.1

# Testing
pytest==8.3.2
pytest-asyncio==0.23.8
httpx==0.27.0

# Utils
python-multipart==0.0.9
```

Install:
```bash
pip install -r requirements.txt
```

### Step 1C — Build the NIC scraper

Create `backend/scraper/nic_scraper.py`:

```python
"""
NIC Scraper — Department for Registration of Persons
Target: https://drp.gov.lk/en/
Scrapes: procedure pages, FAQs, available info

LEARNING NOTE:
- requests.get() sends an HTTP GET request (like your browser loading a page)
- response.text is the raw HTML string
- BeautifulSoup parses that string into a tree you can navigate
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
BASE_URL = "https://drp.gov.lk/en"
HEADERS = {
    # We identify ourselves politely — not hiding that we're a script
    "User-Agent": "GovFlowAI/1.0 Research Bot (government service guidance platform)",
    "Accept-Language": "en-US,en;q=0.9",
}
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Helper: fetch one page ───────────────────────────────────────────────────
def fetch_page(url: str) -> BeautifulSoup | None:
    """
    Fetch a URL and return a BeautifulSoup object.
    Returns None if the request fails.
    
    LEARNING: We wrap requests in try/except because network calls CAN fail.
    Always handle failure gracefully.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()  # raises exception for 4xx/5xx status codes
        print(f"  ✓ Fetched: {url} ({len(response.text)} chars)")
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        print(f"  ✗ Failed: {url} → {e}")
        return None


# ── Scraper 1: FAQ page ──────────────────────────────────────────────────────
def scrape_faq() -> list[dict]:
    """
    Scrapes drp.gov.lk/en/faq.php
    Returns list of {question, answer} dicts
    
    LEARNING: Government FAQ pages are usually accordion/collapse components.
    The text is in the HTML but hidden visually — BeautifulSoup sees all of it.
    """
    soup = fetch_page(f"{BASE_URL}/faq.php")
    if not soup:
        return []

    faqs = []
    
    # Each FAQ item is an <li> inside the .faq-list div
    # LEARNING: soup.select() uses CSS selectors — same syntax as browser DevTools
    faq_items = soup.select(".faq-list li")
    
    for item in faq_items:
        # The question is in the <a> tag inside the accordion trigger
        question_tag = item.find("a", {"data-bs-toggle": "collapse"})
        # The answer is in the collapse div
        answer_tag = item.find("div", {"class": "collapse"})
        
        if question_tag and answer_tag:
            question = question_tag.get_text(strip=True)
            # Remove the chevron icon text that gets picked up
            question = question.replace("", "").strip()
            answer = answer_tag.get_text(separator=" ", strip=True)
            
            # Only add if both exist and question is meaningful
            if len(question) > 10 and len(answer) > 10:
                faqs.append({
                    "question": question,
                    "answer": answer,
                    "source_url": f"{BASE_URL}/faq.php",
                    "section": "faq"
                })
    
    print(f"  → Extracted {len(faqs)} FAQ items")
    return faqs


# ── Scraper 2: NIC procedure pages ───────────────────────────────────────────
def scrape_normal_service() -> list[dict]:
    """
    Scrapes drp.gov.lk/en/normal.php
    Returns list of service procedure sections
    
    LEARNING: This page uses Bootstrap tabs (v-pills).
    Each tab panel contains a different NIC service type.
    """
    soup = fetch_page(f"{BASE_URL}/normal.php")
    if not soup:
        return []

    procedures = []
    
    # Tab panels — each panel is one service type
    # LEARNING: We look for the tab-content div, then find each pane inside
    tab_content = soup.find("div", {"class": "tab-content"})
    if not tab_content:
        # Fallback: grab all content sections
        print("  ⚠ Could not find tab-content, using full page text")
        full_text = soup.get_text(separator="\n", strip=True)
        procedures.append({
            "service_type": "nic_procedures",
            "content": full_text[:5000],  # first 5000 chars
            "source_url": f"{BASE_URL}/normal.php",
            "section": "procedures"
        })
        return procedures
    
    # Map tab IDs to service types
    tab_map = {
        "v-pills-home": "nic_first_time",
        "v-pills-profile": "nic_lost",
        "v-pills-operation": "nic_amendment",
        "v-pills-development": "nic_dual_citizen",
        "v-pills-audit": "nic_one_day_service",
    }
    
    for tab_id, service_type in tab_map.items():
        panel = soup.find("div", {"id": tab_id})
        if panel:
            content = panel.get_text(separator="\n", strip=True)
            # Extract any list items (document lists are usually <li> tags)
            list_items = [li.get_text(strip=True) for li in panel.find_all("li")]
            
            procedures.append({
                "service_type": service_type,
                "content": content,
                "list_items": list_items,
                "source_url": f"{BASE_URL}/normal.php#{tab_id}-tab",
                "section": "procedures"
            })
            print(f"    → {service_type}: {len(content)} chars, {len(list_items)} list items")
    
    return procedures


# ── Scraper 3: Downloads page (forms) ────────────────────────────────────────
def scrape_downloads() -> list[dict]:
    """
    Scrapes drp.gov.lk/en/downloads.php
    Returns list of downloadable forms with URLs
    """
    soup = fetch_page(f"{BASE_URL}/downloads.php")
    if not soup:
        return []

    downloads = []
    
    # Find all links that look like form downloads (PDFs)
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".pdf" in href.lower() or "download" in href.lower():
            full_url = href if href.startswith("http") else f"https://drp.gov.lk/{href.lstrip('/')}"
            downloads.append({
                "name": link.get_text(strip=True),
                "url": full_url,
                "source_url": f"{BASE_URL}/downloads.php",
                "section": "forms"
            })
    
    print(f"  → Found {len(downloads)} downloadable forms")
    return downloads


# ── Main runner ──────────────────────────────────────────────────────────────
def run():
    print("🕷  Starting NIC scraper...")
    print(f"   Target: {BASE_URL}")
    print(f"   Output: {OUTPUT_DIR / 'nic_raw.json'}")
    print()
    
    result = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_department": "Department for Registration of Persons",
        "source_base_url": BASE_URL,
        "data": {}
    }
    
    # 1. FAQs
    print("📄 Scraping FAQs...")
    result["data"]["faqs"] = scrape_faq()
    time.sleep(1)  # LEARNING: Be polite — don't hammer the server
    
    # 2. Procedures
    print("📋 Scraping NIC procedures...")
    result["data"]["procedures"] = scrape_normal_service()
    time.sleep(1)
    
    # 3. Downloads
    print("📎 Scraping downloads/forms...")
    result["data"]["downloads"] = scrape_downloads()
    
    # Save
    output_path = OUTPUT_DIR / "nic_raw.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"✅ Done! Saved to: {output_path}")
    print(f"   FAQs: {len(result['data']['faqs'])}")
    print(f"   Procedures: {len(result['data']['procedures'])}")
    print(f"   Downloads: {len(result['data']['downloads'])}")


if __name__ == "__main__":
    run()
```

### Step 1D — Run it

```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\govflow-ai\backend"
python -m scraper.nic_scraper
```

Expected output:
```
🕷  Starting NIC scraper...
📄 Scraping FAQs...
  ✓ Fetched: https://drp.gov.lk/en/faq.php
  → Extracted 11 FAQ items
📋 Scraping NIC procedures...
  ✓ Fetched: https://drp.gov.lk/en/normal.php
    → nic_first_time: 1234 chars
    → nic_lost: 987 chars
    ...
✅ Done! Saved to: data/nic_raw.json
```

### 📝 Day 1 Practice Task
Open `data/nic_raw.json` in VS Code and find:
1. What is the FAQ answer about processing time?
2. What list items appear under `nic_first_time`?
3. What PDF forms are available?

Write these down — you'll use them to manually build the seed data on Day 4.

---

## DAY 2 — PDF Extraction + DL Manual Data

**Time estimate: 3–4 hours**  
**Goal: DL workflow data in structured JSON (mix of extracted + manual)**

### 🧠 What You'll Learn
- PDF parsing with `pdfplumber` — when PDFs are machine-readable vs image-scanned
- Why manual curation matters for accuracy (especially for government services)
- JSON data modeling — structuring procedure data into a reusable schema
- The admin review principle — never trust automated extraction alone

### Step 2A — Create the DL extractor

Create `backend/scraper/dl_extractor.py`:

```python
"""
Driving Licence Data Extractor
Strategy: Download PDFs from official sources + manual curation
Note: dmt.gov.lk is domain-hijacked — use eservices.motortraffic.gov.lk
      and gov.lk for official info.

LEARNING NOTE:
- PDFs are NOT all the same — some have real text, some are scanned images
- pdfplumber works on text-based PDFs (most official government forms)
- Scanned PDFs need OCR (Tesseract) — we'll skip that for now
"""

import json
import requests
import pdfplumber
from io import BytesIO
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "GovFlowAI/1.0 Research Bot",
}


def try_extract_pdf(url: str) -> str:
    """
    Download a PDF and extract its text.
    Returns extracted text or empty string if it fails.
    
    LEARNING: We use BytesIO to keep the PDF in memory (no need to save to disk).
    pdfplumber opens it and extracts text page by page.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        
        pdf_bytes = BytesIO(response.content)
        text_parts = []
        
        with pdfplumber.open(pdf_bytes) as pdf:
            print(f"  → PDF has {len(pdf.pages)} pages")
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"[Page {i+1}]\n{page_text}")
        
        full_text = "\n\n".join(text_parts)
        print(f"  → Extracted {len(full_text)} chars of text")
        return full_text
        
    except Exception as e:
        print(f"  ✗ PDF extraction failed: {e}")
        return ""


def build_dl_manual_data() -> dict:
    """
    Manually curated Driving Licence workflow data.
    
    LEARNING: This is intentional manual curation because:
    1. The real DMT site requires login
    2. Government procedures require human verification for accuracy
    3. This is the "admin review" step made explicit — YOU are the admin right now
    
    Sources used to build this:
    - eservices.motortraffic.gov.lk (appointment portal structure)
    - gov.lk service listings
    - Yamu.lk verified guide (cross-referenced with official)
    - DMT WhatsApp: 071-4033300
    """
    return {
        "service_type": "driving_licence",
        "department": "Department of Motor Traffic",
        "official_appointment_url": "https://eservices.motortraffic.gov.lk",
        "official_contact_whatsapp": "071-4033300",
        "review_status": "manually_curated",
        "note": "Cross-referenced from eservices.motortraffic.gov.lk and gov.lk. Verify before publishing.",
        
        "sub_services": {
            "dl_new": {
                "name": "New Driving Licence (First Time)",
                "eligibility": {
                    "minimum_age": 18,
                    "requires_learner_permit": True,
                    "learner_permit_holding_period_days": 90
                },
                "required_documents": [
                    {
                        "key": "nic_original",
                        "name": "Original National Identity Card (NIC)",
                        "requirement_type": "required",
                        "notes": "Must be the smart card (12-digit NIC number)"
                    },
                    {
                        "key": "nic_copy",
                        "name": "Photocopy of NIC",
                        "requirement_type": "required",
                        "notes": "Both front and back"
                    },
                    {
                        "key": "birth_certificate",
                        "name": "Birth Certificate",
                        "requirement_type": "required",
                        "notes": "Original or certified copy"
                    },
                    {
                        "key": "medical_certificate",
                        "name": "Medical Certificate from National Transport Medical Institution",
                        "requirement_type": "required",
                        "notes": "Must be from NTMI — not any private hospital"
                    },
                    {
                        "key": "learner_permit",
                        "name": "Current Learner Permit",
                        "requirement_type": "required",
                        "notes": "Must be held for at least 3 months"
                    },
                    {
                        "key": "passport_photo",
                        "name": "Recent Passport-Sized Photographs",
                        "requirement_type": "required",
                        "notes": "Check current DMT specification for count"
                    },
                    {
                        "key": "driving_school_certificate",
                        "name": "Certificate from Registered Driving School",
                        "requirement_type": "conditional",
                        "condition": "If attended a driving school",
                        "notes": "Optional but recommended"
                    }
                ],
                "workflow_steps": [
                    {
                        "step_key": "get_learner_permit",
                        "title": "Obtain a Learner Permit first",
                        "description": "You must hold a learner permit for at least 3 months before applying for the full licence. Visit your nearest DMT district office.",
                        "order": 1,
                        "estimated_time": "1 day to obtain"
                    },
                    {
                        "step_key": "get_medical_certificate",
                        "title": "Get Medical Certificate from NTMI",
                        "description": "Visit the National Transport Medical Institution (NTMI) for a medical fitness examination. This is ONLY accepted from NTMI — not any private hospital.",
                        "order": 2,
                        "estimated_time": "1 day"
                    },
                    {
                        "step_key": "book_appointment",
                        "title": "Book appointment on DMT e-Services portal",
                        "description": "Visit https://eservices.motortraffic.gov.lk to book your appointment at your nearest DMT district office.",
                        "order": 3,
                        "estimated_time": "15 minutes online"
                    },
                    {
                        "step_key": "prepare_documents",
                        "title": "Prepare all required documents",
                        "description": "Gather all documents listed in the checklist. Double-check each item before your appointment.",
                        "order": 4,
                        "estimated_time": "1–2 days"
                    },
                    {
                        "step_key": "attend_dmt_office",
                        "title": "Attend DMT district office on appointment date",
                        "description": "Bring all original documents and photocopies. Submit your application and pay the applicable fee at the cashier.",
                        "order": 5,
                        "estimated_time": "Half day"
                    },
                    {
                        "step_key": "written_test",
                        "title": "Pass the written knowledge test",
                        "description": "A computer-based test on traffic rules and road signs will be conducted at the DMT office.",
                        "order": 6,
                        "estimated_time": "30–60 minutes"
                    },
                    {
                        "step_key": "practical_test",
                        "title": "Pass the practical driving test",
                        "description": "A DMT examiner will conduct the practical driving test at the DMT office grounds.",
                        "order": 7,
                        "estimated_time": "30–60 minutes"
                    },
                    {
                        "step_key": "collect_licence",
                        "title": "Collect your driving licence",
                        "description": "Upon passing, your licence will be issued. Verify the processing time at your DMT office.",
                        "order": 8,
                        "estimated_time": "Same day or few days"
                    }
                ]
            },
            "dl_renewal": {
                "name": "Driving Licence Renewal",
                "renewal_window": "Can be renewed 3 months before expiry or up to 1 year after expiry",
                "required_documents": [
                    {
                        "key": "current_licence",
                        "name": "Current/Expired Driving Licence",
                        "requirement_type": "required"
                    },
                    {
                        "key": "nic_original",
                        "name": "Original NIC",
                        "requirement_type": "required"
                    },
                    {
                        "key": "nic_copy",
                        "name": "Photocopy of NIC",
                        "requirement_type": "required"
                    },
                    {
                        "key": "medical_certificate",
                        "name": "Medical Certificate from NTMI",
                        "requirement_type": "conditional",
                        "condition": "Required if renewing after expiry or for certain age groups. Check with DMT."
                    }
                ],
                "workflow_steps": [
                    {
                        "step_key": "book_appointment",
                        "title": "Book renewal appointment online",
                        "description": "Visit https://eservices.motortraffic.gov.lk and book a renewal appointment.",
                        "order": 1
                    },
                    {
                        "step_key": "prepare_documents",
                        "title": "Prepare renewal documents",
                        "description": "Gather current licence + NIC. Check if a medical certificate is needed for your case.",
                        "order": 2
                    },
                    {
                        "step_key": "attend_dmt_office",
                        "title": "Visit DMT office on your appointment date",
                        "description": "Submit documents and pay the renewal fee.",
                        "order": 3
                    },
                    {
                        "step_key": "collect_renewed_licence",
                        "title": "Collect renewed licence",
                        "description": "Renewed licence is typically issued on the same day.",
                        "order": 4
                    }
                ]
            }
        }
    }


def run():
    print("🚗 Building Driving Licence data...")
    
    # Build manual data
    dl_data = {
        "scraped_at": "2026-08-03T00:00:00Z",
        "source_note": "Manually curated from eservices.motortraffic.gov.lk and gov.lk. Requires admin review before publishing.",
        "data": build_dl_manual_data()
    }
    
    # Save
    output_path = OUTPUT_DIR / "dl_manual.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dl_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved DL data to: {output_path}")
    print(f"   Sub-services: {list(dl_data['data']['sub_services'].keys())}")


if __name__ == "__main__":
    run()
```

### Step 2B — Run it

```bash
python -m scraper.dl_extractor
```

### 📝 Day 2 Practice Task
Read through the `dl_manual.json` file. Ask yourself:
1. Is the NTMI medical certificate rule correct? How would you verify it?
2. What happens if someone has an expired licence for MORE than 1 year?
3. Add a `dl_learner_permit` sub-service to the JSON manually.

---

## DAY 3 — Database Design + SQLAlchemy Models + Alembic

**Time estimate: 4–5 hours**  
**Goal: PostgreSQL running, all tables created via migrations**

### 🧠 What You'll Learn
- Why databases — structured storage that SQL can query efficiently
- SQLAlchemy ORM — Python classes that map to database tables
- Alembic — migration tool (think "git for your database schema")
- JSONB column — flexible storage for condition rules (no need to make 20 boolean columns)
- Foreign keys — how tables relate to each other
- Why you NEVER edit database tables manually in production

### Step 3A — Start PostgreSQL with Docker

Create `docker-compose.yml` in `govflow-ai/` root:

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    container_name: govflow_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: govflow_dev
      POSTGRES_USER: govflow
      POSTGRES_PASSWORD: govflow_secret
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start it:
```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\govflow-ai"
docker compose up -d
```

Verify it's running:
```bash
docker compose ps
```

### Step 3B — Create `.env` file

Create `backend/.env`:
```bash
DATABASE_URL=postgresql://govflow:govflow_secret@localhost:5432/govflow_dev
ENVIRONMENT=development
```

### Step 3C — Create `database.py`

Create `backend/app/database.py`:

```python
"""
Database connection setup.

LEARNING:
- engine = the database connection pool (create once at startup)
- SessionLocal = a factory that creates individual DB sessions
- get_db() = FastAPI dependency that gives each request its own session
  and closes it when the request is done (prevents connection leaks)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    environment: str = "development"
    
    class Config:
        env_file = ".env"


settings = Settings()

# Create the SQLAlchemy engine
# pool_pre_ping=True: test connections before using them (avoids stale connection errors)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.environment == "development",  # log SQL queries in dev
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for all our SQLAlchemy models
# LEARNING: All models inherit from Base — this is how SQLAlchemy knows about them
class Base(DeclarativeBase):
    pass


# FastAPI dependency — use this in every route that needs DB access
def get_db():
    """
    Yields a DB session and closes it after the request completes.
    
    LEARNING: This is a 'context manager as generator' pattern.
    `yield` gives the session to the route handler.
    The finally block guarantees cleanup even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 3D — Create SQLAlchemy Models

Create `backend/app/models/department.py`:
```python
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Department(Base):
    """
    Government department (e.g., DRP, DMT).
    LEARNING: Mapped[] and mapped_column() are SQLAlchemy 2.0 style.
    They're type-safe — your IDE knows the column types.
    """
    __tablename__ = "departments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    website_url: Mapped[str | None] = mapped_column(String(500))
    contact_phone: Mapped[str | None] = mapped_column(String(50))
    contact_email: Mapped[str | None] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationship — lets you do department.services to get all services
    services: Mapped[list["Service"]] = relationship(back_populates="department")
```

Create `backend/app/models/service.py`:
```python
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Service(Base):
    """
    A government service (e.g., NIC First Time, Driving Licence Renewal).
    """
    __tablename__ = "services"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    short_description: Mapped[str | None] = mapped_column(Text)
    # LEARNING: status is a string enum stored as varchar
    # 'draft' | 'in_review' | 'published' | 'archived'
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    department: Mapped["Department"] = relationship(back_populates="services")
    questions: Mapped[list["ServiceQuestion"]] = relationship(back_populates="service")
    workflow_steps: Mapped[list["WorkflowStep"]] = relationship(back_populates="service")
    required_documents: Mapped[list["RequiredDocument"]] = relationship(back_populates="service")
```

Create `backend/app/models/question.py`:
```python
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ServiceQuestion(Base):
    """
    A clarifying question asked before generating a workflow.
    
    LEARNING: condition_json uses JSONB — a PostgreSQL type that stores JSON
    but allows querying inside the JSON. We use it to store rules like:
    {"only_if_answer": {"service_subtype": "nic_lost"}}
    This tells the question engine to only show this question for lost NIC cases.
    """
    __tablename__ = "service_questions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    question_key: Mapped[str] = mapped_column(String(100), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    help_text: Mapped[str | None] = mapped_column(Text)
    # 'text' | 'single_choice' | 'boolean' | 'number' | 'date' | 'district'
    answer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    # JSON condition for when to show this question
    # None = always show; has value = show only when condition passes
    condition_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    
    service: Mapped["Service"] = relationship(back_populates="questions")
    options: Mapped[list["QuestionOption"]] = relationship(back_populates="question")


class QuestionOption(Base):
    """Answer options for single_choice questions."""
    __tablename__ = "question_options"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("service_questions.id"), nullable=False)
    option_key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    question: Mapped["ServiceQuestion"] = relationship(back_populates="options")
```

Create `backend/app/models/workflow_step.py`:
```python
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class WorkflowStep(Base):
    """
    One step in a service workflow.
    condition_json determines WHEN this step applies.
    """
    __tablename__ = "workflow_steps"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    step_key: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    estimated_time: Mapped[str | None] = mapped_column(String(200))
    # Example: {"service_subtype": ["nic_first_time", "nic_lost"]}
    # means this step only appears for first-time or lost NIC
    condition_json: Mapped[dict | None] = mapped_column(JSONB)
    source_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    
    service: Mapped["Service"] = relationship(back_populates="workflow_steps")
```

Create `backend/app/models/required_document.py`:
```python
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RequiredDocument(Base):
    __tablename__ = "required_documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    document_key: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    # 'required' | 'optional' | 'conditional'
    requirement_type: Mapped[str] = mapped_column(String(50), default="required")
    condition_json: Mapped[dict | None] = mapped_column(JSONB)
    source_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    
    service: Mapped["Service"] = relationship(back_populates="required_documents")
```

Create `backend/app/models/__init__.py`:
```python
# Import all models here so Alembic can discover them
from app.models.department import Department
from app.models.service import Service
from app.models.question import ServiceQuestion, QuestionOption
from app.models.workflow_step import WorkflowStep
from app.models.required_document import RequiredDocument

__all__ = [
    "Department", "Service", "ServiceQuestion", "QuestionOption",
    "WorkflowStep", "RequiredDocument"
]
```

### Step 3E — Set up Alembic

```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\govflow-ai\backend"
alembic init migrations
```

Edit `alembic.ini` — find the `sqlalchemy.url` line and change it:
```ini
sqlalchemy.url = postgresql://govflow:govflow_secret@localhost:5432/govflow_dev
```

Edit `migrations/env.py` — add model imports (around line 7):
```python
# Add these imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models import *  # noqa — imports all models so Alembic sees them

# ... rest of the file stays the same
# Change target_metadata line to:
target_metadata = Base.metadata
```

Generate the initial migration:
```bash
alembic revision --autogenerate -m "initial_schema"
```

Run the migration:
```bash
alembic upgrade head
```

Verify tables exist:
```bash
docker exec -it govflow_postgres psql -U govflow -d govflow_dev -c "\dt"
```

You should see: `departments`, `services`, `service_questions`, `question_options`, `workflow_steps`, `required_documents`

### 📝 Day 3 Practice Task
1. Add a `notes` column to `WorkflowStep` (Text, nullable)
2. Create a new migration: `alembic revision --autogenerate -m "add_step_notes"`
3. Run `alembic upgrade head` again
4. Verify the column was added

This is how schema changes work in real projects — you never edit the table directly.

---

## DAY 4 — Seed Data + FastAPI Endpoints

**Time estimate: 4–5 hours**  
**Goal: FastAPI running with real NIC + DL data queryable via API**

### 🧠 What You'll Learn
- Seed scripts — reproducible test data loading (critical for team work)
- FastAPI routing — how URL paths map to Python functions
- Pydantic schemas — separate from SQLAlchemy models (request/response shapes)
- Dependency injection — `Depends(get_db)` pattern
- Interactive API docs — FastAPI's killer feature (Swagger at `/docs`)

### Step 4A — Create seed JSON files

Create `backend/data/seed/departments.json`:
```json
[
  {
    "id": 1,
    "name": "Department for Registration of Persons",
    "slug": "drp",
    "description": "Responsible for issuing National Identity Cards to Sri Lankan citizens.",
    "website_url": "https://drp.gov.lk",
    "contact_phone": "0115226100",
    "contact_email": "info@drp.lk",
    "address": "Suhurupaya, Subuthipura Road, Battaramulla"
  },
  {
    "id": 2,
    "name": "Department of Motor Traffic",
    "slug": "dmt",
    "description": "Responsible for driving licences and vehicle registration in Sri Lanka.",
    "website_url": "https://eservices.motortraffic.gov.lk",
    "contact_phone": "071-4033300",
    "address": "341 Elvitigala Mawatha, Narahenpita, Colombo 05"
  }
]
```

Create `backend/data/seed/services.json`:
```json
[
  {
    "id": 1,
    "department_id": 1,
    "name": "NIC — First Time Application",
    "slug": "nic_first_time",
    "category": "Identity",
    "short_description": "Apply for your first National Identity Card. Available as normal service (up to 3 months) or one-day service.",
    "status": "published"
  },
  {
    "id": 2,
    "department_id": 1,
    "name": "NIC — Lost/Damaged Replacement",
    "slug": "nic_lost",
    "category": "Identity",
    "short_description": "Replace a lost, stolen, or damaged National Identity Card.",
    "status": "published"
  },
  {
    "id": 3,
    "department_id": 2,
    "name": "Driving Licence — New Application",
    "slug": "dl_new",
    "category": "Transport",
    "short_description": "Apply for your first driving licence. Requires a learner permit held for at least 3 months.",
    "status": "published"
  },
  {
    "id": 4,
    "department_id": 2,
    "name": "Driving Licence — Renewal",
    "slug": "dl_renewal",
    "category": "Transport",
    "short_description": "Renew your existing driving licence. Can be renewed 3 months before expiry.",
    "status": "published"
  }
]
```

Create `backend/data/seed/nic_questions.json`:
```json
[
  {
    "service_slug": "nic_first_time",
    "question_key": "is_one_day_service",
    "question_text": "Do you want one-day service (card ready in ~3 hours)?",
    "help_text": "One-day service is available at the DRP head office in Battaramulla. Normal service takes up to 3 months but can be done at any regional office.",
    "answer_type": "boolean",
    "is_required": true,
    "display_order": 1,
    "condition_json": null
  },
  {
    "service_slug": "nic_first_time",
    "question_key": "applicant_district",
    "question_text": "Which district are you from?",
    "help_text": "This determines which regional DRP office handles your application.",
    "answer_type": "district",
    "is_required": true,
    "display_order": 2,
    "condition_json": null
  },
  {
    "service_slug": "nic_first_time",
    "question_key": "applicant_age",
    "question_text": "What is your age?",
    "help_text": "You must be at least 16 years old to apply for an NIC.",
    "answer_type": "number",
    "is_required": true,
    "display_order": 3,
    "condition_json": null
  },
  {
    "service_slug": "nic_lost",
    "question_key": "has_police_report",
    "question_text": "Have you filed a police complaint for the lost NIC?",
    "help_text": "A police report is required when applying for a lost NIC replacement.",
    "answer_type": "boolean",
    "is_required": true,
    "display_order": 1,
    "condition_json": null
  },
  {
    "service_slug": "nic_lost",
    "question_key": "has_old_nic_copy",
    "question_text": "Do you have a photocopy of your old NIC?",
    "help_text": "If available, a copy of the lost NIC speeds up the replacement process.",
    "answer_type": "boolean",
    "is_required": false,
    "display_order": 2,
    "condition_json": null
  }
]
```

### Step 4B — Create the seed script

Create `backend/scripts/seed_db.py`:

```python
"""
Database seeding script.

LEARNING: Seed scripts serve two purposes:
1. Give you realistic data to test with during development
2. Make your database reproducible — any developer can run this and get the same data

Run with: python -m scripts.seed_db
Run with --reset to clear existing data first: python -m scripts.seed_db --reset
"""

import json
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Department, Service, ServiceQuestion, WorkflowStep

DATA_DIR = Path(__file__).parent.parent / "data" / "seed"


def load_json(filename: str) -> list:
    path = DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed_departments(db: Session):
    print("  Seeding departments...")
    for dept_data in load_json("departments.json"):
        existing = db.query(Department).filter(Department.slug == dept_data["slug"]).first()
        if not existing:
            dept = Department(**dept_data)
            db.add(dept)
    db.commit()
    print(f"    ✓ Departments: {db.query(Department).count()}")


def seed_services(db: Session):
    print("  Seeding services...")
    for svc_data in load_json("services.json"):
        existing = db.query(Service).filter(Service.slug == svc_data["slug"]).first()
        if not existing:
            svc = Service(**svc_data)
            db.add(svc)
    db.commit()
    print(f"    ✓ Services: {db.query(Service).count()}")


def seed_questions(db: Session):
    print("  Seeding questions...")
    for q_data in load_json("nic_questions.json"):
        service_slug = q_data.pop("service_slug")
        service = db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            print(f"    ⚠ Service not found: {service_slug}")
            continue
        
        existing = db.query(ServiceQuestion).filter(
            ServiceQuestion.service_id == service.id,
            ServiceQuestion.question_key == q_data["question_key"]
        ).first()
        
        if not existing:
            q = ServiceQuestion(service_id=service.id, **q_data)
            db.add(q)
    
    db.commit()
    print(f"    ✓ Questions: {db.query(ServiceQuestion).count()}")


def run(reset: bool = False):
    print("🌱 Seeding database...")
    
    if reset:
        print("  ⚠ Resetting data...")
        # LEARNING: Delete in reverse FK order to avoid constraint violations
        with SessionLocal() as db:
            db.query(ServiceQuestion).delete()
            db.query(WorkflowStep).delete()
            db.query(Service).delete()
            db.query(Department).delete()
            db.commit()
    
    with SessionLocal() as db:
        seed_departments(db)
        seed_services(db)
        seed_questions(db)
    
    print("✅ Seeding complete!")


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    run(reset=reset)
```

Run it:
```bash
python -m scripts.seed_db
```

### Step 4C — Build the FastAPI app

Create `backend/app/main.py`:
```python
"""
GovFlow AI — FastAPI Application

LEARNING: FastAPI automatically generates interactive docs at /docs (Swagger UI)
and /redoc. You can test every endpoint from the browser — no Postman needed.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import services

app = FastAPI(
    title="GovFlow AI API",
    description="Backend API for GovFlow AI — Sri Lankan citizen service guidance platform",
    version="0.1.0",
)

# CORS — allows the Next.js frontend (on a different port) to call this API
# LEARNING: Browsers block cross-origin requests by default for security.
# CORS middleware adds headers to allow our frontend to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(services.router, prefix="/api/v1", tags=["Services"])


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "GovFlow AI API"}
```

Create `backend/app/schemas/service.py`:
```python
from pydantic import BaseModel


class DepartmentResponse(BaseModel):
    id: int
    name: str
    slug: str
    website_url: str | None
    contact_phone: str | None

    model_config = {"from_attributes": True}


class ServiceResponse(BaseModel):
    id: int
    name: str
    slug: str
    category: str | None
    short_description: str | None
    status: str
    department: DepartmentResponse

    model_config = {"from_attributes": True}


class ServiceListResponse(BaseModel):
    services: list[ServiceResponse]
    total: int
```

Create `backend/app/routers/services.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, ServiceQuestion
from app.schemas.service import ServiceResponse, ServiceListResponse

router = APIRouter()


@router.get("/services", response_model=ServiceListResponse)
def list_services(
    status: str = "published",  # query parameter: /services?status=draft
    db: Session = Depends(get_db)
):
    """
    List all services.
    LEARNING: Depends(get_db) injects a DB session automatically.
    FastAPI handles creation and cleanup — you just use it.
    """
    services = db.query(Service).filter(Service.status == status).all()
    return ServiceListResponse(services=services, total=len(services))


@router.get("/services/{slug}", response_model=ServiceResponse)
def get_service(slug: str, db: Session = Depends(get_db)):
    """Get a single service by its slug."""
    service = db.query(Service).filter(Service.slug == slug).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{slug}' not found")
    return service


@router.get("/services/{slug}/questions")
def get_service_questions(slug: str, db: Session = Depends(get_db)):
    """
    Get all questions for a service.
    LEARNING: We return raw dict here (no Pydantic schema yet).
    We'll add schemas as we build more.
    """
    service = db.query(Service).filter(Service.slug == slug).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{slug}' not found")
    
    questions = (
        db.query(ServiceQuestion)
        .filter(ServiceQuestion.service_id == service.id)
        .order_by(ServiceQuestion.display_order)
        .all()
    )
    
    return {
        "service_slug": slug,
        "questions": [
            {
                "id": q.id,
                "key": q.question_key,
                "text": q.question_text,
                "help_text": q.help_text,
                "answer_type": q.answer_type,
                "is_required": q.is_required,
                "condition": q.condition_json,
            }
            for q in questions
        ]
    }
```

### Step 4D — Run FastAPI

```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\govflow-ai\backend"
uvicorn app.main:app --reload --port 8000
```

Open browser: **http://localhost:8000/docs**

Test these URLs:
- `GET /health` → `{"status": "ok"}`
- `GET /api/v1/services` → list of services
- `GET /api/v1/services/nic_first_time` → NIC service detail
- `GET /api/v1/services/nic_first_time/questions` → questions for NIC

### 📝 Day 4 Practice Task
1. Add a new endpoint: `GET /api/v1/departments` that returns all departments
2. Add a `GET /api/v1/departments/{slug}` endpoint
3. Test both in the Swagger UI at `/docs`

---

## DAY 5 — Question Engine + Workflow Engine (Rule-Based)

**Time estimate: 4–5 hours**  
**Goal: Deterministic engines that produce different outputs for different user answers, with passing tests**

### 🧠 What You'll Learn
- The core principle: AI decides conversation, rules decide procedure
- Condition evaluation — a mini rule interpreter in Python
- Unit testing with `pytest` — how to test without calling real APIs
- Why deterministic systems beat AI for legal/factual outputs
- The `Depends()` injection pattern extended to engines

### Step 5A — Build the Question Engine

Create `backend/app/engines/question_engine.py`:
```python
"""
Question Engine — Deterministic question selection and ordering.

LEARNING: This engine is FULLY deterministic. No AI involved.
Given a service_id and current user answers, it returns the next question to ask.

Why deterministic?
- Government questions are fixed by law/procedure, not guessable
- You can unit test it reliably (same input = same output, always)
- Admins can read and verify the logic
- If OpenAI is down, this still works
"""

from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models import Service, ServiceQuestion, QuestionOption


@dataclass
class Question:
    """Represents a single question to be asked."""
    id: int
    key: str
    text: str
    help_text: str | None
    answer_type: str
    is_required: bool
    options: list[dict]      # for single_choice questions
    condition: dict | None


@dataclass 
class QuestionResult:
    """Result returned by the engine."""
    next_question: Question | None   # None means no more questions
    questions_remaining: int
    total_questions: int


class QuestionEngine:
    """
    Loads service questions from DB and determines which to ask next
    based on the user's current answers.
    
    CONDITION EVALUATION:
    A condition_json like {"only_if_answer": {"has_police_report": true}}
    means: only show this question if the user answered has_police_report = true
    
    condition_json = null means: always show this question
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_next_question(
        self,
        service_slug: str,
        current_answers: dict
    ) -> QuestionResult:
        """
        Given a service and current answers, return the next unanswered question.
        
        Args:
            service_slug: e.g. "nic_first_time"
            current_answers: dict of {question_key: answer_value}
        
        Returns:
            QuestionResult with next_question or None if done
        """
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            raise ValueError(f"Service not found: {service_slug}")
        
        # Load all questions for this service, ordered
        all_questions = (
            self.db.query(ServiceQuestion)
            .filter(ServiceQuestion.service_id == service.id)
            .order_by(ServiceQuestion.display_order)
            .all()
        )
        
        # Filter: only questions whose conditions pass
        applicable_questions = [
            q for q in all_questions
            if self._condition_passes(q.condition_json, current_answers)
        ]
        
        total = len(applicable_questions)
        
        # Find first unanswered question
        for q in applicable_questions:
            if q.question_key not in current_answers:
                # Load options for choice questions
                options = []
                if q.answer_type == "single_choice":
                    options = [
                        {"key": opt.option_key, "label": opt.label}
                        for opt in sorted(q.options, key=lambda o: o.display_order)
                    ]
                
                return QuestionResult(
                    next_question=Question(
                        id=q.id,
                        key=q.question_key,
                        text=q.question_text,
                        help_text=q.help_text,
                        answer_type=q.answer_type,
                        is_required=q.is_required,
                        options=options,
                        condition=q.condition_json,
                    ),
                    questions_remaining=sum(
                        1 for qq in applicable_questions
                        if qq.question_key not in current_answers
                    ),
                    total_questions=total
                )
        
        # All questions answered
        return QuestionResult(
            next_question=None,
            questions_remaining=0,
            total_questions=total
        )
    
    def _condition_passes(self, condition: dict | None, answers: dict) -> bool:
        """
        Evaluate whether a question's condition is satisfied.
        
        CONDITION FORMAT:
        null → always show
        {"only_if_answer": {"key": value}} → show only if answer[key] == value
        {"only_if_answered": "key"} → show only if key has any answer
        
        LEARNING: This is a tiny rule interpreter. As conditions get more complex,
        you'd extend this method. But keep it simple and readable — this is
        the core of your rule engine.
        """
        if condition is None:
            return True
        
        # Condition: show only if a specific answer was given
        if "only_if_answer" in condition:
            required_answers = condition["only_if_answer"]
            for key, expected_value in required_answers.items():
                actual_value = answers.get(key)
                if actual_value != expected_value:
                    return False
        
        # Condition: show only if a key has any value (was previously answered)
        if "only_if_answered" in condition:
            required_key = condition["only_if_answered"]
            if required_key not in answers:
                return False
        
        return True
    
    def validate_answer(self, question_key: str, answer_value, service_slug: str) -> tuple[bool, str | None]:
        """
        Validate a user's answer.
        Returns (is_valid, error_message)
        """
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        question = (
            self.db.query(ServiceQuestion)
            .filter(
                ServiceQuestion.service_id == service.id,
                ServiceQuestion.question_key == question_key
            )
            .first()
        )
        
        if not question:
            return False, f"Question '{question_key}' not found"
        
        if question.answer_type == "boolean":
            if not isinstance(answer_value, bool):
                return False, "Answer must be true or false"
        
        if question.answer_type == "number":
            try:
                val = int(answer_value)
                if val < 0 or val > 150:
                    return False, "Please enter a valid age"
            except (ValueError, TypeError):
                return False, "Answer must be a number"
        
        if question.is_required and (answer_value is None or answer_value == ""):
            return False, "This question is required"
        
        return True, None
```

### Step 5B — Build the Workflow Engine

Create `backend/app/engines/workflow_engine.py`:
```python
"""
Workflow Engine — Generates personalized step lists from user answers.

LEARNING: This is the heart of GovFlow AI's accuracy guarantee.
Steps are stored in the database. This engine decides which steps
APPLY to this specific user based on their answers.

No AI involved. Pure rule evaluation. Fully testable.
"""

from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from app.models import Service, WorkflowStep, RequiredDocument


@dataclass
class WorkflowStepResult:
    id: int
    step_key: str
    title: str
    description: str | None
    order: int
    estimated_time: str | None
    source_url: str | None


@dataclass
class DocumentResult:
    id: int
    document_key: str
    name: str
    description: str | None
    requirement_type: str  # 'required' | 'optional' | 'conditional'
    condition_note: str | None  # human-readable explanation


@dataclass
class GeneratedWorkflow:
    service_name: str
    service_slug: str
    steps: list[WorkflowStepResult]
    required_documents: list[DocumentResult]
    total_steps: int
    answers_used: dict


class WorkflowEngine:
    """
    Generates a personalized workflow based on service + user answers.
    
    HOW IT WORKS:
    1. Load all workflow steps for the service
    2. For each step, evaluate condition_json against user answers
    3. Include steps where condition passes
    4. Same for required documents
    5. Return ordered, filtered list
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate(self, service_slug: str, answers: dict) -> GeneratedWorkflow:
        """
        Generate a personalized workflow.
        
        Args:
            service_slug: e.g. "nic_first_time"
            answers: user's answers from QuestionEngine
        
        Returns:
            GeneratedWorkflow with applicable steps and documents
        """
        service = self.db.query(Service).filter(Service.slug == service_slug).first()
        if not service:
            raise ValueError(f"Service not found: {service_slug}")
        
        # Get all steps
        all_steps = (
            self.db.query(WorkflowStep)
            .filter(WorkflowStep.service_id == service.id)
            .order_by(WorkflowStep.display_order)
            .all()
        )
        
        # Filter applicable steps
        applicable_steps = [
            WorkflowStepResult(
                id=step.id,
                step_key=step.step_key,
                title=step.title,
                description=step.description,
                order=step.display_order,
                estimated_time=step.estimated_time,
                source_url=step.source_url,
            )
            for step in all_steps
            if self._condition_passes(step.condition_json, answers)
        ]
        
        # Get all required documents
        all_docs = (
            self.db.query(RequiredDocument)
            .filter(RequiredDocument.service_id == service.id)
            .all()
        )
        
        applicable_docs = [
            DocumentResult(
                id=doc.id,
                document_key=doc.document_key,
                name=doc.name,
                description=doc.description,
                requirement_type=doc.requirement_type,
                condition_note=self._get_condition_note(doc.condition_json, answers),
            )
            for doc in all_docs
            if self._doc_applies(doc.condition_json, answers)
        ]
        
        return GeneratedWorkflow(
            service_name=service.name,
            service_slug=service_slug,
            steps=applicable_steps,
            required_documents=applicable_docs,
            total_steps=len(applicable_steps),
            answers_used=answers,
        )
    
    def _condition_passes(self, condition: dict | None, answers: dict) -> bool:
        """
        LEARNING: Same condition evaluator pattern as QuestionEngine.
        Could be shared — but we keep it separate so each engine can
        evolve its conditions independently.
        """
        if condition is None:
            return True
        
        # Include if answer matches
        if "include_if" in condition:
            required = condition["include_if"]
            for key, expected in required.items():
                if isinstance(expected, list):
                    if answers.get(key) not in expected:
                        return False
                else:
                    if answers.get(key) != expected:
                        return False
        
        # Exclude if answer matches
        if "exclude_if" in condition:
            excluded = condition["exclude_if"]
            for key, bad_value in excluded.items():
                if answers.get(key) == bad_value:
                    return False
        
        return True
    
    def _doc_applies(self, condition: dict | None, answers: dict) -> bool:
        """Determine if a required document applies to this user's situation."""
        if condition is None:
            return True
        
        if "include_if" in condition:
            required = condition["include_if"]
            for key, expected in required.items():
                if answers.get(key) != expected:
                    return False
        
        return True
    
    def _get_condition_note(self, condition: dict | None, answers: dict) -> str | None:
        """Return a human-readable note about when this document is needed."""
        if condition is None:
            return None
        if "note" in condition:
            return condition["note"]
        return None
```

### Step 5C — Write tests

Create `backend/tests/test_question_engine.py`:
```python
"""
Tests for QuestionEngine.

LEARNING: We test WITHOUT making real database calls by using pytest fixtures
that set up a test database. Every test is isolated — changes in one test
don't affect another.

Key testing principle for AI projects:
- Test the DETERMINISTIC parts exhaustively (engines)
- Test AI parts with mocks (we'll add those later)
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Department, Service, ServiceQuestion
from app.engines.question_engine import QuestionEngine

# ── Test database (in-memory SQLite — no PostgreSQL needed for tests) ────────
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    """Creates a fresh in-memory SQLite database for each test."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    # Seed test data
    dept = Department(id=1, name="Test Dept", slug="test_dept")
    session.add(dept)
    
    service = Service(id=1, department_id=1, name="NIC First Time", slug="nic_first_time", status="published")
    session.add(service)
    session.flush()
    
    # Q1: Always shown
    q1 = ServiceQuestion(
        service_id=1, question_key="applicant_age", question_text="What is your age?",
        answer_type="number", is_required=True, display_order=1, condition_json=None
    )
    # Q2: Only shown if user is under 16 (just for testing conditional logic)
    q2 = ServiceQuestion(
        service_id=1, question_key="guardian_consent", question_text="Do you have guardian consent?",
        answer_type="boolean", is_required=True, display_order=2,
        condition_json={"only_if_answer": {"applicant_age": "15"}}
    )
    # Q3: Always shown
    q3 = ServiceQuestion(
        service_id=1, question_key="is_one_day_service", question_text="Do you want one-day service?",
        answer_type="boolean", is_required=True, display_order=3, condition_json=None
    )
    session.add_all([q1, q2, q3])
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_first_question_returned_with_no_answers(db):
    """With no answers, first question should be returned."""
    engine = QuestionEngine(db)
    result = engine.get_next_question("nic_first_time", {})
    
    assert result.next_question is not None
    assert result.next_question.key == "applicant_age"


def test_second_question_after_first_answered(db):
    """After answering q1, get q3 (q2 is conditional and condition not met)."""
    engine = QuestionEngine(db)
    answers = {"applicant_age": "25"}  # age 25, so guardian_consent condition won't pass
    result = engine.get_next_question("nic_first_time", answers)
    
    assert result.next_question is not None
    # q2 is skipped because applicant_age != "15"
    assert result.next_question.key == "is_one_day_service"


def test_conditional_question_shown_when_condition_met(db):
    """Guardian consent question appears when age is 15."""
    engine = QuestionEngine(db)
    answers = {"applicant_age": "15"}
    result = engine.get_next_question("nic_first_time", answers)
    
    assert result.next_question is not None
    assert result.next_question.key == "guardian_consent"


def test_no_question_when_all_answered(db):
    """When all questions are answered, next_question is None."""
    engine = QuestionEngine(db)
    answers = {
        "applicant_age": "25",
        "is_one_day_service": True,
    }
    result = engine.get_next_question("nic_first_time", answers)
    
    assert result.next_question is None
    assert result.questions_remaining == 0
```

Run tests:
```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\govflow-ai\backend"
pytest tests/ -v
```

Expected:
```
PASSED tests/test_question_engine.py::test_first_question_returned_with_no_answers
PASSED tests/test_question_engine.py::test_second_question_after_first_answered
PASSED tests/test_question_engine.py::test_conditional_question_shown_when_condition_met
PASSED tests/test_question_engine.py::test_no_question_when_all_answered
```

### 📝 Day 5 Practice Task
1. Add a test for `validate_answer()` — test that age `"abc"` fails validation
2. Write 2 WorkflowEngine tests: one where only 3 steps apply, one where all 5 apply
3. Answer this question in your notes: "Why can't we just use GPT to figure out which steps to show?"

---

## Week 1 End-State Checklist

By the end of Day 5, you should have:

- `[ ]` Virtual environment set up, all packages installed
- `[ ]` NIC scraper running → `data/nic_raw.json` created
- `[ ]` DL manual data → `data/dl_manual.json` created  
- `[ ]` PostgreSQL running in Docker
- `[ ]` All SQLAlchemy models created
- `[ ]` Alembic migration ran → all tables exist in DB
- `[ ]` Database seeded with 2 departments + 4 services + questions
- `[ ]` FastAPI running at localhost:8000
- `[ ]` `/api/v1/services` returns real data
- `[ ]` QuestionEngine returns different next-questions based on answers
- `[ ]` WorkflowEngine generates different step lists for different answers
- `[ ]` All pytest tests passing

---

## Daily Schedule Suggestion

| Day | Morning (2h) | Afternoon (2h) |
|-----|-------------|---------------|
| 1 | Set up project, install deps | Build NIC scraper, run it |
| 2 | Read NIC JSON output | Build DL extractor, review output |
| 3 | Set up Docker + PostgreSQL | Build models, run migrations |
| 4 | Build seed scripts + run seeds | Build FastAPI routes, test in Swagger |
| 5 | Build QuestionEngine | Build WorkflowEngine + write tests |

---

## What Comes Next (Week 2 Preview)

After Week 1 you have:
- **Real data** in a real database
- **Real API** serving that data
- **Real engines** that produce correct, deterministic outputs

Week 2 adds:
- **LangGraph** — connects these engines into a conversation state machine
- **OpenAI API** — understands "I want to apply for NIC" and maps it to `nic_first_time`
- **Next.js chat UI** — the browser interface

The engines you built in Week 1 are called by LangGraph in Week 2 — they don't change. That's the key architectural insight: the AI layer sits ON TOP of, not inside, your rule engines.
