# GovFlow AI — MVP Build & Learn Plan
### Focus: NIC Application + Driving Licence | Duration: ~4 Weeks

---

## 🔍 Part 1: Scraping Analysis — Are They Scrapable?

### 1.1 NIC — Department for Registration of Persons (DRP)

**Official URL:** https://drp.gov.lk/en/normal.php  
**Scrapability: ✅ YES — Static HTML, no auth, no bot protection**

| Signal | Finding |
|--------|---------|
| Page type | Static PHP-rendered HTML |
| JavaScript rendering needed? | No — content is in raw HTML |
| Anti-bot / CAPTCHA | None detected |
| robots.txt | Not blocking scraping of info pages |
| Login required | No |
| Terms of use block | No explicit machine-read restriction found |
| Content format | Accordion-style FAQ, tab-based procedure pages |
| Available info | Processing times, steps, documents, fees (Rs.500 for letters), sub-services |

**Sub-pages to scrape:**
- `drp.gov.lk/en/normal.php` — NIC obtaining procedures (first-time, lost, amendment, dual citizen, one-day)
- `drp.gov.lk/en/faq.php` — FAQs (processing time = 3 months normal, 3 hours one-day)
- `drp.gov.lk/en/downloads.php` — Forms (Application for NIC)

**Scraping method:** `requests` + `BeautifulSoup` (Python). Very straightforward.  
**Token estimate for embedding:** ~8,000–12,000 tokens for all NIC pages combined (cheap).  
**LLM extraction cost:** ~$0.01–0.05 per extraction run with GPT-4o-mini.

---

### 1.2 Driving Licence — Department of Motor Traffic (DMT)

**⚠️ IMPORTANT DOMAIN ISSUE: `dmt.gov.lk` has been domain-hijacked by an Indonesian gambling site (PANEN77). This is NOT the real DMT site.**

**Real official sources:**
- **e-Services portal:** https://eservices.motortraffic.gov.lk (appointment booking — login-required dynamic app)
- **GOV.LK listing:** https://www.gov.lk/government/eservices (links to DMT)
- **Form downloads:** Available on the real DMT download page

**Scrapability: ⚠️ PARTIAL — Mixed situation**

| Signal | Finding |
|--------|---------|
| eservices.motortraffic.gov.lk | Login required — not directly scrapable for procedure data |
| dmt.gov.lk | HIJACKED — do NOT use |
| gov.lk driving license pages | Static HTML — scrapable |
| Official PDF forms | Downloadable — extractable with PyPDF2 |
| Official WhatsApp: 071-4033300 | Contact-only |

**Strategy for Driving Licence data:**
1. Use `gov.lk` service listing pages for general info
2. Download and parse PDF application forms directly
3. Manually curate the core workflow (first-time license, renewal) from cross-referenced sources
4. Use `eservices.motortraffic.gov.lk` for linking (appointment URL), not for scraping data

**Token estimate:** ~6,000–10,000 tokens for all DL pages + forms.

---

### 1.3 Scraping Strategy Decision

> **Recommendation: Hybrid approach — scrape what you can, manually curate what you can't.**

This is actually BETTER for learning. You'll practice:
- Automated scraping (DRP pages — easy)
- PDF extraction (DMT forms)
- Manual curation with admin review workflow (core architecture skill)
- Change detection / staleness checks

**Token budget for entire MVP knowledge base (both services):**
- Raw text extraction: ~20,000–30,000 tokens total
- After chunking for RAG (500-token chunks): ~40–60 chunks
- Embedding cost (text-embedding-3-small): < $0.001 total
- Per-query RAG retrieval: ~2,000–4,000 tokens per chat turn ≈ $0.002–0.006 per message

**Monthly token budget at 100 active users/day:** ~$15–40/month (very affordable for MVP)

---

## 🏗️ Part 2: What We're Building (MVP Scope)

### Two Use Cases Only:
1. **NIC — First-time & Lost NIC application** (Department for Registration of Persons)
2. **Driving Licence — New application & Renewal** (Department of Motor Traffic)

