# GovFlow AI Sri Lanka Research and Success Plan

Research date: 2026-07-11

## 1. Executive Summary

GovFlow AI is a strong project idea for Sri Lanka because it addresses a real gap between "information exists online" and "citizens can complete a government process confidently." Sri Lanka already has government portals, e-services, department websites, 1919/GIC support, GovPay, eROC, e-BMD, passport services, NIC services, and emerging digital public infrastructure. The problem is not absence of digital activity. The problem is fragmentation, inconsistent user experience, multilingual access, unclear procedure paths, and repeated office visits caused by missing documents or misunderstood eligibility.

The best way to make GovFlow AI successful is to position it as an AI-powered citizen workflow guide that uses official government information, asks follow-up questions, creates personalized checklists, validates documents before submission, and eventually integrates with official platforms such as GIC/1919, GovPay, SLUDI, digital forms, digital locker, and the National Data Exchange.

GovFlow AI should not begin by trying to replace official portals. It should begin as a trusted guidance layer for high-volume services, then evolve into an integration layer once partnerships and compliance are ready.

## 2. Current Sri Lankan Context

### 2.1 Existing Government Digital Channels

Sri Lanka already has several digital government touchpoints:

- The national portal, GOV.LK, describes itself as the place to find Sri Lankan government services and information: https://www.gov.lk/
- GOV.LK has an online services directory, but the listing is broad and sends users to many different department websites: https://www.gov.lk/government/eservices
- The Government Information Centre, GIC/1919, is positioned as a gateway to government services and information for citizens: https://gic.gov.lk/
- Digital Government Forms exists as a government paperwork platform: https://forms.gov.lk/
- The Registrar General's Department has e-BMD for requesting certified copies of birth, marriage, and death certificates with verification and home delivery: https://www.rgd.gov.lk/web/index.php/en/e-services
- The Registrar of Companies operates eROC as a web-based single window for business registration facilities: https://drc.gov.lk/en/?cat=44
- The Department of Immigration and Emigration provides passport information, downloadable forms, online guidance, digital photograph requirements, and biometric requirements: https://www.immigration.gov.lk/pages_e.php?id=7
- The Department for Registration of Persons provides NIC guidance and FAQs, including processing time details: https://drp.gov.lk/en/faq.php

The opportunity for GovFlow AI is to unify the citizen journey across these channels, not duplicate them.

### 2.2 National Digital Transformation Direction

Sri Lanka's Ministry of Digital Economy has identified digitalization, governance, cybersecurity, financial inclusion, digital skills, and sectoral innovation as key areas in the Digital Economy Blueprint. Its listed focus areas include transparent and efficient government, digital industry development, digital economy growth, strategic industry transformation, and capacity development for industry, government, and citizens.

Relevant national projects listed by the Ministry of Digital Economy include:

- Government Super App Phase I, intended to develop citizen-centric government services.
- AI Powered Government Information Center, intended to modernize GIC and 1919 with an AI-enabled, multilingual, multi-platform solution.
- National Data Exchange, intended to enable secure, authenticated, interoperable data sharing among agencies and with the private sector.
- Digital Economy Sandbox and Experience Center for testing and demonstrating DPI and digital public goods.
- Communication and collaboration tools with legally recognized digital signatures.
- Public AI awareness and local language AI projects for Sinhala and Tamil ASR, STT, and TTS.

Source: Ministry of Digital Economy project PDF: https://mode.gov.lk/assets/files/New%20Projects%20and%20Programs%20initiated%20by%20Ministry%20of%20Digital%20Economy-93b0f8a4d9e9e4963a3147259bdcaf56.pdf

This means GovFlow AI is timely. However, it must be designed to complement government infrastructure, not compete with it.

### 2.3 World Bank Digital Transformation Support

The World Bank approved a USD 50 million Sri Lanka Digital Transformation Project in December 2025. The project aims to modernize government services and make them more accessible and responsive. It specifically mentions:

- Integrated online citizen service portal.
- Secure data sharing across government agencies.
- Digital locker for storing digital documents.
- Scalable government cloud platform.
- Training for citizens and public servants.

Source: https://www.worldbank.org/en/news/press-release/2025/12/19/world-bank-group-and-sri-lanka-partner-to-improve-digital-services-and-grow-the-digital-economy

GovFlow AI can align with these priorities by becoming a workflow, knowledge, and AI assistance layer that can later connect to the citizen portal, digital locker, government cloud, and agency data exchange.

### 2.4 Data Protection and Trust

Sri Lanka has a formal data protection regime. The Data Protection Authority states that the Personal Data Protection Act No. 9 of 2022 created an independent legal foundation for personal data protection, and the Authority was established in August 2023 to regulate personal data processing and protect individuals' privacy.

Source: https://www.dpa.gov.lk/

This is critical for GovFlow AI because the platform may handle NIC numbers, birth certificates, passports, addresses, photographs, business records, marriage records, tax information, and other sensitive personal data. The project must be built privacy-first from the beginning.

## 3. Core Problem GovFlow AI Should Solve

The main citizen pain points are:

- Citizens do not know where to start.
- Government information is spread across many websites.
- Procedures differ by user situation, district, document type, age, citizenship status, and service urgency.
- Users often discover missing documents only after visiting an office.
- Sinhala, Tamil, and English support is uneven across digital channels.
- Existing portals are usually service directories or forms, not personalized completion guides.
- Many citizens need assisted digital service, not only self-service.

GovFlow AI should solve these by converting complex procedures into personalized, step-by-step workflows.

## 4. Best Positioning

Recommended positioning:

> GovFlow AI is a citizen workflow assistant for Sri Lankan government services. It helps people understand, prepare, and complete government procedures using official information, multilingual AI guidance, document readiness checks, and progress tracking.

Avoid positioning it as:

- A replacement for GOV.LK.
- A replacement for 1919/GIC.
- A fake "official" government portal.
- A system that promises approval decisions.
- A tool that gives legal guarantees without agency validation.

The trust message should be: "Guidance based on official sources. Final submission and approval remain with the relevant government department."

## 5. Recommended MVP Scope

Start with 5 high-value services where citizens commonly need guidance:

1. First-time NIC application.
2. Passport new issue or renewal.
3. Business registration through eROC.
4. Birth, marriage, and death certificate copy requests through e-BMD.
5. Driving license application or renewal.

Why these services:

- High public demand.
- Clear documents and eligibility paths.
- Strong need for checklists and progress tracking.
- Existing official information is available online.
- Good demo value for competitions, investors, and government stakeholders.

## 6. MVP Features

### 6.1 Citizen Intake

The user enters a goal in natural language:

- "I want to renew my passport."
- "I need my first NIC."
- "I want to register a private limited company."
- "I need a copy of my birth certificate."

The AI identifies:

- Service type.
- User category.
- Department involved.
- Required follow-up questions.
- Likely forms, documents, fees, appointments, and office visits.

### 6.2 Guided Question Flow

Instead of giving generic instructions, the system asks targeted questions:

- Age.
- District or Divisional Secretariat.
- New application vs renewal vs lost document.
- Local applicant vs overseas applicant.
- Individual vs company.
- One-day service vs normal service.
- Name changes, dual citizenship, marriage status, child applicant, or lost document case.

### 6.3 Personalized Workflow

Output should include:

- Step-by-step tasks.
- Required documents.
- Where to submit.
- Official links.
- Fees where available from official sources.
- Expected processing time where available from official sources.
- Offline steps that still require physical presence.
- Warnings for common mistakes.
- Downloadable or printable checklist.

### 6.4 Source-Grounded AI Answers

Every answer should show:

- The department source used.
- Last checked date.
- Confidence level.
- "Verify with official department before payment/submission" notice for sensitive steps.

Use retrieval-augmented generation rather than allowing the model to answer from memory.

### 6.5 Progress Tracking

Each workflow becomes a checklist:

- Not started.
- In progress.
- Ready to submit.
- Submitted.
- Completed.
- Blocked because of missing document.

### 6.6 Document Readiness Check

The system can help users check whether they have the correct document types:

- NIC copy.
- Birth certificate.
- Marriage certificate.
- Police complaint for lost NIC/passport cases.
- Passport photograph acknowledgement.
- Business registration documents.

For the MVP, avoid storing sensitive documents unless necessary. Start with a manual checklist and optional local-only preview. Add cloud document wallet later.

### 6.7 Multilingual Support

Sinhala, Tamil, and English are essential. For MVP:

- Store canonical workflow content in English.
- Add human-reviewed Sinhala and Tamil versions for top workflows.
- Use AI translation only with clear review and correction.
- Prioritize simple language, not legal wording.

## 7. Architecture Recommendation

Recommended initial stack:

- Frontend: Next.js and React.
- Backend: FastAPI or Node.js.
- Database: PostgreSQL.
- Vector database: pgvector or a managed vector store.
- AI orchestration: LangGraph for workflow state and tool use.
- AI model: OpenAI API with structured outputs.
- OCR: Tesseract initially, then consider cloud OCR if accuracy is insufficient.
- Search/RAG: official source crawler plus human approval queue.
- Authentication: email/phone for MVP, SLUDI-compatible design for future.
- Deployment: Docker, later government cloud or compliant local hosting.

## 8. Knowledge Base Strategy

The knowledge base is the heart of the project.

### 8.1 Source Types

Use only trusted sources:

- GOV.LK.
- Department websites.
- Ministry websites.
- Official PDFs and forms.
- Gazette/legal documents where needed.
- Verified government APIs if available.

### 8.2 Content Pipeline

1. Crawl official pages and PDFs.
2. Extract clean text and metadata.
3. Split into service-specific chunks.
4. Add source URL, department, language, date retrieved, and review status.
5. Have a human reviewer approve each service workflow.
6. Store embeddings for retrieval.
7. Generate structured workflow templates.
8. Re-check sources on a schedule.

### 8.3 Suggested Data Model

Core tables:

- `services`
- `departments`
- `service_versions`
- `eligibility_rules`
- `required_documents`
- `workflow_steps`
- `fees`
- `processing_times`
- `forms`
- `source_documents`
- `user_workflows`
- `user_workflow_steps`
- `document_check_items`
- `audit_logs`

## 9. AI Safety and Reliability Rules

GovFlow AI should follow these rules:

- Never invent fees, deadlines, office locations, or legal requirements.
- Always cite official sources.
- If information is missing or conflicting, say so clearly.
- Separate "official requirement" from "helpful preparation tip."
- Keep human review for new or changed workflows.
- Show when a source was last checked.
- Use structured outputs for workflow generation.
- Log AI decisions for auditability.
- Allow users to report incorrect guidance.

## 10. Privacy and Compliance Requirements

Minimum privacy controls:

- Collect only data needed for the workflow.
- Let users use the system without uploading documents where possible.
- Encrypt sensitive data at rest and in transit.
- Avoid storing raw IDs and documents in early MVP unless necessary.
- Add consent screens for document uploads.
- Add deletion/export request flows.
- Keep audit logs for access to sensitive data.
- Separate personally identifiable information from analytics data.
- Prepare a privacy notice aligned with Sri Lanka's PDPA.
- Conduct a data protection impact assessment before document wallet features.

## 11. Partnership Strategy

### 11.1 Short-Term

Build a working MVP independently using public official information.

Target early validation from:

- University mentors.
- Legal/public administration advisors.
- Civic tech communities.
- Small business owners.
- Students applying for NIC/passport services.

