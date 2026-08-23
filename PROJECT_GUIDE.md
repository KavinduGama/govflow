# GovFlow AI — Project Status & Developer Guide

> **Last Updated:** August 16, 2026  
> **Status:** ✅ Backend Agentic Refactor Complete | ⚡ Frontend UI built 

---

## What Is This Project?

GovFlow AI is a **Sri Lankan government service guidance platform** powered by an autonomous AI chat assistant. Citizens describe what they need (e.g. "I want to get my first NIC") and the system:

1. **Dynamically manages conversation** using an OpenAI (GPT-5.5) Tool-Calling Agent.
2. **Determines Eligibility** by autonomously invoking the `get_eligibility_questions` tool and chatting with the user to collect answers.
3. **Generates a personalized workflow** by invoking the `generate_workflow_plan` tool once it has all the data it needs — retrieving the exact steps, documents, and locations for the user.

---

## Architecture Overview

```
┌─────────────────┐       HTTP/JSON        ┌──────────────────────────┐
│   Next.js App   │ ◄───────────────────►  │   FastAPI Backend        │
│   (port 3000)   │                         │   (port 8000)            │
│                 │                         │                          │
│  - Landing page │   POST /api/v1/chat     │  ┌────────────────────┐  │
│  - /chat page   │ ──────────────────────► │  │  LangGraph Agent   │  │
│  - /services    │                         │  │  ┌──────────────┐  │  │
│  - /about       │                         │  │  │ agent_node   │◄─┐│  │
│                 │                         │  │  │(GPT-5.5)     │  ││  │
└─────────────────┘                         │  │  └──────┬───────┘  ││  │
                                            │  │         │          ││  │
                                            │  │  ┌──────▼───────┐  ││  │
                                            │  │  │ tool_node    ├──┘│  │
                                            │  │  └──────────────┘  │  │
                                            │  └────────────────────┘  │
                                            │           │              │
                                            │           ▼              │
                                            │  ┌────────────────────┐  │
                                            │  │   PostgreSQL DB    │  │
                                            │  │   (Docker:5460)    │  │
                                            │  └────────────────────┘  │
                                            └──────────────────────────┘
```

---

## Agentic Chat Flow (LangGraph)

The chat architecture has been recently refactored from a rigid flow-chart to a true Tool-Calling Agent.

```
          ┌─────────────┐
          │    START    │
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │  agent_node │◄──────────────┐
          │ (LLM + Msg) │               │
          └──────┬──────┘               │
                 │                      │
       Does LLM call a tool?            │
      ┌──────────┴──────────┐           │
      │                     │           │
     NO                    YES          │
      │                     │           │
      ▼                     ▼           │
 ┌─────────┐         ┌─────────────┐    │
 │   END   │         │  tool_node  │────┘
 │ (Reply) │         │ (Execution) │
 └─────────┘         └─────────────┘
```

### Core Tools Available to the Agent (`backend/app/chat/tools.py`):
1. **`search_knowledge_base(query)`**: (Coming soon) Semantic search over pgvector database to answer general questions (e.g., office hours, general rules).
2. **`get_eligibility_questions(service_code)`**: Returns a JSON list of questions the agent *must* ask the user to determine their exact situation (e.g., "Do you want one-day service?", "Has your license expired?").
3. **`generate_workflow_plan(service_code, condition)`**: Triggered when the agent has collected all eligibility answers. Returns the structured final workflow (`steps`, `documents`) natively to the frontend.

---

## What's Been Built So Far

### ✅ Backend (FastAPI + Python)

| Component | File(s) | Status |
|---|---|---|
| FastAPI app + CORS | `app/main.py` | ✅ Working |
| Database connection (SQLAlchemy) | `app/database.py` | ✅ Working |
| Service & Workflow models | `app/models/` | ✅ Working |
| Services API router | `app/routers/services.py` | ✅ Working |
| Chat API router | `app/routers/chat.py` | ✅ Refactored |
| **Agentic LangGraph loop** | `app/chat/graph.py`, `state.py`, `nodes.py` | ✅ Refactored |
| **Agent Tools** | `app/chat/tools.py` | ✅ Built |
| Workflow engine (rule-based) | `app/engines/workflow_engine.py` | ✅ Working |
| Database seeding script | `scripts/seed_db.py` | ✅ Working |

### ✅ Frontend (Next.js + React)

| Component | File(s) | Status |
|---|---|---|
| Root layout + global CSS | `src/app/layout.js`, `globals.css` | ✅ Built |
| Landing / hero page | `src/app/page.js` | ✅ Built |
| AI Chat page | `src/app/chat/page.js`, `chat.css` | ✅ Built & Fixed |
| Services page | `src/app/services/page.js` | ✅ Built |

---

## How to Run

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker Desktop (running)

### 1. Start the Database
```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\GovernmentAI"
docker compose up -d
```

### 2. Start the Backend
```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\GovernmentAI\backend"
python -m uvicorn app.main:app
```
Backend will be at: **http://localhost:8000**  

### 3. Start the Frontend
```bash
cd "c:\Users\kavin\Desktop\MY PROJECTS\GovernmentAI\frontend"
npm run dev
```
Frontend will be at: **http://localhost:3000**

### 4. Try the Chat
- Open **http://localhost:3000/chat**
- Type something like: *"I want to get my first NIC"* or *"I want to renew my driving license"*
- The AI will autonomously decide which eligibility questions to ask you and will generate a personalized workflow once it has the data it needs!

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/services` | List all services |
| `GET` | `/api/v1/services/{code}` | Get service details |
| `GET` | `/api/v1/services/{code}/questions` | Get questions for a service |
| `POST` | `/api/v1/chat` | Send a chat message (body: `{thread_id, message}`). Handles Agent routing entirely server-side. |

---

## What's Next (Suggested)

- [ ] **Wire up Semantic Search**: Integrate the `pgvector` knowledge base (from `embed_documents.py`) directly into the `search_knowledge_base` tool so the agent can answer general queries like "What are the DRP office hours?".
- [ ] **Add more NIC services** — `nic_amendment`, `nic_dual_citizen` from the scraped data.
- [ ] **Improve chat UX** — Display the workflow beautifully when the agent returns it.
- [ ] **Admin panel** — A way to manage services, questions, and workflow steps without editing JSON.
- [ ] **Persistent chat history** — Currently uses in-memory `MemorySaver` (resets on server restart). We should upgrade to `SqliteSaver` or Postgres checkpointing.