### MVP Feature Set:
- Chat interface where user types their goal
- AI matches the service (NIC or DL)
- Asks 3–5 clarifying questions
- Generates a personalized step-by-step workflow
- Shows required documents checklist
- Shows fees and processing times (from official sources)
- Lets user mark steps as done (progress tracker)
- Every answer cites the source URL
- Admin can view/edit service data

---

## 📚 Part 3: What You'll Learn (Mentorship Curriculum)

Each week covers build work + learning concepts. You learn BY building, not separately.

| Concept | Where You Learn It |
|---------|-------------------|
| Web scraping (BeautifulSoup, requests) | Week 1 — Building the data ingestion script |
| FastAPI + Pydantic | Week 1 — Building the API foundation |
| PostgreSQL + SQLAlchemy | Week 1 — Designing and creating the database |
| LangGraph state machines | Week 2 — Building the conversation orchestrator |
| OpenAI API (structured outputs) | Week 2 — Intent detection + service matching |
| RAG (chunking, embeddings, pgvector) | Week 3 — Building the knowledge base retrieval |
| React + Next.js | Week 2–4 — Building the chat UI |
| Prompt engineering | Week 2–4 — Writing and tuning system prompts |
| Token optimization | Week 2–4 — Monitoring and reducing cost |
| Admin CRUD design | Week 3–4 — Building the admin panel |

---

## 🗓️ Part 4: Week-by-Week Plan

---

### WEEK 1: Data, Database & Backend Foundation

**Theme: "Get the data. Build the bones."**  
**Goal: Have real NIC and DL data in a database by end of week.**

---

#### Day 1 — Project Setup + Scraper for NIC

**What you build:**
- Python project with `uv` or `pip`
- Scraper for `drp.gov.lk` (NIC pages)
- Saves raw HTML + extracted text to JSON

**What you learn:**
- `requests` library — making HTTP GET requests
- `BeautifulSoup` — parsing HTML trees, finding elements by tag/class/id
- Why we save raw HTML first (reproducibility — if site changes, you have backup)
- `robots.txt` ethics and when scraping is acceptable

**Concepts explained:**
```
requests.get(url) → HTTP response object
response.text → raw HTML string
BeautifulSoup(html, 'html.parser') → parse tree
soup.find('div', {'class': 'faq-list'}) → target element
element.get_text() → clean text
```

**Deliverable:** `scraper/nic_scraper.py` that outputs `data/nic_raw.json`

**Practice task:** After building the NIC scraper, extend it to also scrape `drp.gov.lk/en/faq.php` and merge the FAQs into the same output.

---

#### Day 2 — PDF Extraction + DL Data

**What you build:**
- PDF downloader for DMT forms (using `requests`)
- PDF text extractor using `pdfplumber` or `PyPDF2`
- Manual JSON file for DL procedure (you type the workflow yourself from cross-referenced sources)

**What you learn:**
- PDF parsing — why it's messy (non-text PDFs, scanned images vs digital PDFs)
- When to use manual curation vs automation (trust & accuracy tradeoffs)
- JSON as a data interchange format

**Deliverable:** `data/dl_manual.json` with structured DL workflow + `data/dl_form_text.txt`

---

#### Day 3 — Database Design + SQLAlchemy Models

**What you build:**
- PostgreSQL setup (Docker or local)
- SQLAlchemy models for: `departments`, `services`, `service_questions`, `workflow_steps`, `required_documents`, `source_documents`
- Alembic migration to create tables

**What you learn:**
- Relational databases — why tables, why foreign keys
- SQLAlchemy ORM — Python classes → SQL tables
- Alembic — database migrations (never edit schema manually in production)
- `condition_json` pattern — flexible rule storage in a JSONB column

**Key concept: Why condition_json?**
```
# Instead of 20 boolean columns:
condition_json = {
  "applicant_age_min": 16,
  "service_type": ["lost", "first_time"],
  "not_overseas": true
}
# This is evaluated at runtime by your rule engine
```

**Deliverable:** Running PostgreSQL with all tables created via migration

---

#### Day 4 — Seed Data + FastAPI Setup

**What you build:**
- Seed scripts that load NIC and DL data from JSON files into PostgreSQL
- FastAPI app with basic health check endpoint
- Pydantic schemas for service and question response types

