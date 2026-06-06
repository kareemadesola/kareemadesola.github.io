#!/usr/bin/env python3
"""
Resume generator for Adesola Kareem.
Generates a one-page tailored PDF resume optimised for ATS and human reviewers.

Usage:
    python3 generate_resume.py --company "Acme Corp" --role "Backend Engineer"
    python3 generate_resume.py --company "Acme Corp" --role "Backend Engineer" --focus "python fastapi llm"
    python3 generate_resume.py  # generates base resume
"""

import argparse
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors


# ─────────────────────────────────────────────
# MASTER CONTENT
# ─────────────────────────────────────────────

CONTACT = {
    "name": "ADESOLA KAREEM",
    "location": "Lagos, Nigeria (Open to Remote)",
    "phone": "+2349070708811",
    "email": "kareemadesola1999@gmail.com",
    "linkedin": "https://linkedin.com/in/adesola-kareem-686541181",
    "github": "https://github.com/kareemadesola",
}

# Skills ordered by group; reorder_skills() re-sorts based on focus keywords
SKILLS = [
    ("Languages",   "Python (5+ yrs), JavaScript/Node.js, Java"),
    ("Backend",     "FastAPI, REST APIs, Pydantic, JSON Schema, Microservices, Event-Driven Architecture"),
    ("Data",        "PostgreSQL, pgvector, Redis, MongoDB, Solr, SQL"),
    ("AI/LLM",      "LLM routing, Embeddings (OpenAI, Azure, Anthropic, Vertex, Cohere), RAG, FAISS, Presidio, spaCy"),
    ("Infra",       "RabbitMQ, Docker, Kubernetes, GCP, GitLab CI/CD, JWT, OAuth2"),
    ("Observability", "Grafana, Prometheus, Kibana, Structured Logging"),
]

# Priority weight per focus tag -> skill row index
_SKILL_FOCUS = {
    "Languages":     ["python"],
    "Backend":       ["fastapi", "api", "backend", "architecture", "rabbitmq", "distributed"],
    "Data":          ["postgresql", "database", "optimization", "performance"],
    "AI/LLM":        ["llm", "ai", "embeddings", "ml", "hipaa"],
    "Infra":         ["devops", "cloud", "auth", "security", "reliability"],
    "Observability": ["monitoring", "observability"],
}

# Each bullet: (text, [tags])
# ATS rule: keep each bullet under 180 chars; start with an action verb; include numbers.
WEBMD_BULLETS = [
    # Performance & Scale
    ("Resolved 6 concurrent performance bottlenecks under a 2M-document load test: async locking, TCP reuse, GC safety, bulk CTE deletes, connection cleanup, and logger crash fix",
     ["performance", "distributed", "postgresql", "optimization", "reliability"]),
    ("Reduced database round-trips to 3 for any batch size via bulk unnest() inserts (delete + doc + chunk/embedding in one transaction)",
     ["database", "performance", "postgresql", "optimization"]),
    ("Eliminated pod restarts under load by integrating tenacity retry logic (3 attempts, exponential backoff 1s-8s) for transient 502/503/504 errors",
     ["reliability", "distributed", "backend", "performance"]),
    # Architecture & Pipeline
    ("Built pgvector storage backend from scratch: asyncpg, HNSW index, schema-per-business-unit multi-tenant routing, and GIN full-text index",
     ["database", "postgresql", "architecture", "backend"]),
    ("Designed RabbitMQ batch pipeline: in-memory buffer with configurable flush on BATCH_SIZE or interval; idempotent dedup across 6 composite fields",
     ["distributed", "backend", "architecture", "rabbitmq", "performance"]),
    ("Designed multi-backend storage routing (pgvector + Solr) by business unit via env config, with per-backend failure isolation",
     ["distributed", "database", "backend", "architecture"]),
    ("Implemented retrieval_mode field (chunk/segment/document) stored across pgvector and Solr, controlling how content surfaces at query time",
     ["backend", "database", "api", "architecture"]),
    ("Implemented delete-flag routing on ingest payloads triggering composite-key deletion across all storage backends",
     ["backend", "api", "distributed", "architecture"]),
    # LLM / AI
    ("Built multi-provider LLM and embedding routing (OpenAI, Azure, Anthropic, Vertex, Cohere) with model-aware batching grouped by embedding model",
     ["llm", "ai", "embeddings", "ml", "performance"]),
    ("Built HIPAA-compliant PII anonymization service (FastAPI + Presidio + spaCy) on Kubernetes - patched CVEs and resolved security vulnerabilities for compliance",
     ["llm", "ai", "security", "fastapi", "hipaa"]),
    # Ops & Observability
    ("Drove end-to-end deployments across 5 environments (DevInt, QA, Staging, Production, HIPAA) for athena-vector-processor and athena-ingestion-service",
     ["devops", "backend", "reliability"]),
    ("Built Grafana dashboards for production monitoring and designed structured logging spec with document/chunk identifiers across the pipeline",
     ["observability", "monitoring", "backend"]),
    ("Built JWT-secured REST APIs with Helios OAuth2 for authenticated multi-tenant content processing",
     ["api", "security", "backend", "auth"]),
]

