#!/usr/bin/env python3
"""
Resume generator for Adesola Kareem.
One-page, ATS-optimised PDF. Always fits on a single page.

Usage:
    python3 generate_resume.py
    python3 generate_resume.py --company "Stripe" --role "Backend Engineer"
    python3 generate_resume.py --company "OpenAI" --role "AI Engineer" --focus "llm ai embeddings"
"""

import argparse
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


# ─────────────────────────────────────────────
# MASTER CONTENT
# ─────────────────────────────────────────────

CONTACT = {
    "name":     "ADESOLA KAREEM",
    "line1":    "Lagos, Nigeria (Open to Remote)  |  +2349070708811  |  kareemadesola1999@gmail.com",
    "line2":    "https://linkedin.com/in/adesola-kareem-686541181  |  https://github.com/kareemadesola",
}

# 4 rows — keeps skills compact while covering all ATS keywords
# Merged: Backend+Infra into one row; AI/LLM+Observability into one row
SKILLS = [
    ("Languages",        "Python (5+ yrs), JavaScript/Node.js, Java"),
    ("Backend + Infra",  "FastAPI, REST APIs, Pydantic, RabbitMQ, Docker, Kubernetes, GCP, GitLab CI/CD, JWT, OAuth2"),
    ("Data",             "PostgreSQL, pgvector, Redis, MongoDB, Solr, SQL"),
    ("AI/ML + Ops",      "LLM routing, Embeddings (OpenAI, Azure, Anthropic, Vertex, Cohere), RAG, FAISS, Presidio, Grafana, Prometheus"),
]

_SKILL_FOCUS = {
    "Languages":       ["python"],
    "Backend + Infra": ["fastapi", "api", "backend", "distributed", "rabbitmq", "devops", "cloud", "auth", "security", "reliability", "architecture"],
    "Data":            ["postgresql", "database", "optimization", "performance"],
    "AI/ML + Ops":     ["llm", "ai", "embeddings", "ml", "hipaa", "monitoring", "observability"],
}

