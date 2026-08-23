# GovFlow AI — ChatGPT Image Prompts for Architecture Diagrams

> Copy each prompt and paste it directly into ChatGPT. If the text labels are wrong, ask ChatGPT to fix specific labels in a follow-up message.

---

## Prompt 1 — High-Level System Architecture

```
Create a professional software architecture diagram for a platform called "GovFlow AI". 
Use a clean, modern tech style with a white or very light grey background, subtle rounded 
rectangles for groups, and a blue-green color palette. Use clear sans-serif font labels.

The diagram has these layers from top to bottom:

LAYER 1 — CLIENT LAYER (light blue group box, top left):
  Two boxes side by side: "Citizen" and "Admin"
  Both have arrows pointing right into the Frontend layer.

LAYER 2 — FRONTEND: Next.js + TypeScript (green group box, top right/center):
  Five boxes in a row: "Chat Interface", "Services List", "Workflow Viewer", 
  "Progress Tracker", "Admin Dashboard"
  All have a downward arrow into the Backend.

LAYER 3 — BACKEND: FastAPI + Python (large blue group box, middle):
  At the top of this box: "REST API Layer" (full-width bar)
  Below, three sub-groups side by side:

  Sub-group A — LANGGRAPH ORCHESTRATOR (purple/violet box, left):
    Nodes listed vertically with arrows between them:
    "detect_intent" → "match_service" → "ask_question" → "generate_workflow" → "source_qa"
    A dashed arrow from "detect_intent" to "fallback" on the side

  Sub-group B — CORE MODULES (orange/amber box, center):
    Six module boxes in a 2x3 grid:
    "Service Catalog", "Question Engine", "Workflow Engine",
    "Document Checklist", "Knowledge Base", "Progress Tracker"
    Below those: "Admin Review" (full width)
    In the center-right, a highlighted oval/circle labeled 
    "Condition Evaluator (shared)" with arrows pointing to it from multiple modules

  Sub-group C — AI LAYER (teal box, right):
    Three boxes stacked: "Service Matcher", "RAG Engine", "Content Extractor"

LAYER 4 — DATABASE: PostgreSQL (dark green group box, bottom left):
  Two boxes: "Relational Tables" and "pgvector — Embeddings"
  Bidirectional arrow between them.

LAYER 5 — EXTERNAL (grey group box, bottom right):
  Two boxes: "OpenAI GPT-4o" and "Gov Websites & PDFs"

Arrows:
- LangGraph nodes call Core Modules
- Core Modules feed into Condition Evaluator
- AI Layer connects to OpenAI and Gov sources
- All modules store data in PostgreSQL
- RAG Engine connects to pgvector

Style: professional tech company diagram, 16:9 ratio, no hand-drawn look, 
clean sharp edges, icon-free or minimal icons, readable labels.
```

---

## Prompt 2 — Citizen Chat Flow (Sequence Diagram)

```
Create a professional UML sequence diagram for a software system called "GovFlow AI".
Use a clean modern style, white background, dark navy or dark grey participant bars 
at the top, light colored message arrows with clear labels, and alternating white/light 
grey background bands for readability.

Participants (left to right, shown as labeled vertical bars):
"Citizen" | "Next.js UI" | "FastAPI" | "LangGraph" | "Question Engine" | 
"Workflow Engine" | "Condition Evaluator" | "PostgreSQL" | "OpenAI"

Messages (top to bottom, with arrow labels):
1. Citizen → Next.js UI: "I want to get my NIC"
2. Next.js UI → FastAPI: POST /chat/sessions/{id}/messages
3. FastAPI → LangGraph: process_message(state)
4. LangGraph → OpenAI: classify intent
5. OpenAI → LangGraph: intent = "NIC application"
6. LangGraph → PostgreSQL: fetch matching services
7. PostgreSQL → LangGraph: ["first_time_nic", "nic_replacement"]
8. LangGraph → OpenAI: confirm best match
9. OpenAI → LangGraph: first_time_nic (confidence 0.94)

[Loop box labeled "Repeat for each required question"]
10. LangGraph → Question Engine: get_next_question(service, answers)
11. Question Engine → PostgreSQL: fetch questions
12. Question Engine → Condition Evaluator: evaluate which questions apply
13. Condition Evaluator → Question Engine: next question = "What is your age?"
14. LangGraph → Citizen: asks question in chat
15. Citizen → LangGraph: answer

16. LangGraph → Workflow Engine: generate_workflow(service, answers)
17. Workflow Engine → PostgreSQL: fetch steps, documents, fees
18. Workflow Engine → Condition Evaluator: evaluate conditions per item
19. Condition Evaluator → Workflow Engine: applicable items
20. Workflow Engine → LangGraph: personalized workflow
21. LangGraph → Next.js UI: workflow preview
22. Next.js UI → Citizen: Steps · Documents · Fees · Official Sources

Style: clean technical diagram, 16:9, blue-purple color palette for arrows, 
loop boxes in dashed borders, readable font size, professional presentation quality.
```