NOMBA_BULLETS = [
    ("Reduced GCP infrastructure costs by 25% through caching strategy and service-level optimization",
     ["cloud", "backend", "performance", "optimization"]),
    ("Built a high-volume CSV export pipeline backed by MongoDB aggregation and Redis caching",
     ["backend", "database", "python"]),
]

PCU_BULLETS = [
    ("Trained 20+ faculty on AI tools (ChatGPT, Claude), improving team productivity by ~40%",
     ["ai", "llm"]),
]

PROJECTS = [
    {
        "name": "Scalable Notification Service",
        "link": "github.com/kareemadesola/scalable-notification-service",
        "date": "May 2026 - Present",
        "stack": "FastAPI, RabbitMQ, Redis, PostgreSQL, Docker, Prometheus, Grafana",
        "bullets": [
            ("Production-grade multi-channel notification system (email, SMS, push, WebSocket) with independent channel scaling and dead-letter queues",
             ["backend", "distributed", "rabbitmq", "architecture"]),
            ("Built Redis rate limiting and Prometheus + Grafana observability stack; designed for ~17K notifications/sec throughput",
             ["performance", "monitoring", "observability", "redis"]),
        ],
        "tags": ["backend", "distributed", "rabbitmq", "redis", "performance", "architecture"],
    },
    {
        "name": "AI Investigation and Research Assistant",
        "link": "github.com/kareemadesola/ai-investigation-assistant",
        "date": "Apr 2026",
        "stack": "Python, FAISS, RAG, Agentic pipeline",
        "bullets": [
            ("Agentic RAG system combining FAISS vector search, multi-step reasoning, and a hallucination detection evaluation layer",
             ["ai", "llm", "rag", "ml"]),
        ],
        "tags": ["ai", "llm", "rag", "ml", "python"],
    },
    {
        "name": "Physiotherapy Recommendation System",
        "link": "github.com/kareemadesola/bsc_csc_project",
        "date": "2023 (BSc Final Year Project)",
        "stack": "Python, scikit-learn, Flask, Docker, Render",
        "bullets": [
            ("Random Forest classifier on MIMIC-IV arthritis case notes - 4 exercise classes, 5,045-sample test set, 100% accuracy and AUC-ROC",
             ["ml", "ai", "python"]),
        ],
        "tags": ["ml", "ai", "python", "backend"],
    },
]

EDUCATION = {
    "school": "Obafemi Awolowo University, Ile-Ife, Nigeria",
    "degree": "BSc Computer Science with Mathematics - First Class Honours (GPA: 4.62)",
    "date": "Aug 2023",
    "extra": "Scholarships: NNPC-CHEVRON National University Scholarship, Adewale Obadimu Scholarship",
}

CERTIFICATIONS = "HackerRank: Java (2024), REST API (2023), Problem Solving (2023), Python (2022)"


# ─────────────────────────────────────────────
# TAILORING LOGIC
# ─────────────────────────────────────────────

def _focus_set(focus_keywords: list[str]) -> set[str]:
    return set(focus_keywords)