### 11.2 Medium-Term

Approach:

- Ministry of Digital Economy.
- ICTA/GovTech Sri Lanka.
- GIC/1919 team.
- Department for Registration of Persons.
- Department of Immigration and Emigration.
- Registrar General's Department.
- Department of Registrar of Companies.

The pitch should be: "We can help reduce repetitive inquiries and improve citizen readiness before they reach your counters."

### 11.3 Long-Term

Seek integration with:

- National citizen service portal.
- Digital locker.
- GovPay.
- National Data Exchange.
- SLUDI/digital identity.
- Digital forms.
- GIC/1919 AI modernization.

## 12. Product Roadmap

### Phase 1: Research Prototype, 4 to 6 weeks

- Build service knowledge base for 5 services.
- Build AI intake and follow-up question flow.
- Generate personalized checklists.
- Add official source citations.
- Add English UI first.
- Validate with 20 to 30 users.

### Phase 2: MVP, 8 to 12 weeks

- Add Sinhala and Tamil for selected workflows.
- Add user accounts and progress tracking.
- Add PDF checklist export.
- Add admin panel for reviewing service information.
- Add feedback/report issue flow.
- Add basic document readiness checklist.
- Run pilot with 100 to 300 users.

### Phase 3: Pilot With Institution, 3 to 6 months

- Pick one department or service cluster.
- Add official content review.
- Add analytics dashboard for common citizen questions.
- Add GIC/1919 handoff or support scripts.
- Add appointment/payment links where official links exist.
- Measure reduction in incomplete submissions.

### Phase 4: National-Scale Platform, 6 to 18 months

- Add official integrations.
- Add document wallet integration.
- Add GovPay links or payment status integration.
- Add SLUDI login when available.
- Add National Data Exchange integrations when approved.
- Add voice interface for Sinhala and Tamil.
- Expand to 50+ services.

## 13. High-Impact Use Cases

### First-Time NIC

Official DRP information indicates that normal service can take up to 3 months, while one-day service can be completed in about 3 hours where there are no issues with submitted information. This is a strong use case for readiness checking.

Source: https://drp.gov.lk/en/faq.php

### Passport

The Department of Immigration and Emigration requires digital photographs through authorized studios and fingerprints for applicants between 16 and 60 at designated offices. Printed photographs are no longer accepted for passport applications.

Source: https://www.immigration.gov.lk/pages_e.php?id=7

### Business Registration

eROC is already a web-based single window for business registration. GovFlow AI should guide users before and during eROC usage, especially around business type, ownership structure, documents, and post-registration obligations.

Source: https://drc.gov.lk/en/?cat=44

### Birth, Marriage, and Death Certificates

e-BMD enables citizens to request certified copies of birth, marriage, and death certificates with secure verification and home delivery. GovFlow AI can help users know which certificate type and details they need before applying.

Source: https://www.rgd.gov.lk/web/index.php/en/e-services

## 14. Success Metrics

Track:

- Number of workflows started.
- Number of workflows completed.
- Percentage of users who say they know the next step.
- Percentage of users who avoided an unnecessary office visit.
- Reduction in missing-document cases during pilot.
- Average time to generate a checklist.
- Source coverage per service.
- User satisfaction by language.
- Number of corrections reported and resolved.
- Number of official departments engaged.

## 15. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| AI gives outdated or wrong instructions | Use RAG from official sources, cite sources, add human review, schedule source checks |
| Users think GovFlow AI is an official approval system | Use clear wording: guidance only, final approval by department |
| Sensitive document/privacy risk | Minimize data collection, encrypt data, avoid document storage in MVP |
| Sinhala/Tamil errors | Human-review key workflows, use simple language, collect corrections |
| Government information changes without notice | Add last-checked dates and automated monitoring |
| No official API access | Start with public sources and deep links, then pursue partnerships |
| Too broad MVP | Start with 5 services only |
| Trust barrier | Show official citations and build with local advisors |

