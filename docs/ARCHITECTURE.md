# GovFlow AI Full Architecture

Version: 1.1  
Project country: Sri Lanka  
Architecture style: Chat-first modular monolith with LangGraph orchestration and manual rule engines  
Primary goal: Help citizens understand, prepare, and track Sri Lankan government service procedures using official information.

## 1. Product Vision

GovFlow AI is a chat-first citizen service workflow platform for Sri Lanka. A user should be able to open a chat, say what they want to do, answer a few questions, and receive a clear personalized government-service roadmap with required documents, official sources, fees, locations, forms, and progress tracking.

The project should use LangGraph from the beginning as the conversation orchestrator. However, government-service logic should still be built manually as deterministic modules so the system is understandable, inspectable, and reliable. LangGraph should decide the conversation path; the rule engine should decide the official workflow.

## 2. Architecture Principle

Build the project in this order:

1. Chat interface.
2. LangGraph conversation orchestration.
3. Manual service data.
4. Manual workflow rules.
5. Manual question branching.
6. Manual document checklist.
7. Manual progress tracking.
8. Admin tools for updating content.
9. RAG over official sources.
10. Document upload/OCR and future official integrations.

This prevents the project from becoming a black-box chatbot. The chat experience is AI-powered, but the government procedure output is generated from official, reviewable service data and rules. If the LLM is unavailable, the system should still support a guided non-AI fallback flow.

## 3. Recommended Tech Stack

### 3.1 Frontend

- Framework: Next.js
- Language: TypeScript
- UI: Tailwind CSS or CSS Modules
- State: React state first, then Zustand if needed
- Forms: React Hook Form
- Validation: Zod

### 3.2 Backend

- Framework: FastAPI
- Language: Python
- Validation: Pydantic
- ORM: SQLAlchemy
- Migrations: Alembic
- Auth: JWT/session-based auth later

FastAPI is recommended because it is clear, beginner-friendly, strongly typed with Pydantic, and excellent for API learning.

### 3.3 Database

- PostgreSQL
- pgvector later for RAG

Start with normal relational tables. Add vector search only after the manual knowledge base works.

### 3.4 LangGraph and AI Layer

- LangGraph from the beginning for chat state, routing, and tool orchestration
- OpenAI API for natural language understanding, service matching, source-grounded Q&A, and summaries
- RAG using PostgreSQL + pgvector
- OCR with Tesseract first

LangGraph should not replace the service catalog, question engine, condition evaluator, or workflow engine. It should call them as tools/nodes.

## 4. High-Level System Diagram

```text
Citizen Browser
    |
    v
Next.js Frontend
    |
    v
FastAPI Backend
    |
    +--> LangGraph Chat Orchestrator
    +--> Service Catalog Module
    +--> Question Engine Module
    +--> Workflow Engine Module
    +--> Document Checklist Module
    +--> Progress Tracker Module
    +--> Knowledge Base Module
    +--> Admin Review Module
    +--> AI/RAG Module
    |
    v
PostgreSQL Database
    |
    +--> Relational service data
    +--> Official source metadata
    +--> User workflow progress
    +--> Vector embeddings, later
```

## 5. Main User Roles

### 5.1 Citizen

The citizen uses the platform to:

- Start a chat and describe a government-service goal.
- Let the system match the correct service.
- Answer follow-up questions inside chat.
- Receive a personalized workflow.
- See required documents.
- Save progress.
- Mark steps as complete.
- View official source links.
- Ask help questions using source-grounded AI.

### 5.2 Admin/Content Reviewer

The admin manages:

- Services.
- Departments.
- Official sources.
- Workflow steps.
- Required documents.
- Rules and branching logic.
- Fees and processing times.
- Content versions.
- User feedback corrections.

### 5.3 Future Government Officer

Later, a government officer may:

- Verify official workflow content.
- Publish approved service versions.
- Review common user blockers.
- Update official contact or fee changes.

## 6. Core Modules

## 6.0 LangGraph Chat Orchestrator Module

Purpose: Manage the citizen conversation from the first message to the final workflow.

This is the main entry point for citizens. The user should not need to browse service categories first. They can start with:

```text
I want to renew my passport.
I lost my NIC.
I want to register a business.
I need a copy of my birth certificate.
```

Responsibilities:

- Maintain conversation state.
- Classify the user's intent.
- Match the user to a likely government service.
- Ask clarifying questions one at a time.
- Call the deterministic question engine.
- Store answers.
- Call the deterministic workflow engine.
- Present the generated workflow in chat.
- Hand off to source-grounded Q&A when the user asks explanation questions.
- Escalate uncertainty by saying what information is missing.

LangGraph nodes:

```text
start
detect_intent
match_service
clarify_service
ask_next_question
store_answer
check_required_answers
generate_workflow
explain_workflow
source_grounded_qa
save_workflow
fallback
end
```

Important:

LangGraph controls the conversation. It does not own government rules. Workflow correctness must come from service data, conditions, official sources, and admin-reviewed content.

## 6.1 Service Catalog Module

Purpose: Store and display supported government services.

Examples:

- First-time NIC application.
- Lost NIC replacement.
- Passport renewal.
- New passport.
- Business registration.
- Birth certificate copy request.
- Driving license renewal.

Responsibilities:

- List services.
- Group services by category.
- Connect services to departments.
- Store service status: draft, reviewed, published, archived.

Key data:

- Service name.
- Description.
- Category.
- Department.
- Official source URLs.
- Supported languages.
- Published version.

## 6.2 Department Directory Module

Purpose: Store government department details.

Examples:

- Department for Registration of Persons.
- Department of Immigration and Emigration.
- Department of Registrar of Companies.
- Registrar General's Department.
- Department of Motor Traffic.

Responsibilities:

- Store official contact details.
- Store office locations.
- Store official websites.
- Connect departments to services.

## 6.3 Knowledge Base Module

Purpose: Store official source material and human-reviewed summaries.

This module should be manual first. Do not start with automatic scraping. Begin by manually adding official source pages and the exact information used.

Responsibilities:

- Store official URLs.
- Store source type: webpage, PDF, form, gazette, FAQ.
- Store extracted text or summary.
- Store retrieval date.
- Store review status.
- Store language.
- Link sources to services, documents, fees, and workflow steps.

Later responsibilities:

- Chunk official text for RAG.
- Generate embeddings.
- Track source changes.

## 6.4 Question Engine Module

Purpose: Ask the right follow-up questions before generating a workflow.

Example:

For passport renewal:

- Are you applying from Sri Lanka or overseas?
- Is this a new passport, renewal, lost passport, or damaged passport?
- Are you between 16 and 60?
- Do you need normal or urgent service?
- Has your name changed?

Responsibilities:

- Load questions for a service.
- Show questions in order.
- Skip irrelevant questions using rules.
- Store user answers.
- Pass answers to the workflow engine.

Important rule:

The question engine should be deterministic. AI may later suggest the correct service, but the question flow itself should be controlled by stored rules.

## 6.5 Workflow Engine Module

Purpose: Generate a personalized step-by-step workflow from service rules and user answers.

Responsibilities:

- Select relevant workflow steps.
- Hide steps that do not apply.
- Add warnings for special cases.
- Attach required documents to each step.
- Attach source links.
- Attach estimated fees and processing times where available.

Example rule:

```text
If service = passport_renewal
And applicant_age between 16 and 60
Then include fingerprint_collection_step
```

The workflow engine should be rule-based first. This helps you learn and makes the system explainable.

## 6.6 Document Checklist Module

Purpose: Show what the user must prepare.

Responsibilities:

- List required documents.
- Mark document as required, optional, or conditional.
- Explain when a conditional document is needed.
- Link document requirement to official source.
- Let user mark each document as ready.

Later responsibilities:

- Upload document.
- OCR document.
- Validate document type.
- Check expiry dates or missing fields where possible.

## 6.7 Progress Tracker Module

Purpose: Allow citizens to save and track their workflow.

Statuses:

- Not started.
- In progress.
- Ready to submit.
- Submitted.
- Completed.
- Blocked.

Responsibilities:

- Save generated workflow.
- Save completed steps.
- Save document readiness.
- Show progress percentage.
- Let users add notes.
- Let users resume later.

## 6.8 Admin Review Module

Purpose: Keep the platform accurate and maintainable.

Responsibilities:

- Add/edit departments.
- Add/edit services.
- Add/edit source links.
- Add/edit questions.
- Add/edit workflow steps.
- Add/edit required documents.
- Publish service versions.
- Review feedback from users.
- View change history.

Important:

No service content should go live without an admin review status.

## 6.9 AI/RAG Module

Purpose: Improve usability without replacing the rule engine.

AI can help with:

- Understanding natural language goals.
- Suggesting the best matching service.
- Explaining official information in simple language.
- Answering questions from official sources.
- Translating reviewed content.
- Summarizing uploaded official documents for admins.

AI should not:

- Invent fees.
- Invent legal requirements.
- Decide final eligibility.
- Replace official sources.
- Change workflow rules without review.

## 7. Data Model

Use snake_case table names.

## 7.1 departments

Stores government departments.

```text
id
name
slug
description
website_url
contact_phone
contact_email
address
created_at
updated_at
```

## 7.2 services

Stores government services.

```text
id
department_id
name
slug
category
short_description
status
current_version_id
created_at
updated_at
```

Status values:

```text
draft
in_review
published
archived
```

## 7.3 service_versions

Stores versioned service content.

```text
id
service_id
version_number
title
summary
language
review_status
published_at
created_at
updated_at
```

Review status values:

```text
draft
needs_review
approved
rejected
published
```

## 7.4 source_documents

Stores official sources.

```text
id
department_id
service_id
title
source_type
url
language
retrieved_at
last_checked_at
review_status
notes
created_at
updated_at
```

Source type values:

```text
webpage
pdf
form
faq
gazette
other
```

## 7.5 service_questions

Stores follow-up questions.

```text
id
service_version_id
question_key
question_text
help_text
answer_type
is_required
display_order
condition_json
created_at
updated_at
```

Answer type values:

```text
text
single_choice
multi_choice
number
date
boolean
district
file_later
```

## 7.6 question_options

Stores answer options for choice questions.

```text
id
question_id
option_key
label
description
display_order
created_at
updated_at
```

## 7.7 workflow_steps

Stores possible steps for a service.

```text
id
service_version_id
step_key
title
description
display_order
condition_json
estimated_time
source_document_id
created_at
updated_at
```

## 7.8 required_documents

Stores documents required by a service.

```text
id
service_version_id
document_key
name
description
requirement_type
condition_json
source_document_id
created_at
updated_at
```

Requirement type values:

```text
required
optional
conditional
```

## 7.9 step_documents

Connects workflow steps to required documents.

```text
id
workflow_step_id
required_document_id
created_at
```

## 7.10 fees

Stores official or estimated fees.

```text
id
service_version_id
label
amount
currency
condition_json
source_document_id
created_at
updated_at
```

Important:

If a fee is not confirmed from an official source, do not store it as official.

## 7.11 processing_times

Stores official or estimated processing times.

```text
id
service_version_id
label
duration_text
condition_json
source_document_id
created_at
updated_at
```

## 7.12 users

Stores citizen/admin accounts.

```text
id
name
email
phone
password_hash
role
created_at
updated_at
```

Role values:

```text
citizen
admin
reviewer
government_officer
```

## 7.13 user_workflows

Stores generated workflows for users.

```text
id
user_id
service_id
service_version_id
title
status
answers_json
generated_summary
created_at
updated_at
```

## 7.14 chat_sessions

Stores citizen chat sessions.

```text
id
user_id
active_service_id
active_service_version_id
active_user_workflow_id
status
conversation_state_json
created_at
updated_at
```

Session status values:

```text
active
workflow_generated
completed
abandoned
```

## 7.15 chat_messages

Stores messages in each chat session.

```text
id
chat_session_id
role
content
message_type
metadata_json
created_at
```

Role values:

```text
user
assistant
system
tool
```

Message type values:

```text
text
question
answer
workflow_preview
source_citation
error
```

## 7.16 user_workflow_steps

Stores user-specific step progress.

```text
id
user_workflow_id
workflow_step_id
status
notes
completed_at
created_at
updated_at
```

Step status values:

```text
not_started
in_progress
completed
blocked
skipped
```

## 7.17 user_document_checklist

Stores user-specific document readiness.

```text
id
user_workflow_id
required_document_id
status
notes
created_at
updated_at
```

Document status values:

```text
not_ready
ready
not_applicable
needs_help
```

## 7.18 user_feedback

Stores citizen feedback and corrections.

```text
id
user_id
service_id
user_workflow_id
feedback_type
message
status
created_at
updated_at
```

## 7.19 audit_logs

Tracks important admin changes.

```text
id
actor_user_id
action
entity_type
entity_id
before_json
after_json
created_at
```

## 7.20 Future RAG Tables

Add later:

```text
knowledge_chunks
embeddings
ai_interactions
document_uploads
ocr_results
```