# Bullets: (text ≤180 chars, [tags])  — all start with action verb, include numbers
WEBMD_BULLETS = [
    ("Resolved 6 concurrent performance bottlenecks under a 2M-document load test: async locking, TCP reuse, GC safety, bulk CTE deletes, connection cleanup, and logger crash fix",
     ["performance", "distributed", "postgresql", "optimization", "reliability"]),
    ("Reduced database round-trips to 3 for any batch size via bulk unnest() inserts (delete + doc + chunk/embedding in one transaction)",
     ["database", "performance", "postgresql", "optimization"]),
    ("Eliminated pod restarts under load by integrating tenacity retry logic (3 attempts, exponential backoff 1s-8s) for transient 502/503/504 errors",
     ["reliability", "distributed", "backend", "performance"]),
    ("Built pgvector storage backend from scratch: asyncpg, HNSW index, schema-per-business-unit multi-tenant routing, and GIN full-text index",
     ["database", "postgresql", "architecture", "backend"]),
    ("Designed RabbitMQ batch pipeline: in-memory buffer with configurable flush on BATCH_SIZE or interval; idempotent dedup across 6 composite fields",
     ["distributed", "backend", "architecture", "rabbitmq", "performance"]),
    ("Built multi-provider LLM and embedding routing (OpenAI, Azure, Anthropic, Vertex, Cohere) with model-aware batching grouped by embedding model",
     ["llm", "ai", "embeddings", "ml", "performance"]),
    ("Built HIPAA-compliant PII anonymization service (FastAPI + Presidio + spaCy) on Kubernetes - patched CVEs for compliance",
     ["llm", "ai", "security", "fastapi", "hipaa"]),
    ("Designed multi-backend storage routing (pgvector + Solr) by business unit via env config, with per-backend failure isolation",
     ["distributed", "database", "backend", "architecture"]),
    ("Drove end-to-end deployments across 5 environments (DevInt, QA, Staging, Production, HIPAA)",
     ["devops", "backend", "reliability"]),
    ("Built Grafana dashboards and structured logging spec with document/chunk identifiers across the pipeline",
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

PROJECTS = [
    {
        "name": "Scalable Notification Service",
        "link": "github.com/kareemadesola/scalable-notification-service",
        "date": "May 2026 - Present",
        "stack": "FastAPI, RabbitMQ, Redis, PostgreSQL, Docker, Prometheus, Grafana",
        "bullets": [
            ("Production-grade multi-channel system (email, SMS, push, WebSocket) with dead-letter queues, Redis rate limiting, and ~17K notifications/sec throughput",
             ["backend", "distributed", "rabbitmq", "redis", "performance", "architecture"]),
        ],
        "tags": ["backend", "distributed", "rabbitmq", "redis", "performance", "architecture"],
    },
    {
        "name": "AI Investigation and Research Assistant",
        "link": "github.com/kareemadesola/ai-investigation-assistant",
        "date": "Apr 2026",
        "stack": "Python, FAISS, RAG, Agentic pipeline",
        "bullets": [
            ("Agentic RAG system combining FAISS vector search, multi-step reasoning, and a hallucination detection layer",
             ["ai", "llm", "rag", "ml"]),
        ],
        "tags": ["ai", "llm", "rag", "ml", "python"],
    },
    {
        "name": "Physiotherapy Recommendation System",
        "link": "github.com/kareemadesola/bsc_csc_project",
        "date": "2023",
        "stack": "Python, scikit-learn, Flask, Docker",
        "bullets": [
            ("Random Forest classifier on 25K+ arthritis case notes - 4 exercise classes, 100% test accuracy, deployed on Render",
             ["ml", "ai", "python", "backend"]),
        ],
        "tags": ["ml", "ai", "python", "backend"],
    },
]

EDUCATION = {
    "school": "Obafemi Awolowo University, Ile-Ife, Nigeria",
    "degree": "BSc Computer Science with Mathematics - First Class Honours (GPA: 4.62/5.0)",
    "date":   "Aug 2023",
}

PCU_BULLETS = [
    ("Trained 20+ faculty on AI tools (ChatGPT, Claude), improving team productivity by ~40%",
     ["ai", "llm"]),
]

CERTIFICATIONS = "HackerRank: Java (2024), REST API (2023), Problem Solving (2023), Python (2022)"


# ─────────────────────────────────────────────
# TAILORING LOGIC
# ─────────────────────────────────────────────

def build_summary(role: str, focus: list[str]) -> str:
    """Two tight sentences: who you are + one proof point. Always fits in 2 lines."""
    f = set(focus)

    # Sentence 1 — specialization
    if f & {"llm", "ai", "ml", "embeddings"}:
        spec = "LLM-powered platforms, AI pipelines, and vector search systems"
    elif f & {"distributed", "rabbitmq"}:
        spec = "event-driven distributed systems and high-throughput data pipelines"
    elif f & {"performance", "optimization"}:
        spec = "high-throughput backend systems and performance engineering"
    elif f & {"postgresql", "database"}:
        spec = "scalable data backends (pgvector, PostgreSQL) and distributed pipelines"
    elif f & {"security", "hipaa"}:
        spec = "HIPAA-compliant services, secure API design, and backend infrastructure"
    elif f & {"devops", "cloud"}:
        spec = "backend services and cloud infrastructure (GCP, Docker, Kubernetes)"
    else:
        spec = "distributed pipelines, high-throughput data systems, and REST API design"

    s1 = f"Backend Software Engineer with 2+ years of production Python experience specializing in {spec}."

    # Sentence 2 — proof (max 2 achievements)
    proofs = []
    if f & {"performance", "distributed", "reliability", "rabbitmq"}:
        proofs.append("resolved 6 concurrent bottlenecks under a 2M-document load test")
    if f & {"llm", "ai", "embeddings"}:
        proofs.append("built multi-provider LLM and embedding routing across 5 AI providers")
    if f & {"postgresql", "database"}:
        proofs.append("built pgvector storage with HNSW indexing serving 2M+ documents")
    if f & {"security", "hipaa"}:
        proofs.append("deployed a HIPAA-compliant PII anonymization service on Kubernetes")
    if f & {"devops", "cloud"}:
        proofs.append("drove deployments across 5 environments including Production and HIPAA")
    if not proofs:
        proofs = ["owned the full Athena AI ingestion pipeline from design through production and HIPAA deployments"]

    s2 = "At WebMD, " + "; ".join(proofs[:2]) + "."

    return f"{s1} {s2}"


def reorder_skills(focus: list[str]) -> list[tuple[str, str]]:
    f = set(focus)
    scored = []
    for label, value in SKILLS:
        tags = _SKILL_FOCUS.get(label, [])
        score = sum(1 for t in tags if t in f)
        scored.append((score, label, value))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(lbl, val) for _, lbl, val in scored]


def score_bullet(tags: list[str], focus: list[str]) -> int:
    if not focus:
        return 1
    return sum(1 for kw in focus if any(kw in t for t in tags))


def select_bullets(bullet_list, focus, min_count=3, max_count=5):
    if not focus:
        return [b[0] for b in bullet_list[:max_count]]
    scored = [(score_bullet(b[1], focus), b[0]) for b in bullet_list]
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [t for s, t in scored if s > 0]
    if len(selected) < min_count:
        selected += [t for s, t in scored if s == 0][:min_count - len(selected)]
    return selected[:max_count]


def select_projects(focus, max_projects=2):
    if not focus:
        return PROJECTS[:max_projects]
    scored = [(sum(1 for kw in focus if any(kw in t for t in p["tags"])), p) for p in PROJECTS]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:max_projects]]


# ─────────────────────────────────────────────
# PDF STYLES  (tuned to guarantee 1 page)
# ─────────────────────────────────────────────