**What you learn:**
- FastAPI — why it's the best Python API framework for learning (auto docs, type hints)
- Pydantic — data validation and serialization
- Seed scripts — why you need reproducible test data
- API design — REST vs purpose-built endpoints

**Key FastAPI concept:**
```python
@app.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
```

**Deliverable:** FastAPI running at localhost:8000 with `/services` and `/services/{id}` endpoints, auto Swagger docs at `/docs`

---

#### Day 5 — Question Engine + Workflow Engine (Rule-Based)

**What you build:**
- `QuestionEngine` class — loads questions for a service, evaluates `condition_json` to skip irrelevant questions
- `WorkflowEngine` class — takes user answers, evaluates step conditions, returns ordered list of applicable steps
- Unit tests for both engines

**What you learn:**
- Why deterministic engines beat AI for legal/official workflows
- Condition evaluation — writing a simple JSON rule interpreter
- Unit testing with `pytest`
- The separation principle: AI decides conversation flow, rules decide procedure output

**Condition evaluator example:**
```python
def evaluate_condition(condition: dict, answers: dict) -> bool:
    if "applicant_age_min" in condition:
        if answers.get("age", 0) < condition["applicant_age_min"]:
            return False
    if "service_type" in condition:
        if answers.get("service_type") not in condition["service_type"]:
            return False
    return True
```

**Deliverable:** Both engines tested with NIC use case (first-time vs lost NIC produces different step lists)

---

### WEEK 2: LangGraph + OpenAI + Chat Interface

**Theme: "Make it talk."**  
**Goal: Working chat that detects intent, asks questions, and returns a workflow.**

---

#### Day 6 — LangGraph Introduction + State Design

**What you build:**
- LangGraph graph with nodes: `detect_intent → match_service → ask_next_question → store_answer → generate_workflow → end`
- Conversation state schema using TypedDict
- Run a simple test conversation in Python (no UI yet)

**What you learn:**
- LangGraph fundamentals — why a graph beats a loop for conversations
- State machines — what they are and why they're perfect for multi-turn AI
- TypedDict for state typing in Python
- The difference between a LangGraph node (a function) and an edge (a condition)

**LangGraph state design:**
```python
class ConversationState(TypedDict):
    messages: list[dict]          # raw chat history
    detected_service: str | None  # "nic_first_time", "dl_renewal", etc.
    current_question_index: int
    answers: dict[str, Any]
    workflow_steps: list[dict]
    status: str                   # "intent_detection", "questioning", "workflow_ready"
```

**Key insight:** LangGraph replaces a messy `if-elif` chain with explicit, inspectable state transitions.

**Deliverable:** Working LangGraph graph that can route a test message through all nodes

---

#### Day 7 — OpenAI Integration: Intent Detection + Service Matching

**What you build:**
- OpenAI call inside `detect_intent` node using structured outputs
- Service matching logic: classify user message into one of: `nic_first_time`, `nic_lost`, `dl_new`, `dl_renewal`, `unknown`
- Fallback: if confidence is low, ask clarifying question before matching

**What you learn:**
- OpenAI chat completions API
- Structured outputs with `response_format={"type": "json_object"}`
- System prompt engineering — how to constrain the model
- Confidence scoring — why "I don't know" is safer than a wrong guess
- Token counting with `tiktoken`

**System prompt strategy:**
```
You are a Sri Lankan government service classifier. 
Given a user message, classify it into one of these services: 
nic_first_time, nic_lost, dl_new, dl_renewal.

If you are confident (>90%), return the service_id.
If you are not confident, return "unclear" and a clarifying question.

NEVER guess. NEVER return a service not in the list.
Return JSON: {"service_id": string, "confidence": float, "clarifying_question": string | null}
```

**Token optimization lesson:**
- Short, specific system prompts cost less
- Structured output prevents model from rambling
- Cache service list in system prompt (not retrieved per-message)

**Deliverable:** Intent detector tested with 10+ different input phrases

---

#### Day 8 — Full Conversation Flow + Question Asking

