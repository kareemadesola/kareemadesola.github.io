# Adesola Kareem — Career Portfolio & Application Tracker

**Email:** kareemadesola1999@gmail.com | **Phone:** +2349070708811  
**LinkedIn:** linkedin.com/in/adesola-kareem-686541181 | **GitHub:** github.com/kareemadesola  
**Location:** Lagos, Nigeria (fully remote)

---

## GitHub Projects

### Scalable Notification Service *(May 2026 – Present)*
`FastAPI · RabbitMQ · Redis · PostgreSQL · Docker · Prometheus · Grafana`  
Production-grade multi-channel notification system. Handles email, SMS, push, and in-app WebSocket delivery with independent channel scaling, exponential backoff retry, dead-letter queues, JWT auth with refresh tokens, Redis rate limiting, and full Prometheus + Grafana observability.  
Designed for ~17K notifications/sec with horizontal scaling strategy.  
→ github.com/kareemadesola/scalable-notification-service

### AI Investigation & Research Assistant *(April 2026)*
`Python · FAISS · RAG · LangChain-style agentic pipeline`  
Agentic RAG system that combines vector search, multi-step reasoning, and a structured evaluation layer for hallucination detection. Demonstrates retrieval → reasoning → synthesis → evaluation pipeline.  
→ github.com/kareemadesola/ai-investigation-assistant

### Physiotherapy Recommendation System *(BSc Final Year Project, 2023)*
`Python · scikit-learn · Flask · Docker · Pandas · Render`  
ML-powered clinical decision support tool that recommends personalised physiotherapy exercise regimens for arthritis patients. Trained a Random Forest classifier on a dataset derived from MIMIC-IV arthritis case notes — 4 exercise classes, 5,045-sample test set, 100% test accuracy (AUC-ROC 1.0). Web UI built with Flask + Jinja2; deployed to Render via Docker. Includes a `/metrics` endpoint with confusion matrix and feature importance visualisations.  
→ github.com/kareemadesola/bsc_csc_project

### System Design Masterclass *(March 2026)*
Active study of distributed systems design patterns (Udemy course), documented as working notes.  
→ github.com/kareemadesola/system-design-masterclass

---

## Work Experience

### WebMD — Software Engineer (Backend) *(Mar 2025 – Present)*
`Python · FastAPI · Pydantic · RabbitMQ · pgvector · Solr · Redis · Docker · GCP`
- Designed and built scalable Python/FastAPI REST APIs with Pydantic data models and JSON Schema contracts for high-throughput content ingestion
- Fixed vector re-indexing inconsistencies with atomic updates, improving retrieval accuracy
- Implemented multi-provider LLM + embedding routing (OpenAI, Azure, Anthropic, Vertex, Cohere)
- Designed model-aware embedding pipeline with batching and grouping for performance optimization
- Built PII anonymization service (FastAPI + Presidio + spaCy) for HIPAA-aware LLM workflows
- Added queue pressure controls and failure isolation (per-backend try/except) for system reliability
- Designed multi-backend storage routing (pgvector + Solr) by business unit via env config
- Designed idempotent processing and deduplication for consistency in distributed pipelines
- Reduced DB round-trips via bulk unnest() inserts (3 round-trips for any batch size)
- Built JWT-secured APIs with Helios OAuth2 for authenticated multi-tenant content processing

**Repositories** *(private — gitlab.webmd.com/WebMD/helios/athena)*

| Repo | Description |
|------|-------------|
| `athena-ingestion-service` | Core ingestion pipeline — partitions, chunks, vectorises and stores semantic content; FastAPI + RabbitMQ + pgvector + Solr |
| `athena-vector-processor` | RabbitMQ consumer worker — dequeues ingestion jobs, calls embedding providers, writes to pgvector/Solr with idempotent dedup |
| `athena-api` | Public-facing REST API for the Athena AI platform — JWT/OAuth2 auth, multi-tenant routing, HIPAA-compliant endpoints |
| `athena-vector-files-service` | File-based vector operations service — handles document uploads and chunk storage for the retrieval pipeline |
| `presidio-fastapi-scrubber` | HIPAA-compliant PII anonymisation microservice (FastAPI + Presidio + spaCy); scrubs PHI from content before LLM processing |
| `presidio-guardrails-anonymizer` | LLM guardrails anonymiser — strips PII from prompts and completions at inference time; includes memory profiling and CVE patches |

### Nomba — Software Engineer *(Nov 2023 – Feb 2024)*
`Python · MongoDB · Redis · GCP`
- Reduced GCP infrastructure costs by 25% via caching and service optimization
- Built a CSV export pipeline using MongoDB and Redis

### Precious Cornerstone University (NYSC) — Research Assistant *(Mar 2024 – Jan 2025)*
- Trained faculty on AI tools (ChatGPT, Claude), improving productivity by ~40%

---

## Education

**Obafemi Awolowo University**, Ile-Ife, Nigeria  
BSc Computer Science with Mathematics — **First Class Honours** *(Aug 2023)*  
GPA: 4.62 | Scholarships: NNPC–CHEVRON National University Scholarship, Adewale Obadimu Scholarship

---

## Certifications

- HackerRank: Java (2024), REST API (2023), Problem Solving (2023), Python (2022)

---

## Core Stack

| Area | Technologies |
|------|-------------|
| Languages | Python (5+ yrs), JavaScript/Node.js, Java |
| Backend | FastAPI, REST APIs, Pydantic, Express.js, Microservices |
| Data | PostgreSQL (pgvector), Redis, MongoDB, Solr |
| AI/LLM | RAG, LLM routing, embeddings (OpenAI/Azure/Anthropic/Vertex/Cohere), FAISS, Presidio |
| Infra | RabbitMQ, Docker, GCP, GitLab CI/CD, JWT/OAuth2 |
| Observability | Prometheus, Grafana, Kibana |

---

## Notes

- Resume format: **PDF only** (not DOCX)
- Resume generator: `python3 generate_resume.py --company "Acme" --role "Backend Engineer" --focus "python fastapi distributed"`
- Salary expectation: $3,500 USD/month
- Open to: remote roles globally; Lagos-based or willing to relocate