Do not create these in the first database migration unless you are ready to build them.

## 8. Rule System Design

Use JSON conditions first. This is simple and flexible.

Example condition:

```json
{
  "all": [
    { "field": "application_type", "operator": "equals", "value": "renewal" },
    { "field": "age", "operator": "between", "value": [16, 60] }
  ]
}
```

Supported operators:

```text
equals
not_equals
in
not_in
greater_than
less_than
between
exists
not_exists
```

The backend should have one condition evaluator used by:

- Questions.
- Workflow steps.
- Required documents.
- Fees.
- Processing times.

This is one of the most important parts of the system.

## 9. Backend API Design

Base URL:

```text
/api/v1
```

## 9.1 Public Citizen APIs

```text
POST   /chat/sessions
GET    /chat/sessions/{session_id}
POST   /chat/sessions/{session_id}/messages
GET    /chat/sessions/{session_id}/messages

GET    /services
GET    /services/{service_slug}
GET    /services/{service_slug}/questions
POST   /workflow-preview
POST   /workflows
GET    /workflows/{workflow_id}
PATCH  /workflows/{workflow_id}/steps/{step_id}
PATCH  /workflows/{workflow_id}/documents/{document_id}
POST   /feedback
```

The chat APIs are the primary citizen entry point. The service and workflow APIs remain available for direct UI screens, testing, admin preview, and non-AI fallback flows.

## 9.2 Auth APIs, Later But Plan Now

```text
POST   /auth/register
POST   /auth/login
POST   /auth/logout
GET    /auth/me
POST   /auth/forgot-password
POST   /auth/reset-password
```

## 9.3 Admin APIs

```text
GET    /admin/departments
POST   /admin/departments
PATCH  /admin/departments/{id}

GET    /admin/services
POST   /admin/services
PATCH  /admin/services/{id}

GET    /admin/services/{id}/versions
POST   /admin/services/{id}/versions
PATCH  /admin/service-versions/{id}
POST   /admin/service-versions/{id}/publish

GET    /admin/source-documents
POST   /admin/source-documents
PATCH  /admin/source-documents/{id}

GET    /admin/service-versions/{id}/questions
POST   /admin/service-versions/{id}/questions
PATCH  /admin/questions/{id}
DELETE /admin/questions/{id}

GET    /admin/service-versions/{id}/workflow-steps
POST   /admin/service-versions/{id}/workflow-steps
PATCH  /admin/workflow-steps/{id}
DELETE /admin/workflow-steps/{id}

GET    /admin/service-versions/{id}/documents
POST   /admin/service-versions/{id}/documents
PATCH  /admin/documents/{id}
DELETE /admin/documents/{id}

GET    /admin/feedback
PATCH  /admin/feedback/{id}
```

## 9.4 LangGraph/Internal AI APIs

```text
POST   /ai/match-service
POST   /ai/ask
POST   /ai/summarize-source
POST   /ai/translate
```

These should call the existing service, knowledge, and workflow modules. They should not bypass them.

## 10. Frontend Application Structure

Recommended routes:

```text
/
/chat
/chat/[sessionId]
/services
/services/[slug]
/start/[slug]
/workflow/[id]
/dashboard
/login
/register

/admin
/admin/departments
/admin/services
/admin/services/[id]
/admin/services/[id]/versions
/admin/service-versions/[id]/questions
/admin/service-versions/[id]/workflow
/admin/service-versions/[id]/documents
/admin/sources
/admin/feedback
```

## 11. Main Citizen Flow

```text
1. Citizen lands on home page.
2. Citizen starts a chat.
3. Citizen says what they want to do.
4. LangGraph detects intent and matches a likely service.
5. If uncertain, LangGraph asks a clarification question.
6. LangGraph asks the next required service question.
7. Citizen answers inside chat.
8. Backend stores the answer and evaluates conditions.
9. When enough answers exist, LangGraph calls the workflow engine.
10. Backend returns personalized workflow preview.
11. Citizen saves workflow.
12. Citizen sees checklist, documents, fees, sources, and progress.
13. Citizen marks steps and documents as completed.
```

## 12. Main Admin Flow

```text
1. Admin creates department.
2. Admin creates service.
3. Admin creates service version.
4. Admin adds official source documents.
5. Admin adds questions and answer options.
6. Admin adds workflow steps with conditions.
7. Admin adds required documents with conditions.
8. Admin adds fees and processing times.
9. Admin tests workflow preview using sample answers.
10. Admin publishes service version.
```

