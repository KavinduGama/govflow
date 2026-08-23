# GovFlow AI — Project Idea

> A chat-first platform that helps Sri Lankan citizens understand and navigate government services.

---

## The Problem

Government services in Sri Lanka (NIC, passport, business registration, etc.) are confusing. Citizens don't know what documents they need, where to go, how much it costs, or what steps to follow. There is no single reliable place to get a clear, personalized answer.

---

## What We're Building

A web app where a citizen opens a chat, says what they want to do, answers a few questions, and gets a clear step-by-step government service guide — with required documents, fees, office locations, and official sources.

```
"I want to renew my passport."
→ System asks 3–4 questions
→ Returns a personalized checklist and workflow
→ Citizen can save progress and track completion
```

---

## How It Works

| Layer | What it does |
|-------|-------------|
| **Chat (LangGraph)** | Understands what the citizen wants and guides the conversation |
| **Rule Engine** | Generates the correct official workflow based on answers — no AI guessing |
| **Service Data** | Manually curated, admin-reviewed government procedure data |
| **AI (OpenAI)** | Helps match intent and explain steps — never invents official rules |
| **Progress Tracker** | Lets citizens save and resume their workflow |

---

## Key Principle

**AI handles conversation. Rules handle procedure.**

The workflow output (steps, documents, fees) always comes from official, human-reviewed data — not from an LLM. If AI is unavailable, the system still works.

---

## Tech Stack

- **Frontend:** Next.js + TypeScript
- **Backend:** FastAPI + Python
- **Database:** PostgreSQL
- **AI/Chat:** LangGraph + OpenAI API
- **Later:** pgvector for RAG over official sources

---

## MVP Services (Start Small)

1. First-time NIC application
2. Passport renewal
3. Business registration (eROC)

---

## Who Uses It

| User | What they do |
|------|-------------|
| **Citizen** | Chat to get a workflow, track progress |
| **Admin** | Add/review/publish service data and rules |

---

## What Makes It Different

- Chat-first, not a form or FAQ page
- Workflows come from official sources, not AI guesses
- Admin review required before anything goes live
- Designed for Sri Lanka's actual government structure
- Built to eventually support Sinhala and Tamil

---

## Build Order (Big Picture)

1. Chat interface + basic conversation
2. LangGraph orchestration
3. Service data + admin editor
4. Question engine + condition rules
5. Workflow generator
6. Document checklist + progress tracker
7. RAG over official sources (later)
