# 🎙️ GovFlow AI — Live Demo & Presentation Script

**Project**: GovFlow AI — Intelligent Citizen Service Guidance & Knowledge Base  
**Target Duration**: 5 – 7 minutes  
**Audience**: Stakeholders, Evaluators, Technical Panels, Clients  

---

## 📋 Pre-Demo Checklist
Before starting your screen share or presentation, ensure:
- [ ] Backend is running: `http://localhost:8000`
- [ ] Frontend is running: `http://localhost:3000`
- [ ] Have two browser tabs ready:
  - Tab 1: Citizen Chat (`http://localhost:3000`)
  - Tab 2: Admin Dashboard (`http://localhost:3000/admin`)

---

## 🎬 Act 1: Introduction & The Problem (1 minute)

### [ACTION]
*Keep screen on the GovFlow AI landing page or Citizen Chat interface (`http://localhost:3000`).*

### [SPOKEN SCRIPT]
> "Hello everyone. Today, I’m excited to show you **GovFlow AI** — an intelligent digital assistant and knowledge pipeline built to simplify government citizen services in Sri Lanka.
>
> Navigating public services is notoriously frustrating. Citizens often spend hours digging through fragmented official websites, trying to figure out which documents they need, what fees apply, or what office counter to visit. Often, they wait in long queues only to be turned away because they missed one document.
>
> Generic AI chatbots don't solve this because they hallucinate outdated rules or make assumptions. 
>
> **GovFlow AI solves this with a dual architecture**: 
> 1. An intelligent **Decision Workflow Engine** for structured, multi-step services like getting a National Identity Card or Driving Licence.
> 2. An automated **Retrieval-Augmented Generation (RAG) Knowledge Base** powered by real scraped government data and PostgreSQL vector search.
>
> Let me show you how it works in real time."

---

## 🎬 Act 2: Citizen Experience & Real RAG in Action (2 minutes)

### [ACTION]
*Navigate to `http://localhost:3000`.*  
*Type the following prompt into the chat box and press send:*  
`What are the DRP office hours and how long does one day service take for NIC?`

### [SPOKEN SCRIPT]
> "Let's put ourselves in the shoes of a citizen who needs an urgent National Identity Card today.
>
> I'll ask: *'What are the DRP office hours and how long does one day service take for NIC?'*"

### [ACTION]
*Wait for the response to render. Point your cursor at the bullet points in the AI response.*

### [SPOKEN SCRIPT]
> "Notice the response. This isn't generic text. 
> 
> The system tells us with pin-point precision:
> - The exact application hours: **7:30 AM to 12:30 PM**.
> - The exact location: **Terminal D on the 9th floor of the Head Office in Battaramulla**, as well as the **Galle Provincial Office**.
> - The exact processing time: **Within 3 hours** under One Day Service.
>
> How does it know this? It didn't guess. Behind the scenes, the backend converted this question into a vector embedding, searched our PostgreSQL vector database using cosine similarity, found the official scraped section from the Department for Registration of Persons, and grounded the answer in ground truth."

### [ACTION]
*Now ask a more specific follow-up in the chat:*  
`Can someone else collect my NIC if I am elderly or sick?`

### [SPOKEN SCRIPT]
> "Let's test an edge case: *'Can someone else collect my NIC if I am elderly or sick?'*
>
> Look at the answer: It correctly specifies that only an authorized immediate family member — mother, father, spouse, or next of kin — can collect it, **and they must bring a letter certified by the Grama Niladhari**.
>
> This level of accuracy is essential for public sector applications."

---

## 🎬 Act 3: The Admin Experience & The Data Problem (1.5 minutes)

### [ACTION]
*Switch to Tab 2: `http://localhost:3000/admin`.*  
*Scroll smoothly past the Overview KPIs down to the **Knowledge Base & Vector Synchronization** section.*