def build_summary(role: str, focus: list[str]) -> str:
    """Construct a targeted summary from focus keywords. Every field is dynamic."""
    f = _focus_set(focus)

    # Opening — always anchor on 2+ years + Python
    opening = "Backend Software Engineer with 2+ years of production Python experience"

    # Specialization clause — pick up to 2 most relevant phrases
    specs = []
    if f & {"llm", "ai", "ml", "embeddings"}:
        specs.append("LLM-powered platforms and AI/ML pipelines")
    if f & {"distributed", "rabbitmq"}:
        specs.append("event-driven distributed systems")
    if f & {"performance", "optimization"}:
        specs.append("high-throughput data engineering")
    if f & {"postgresql", "database"} and "llm" not in f:
        specs.append("scalable database backends (pgvector, PostgreSQL)")
    if f & {"security", "hipaa"}:
        specs.append("HIPAA-compliant and secure service design")
    if f & {"devops", "cloud"} and not (f & {"llm", "distributed"}):
        specs.append("cloud infrastructure and production operations")
    if f & {"fastapi", "api"} and not specs:
        specs.append("FastAPI REST service design")

    if specs:
        spec_clause = ", specializing in " + " and ".join(specs[:2])
    else:
        spec_clause = ", specializing in distributed pipelines, high-throughput systems, and API design"

    # Proof point — pick the most relevant achievement
    achievements = []
    if f & {"performance", "optimization", "distributed", "reliability"}:
        achievements.append(
            "resolved 6 concurrent performance bottlenecks under a 2M-document load test"
        )
    if f & {"llm", "ai", "embeddings"}:
        achievements.append(
            "implemented multi-provider LLM and embedding routing across 5 AI providers"
        )
    if f & {"postgresql", "database"}:
        achievements.append(
            "built pgvector storage with HNSW indexing and multi-tenant schema routing"
        )
    if f & {"security", "hipaa"}:
        achievements.append(
            "deployed a HIPAA-compliant PII anonymization service on Kubernetes"
        )
    if f & {"devops", "cloud"}:
        achievements.append(
            "drove deployments across 5 environments including Production and HIPAA clusters"
        )
    if not achievements:
        achievements.append(
            "owned the full Athena vector ingestion pipeline from design to production"
        )

    proof = "At WebMD, " + "; ".join(achievements[:2]) + "."

    # Closing — always highlight breadth
    closing = "Strong in system design, API architecture, and engineering for production scale."

    return f"{opening}{spec_clause}. {proof} {closing}"


def reorder_skills(focus: list[str]) -> list[tuple[str, str]]:
    """Return SKILLS re-sorted so most relevant categories appear first."""
    f = _focus_set(focus)
    scored = []
    for label, value in SKILLS:
        relevant_tags = _SKILL_FOCUS.get(label, [])
        score = sum(1 for tag in relevant_tags if tag in f)
        scored.append((score, label, value))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(label, value) for _, label, value in scored]


def score_bullet(bullet_tags: list[str], focus_keywords: list[str]) -> int:
    if not focus_keywords:
        return 1
    return sum(1 for kw in focus_keywords if any(kw in tag for tag in bullet_tags))


def select_bullets(bullet_list, focus_keywords, min_count=3, max_count=6):
    if not focus_keywords:
        return [b[0] for b in bullet_list[:max_count]]
    scored = [(score_bullet(b[1], focus_keywords), b[0]) for b in bullet_list]
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [text for s, text in scored if s > 0]
    if len(selected) < min_count:
        remaining = [text for s, text in scored if s == 0]
        selected.extend(remaining[:min_count - len(selected)])
    return selected[:max_count]


def select_projects(focus_keywords, max_projects=2):
    if not focus_keywords:
        return PROJECTS[:max_projects]
    scored = []
    for p in PROJECTS:
        score = sum(1 for kw in focus_keywords if any(kw in tag for tag in p["tags"]))
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:max_projects]]


# ─────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────

def build_styles():
    name_style = ParagraphStyle(
        "Name", fontSize=16, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=2,
    )
    contact_style = ParagraphStyle(
        "Contact", fontSize=8, fontName="Helvetica",
        alignment=TA_CENTER, spaceAfter=5, leading=12,
    )
    section_style = ParagraphStyle(
        "Section", fontSize=10, fontName="Helvetica-Bold",
        spaceBefore=6, spaceAfter=2, textColor=colors.black,
    )
    body_style = ParagraphStyle(
        "Body", fontSize=8.8, fontName="Helvetica",
        spaceAfter=2, leading=12,
    )
    bullet_style = ParagraphStyle(
        "Bullet", fontSize=8.8, fontName="Helvetica",
        spaceAfter=1.5, leftIndent=10, leading=12,
    )
    job_header_style = ParagraphStyle(
        "JobHeader", fontSize=9.5, fontName="Helvetica-Bold",
        spaceAfter=1, spaceBefore=4,
    )
    job_meta_style = ParagraphStyle(
        "JobMeta", fontSize=8, fontName="Helvetica-Oblique",
        spaceAfter=2,
    )
    return {
        "name": name_style,
        "contact": contact_style,
        "section": section_style,
        "body": body_style,
        "bullet": bullet_style,
        "job_header": job_header_style,
        "job_meta": job_meta_style,
    }


def hr():
    return HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceAfter=3, spaceBefore=0)


def thin_hr():
    return HRFlowable(width="100%", thickness=0.3, color=colors.grey, spaceAfter=3, spaceBefore=0)