---

## Prompt 3 — Admin Content Creation Flow (Sequence Diagram)

```
Create a professional UML sequence diagram titled "Admin Content Creation Flow" 
for a platform called GovFlow AI. Clean white background, modern sans-serif font, 
dark participant bars at the top, colored message arrows.

Participants (left to right):
"Admin" | "Admin UI" | "FastAPI" | "AI Extractor" | "Gov Website / PDF" | "PostgreSQL"

Messages (top to bottom):
1. Admin → Admin UI: Paste official government URL or upload PDF
2. Admin UI → FastAPI: POST /admin/source-documents
3. FastAPI → AI Extractor: extract_structured_data(source)
4. AI Extractor → Gov Website/PDF: fetch content
5. Gov Website/PDF → AI Extractor: raw official text
6. AI Extractor → AI Extractor: [self-arrow] AI reads and extracts structure
7. AI Extractor → FastAPI: suggested questions, steps, documents, fees
8. FastAPI → Admin UI: AI extraction preview
9. Admin UI → Admin: Review AI suggestions

[Loop box labeled "For each suggested item"]
10. Admin → Admin UI: Accept / Edit / Reject

11. Admin UI → FastAPI: POST confirmed data
12. FastAPI → PostgreSQL: save verified rules

13. Admin → Admin UI: Test with sample answers
14. Admin UI → FastAPI: POST /workflow-preview
15. FastAPI → Admin UI: preview result
16. Admin UI → Admin: Verify output is correct

17. Admin → Admin UI: Publish service version
18. Admin UI → FastAPI: POST /admin/service-versions/{id}/publish
19. FastAPI → PostgreSQL: status = published
20. Admin UI → Admin: ✅ Live for citizens

Style: tech company presentation quality, green-teal color palette for arrows, 
loop box in dashed border with label, 16:9 landscape, clean and readable.
```

---

## Prompt 4 — LangGraph Node Map (State/Flow Diagram)

```
Create a professional software state diagram titled "LangGraph Conversation Node Map" 
for a platform called GovFlow AI. 

Use a dark navy background with light colored node boxes and bright colored arrows. 
Nodes should be rounded rectangles with a subtle glow. Use a purple/violet color scheme 
for nodes and teal/cyan for arrows.

Nodes and transitions (show as a vertical flow with branches):

[START] → detect_intent

detect_intent:
  → match_service  (label: "intent clear")
  → fallback  (label: "intent unclear", dashed red arrow)

match_service:
  → clarify_service  (label: "low confidence")
  → ask_next_question  (label: "service confirmed")

clarify_service:
  → match_service  (label: "citizen confirms", curved back arrow)
  → fallback  (label: "cannot resolve", dashed red arrow)

ask_next_question → store_answer
store_answer → check_required_answers

check_required_answers:
  → ask_next_question  (label: "more questions needed", curved left arrow)
  → generate_workflow  (label: "all answers collected")

generate_workflow → explain_workflow

explain_workflow:
  → source_grounded_qa  (label: "citizen asks follow-up", dashed arrow)
  → save_workflow  (label: "citizen accepts")

source_grounded_qa → explain_workflow  (curved back arrow, label: "answer delivered")

save_workflow → [END]
fallback → [END]

Style: dark mode diagram, futuristic but professional, 16:9, suitable for a company 
architecture deck. Node labels in white, arrow labels in light grey. No clipart or icons.
```