## 13. First MVP Services

Build only these first:

1. First-time NIC application.
2. Passport renewal.
3. Business registration through eROC.

After those work, add:

4. Birth certificate copy request.
5. Driving license renewal.

## 14. First MVP Screens

Citizen:

- Home/search page.
- Services list.
- Service details page.
- Question flow page.
- Workflow result page.
- Saved workflow dashboard.

Admin:

- Admin dashboard.
- Service editor.
- Question editor.
- Workflow step editor.
- Document requirement editor.
- Source document editor.

## 15. Folder Structure

Recommended repository structure:

```text
GovernmentAI/
+-- ARCHITECTURE.md
+-- GovFlow_AI_Sri_Lanka_Research.md
+-- backend/
|   +-- app/
|   |   +-- main.py
|   |   +-- core/
|   |   |   +-- config.py
|   |   |   +-- database.py
|   |   |   +-- security.py
|   |   +-- modules/
|   |   |   +-- chat/
|   |   |   +-- langgraph_orchestrator/
|   |   |   +-- departments/
|   |   |   +-- services/
|   |   |   +-- knowledge_base/
|   |   |   +-- questions/
|   |   |   +-- workflows/
|   |   |   +-- documents/
|   |   |   +-- progress/
|   |   |   +-- feedback/
|   |   |   +-- admin/
|   |   |   +-- ai_rag/
|   |   +-- shared/
|   |       +-- condition_evaluator.py
|   |       +-- enums.py
|   |       +-- exceptions.py
|   +-- migrations/
|   +-- tests/
|   +-- pyproject.toml
|   +-- README.md
+-- frontend/
|   +-- app/
|   |   +-- page.tsx
|   |   +-- chat/
|   |   +-- services/
|   |   +-- start/
|   |   +-- workflow/
|   |   +-- dashboard/
|   |   +-- admin/
|   +-- components/
|   +-- lib/
|   +-- types/
|   +-- package.json
|   +-- README.md
+-- docs/
|   +-- API.md
|   +-- DATABASE.md
|   +-- WORKFLOW_RULES.md
|   +-- LANGGRAPH_FLOW.md
|   +-- MVP_SCOPE.md
+-- docker-compose.yml
```

## 16. Backend Module Pattern

Each backend module should follow a similar pattern:

```text
module/
+-- models.py
+-- schemas.py
+-- repository.py
+-- service.py
+-- router.py
+-- tests.py
```

Meaning:

- `models.py`: database tables.
- `schemas.py`: request and response shapes.
- `repository.py`: database queries.
- `service.py`: business logic.
- `router.py`: API endpoints.
- `tests.py`: module tests.

This is excellent for learning because it teaches clean backend separation.

## 17. Chat-First Implementation Order

Build in this exact order:

### Step 1: Project Setup

- Create backend FastAPI app.
- Create frontend Next.js app.
- Create PostgreSQL database.
- Add Docker Compose.
- Add environment configuration for OpenAI/LangGraph.

### Step 2: Chat Foundation

- Create `chat_sessions` table.
- Create `chat_messages` table.
- Create `POST /chat/sessions`.
- Create `POST /chat/sessions/{session_id}/messages`.
- Create basic chat UI.
- Store user and assistant messages.

At this point, the assistant can return simple placeholder responses while the graph is being built.

### Step 3: LangGraph Skeleton

- Create LangGraph state schema.
- Add `start` node.
- Add `detect_intent` node.
- Add `fallback` node.
- Add basic graph routing.
- Connect chat API to LangGraph.
- Save graph state in `chat_sessions.conversation_state_json`.

### Step 4: Core Service Database

- Departments.
- Services.
- Service versions.
- Source documents.

### Step 5: Admin Service Management

- Create/edit departments.
- Create/edit services.
- Create/edit service versions.
- Create/edit official source links.

### Step 6: Service Matching Node

- Add `match_service` LangGraph node.
- Use simple manual keyword matching first.
- Later replace or enhance with LLM-based matching.
- Return top service candidate and confidence.

### Step 7: Question Engine

- Store questions.
- Store options.
- Let LangGraph ask questions inside chat.
- Save answers in `chat_sessions.conversation_state_json`.

### Step 8: Condition Evaluator

- Build JSON condition evaluator.
- Unit test it heavily.
- Use it for question visibility.

### Step 9: Workflow Engine

