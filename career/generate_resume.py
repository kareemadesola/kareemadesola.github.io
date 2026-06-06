#!/usr/bin/env python3
"""
Resume generator for Adesola Kareem.
Layout mirrors the Google Docs template: dates right-aligned, thick section rules,
bullet char •, Projects before Education. Always fits on one page.

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
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors


# ─────────────────────────────────────────────
# MASTER CONTENT
# ─────────────────────────────────────────────

CONTACT = {
    "name":  "ADESOLA KAREEM",
    "line1": "Lagos, Nigeria  |  +2349070708811  |  kareemadesola1999@gmail.com",
    "line2": "linkedin.com/in/adesola-kareem-686541181  |  github.com/kareemadesola",
}

SKILLS = [
    ("Languages",       "Python (5+ yrs), JavaScript/Node.js, Java"),
    ("Backend + Infra", "FastAPI, REST APIs, Pydantic, RabbitMQ, Docker, Kubernetes, GCP, GitLab CI/CD, JWT, OAuth2"),
    ("Data",            "PostgreSQL (pgvector), Redis, MongoDB, Solr, SQL"),
    ("AI/ML + Ops",     "LLM routing, Embeddings (OpenAI, Azure, Anthropic, Vertex, Cohere), RAG, FAISS, Presidio, Grafana, Prometheus"),
]

_SKILL_FOCUS = {
    "Languages":       ["python"],
    "Backend + Infra": ["fastapi", "api", "backend", "distributed", "rabbitmq", "devops", "cloud", "auth", "security", "reliability", "architecture"],
    "Data":            ["postgresql", "database", "optimization", "performance"],
    "AI/ML + Ops":     ["llm", "ai", "embeddings", "ml", "hipaa", "monitoring", "observability"],
}

# Bullets: (text ≤180 chars, [tags]) — action verb, quantified
WEBMD_BULLETS = [
    ("Resolved 6 concurrent performance bottlenecks under a 2M-document load test: async locking, TCP reuse, GC safety, bulk CTE deletes, connection cleanup, and logger crash fix",
     ["performance", "distributed", "postgresql", "optimization", "reliability"]),
    ("Reduced database round-trips to 3 for any batch size via bulk unnest() inserts (delete + doc + chunk/embedding in one transaction)",
     ["database", "performance", "postgresql", "optimization"]),
    ("Eliminated pod restarts under load by integrating tenacity retry logic (3 attempts, exponential backoff 1s–8s) for transient 502/503/504 errors",
     ["reliability", "distributed", "backend", "performance"]),
    ("Built pgvector storage backend from scratch: asyncpg, HNSW index, schema-per-business-unit multi-tenant routing, and GIN full-text index",
     ["database", "postgresql", "architecture", "backend"]),
    ("Designed RabbitMQ batch pipeline: in-memory buffer with configurable flush on BATCH_SIZE or interval; idempotent dedup across 6 composite fields",
     ["distributed", "backend", "architecture", "rabbitmq", "performance"]),
    ("Built multi-provider LLM and embedding routing (OpenAI, Azure, Anthropic, Vertex, Cohere) with model-aware batching grouped by embedding model",
     ["llm", "ai", "embeddings", "ml", "performance"]),
    ("Built HIPAA-compliant PII anonymization service (FastAPI + Presidio + spaCy) on Kubernetes — patched CVEs for compliance",
     ["llm", "ai", "security", "fastapi", "hipaa"]),
    ("Designed multi-backend storage routing (pgvector + Solr) by business unit with per-backend failure isolation",
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

PCU_BULLETS = [
    ("Trained 20+ faculty on AI tools (ChatGPT, Claude), improving team productivity by ~40%",
     ["ai", "llm"]),
]

PROJECTS = [
    {
        "name": "Scalable Notification Service",
        "link": "github.com/kareemadesola/scalable-notification-service",
        "date": "May 2026 – Present",
        "stack": "FastAPI · RabbitMQ · Redis · PostgreSQL · Docker · Prometheus · Grafana",
        "bullets": [
            ("Built production-grade multi-channel system (email, SMS, push, WebSocket) with dead-letter queues, Redis rate limiting, and ~17K notifications/sec throughput",
             ["backend", "distributed", "rabbitmq", "redis", "performance", "architecture"]),
        ],
        "tags": ["backend", "distributed", "rabbitmq", "redis", "performance", "architecture"],
    },
    {
        "name": "AI Investigation and Research Assistant",
        "link": "github.com/kareemadesola/ai-investigation-assistant",
        "date": "Apr 2026",
        "stack": "Python · FAISS · RAG · Agentic pipeline",
        "bullets": [
            ("Agentic RAG system combining FAISS vector search, multi-step reasoning, and a hallucination detection evaluation layer",
             ["ai", "llm", "rag", "ml"]),
        ],
        "tags": ["ai", "llm", "rag", "ml", "python"],
    },
    {
        "name": "Physiotherapy Recommendation System",
        "link": "github.com/kareemadesola/bsc_csc_project",
        "date": "2023",
        "stack": "Python · scikit-learn · Flask · Docker",
        "bullets": [
            ("Random Forest classifier on 25K+ arthritis case notes — 4 exercise classes, 100% test accuracy, deployed on Render",
             ["ml", "ai", "python", "backend"]),
        ],
        "tags": ["ml", "ai", "python", "backend"],
    },
]

EDUCATION = {
    "school": "Obafemi Awolowo University, Ile-Ife, Nigeria",
    "degree": "BSc Computer Science with Mathematics — First Class Honours (GPA: 4.62/5.0)",
    "date":   "Aug 2023",
}

CERTIFICATIONS = "HackerRank: Java (2024), REST API (2023), Problem Solving (2023), Python (2022)"


# ─────────────────────────────────────────────
# TAILORING LOGIC
# ─────────────────────────────────────────────

def build_summary(role: str, focus: list[str]) -> str:
    f = set(focus)

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
    scored = [(sum(1 for t in _SKILL_FOCUS.get(lbl, []) if t in f), lbl, val) for lbl, val in SKILLS]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(lbl, val) for _, lbl, val in scored]


def score_bullet(tags, focus):
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
# STYLES
# ─────────────────────────────────────────────

# Usable content width: letter (8.5in) minus 0.5in margins each side = 7.5in = 540pt
_CONTENT_W = 7.5 * inch


def build_styles():
    return {
        "name": ParagraphStyle(
            "Name", fontSize=17, fontName="Helvetica-Bold",
            alignment=TA_CENTER, leading=22, spaceAfter=3,
        ),
        "contact": ParagraphStyle(
            "Contact", fontSize=8, fontName="Helvetica",
            alignment=TA_CENTER, leading=11, spaceAfter=2,
        ),
        "section": ParagraphStyle(
            "Section", fontSize=10, fontName="Helvetica-Bold",
            spaceBefore=5, spaceAfter=1,
        ),
        "body": ParagraphStyle(
            "Body", fontSize=8.8, fontName="Helvetica",
            spaceAfter=2, leading=11.5,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontSize=8.8, fontName="Helvetica",
            spaceAfter=1.2, leftIndent=10, leading=11.5,
        ),
        # Left cell of job header row (bold title)
        "job_title": ParagraphStyle(
            "JobTitle", fontSize=9.5, fontName="Helvetica-Bold",
            spaceAfter=0, spaceBefore=0, leading=12,
        ),
        # Right cell of job header row (date)
        "job_date": ParagraphStyle(
            "JobDate", fontSize=8.5, fontName="Helvetica",
            alignment=TA_RIGHT, spaceAfter=0, spaceBefore=0, leading=12,
        ),
        "job_meta": ParagraphStyle(
            "JobMeta", fontSize=8, fontName="Helvetica-Oblique",
            spaceAfter=2, leading=10,
        ),
    }


def section_rule():
    """Thick rule that follows a section header — matches Google Docs style."""
    return HRFlowable(width="100%", thickness=0.75, color=colors.black, spaceAfter=3, spaceBefore=0)


def job_row(title: str, date: str, s: dict) -> Table:
    """Company/title on the left, date right-aligned — same line."""
    t = Table(
        [[Paragraph(title, s["job_title"]), Paragraph(date, s["job_date"])]],
        colWidths=[_CONTENT_W - 1.55 * inch, 1.55 * inch],
        spaceBefore=4,
    )
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return t


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
        topMargin=0.45 * inch, bottomMargin=0.45 * inch,
    )
    s = build_styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────
    story.append(Paragraph(CONTACT["name"], s["name"]))
    story.append(Paragraph(CONTACT["line1"], s["contact"]))
    story.append(Paragraph(CONTACT["line2"], s["contact"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=colors.black, spaceAfter=4, spaceBefore=2))

    # ── Summary ─────────────────────────────────────────────────────────
    story.append(Paragraph("PROFESSIONAL SUMMARY", s["section"]))
    story.append(section_rule())
    story.append(Paragraph(build_summary(role, focus), s["body"]))

    # ── Skills ──────────────────────────────────────────────────────────
    story.append(Paragraph("SKILLS", s["section"]))
    story.append(section_rule())
    for label, value in reorder_skills(focus):
        story.append(Paragraph(f"<b>{label}:</b> {value}", s["body"]))

    # ── Work Experience ──────────────────────────────────────────────────
    story.append(Paragraph("WORK EXPERIENCE", s["section"]))
    story.append(section_rule())

    story.append(job_row("WebMD — Software Engineer (Backend)", "Mar 2025 – Present", s))
    story.append(Paragraph(
        "Python · FastAPI · RabbitMQ · pgvector · PostgreSQL · Redis · Docker · GCP",
        s["job_meta"],
    ))
    for b in select_bullets(WEBMD_BULLETS, focus, min_count=4, max_count=5):
        story.append(Paragraph(f"• {b}", s["bullet"]))

    story.append(job_row("Nomba — Software Engineer", "Nov 2023 – Feb 2024", s))
    story.append(Paragraph("Python · MongoDB · Redis · GCP", s["job_meta"]))
    for b in select_bullets(NOMBA_BULLETS, focus, min_count=1, max_count=2):
        story.append(Paragraph(f"• {b}", s["bullet"]))

    story.append(job_row("Precious Cornerstone University (NYSC) — Research Assistant", "Mar 2024 – Jan 2025", s))
    story.append(Paragraph(f"• {PCU_BULLETS[0][0]}", s["bullet"]))

    # ── Projects ─────────────────────────────────────────────────────────
    story.append(Paragraph("PROJECTS", s["section"]))
    story.append(section_rule())
    for p in select_projects(focus, max_projects=2):
        story.append(job_row(p["name"], p["date"], s))
        story.append(Paragraph(f"{p['stack']}  |  {p['link']}", s["job_meta"]))
        for b in select_bullets(p["bullets"], focus, min_count=1, max_count=1):
            story.append(Paragraph(f"• {b}", s["bullet"]))

    # ── Education ────────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", s["section"]))
    story.append(section_rule())
    story.append(job_row(EDUCATION["school"], EDUCATION["date"], s))
    story.append(Paragraph(EDUCATION["degree"], s["body"]))

    # ── Certifications ───────────────────────────────────────────────────
    story.append(Paragraph("CERTIFICATIONS", s["section"]))
    story.append(section_rule())
    story.append(Paragraph(CERTIFICATIONS, s["body"]))

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