---

## Prompt 5 — Hybrid AI + Rule Engine Flow

```
Create a professional flowchart diagram titled "Hybrid AI + Rule Engine Design" 
for a platform called GovFlow AI. This is the most important diagram in the deck.

Layout: two parallel paths that meet in the middle, on a white background.

LEFT PATH — Content Creation (label this section "Content Creation Path"):
  Start node (rounded): "Official Government Source\n(Website / PDF / Gazette)"
    ↓ arrow labeled "AI reads source"
  Process box: "AI Content Extractor"
    ↓ arrow
  Diamond decision: "Admin Review"
    → Right branch (label "Accept"): goes to the Central DB
    → Far right branch (label "Edit then Accept"): goes to the Central DB
    → Down branch (label "Reject"): goes to dead-end box "Discarded ✗"

CENTRAL NODE (highlighted, green border, prominent):
  Cylinder/database shape: "✅ Verified Rule Database\n(steps · questions · documents · fees)"

  Two arrows OUT from the database:
    → Down-left: "Condition Evaluator"
    → Down-right: "pgvector RAG Embeddings"

RIGHT PATH — Citizen Query (label this section "Citizen Query Path"):
  Start node: "Citizen Message"
    ↓
  Box: "LangGraph Orchestrator"
    ↓
  Box: "Intent Classifier (OpenAI)"
    ↓
  Box: "Question Engine"
    ↓ arrow to Condition Evaluator (connects to central component)
  
  Condition Evaluator leads to:
  End node (blue, prominent): "🎯 Personalized Workflow Output\n(Steps · Documents · Fees · Sources)"

BOTTOM PATH — Follow-up Questions:
  Start node: "Citizen Follow-up Question"
    → "RAG Retriever"
    → "pgvector Embeddings" (connects back to central)
    → "LLM Answer with Source Citation (OpenAI)"

Style: clean professional flowchart, color-coded paths (green for creation path, 
blue for citizen path, purple for follow-up), white background, 16:9 landscape, 
suitable for executive presentation. No clip art.
```

---

## Prompt 6 — Database Entity Relationship Diagram (ERD)

```
Create a clean, professional database Entity Relationship Diagram (ERD) for a 
platform called GovFlow AI. White background, modern style, tables shown as rectangles 
with a header row and listed fields. Use blue for table headers, white for field rows, 
thin grey borders. Relationship lines with crow's foot notation at the "many" ends.

Tables and their key fields:

departments: id (PK), name, slug, website_url, contact_email, address
services: id (PK), department_id (FK), name, slug, category, status
service_versions: id (PK), service_id (FK), version_number, language, review_status, published_at
service_questions: id (PK), service_version_id (FK), question_key, answer_type, condition_json, display_order
workflow_steps: id (PK), service_version_id (FK), step_key, title, condition_json, estimated_time
required_documents: id (PK), service_version_id (FK), document_key, requirement_type, condition_json
source_documents: id (PK), service_id (FK), source_type, url, review_status
users: id (PK), name, email, role, password_hash
user_workflows: id (PK), user_id (FK), service_version_id (FK), status, answers_json
chat_sessions: id (PK), user_id (FK), active_service_id (FK), status, conversation_state_json

Relationships:
- departments ONE to MANY services
- services ONE to MANY service_versions
- service_versions ONE to MANY service_questions
- service_versions ONE to MANY workflow_steps
- service_versions ONE to MANY required_documents
- services ONE to MANY source_documents
- users ONE to MANY user_workflows
- users ONE to MANY chat_sessions
- user_workflows MANY to ONE service_versions

Layout: arrange tables to minimize crossing lines. Group related tables together.
Style: professional, enterprise-grade ERD, no hand-drawn style, 16:9, readable labels.
```

