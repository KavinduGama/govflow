# GovFlow AI — Mermaid Diagram Collection

Paste each block at [mermaid.live](https://mermaid.live) to generate a clean image.

---

## Diagram 1 — High-Level System Architecture

```mermaid
graph TD
    subgraph CL["CLIENT LAYER"]
        direction LR
        CIT["👤 Citizen"]
        ADM["🔧 Admin"]
    end

    subgraph FE["FRONTEND — Next.js + TypeScript"]
        direction LR
        CH["Chat Interface"]
        SL["Services List"]
        WV["Workflow Viewer"]
        PT["Progress Tracker"]
        AU["Admin Dashboard"]
    end

    subgraph BE["BACKEND — FastAPI + Python"]
        API["REST API Layer"]

        subgraph LG["LangGraph Orchestrator"]
            direction TB
            DI["detect_intent"] --> MS["match_service"] --> AQ["ask_question"] --> GW["generate_workflow"] --> SQ["source_qa"]
            DI --> FB["fallback"]
        end

        subgraph CM["Core Modules"]
            SC["Service Catalog"] --- QE["Question Engine"] --- WE["Workflow Engine"]
            DC["Document Checklist"] --- KB["Knowledge Base"] --- AR["Admin Review"]
        end

        CE(["⚙️ Condition Evaluator"])

        subgraph AI["AI Layer"]
            direction LR
            SM["Service Matcher"] --- RG["RAG Engine"] --- EX["Content Extractor"]
        end
    end

    subgraph DB["DATABASE — PostgreSQL"]
        direction LR
        REL[("Relational Tables")]
        VEC[("pgvector — Embeddings")]
    end

    subgraph EXT["EXTERNAL"]
        direction LR
        OAI["OpenAI GPT-4o"]
        GOV["Gov Websites & PDFs"]
    end

    CIT --> FE
    ADM --> FE
    FE --> API
    API --> LG
    API --> CM
    MS --> SM
    AQ --> QE
    GW --> WE
    SQ --> RG
    QE --> CE
    WE --> CE
    DC --> CE
    CM --> REL
    RG --> VEC
    SM --> OAI
    RG --> OAI
    EX --> OAI
    EX --> GOV
```

---

## Diagram 2 — Citizen Chat Flow (Sequence)

```mermaid
sequenceDiagram
    actor C as Citizen
    participant UI as Next.js
    participant API as FastAPI
    participant LG as LangGraph
    participant QE as Question Engine
    participant WE as Workflow Engine
    participant CE as Condition Evaluator
    participant DB as PostgreSQL
    participant AI as OpenAI

    C->>UI: "I want to get my NIC"
    UI->>API: POST /chat/sessions/{id}/messages
    API->>LG: process_message(state)

    LG->>AI: classify intent
    AI-->>LG: intent = "NIC application"

    LG->>DB: fetch matching services
    DB-->>LG: ["first_time_nic", "nic_replacement"]

    LG->>AI: confirm best match
    AI-->>LG: first_time_nic (confidence 0.94)

    loop For each required question
        LG->>QE: get_next_question(service, answers)
        QE->>DB: fetch questions
        QE->>CE: evaluate conditions
        CE-->>QE: next question
        QE-->>LG: "What is your age?"
        LG-->>C: asks question via chat
        C-->>LG: answers
        LG->>DB: store answer
    end

    LG->>WE: generate_workflow(service, answers)
    WE->>DB: fetch steps, docs, fees
    WE->>CE: evaluate conditions per item
    CE-->>WE: applicable items only
    WE-->>LG: personalized workflow

    LG-->>UI: workflow preview
    UI-->>C: Steps · Documents · Fees · Sources
```

---

## Diagram 3 — Admin Content Creation Flow (Sequence)

```mermaid
sequenceDiagram
    actor A as Admin
    participant UI as Admin UI
    participant API as FastAPI
    participant EX as AI Extractor
    participant GOV as Gov Website/PDF
    participant DB as PostgreSQL

    A->>UI: Paste official URL or upload PDF
    UI->>API: POST /admin/source-documents
    API->>EX: extract_structured_data(source)
    EX->>GOV: fetch content
    GOV-->>EX: raw official text

    EX->>EX: AI reads and extracts structure
    EX-->>API: suggested questions, steps, documents, fees

    API-->>UI: AI extraction preview
    UI-->>A: Review suggestions

    loop For each suggested item
        A->>UI: Accept / Edit / Reject
    end

    UI->>API: POST confirmed data
    API->>DB: save verified rules

    A->>UI: Test with sample answers
    UI->>API: POST /workflow-preview
    API-->>UI: preview result
    UI-->>A: Verify output looks correct

    A->>UI: Publish service version
    UI->>API: POST /admin/service-versions/{id}/publish
    API->>DB: status = published
    UI-->>A: ✅ Live for citizens
```

---

## Diagram 4 — LangGraph Node Map (State Diagram)

```mermaid
stateDiagram-v2
    [*] --> detect_intent

    detect_intent --> match_service : intent clear
    detect_intent --> fallback : intent unclear

    match_service --> clarify_service : low confidence
    match_service --> ask_next_question : service confirmed

    clarify_service --> match_service : citizen confirms
    clarify_service --> fallback : cannot resolve

    ask_next_question --> store_answer
    store_answer --> check_required_answers

    check_required_answers --> ask_next_question : more questions needed
    check_required_answers --> generate_workflow : all answers collected

    generate_workflow --> explain_workflow

    explain_workflow --> source_grounded_qa : citizen asks follow-up
    explain_workflow --> save_workflow : citizen accepts

    source_grounded_qa --> explain_workflow : answer delivered

    save_workflow --> [*]
    fallback --> [*]
```

---

## Diagram 5 — Hybrid AI + Rule Engine Flow

```mermaid
flowchart TD
    GOV(["📄 Official Gov Source\nWebsite / PDF / Gazette"])
    EX["AI Content Extractor\nreads and interprets source"]
    REV{"Admin Review Interface"}
    DB[("✅ Verified Rule Database\nsteps · questions · docs · fees")]
    DISC["❌ Discarded"]
    CE["Condition Evaluator"]
    EMB["pgvector\nRAG Embeddings"]

    CIT(["💬 Citizen Message"])
    LG["LangGraph Orchestrator"]
    IC["Intent Classifier\nOpenAI"]
    QEN["Question Engine"]
    OUT["🎯 Personalized Workflow\nSteps · Documents · Fees · Sources"]

    FUP(["❓ Follow-up Question"])
    RAGR["RAG Retriever"]
    ANS["✅ LLM Answer\nwith Source Citation"]

    GOV --> EX --> REV
    REV -->|Accept| DB
    REV -->|Edit then Accept| DB
    REV -->|Reject| DISC

    DB --> CE
    DB --> EMB

    CIT --> LG --> IC --> QEN --> CE --> OUT
    FUP --> RAGR --> EMB --> ANS
```

---

## Diagram 6 — Database Entity Relationships (ERD)

```mermaid
erDiagram
    departments {
        uuid id PK
        string name
        string slug
        string website_url
        string contact_email
        string address
    }
    services {
        uuid id PK
        uuid department_id FK
        string name
        string slug
        string category
        string status
    }
    service_versions {
        uuid id PK
        uuid service_id FK
        int version_number
        string language
        string review_status
        timestamp published_at
    }
    service_questions {
        uuid id PK
        uuid service_version_id FK
        string question_key
        string answer_type
        json condition_json
        int display_order
    }
    workflow_steps {
        uuid id PK
        uuid service_version_id FK
        string step_key
        string title
        json condition_json
        string estimated_time
    }
    required_documents {
        uuid id PK
        uuid service_version_id FK
        string document_key
        string requirement_type
        json condition_json
    }
    source_documents {
        uuid id PK
        uuid service_id FK
        string source_type
        string url
        string review_status
    }
    users {
        uuid id PK
        string name
        string email
        string role
    }
    user_workflows {
        uuid id PK
        uuid user_id FK
        uuid service_version_id FK
        string status
        json answers_json
    }
    chat_sessions {
        uuid id PK
        uuid user_id FK
        uuid active_service_id FK
        string status
        json conversation_state_json
    }

    departments ||--o{ services : "owns"
    services ||--o{ service_versions : "versioned as"
    service_versions ||--o{ service_questions : "has"
    service_versions ||--o{ workflow_steps : "has"
    service_versions ||--o{ required_documents : "has"
    services ||--o{ source_documents : "sourced from"
    users ||--o{ user_workflows : "has"
    users ||--o{ chat_sessions : "opens"
    user_workflows }o--|| service_versions : "based on"
```

---

## Diagram 7 — Deployment Architecture

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        USER(["👤 User"])
    end

    subgraph Edge["CDN / Edge — Vercel or Cloudflare"]
        CDN["Static Assets & Edge Cache"]
    end

    subgraph App["Application Layer"]
        FE["Next.js Container\nFrontend"]
        BE1["FastAPI Instance 1"]
        BE2["FastAPI Instance 2"]
        WK["Background Worker\nRAG indexing & embeddings"]
    end

    subgraph Data["Data Layer"]
        PG[("Managed PostgreSQL\n+ pgvector")]
        OBJ["Object Storage\ndocument uploads — future"]
    end

    subgraph Observe["Observability"]
        LOG["Centralized Logs"]
        ERR["Error Tracking"]
        UPT["Uptime Monitoring"]
    end

    subgraph ExtAPI["External APIs"]
        OAI["OpenAI GPT-4o"]
    end

    USER --> CDN --> FE
    FE --> BE1 & BE2
    BE1 & BE2 --> PG
    WK --> PG
    BE1 & BE2 --> OAI
    BE1 & BE2 --> LOG & ERR
    UPT -.->|monitors| BE1
```

---

## Diagram 8 — Security & Access Control

```mermaid
flowchart TD
    CIT(["👤 Citizen"])
    ADM(["🔧 Admin"])

    subgraph Transport["Transport Layer"]
        HTTPS["HTTPS Only"]
    end

    subgraph AppLayer["Application Layer"]
        FE["Next.js Frontend"]
        API["FastAPI Backend"]
        JWT["JWT Auth Middleware"]
        RBAC["Role-Based Access Control"]
    end

    subgraph Roles["Roles"]
        R1["citizen\nown data only"]
        R2["admin\nall content"]
        R3["reviewer\nreview queue"]
        R4["government_officer\nfuture"]
    end

    subgraph DataLayer["Data Layer"]
        DB[("PostgreSQL\nEncrypted at rest")]
        AUDIT[("audit_logs\nall admin actions")]
    end

    CIT --> HTTPS --> FE --> API --> JWT --> RBAC
    ADM --> HTTPS

    RBAC --> R1 & R2 & R3 & R4
    R1 --> DB
    R2 --> DB & AUDIT
    R3 --> DB
```