**What you build:**
- Complete `ask_next_question` node — retrieves question from DB, formats it for chat
- `store_answer` node — validates user answer against expected type (boolean, choice, text)
- `check_required_answers` edge condition — determines when to move to workflow generation
- End-to-end test: text input → questions answered → workflow output (in terminal)

**What you learn:**
- Multi-turn conversation management
- Answer validation (why you can't trust raw user input)
- LangGraph edges as conditions (the routing logic)
- Streaming responses vs batch responses

**Deliverable:** Full conversation in terminal — type "I want to apply for NIC for first time" and get a complete workflow

---

#### Day 9 — Next.js Chat UI (Frontend)

**What you build:**
- Next.js project with TypeScript
- Chat UI component: message list, input box, send button
- API connection to FastAPI backend
- Message streaming (show AI typing)
- Basic styling (clean, not fancy yet)

**What you learn:**
- Next.js App Router — file-based routing
- `fetch` API and async/await for API calls
- React state management with `useState` and `useEffect`
- Streaming responses with `ReadableStream`
- TypeScript interfaces for message types

**Component structure:**
```
app/
  page.tsx           ← main chat page
  api/
    chat/
      route.ts       ← Next.js API route → calls FastAPI
components/
  ChatWindow.tsx     ← message list
  MessageBubble.tsx  ← individual message
  ChatInput.tsx      ← text input + send
```

**Deliverable:** Chat UI running in browser, connected to backend

---

#### Day 10 — Workflow Display + Document Checklist UI

**What you build:**
- Workflow display component — renders steps as a visual timeline
- Document checklist component — renders documents with checkbox for each
- Mark step as done (localStorage for now, no auth yet)
- Source citation display — "Source: drp.gov.lk — Last checked: 2026-08-01"

**What you learn:**
- Component design — breaking UI into small reusable pieces
- Local state vs server state
- UX principles for government services (clarity, not cleverness)
- Accessibility basics (labels, aria attributes)

**Deliverable:** Full flow — chat → questions → workflow with checkboxes

---

### WEEK 3: RAG Knowledge Base + Source Grounding

**Theme: "Ground everything in official sources."**  
**Goal: AI answers questions using real DRP/DMT content, not hallucinations.**

---

#### Day 11 — Text Chunking + Embedding Strategy

**What you build:**
- Text chunker: splits scraped content into ~500-token chunks
- Metadata tagger: each chunk tagged with `{service_id, source_url, section_title, retrieved_date}`
- Embedding generator: calls OpenAI `text-embedding-3-small` for each chunk
- Stores chunks + embeddings in PostgreSQL with `pgvector`

**What you learn:**
- Why chunking matters — too large = irrelevant context, too small = missing context
- Embedding vectors — what they are (numbers that represent meaning)
- pgvector — how to store and query embeddings in PostgreSQL
- Cosine similarity — how semantic search works

**Chunking strategy for government content:**
```python
# Strategy: chunk by section/accordion, not arbitrary character count
# NIC FAQ → each Q&A pair = one chunk
# NIC procedure steps → each step = one chunk
# This preserves semantic integrity
```

**Token cost example:**
```
NIC page: ~3,000 tokens → ~6 chunks
Embedding 6 chunks with text-embedding-3-small: 
$0.000020 per 1K tokens × 3 = $0.00006
Total for entire knowledge base: < $0.01
```

**Deliverable:** `chunks` table in PostgreSQL with vector column, all NIC + DL content embedded

---

#### Day 12 — Semantic Search + RAG Retrieval

**What you build:**
- `retrieve_context()` function — converts user question to embedding, queries pgvector for top 3 similar chunks
- `source_grounded_qa` node in LangGraph — user asks "what documents do I need?" → retrieves chunks → answers with citations
- Test: ask 10 different questions, verify answers come from real sources

**What you learn:**
- Vector similarity search (`<=>` operator in pgvector)
- RAG pattern — Retrieve → Augment → Generate
- Why RAG beats fine-tuning for factual Q&A
- Hallucination prevention — constraining model to only use retrieved context

**RAG prompt pattern:**
```
You are a helpful assistant for Sri Lankan government services.

Answer the user's question using ONLY the provided context below.
If the answer is not in the context, say "I don't have that information. Please check [official_url]."
Always cite the source URL at the end of your answer.

CONTEXT:
{retrieved_chunks}

USER QUESTION: {user_question}
```

**Deliverable:** Source-grounded Q&A working in chat — every factual answer has a citation

---

#### Day 13 — Source Staleness Monitoring

**What you build:**
- `check_source_freshness.py` script — re-fetches official pages, compares with stored content
- Difference detector — flags if content changed (using text diff or hash comparison)
- Adds `last_checked_at` and `content_changed` flags to `source_documents` table
- Can be run as a scheduled job (cron)

**What you learn:**
- Content hashing (MD5/SHA256 — detect changes cheaply)
- Why government websites change without notice
- Cron jobs / scheduled tasks
- The importance of "last checked" dates in AI applications

**Deliverable:** Script that re-checks all sources and reports changes

---

#### Day 14 — Admin Panel: Service Content Editor

**What you build:**
- Admin login page (simple hardcoded credentials for MVP)
- Service list view
- Service edit form: steps, questions, documents, fees
- Source document list with review status
- "Publish" action — marks service version as published

**What you learn:**
- Admin panel design patterns
- Form handling in React (React Hook Form + Zod validation)
- Optimistic UI updates
- Role-based access (admin vs citizen)

**Deliverable:** Admin can add a new workflow step for NIC from the browser

---

#### Day 15 — User Authentication + Saved Workflows

**What you build:**
- JWT-based auth (register, login, /me endpoint)
- Protected routes in Next.js (middleware)
- Save workflow to database (`user_workflows` table)
- Progress tracker: load saved workflow, persist step completion to server

**What you learn:**
- JWT — how tokens work, what's stored client-side vs server-side
- HTTP-only cookies vs localStorage (security tradeoff)
- Database associations (user_id FK relationships)
- Protected API endpoints with FastAPI `Depends()`

**Deliverable:** User can register, start a workflow, mark steps done, and resume on next visit

---

### WEEK 4: Polish, Feedback & Demo Prep

**Theme: "Make it real. Make it demoable."**  
**Goal: Working MVP you can show to anyone.**

---

#### Day 16 — Token Optimization & Cost Monitoring

**What you build:**
- Token usage logger — log tokens used per conversation turn
- Cost estimator — calculate $ cost per user session
- Prompt optimization — reduce system prompt size without losing quality
- Context window management — summarize old messages to avoid overflow

**What you learn:**
- `tiktoken` — counting tokens before sending to API
- Cost calculation: GPT-4o-mini input = $0.15/1M tokens, output = $0.60/1M tokens
- Context window management for long conversations
- Prompt compression techniques

**Token budget per user session:**
```
Intent detection:     ~500 tokens   → $0.00008
Question flow:        ~1,500 tokens → $0.00023
Workflow generation:  ~2,000 tokens → $0.00030
3 RAG Q&A turns:      ~6,000 tokens → $0.00090
Total per session:    ~10,000 tokens → ~$0.0015 per user
```

---

#### Day 17 — Feedback System + Error Handling

**What you build:**
- "Was this helpful?" thumbs up/down on each AI answer
- "Report incorrect information" button on workflow steps
- `user_feedback` table storage
- Error boundaries in React
- Proper HTTP error responses from FastAPI (not 500 for everything)

**What you learn:**
- Feedback loops in AI systems (why they're critical)
- Error handling in async Python
- React error boundaries
- HTTP status codes and when to use each

---

#### Day 18 — UI Polish + Mobile Responsiveness

**What you build:**
- Responsive layout for mobile screens
- Loading states and skeleton screens
- Progress bar for question flow ("Step 2 of 4")
- Dark mode support

**What you learn:**
- CSS Grid and Flexbox responsive patterns
- UX micro-animations (subtle, not distracting)
- Performance — why skeleton screens feel faster
- Accessibility: keyboard navigation, color contrast

---

#### Day 19 — Testing

**What you build:**
- Backend: pytest tests for QuestionEngine, WorkflowEngine, and API endpoints
- Frontend: basic smoke test with Playwright (navigate to chat, send message, get response)
- Integration test: full conversation flow in Python (no UI)

**What you learn:**
- pytest fixtures and parametrize
- Mocking OpenAI in tests (don't call real API in tests)
- Integration vs unit vs E2E testing
- Why testing AI systems is different (non-deterministic outputs)

---

#### Day 20 — Demo Prep + Documentation

**What you build:**
- README with setup instructions
- `.env.example` file
- Docker Compose file for local setup
- Demo script: two flows to show (NIC first-time, DL renewal)
- Deploy to free tier (Railway, Render, or Fly.io)

**What you learn:**
- Docker and Docker Compose basics
- Environment variables and secrets management
- Deployment pipeline
- How to present a technical project to non-technical stakeholders

---

## 🧠 Part 5: Concept Map (What You'll Know After This)

```
Web Scraping ──────────────────────────────────────────────────┐
  requests, BeautifulSoup, PDF parsing, staleness checks        │
                                                                 │
Database ─────────────────────────────────────────────────────┐ │
  PostgreSQL, SQLAlchemy ORM, Alembic, pgvector, JSONB         │ │
                                                               │ │
FastAPI ──────────────────────────────────────────────────────┤ ├──→ GovFlow AI MVP
  Pydantic, dependency injection, JWT auth, error handling     │ │
                                                               │ │
LangGraph ────────────────────────────────────────────────────┘ │
  State machines, nodes, edges, conversation memory             │
                                                                 │
OpenAI API ───────────────────────────────────────────────────┘
  Chat completions, structured outputs, embeddings, RAG,
  prompt engineering, token counting, cost optimization

Next.js + React
  App Router, TypeScript, hooks, streaming, responsive UI
```

---

## 📊 Part 6: Architecture Decision Log

### Why two use cases only?
- Depth > breadth for MVP learning
- NIC = simple, well-documented → perfect for learning the pattern
- DL = slightly more complex, has e-services portal → teaches data source challenges
- Together they cover every pattern you need for all future services

### Why manual curation + scraping hybrid?
- DRP site is fully scrapable — great for automation learning
- DMT e-services requires login — teaches "when not to scrape"
- Manual curation teaches admin review workflow — core to the architecture

### Why LangGraph before RAG?
- Conversation orchestration is the hard part
- RAG is easier once conversation state works
- You need to understand what the AI is doing before you optimize it

### Why deterministic rule engine alongside LLM?
- Government workflows MUST be correct
- LLMs hallucinate facts — rules don't
- This makes the system auditable and trustworthy
- If OpenAI goes down, the rule engine still works

---

## 🚨 Part 7: Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| DMT website still hijacked | Use `gov.lk` listing + manual curation + PDF forms |
| DRP changes their site structure | Save raw HTML locally; re-scraping is fast |
| OpenAI API costs too high | Use GPT-4o-mini (cheapest capable model); add token budget per session |
| NIC/DL rules change | `last_checked_at` flag + weekly re-scrape job |
| Overwhelmed by complexity | Follow day-by-day plan; don't skip ahead |
| LangGraph confusion | Start with 3 nodes only; add more after first loop works |

---

## ✅ Week 1 Completion Checklist

- [ ] Python project set up with virtual environment
- [ ] NIC scraper runs and outputs `nic_raw.json`
- [ ] DL manual JSON file created
- [ ] PostgreSQL running locally (Docker preferred)
- [ ] SQLAlchemy models and Alembic migration created
- [ ] Database seeded with NIC + DL data
- [ ] FastAPI running with `/services` endpoint
- [ ] QuestionEngine unit tests pass
- [ ] WorkflowEngine unit tests pass
- [ ] First-time NIC vs Lost NIC produces different step lists ✓

---

## 🔗 Official Source URLs (Both Use Cases)

### NIC
- Main procedures: https://drp.gov.lk/en/normal.php
- FAQs: https://drp.gov.lk/en/faq.php
- Downloads/Forms: https://drp.gov.lk/en/downloads.php
- Contact: 0115226100

### Driving Licence  
- e-Services (appointment): https://eservices.motortraffic.gov.lk
- GOV.LK listing: https://www.gov.lk/government/eservices
- DMT WhatsApp: 071-4033300
- ⚠️ Do NOT use dmt.gov.lk — domain is hijacked