### [SPOKEN SCRIPT]
> "Now, let’s look at the administration side. 
>
> A major challenge with government platforms is that **government regulations change**. Fees get revised, forms update, and office protocols shift. 
>
> In traditional systems, engineers have to manually re-scrape pages, re-embed entire websites, and incur high API bills.
>
> In GovFlow, we built a dedicated **Scrape & Sync Pipeline** right inside the Admin panel.
>
> Here in the Knowledge Base section, the admin can see all 10 official ingested documents — including FAQs, procedural tabs, and official downloadable PDF application forms. We have **53 active vector chunks** currently live in PostgreSQL."

---

## 🎬 Act 4: The "Scrape & Sync" Live Demo & Cost Optimization (1.5 minutes)

### [ACTION]
*Point to the **"🔄 Scrape & Sync"** button.*  
*Click the button.*  
*(The button turns into a loading spinner for 1-2 seconds, then the green sync result card appears).*

### [SPOKEN SCRIPT]
> "When the admin clicks **'Scrape & Sync'**, the system triggers our ingestion engine. 
>
> Watch what happens. The sync finishes in just two seconds.
>
> Look at this metric right here: **OpenAI Cost Saved: 100% Saved**.
>
> How did we achieve 100% savings? 
> 
> We engineered a **SHA-256 change detection layer**:
> - Before sending text to OpenAI's embedding API, every single chunk is assigned a SHA-256 cryptographic hash.
> - The engine compares these hashes against our database. 
> - If the text hasn't changed on the government portal, **it completely skips the embedding API**.
> - **Only new or modified clauses** are sent to OpenAI.
> - And if a rule has been removed, the obsolete chunk is automatically purged.
>
> This guarantees that running updates costs almost **zero dollars** when policies remain unchanged, making this architecture scalable and enterprise-ready for national-scale deployments."

---

## 🎬 Act 5: Summary & Wrap-Up (30 seconds)

### [ACTION]
*Scroll up to show the dashboard stats (Services: 4, Questions: 8, Workflow Steps: 22, Vector Chunks: 53).*

### [SPOKEN SCRIPT]
> "To summarize what you've seen today:
> 1. **Zero Hallucination Citizen Guidance**: Real government data retrieved via pgvector cosine semantic search.
> 2. **One-Click Admin Sync**: On-demand scraping and automated document ingestion.
> 3. **Intelligent Change Detection**: Cryptographic chunk hashing that saves up to 100% of LLM embedding costs.
> 4. **Modern, Robust Stack**: Next.js frontend, FastAPI backend, Dockerized PostgreSQL with pgvector, and OpenAI embeddings.
>
> Thank you! I'd love to answer any questions."

---

## 💡 Anticipated Q&A (Cheat Sheet for the Presenter)

### Q1: *"What happens if the government website is down when the admin clicks Scrape & Sync?"*
> **Answer**: "We built resilient error handling into `ingestion.py`. If the live portal experiences connection timeouts or is offline, the ingestion engine automatically catches the error and falls back to our latest verified local dataset. The system remains 100% functional and never crashes."

### Q2: *"Can this be run automatically on a schedule instead of clicking a button?"*
> **Answer**: "Yes! We exposed the entire pipeline through a standard endpoint: `POST /api/v1/admin/scrape-sync`. It can easily be connected to a weekly cron job, Windows Task Scheduler, or a FastAPI background worker with just one line of code. And because of our SHA-256 change detection, even if a cron job runs every night, it costs $0 if nothing changed."

### Q3: *"How does GovFlow handle both general Q&A and guided step-by-step applications?"*
> **Answer**: "GovFlow uses a dual-engine architecture:
> - If a citizen has an open-ended question (like *'What are the office hours?'*), the **Semantic RAG Engine** handles it.
> - If a citizen wants a complete checklist for their personal situation, our **Decision Workflow Engine** guides them through tailored questions (e.g. age, first-time vs renewal) and compiles an exact personalized document checklist."

### Q4: *"What embedding model and vector database are you using?"*
> **Answer**: "We use OpenAI's `text-embedding-3-small` (1536 dimensions) for high-accuracy semantic embeddings, stored in a PostgreSQL database using the `pgvector` extension with cosine distance indexing (`<=>`)."