- Store workflow steps.
- Apply condition evaluator.
- Generate personalized workflow preview.
- Add `generate_workflow` LangGraph node.

### Step 10: Document Checklist

- Store required documents.
- Apply condition evaluator.
- Attach documents to workflow.

### Step 11: User Workflows

- Save generated workflows.
- Track step progress.
- Track document readiness.
- Add `save_workflow` LangGraph node.

### Step 12: Admin Review and Publish

- Draft service versions.
- Publish service versions.
- Only published versions appear to citizens.

### Step 13: LLM Service Matching

Enhance service matching:

```text
User types: "I lost my ID"
LLM suggests: Lost NIC replacement service
```

The actual workflow remains rule-based.

### Step 14: RAG Q&A

Add official-source Q&A only after sources and workflows are stable.

## 18. Testing Strategy

Start testing early.

Backend tests:

- LangGraph route tests.
- Chat session/message tests.
- Condition evaluator tests.
- Workflow generation tests.
- Document requirement tests.
- API response tests.

Frontend tests later:

- Chat flow renders correctly.
- Chat question/answer messages render correctly.
- Conditional questions appear/disappear correctly.
- Workflow result displays steps and documents.

Manual acceptance tests:

- First-time NIC workflow.
- Passport renewal workflow for age 16-60.
- Passport renewal workflow for under 16.
- Business registration workflow for sole owner.
- Business registration workflow for multiple owners.

## 19. Security and Privacy

Minimum requirements from the start:

- Do not store sensitive documents in MVP.
- Do not ask for NIC number unless absolutely needed.
- Do not store birth certificate/passport images in MVP.
- Use HTTPS in production.
- Hash passwords.
- Use role-based access for admin routes.
- Log admin changes.
- Keep source citations visible.
- Add privacy notice before user accounts.

Future requirements:

- Data deletion request.
- Document encryption.
- File virus scanning.
- Data protection impact assessment.
- Consent logs.
- Access logs for sensitive records.

## 20. AI Boundaries

AI is allowed to:

- Match user text to a service.
- Route the conversation through LangGraph.
- Decide the next conversational action.
- Explain published workflow steps.
- Search official source chunks.
- Summarize official pages for admin review.
- Translate draft content for human review.

AI is not allowed to:

- Publish official content.
- Modify rules without admin approval.
- Give final legal/approval decisions.
- Invent official requirements.
- Answer without citing sources in government procedure questions.
- Override the deterministic workflow engine.

## 21. Deployment Plan

Development:

```text
Frontend: localhost:3000
Backend: localhost:8000
Database: localhost:5432
```

Production later:

- Frontend: Vercel or Docker-hosted Next.js.
- Backend: Docker container.
- Database: managed PostgreSQL.
- Files: object storage only when document uploads are added.
- Monitoring: logs, error tracking, uptime checks.

For a Sri Lankan government-aligned pilot, plan for local or government-approved hosting if required.

## 22. Non-Negotiable Design Decisions

These decisions should not change casually:

1. Chat is the primary citizen interface.
2. LangGraph is the conversation orchestrator from the beginning.
3. Manual workflow engine remains the authority for procedure generation.
4. Rule-based branching remains the authority for required questions and workflow conditions.
5. Official sources required for government claims.
6. Published service versions only for citizens.
7. Admin review before publishing.
8. AI as assistant and router, not government authority.
9. PostgreSQL as the main system of record.
10. Modular monolith before microservices.

## 23. What We Should Build First

The first coding milestone should be:

```text
Backend:
- FastAPI setup
- PostgreSQL setup
- LangGraph setup
- chat_sessions table
- chat_messages table
- departments table
- services table
- service_versions table
- source_documents table
- basic chat APIs
- basic service/admin CRUD APIs

Frontend:
- Next.js setup
- chat page
- services list page
- service details page
- basic admin service editor
```

After that, connect the LangGraph service-matching node to the question engine.

## 24. Final Architecture Summary

GovFlow AI should be built as a chat-first modular monolith with LangGraph orchestrating the conversation and a strong rule-based workflow engine generating official procedure outputs. The project should start with chat sessions, LangGraph state, official government service models, questions, workflow steps, required documents, sources, and user progress. AI should improve conversation, service matching, explanations, translations, and official-source Q&A, while the deterministic workflow engine remains the authority for procedure generation.

This architecture gives you a clear learning path and keeps the project flexible enough to grow into a serious Sri Lankan citizen service platform.