## 16. Recommended Demo Story

Best demo flow:

1. User types: "I want to register a business in Sri Lanka."
2. AI asks: business type, owners, district, local/foreign ownership, company name status.
3. System generates a workflow:
   - Choose business structure.
   - Prepare documents.
   - Use eROC.
   - Pay applicable fees through official channels.
   - Track registration steps.
   - Get post-registration reminders.
4. User sees official source links and a progress checklist.
5. Admin dashboard shows which official sources were used.

This demo is strong because business registration supports entrepreneurship and connects to national digital economy goals.

## 17. What To Build First

Build these first:

- Service catalog with 5 services.
- Official source ingestion.
- RAG answer engine with citations.
- Workflow generator.
- Follow-up question engine.
- Progress checklist.
- Admin review screen.
- Feedback/correction screen.

Do not build these first:

- Full document wallet.
- Payment processing.
- SLUDI login.
- National Data Exchange integration.
- Mobile app.
- Voice assistant.

Those are valuable later, but they will slow the MVP.

## 18. Recommended File/Feature Structure For Implementation

Suggested application modules:

- `services-catalog`: list of supported services and departments.
- `knowledge-base`: official documents, chunks, citations, embeddings.
- `workflow-engine`: rule-based and AI-assisted workflow generation.
- `question-engine`: follow-up questions and branching logic.
- `citizen-dashboard`: saved workflows and progress tracking.
- `admin-review`: source review, correction, versioning.
- `document-readiness`: checklist and optional OCR validation.
- `analytics`: anonymous usage and common blockers.

## 19. Final Recommendation

GovFlow AI can become successful in Sri Lanka if it focuses on a narrow but painful citizen problem: helping people complete government procedures correctly the first time. The winning strategy is:

1. Start with 5 high-demand services.
2. Use official sources only.
3. Build source-grounded AI workflows, not generic chatbot answers.
4. Support Sinhala, Tamil, and English.
5. Design for PDPA compliance from day one.
6. Partner with government after proving usefulness with a working MVP.
7. Align with national initiatives such as the Government Super App, AI-powered GIC/1919, GovPay, National Data Exchange, digital locker, and SLUDI.

If executed carefully, GovFlow AI can be a practical bridge between citizens and Sri Lanka's emerging digital government infrastructure.

## 20. Source List

- GOV.LK national portal: https://www.gov.lk/
- GOV.LK online services directory: https://www.gov.lk/government/eservices
- Government Information Centre: https://gic.gov.lk/
- Digital Government Forms: https://forms.gov.lk/
- Ministry of Digital Economy: https://mode.gov.lk/
- Ministry of Digital Economy projects PDF: https://mode.gov.lk/assets/files/New%20Projects%20and%20Programs%20initiated%20by%20Ministry%20of%20Digital%20Economy-93b0f8a4d9e9e4963a3147259bdcaf56.pdf
- World Bank Sri Lanka Digital Transformation Project: https://www.worldbank.org/en/news/press-release/2025/12/19/world-bank-group-and-sri-lanka-partner-to-improve-digital-services-and-grow-the-digital-economy
- Data Protection Authority of Sri Lanka: https://www.dpa.gov.lk/
- Department for Registration of Persons FAQ: https://drp.gov.lk/en/faq.php
- Department of Immigration and Emigration passport information: https://www.immigration.gov.lk/pages_e.php?id=7
- Department of Registrar of Companies eROC: https://drc.gov.lk/en/?cat=44
- Registrar General's Department e-services: https://www.rgd.gov.lk/web/index.php/en/e-services
- ICTA SLUDI page: https://www.icta.lk/projects/digital-government/sludi
- ICTA Digital Government Policy PDF: https://www.icta.lk/icta-assets/uploads/2022/06/Digital-Govt-Policy_Ver-4.2_Latest.pdf