---

## Prompt 7 — Deployment Architecture

```
Create a professional cloud deployment architecture diagram titled "GovFlow AI — 
Deployment Architecture". Use a clean modern style with a light grey or white background, 
colored zone boxes with subtle borders, and clear sans-serif labels.

Show these zones as horizontal bands or grouped boxes from top to bottom:

ZONE 1 — Internet (thin top bar):
  User icon with label "User (Citizen / Admin)"

ZONE 2 — CDN / Edge (light blue group):
  Box: "CDN — Vercel or Cloudflare\n(Static assets, edge caching)"

ZONE 3 — Application Layer (light purple group):
  Three boxes side by side:
  "Next.js Container\n(Frontend)"
  "FastAPI — Instance 1\n(Backend)"
  "FastAPI — Instance 2\n(Horizontal scale)"
  One box below: "Background Worker\n(RAG indexing, embedding generation)"

ZONE 4 — Data Layer (light green group):
  Two boxes side by side:
  "Managed PostgreSQL\n+ pgvector extension"
  "Object Storage\n(Document uploads — Phase 2)"

ZONE 5 — Observability (light orange group, side panel or bottom):
  Three boxes: "Centralized Logs" | "Error Tracking" | "Uptime Monitoring"

ZONE 6 — External APIs (grey group, side):
  One box: "OpenAI GPT-4o API"

Arrows:
- User → CDN → Next.js → FastAPI Instances
- FastAPI Instances → PostgreSQL
- Background Worker → PostgreSQL
- FastAPI → OpenAI (external arrow)
- FastAPI → Observability (monitoring arrows, dashed)

Note at bottom: "For government-aligned deployment, on-premise or local hosting 
may be required for data residency compliance."

Style: AWS/GCP-style architecture diagram but cloud-agnostic, 16:9, 
professional enterprise quality, no comic or hand-drawn style.
```

---

## Prompt 8 — Security & Access Control

```
Create a professional security architecture diagram titled "GovFlow AI — 
Security & Access Control Model". Use a clean modern style, dark navy and 
teal color palette, white background, with labeled security zones shown as 
nested rounded rectangles.

Layout: three nested zones:

OUTER ZONE — "Public Internet":
  Contains: Citizen user icon and Admin user icon

MIDDLE ZONE — "Application Zone (HTTPS Only)":
  Boxes in sequence connected by arrows:
  "Next.js Frontend" → "FastAPI Backend" → "JWT Auth Middleware" → "Role-Based Access Control (RBAC)"

  Below RBAC, show four role boxes branching out:
  "citizen\n(own data only)" | "admin\n(all content + audit)" | 
  "reviewer\n(review queue)" | "government_officer\n(future)"

INNER ZONE — "Data Zone (Restricted)":
  Two database icons:
  "PostgreSQL\n(encrypted at rest)"
  "audit_logs\n(all admin changes recorded)"

Arrows:
- Citizen → HTTPS → Frontend
- Admin → HTTPS → Frontend (or directly to Admin UI)
- Roles connect to PostgreSQL with access labels
- Admin role also connects to audit_logs
- All arrows between zones labeled with access conditions

Add a small key/legend:
  Solid arrow = authenticated access
  Dashed arrow = restricted/admin only

Style: enterprise security diagram, professional, 16:9 landscape, suitable 
for a security review presentation. No clip art. Clean and readable.
```

---

## Tips for Best Results

- If text labels are wrong or missing, follow up with: *"Fix the label [X] to say [Y]"*
- If layout is off, say: *"Make the diagram wider, horizontal layout"*
- For consistent style across all diagrams, start each prompt with: *"In the same style as my previous architecture diagrams..."*
- Ask for **PNG with transparent background** if you want to drop them into slides