def generate_resume(company="", role="", focus_keywords=None, output_path=None):
    focus = [kw.lower() for kw in (focus_keywords or [])]

    if not output_path:
        safe = lambda s: s.replace(" ", "_").replace("/", "-")
        name = (
            f"Adesola_Kareem_{safe(company)}_{safe(role)}.pdf"
            if company and role
            else "Adesola_Kareem_Resume_Base.pdf"
        )
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resumes", name)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.55 * inch, rightMargin=0.55 * inch,
        topMargin=0.45 * inch, bottomMargin=0.45 * inch,
    )
    s = build_styles()
    story = []

    # ── Header ─────────────────────────────────────────────────────────
    story.append(Paragraph(CONTACT["name"], s["name"]))
    story.append(Paragraph(
        f"{CONTACT['location']}  |  {CONTACT['phone']}  |  {CONTACT['email']}<br/>"
        f"{CONTACT['linkedin']}  |  {CONTACT['github']}",
        s["contact"],
    ))
    story.append(hr())

    # ── Summary ────────────────────────────────────────────────────────
    story.append(Paragraph("PROFESSIONAL SUMMARY", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(build_summary(role, focus), s["body"]))

    # ── Skills ─────────────────────────────────────────────────────────
    story.append(Paragraph("SKILLS", s["section"]))
    story.append(thin_hr())
    ordered_skills = reorder_skills(focus)
    for label, value in ordered_skills:
        story.append(Paragraph(f"<b>{label}:</b> {value}", s["body"]))

    # ── Work Experience ────────────────────────────────────────────────
    story.append(Paragraph("WORK EXPERIENCE", s["section"]))
    story.append(thin_hr())

    story.append(Paragraph("<b>WebMD</b> - Software Engineer, Backend", s["job_header"]))
    story.append(Paragraph(
        "Mar 2025 - Present  |  Python, FastAPI, RabbitMQ, pgvector, PostgreSQL, Redis, Docker, GCP",
        s["job_meta"],
    ))
    for b in select_bullets(WEBMD_BULLETS, focus, min_count=5, max_count=7):
        story.append(Paragraph(f"- {b}", s["bullet"]))

    story.append(Paragraph("<b>Nomba</b> - Software Engineer", s["job_header"]))
    story.append(Paragraph(
        "Nov 2023 - Feb 2024  |  Python, MongoDB, Redis, GCP",
        s["job_meta"],
    ))
    for b in select_bullets(NOMBA_BULLETS, focus, min_count=1, max_count=2):
        story.append(Paragraph(f"- {b}", s["bullet"]))

    story.append(Paragraph("<b>Precious Cornerstone University (NYSC)</b> - Research Assistant", s["job_header"]))
    story.append(Paragraph("Mar 2024 - Jan 2025", s["job_meta"]))
    story.append(Paragraph(f"- {PCU_BULLETS[0][0]}", s["bullet"]))

    # ── Education ──────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(
        f"<b>{EDUCATION['school']}</b>  |  {EDUCATION['date']}",
        s["job_header"],
    ))
    story.append(Paragraph(EDUCATION["degree"], s["body"]))
    story.append(Paragraph(EDUCATION["extra"], s["body"]))

    # ── Certifications ─────────────────────────────────────────────────
    story.append(Paragraph("CERTIFICATIONS", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(CERTIFICATIONS, s["body"]))

    # ── Projects ───────────────────────────────────────────────────────
    story.append(Paragraph("PROJECTS", s["section"]))
    story.append(thin_hr())
    for p in select_projects(focus):
        story.append(Paragraph(f"<b>{p['name']}</b>  |  {p['date']}", s["job_header"]))
        story.append(Paragraph(f"{p['stack']}  |  {p['link']}", s["job_meta"]))
        for b in select_bullets([(b[0], b[1]) for b in p["bullets"]], focus, min_count=1, max_count=2):
            story.append(Paragraph(f"- {b}", s["bullet"]))

    doc.build(story)
    print(f"Resume generated: {output_path}")
    return output_path


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a one-page tailored PDF resume")
    parser.add_argument("--company", default="", help="Company name")
    parser.add_argument("--role", default="", help="Role title")
    parser.add_argument("--focus", default="", help="Space-separated focus keywords")
    parser.add_argument("--output", default="", help="Override output file path")
    args = parser.parse_args()

    generate_resume(
        company=args.company,
        role=args.role,
        focus_keywords=args.focus.split() if args.focus else [],
        output_path=args.output or None,
    )