def build_styles():
    return {
        "name": ParagraphStyle(
            "Name", fontSize=15, fontName="Helvetica-Bold",
            alignment=TA_CENTER, spaceAfter=1,
        ),
        "contact": ParagraphStyle(
            "Contact", fontSize=7.5, fontName="Helvetica",
            alignment=TA_CENTER, spaceAfter=4, leading=11,
        ),
        "section": ParagraphStyle(
            "Section", fontSize=9, fontName="Helvetica-Bold",
            spaceBefore=4, spaceAfter=1,
        ),
        "body": ParagraphStyle(
            "Body", fontSize=8.5, fontName="Helvetica",
            spaceAfter=1.5, leading=11,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontSize=8.5, fontName="Helvetica",
            spaceAfter=1, leftIndent=9, leading=11,
        ),
        "job_header": ParagraphStyle(
            "JobHeader", fontSize=9, fontName="Helvetica-Bold",
            spaceAfter=0, spaceBefore=3,
        ),
        "job_meta": ParagraphStyle(
            "JobMeta", fontSize=7.5, fontName="Helvetica-Oblique",
            spaceAfter=1.5, leading=10,
        ),
    }


def hr():
    return HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceAfter=2, spaceBefore=0)

def thin_hr():
    return HRFlowable(width="100%", thickness=0.3, color=colors.grey, spaceAfter=2, spaceBefore=0)


# ─────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────

def generate_resume(company="", role="", focus_keywords=None, output_path=None):
    focus = [kw.lower() for kw in (focus_keywords or [])]

    if not output_path:
        safe = lambda s: s.replace(" ", "_").replace("/", "-")
        fname = (
            f"Adesola_Kareem_{safe(company)}_{safe(role)}.pdf"
            if company and role else
            "Adesola_Kareem_Resume_Base.pdf"
        )
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resumes", fname)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch,
        topMargin=0.42 * inch, bottomMargin=0.42 * inch,
    )
    s = build_styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────
    story.append(Paragraph(CONTACT["name"], s["name"]))
    story.append(Paragraph(CONTACT["line1"], s["contact"]))
    story.append(Paragraph(CONTACT["line2"], s["contact"]))
    story.append(hr())

    # ── Summary ─────────────────────────────────────────────────────────
    story.append(Paragraph("PROFESSIONAL SUMMARY", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(build_summary(role, focus), s["body"]))

    # ── Skills ──────────────────────────────────────────────────────────
    story.append(Paragraph("SKILLS", s["section"]))
    story.append(thin_hr())
    for label, value in reorder_skills(focus):
        story.append(Paragraph(f"<b>{label}:</b> {value}", s["body"]))

    # ── Work Experience ──────────────────────────────────────────────────
    story.append(Paragraph("WORK EXPERIENCE", s["section"]))
    story.append(thin_hr())

    story.append(Paragraph("<b>WebMD</b> - Software Engineer, Backend", s["job_header"]))
    story.append(Paragraph(
        "Mar 2025 - Present  |  Python, FastAPI, RabbitMQ, pgvector, PostgreSQL, Redis, Docker, GCP",
        s["job_meta"],
    ))
    for b in select_bullets(WEBMD_BULLETS, focus, min_count=4, max_count=5):
        story.append(Paragraph(f"- {b}", s["bullet"]))

    story.append(Paragraph("<b>Nomba</b> - Software Engineer", s["job_header"]))
    story.append(Paragraph("Nov 2023 - Feb 2024  |  Python, MongoDB, Redis, GCP", s["job_meta"]))
    for b in select_bullets(NOMBA_BULLETS, focus, min_count=1, max_count=2):
        story.append(Paragraph(f"- {b}", s["bullet"]))

    story.append(Paragraph("<b>Precious Cornerstone University (NYSC)</b> - Research Assistant", s["job_header"]))
    story.append(Paragraph("Mar 2024 - Jan 2025", s["job_meta"]))
    story.append(Paragraph(f"- {PCU_BULLETS[0][0]}", s["bullet"]))

    # ── Education ────────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(
        f"<b>{EDUCATION['school']}</b>  |  {EDUCATION['date']}", s["job_header"],
    ))
    story.append(Paragraph(EDUCATION["degree"], s["body"]))

    # ── Certifications ───────────────────────────────────────────────────
    story.append(Paragraph("CERTIFICATIONS", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(CERTIFICATIONS, s["body"]))

    # ── Projects ─────────────────────────────────────────────────────────
    story.append(Paragraph("PROJECTS", s["section"]))
    story.append(thin_hr())
    for p in select_projects(focus, max_projects=2):
        story.append(Paragraph(f"<b>{p['name']}</b>  |  {p['date']}", s["job_header"]))
        story.append(Paragraph(f"{p['stack']}  |  {p['link']}", s["job_meta"]))
        for b in select_bullets(p["bullets"], focus, min_count=1, max_count=1):
            story.append(Paragraph(f"- {b}", s["bullet"]))

    doc.build(story)
    print(f"Resume generated: {output_path}")
    return output_path


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", default="")
    parser.add_argument("--role", default="")
    parser.add_argument("--focus", default="")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    generate_resume(
        company=args.company,
        role=args.role,
        focus_keywords=args.focus.split() if args.focus else [],
        output_path=args.output or None,
    )
