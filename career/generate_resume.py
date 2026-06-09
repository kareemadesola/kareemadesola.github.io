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
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors


# ─────────────────────────────────────────────
# MASTER CONTENT
# ─────────────────────────────────────────────

CONTACT = {
    "name":  "Adesola Kareem",
    "line1": "Open to Remote (UTC+1)  |  kareemadesola1999@gmail.com",
    "line2": "linkedin.com/in/adesolakareem-686541181  |  github.com/kareemadesola",
}

SKILLS = [
    ("Languages",              "Python, TypeScript, JavaScript (Node.js), Java"),
    ("Backend & APIs",         "FastAPI, SQLAlchemy, Pydantic, Celery, REST APIs, Microservices"),
    ("Databases & Storage",    "PostgreSQL (pgvector), Redis, MongoDB, Solr"),
    ("Messaging & Async",      "RabbitMQ, Celery"),
    ("Infrastructure & DevOps","Docker, Kubernetes, GCP, GitLab CI/CD"),
    ("AI & Data",              "LLMs, Embeddings, Vector Search, FAISS, pgvector, Presidio"),
    ("Core Concepts",          "Algorithms & Data Structures, System Design, Agile Ceremonies, RFCs, ADRs, PR Reviews"),
]

_SKILL_FOCUS = {
    "Languages":               ["python"],
    "Backend & APIs":          ["fastapi", "api", "backend", "distributed", "rabbitmq", "devops", "cloud", "auth", "security", "reliability", "architecture"],
    "Databases & Storage":     ["postgresql", "database", "optimization", "performance"],
    "Messaging & Async":       ["rabbitmq", "distributed", "backend"],
    "Infrastructure & DevOps": ["devops", "cloud", "kubernetes", "docker"],
    "AI & Data":               ["llm", "ai", "embeddings", "ml", "hipaa", "monitoring", "observability"],
    "Core Concepts":           ["architecture", "backend", "reliability"],
}

# Bullets: (text ≤180 chars, [tags]) — action verb, quantified
WEBMD_BULLETS = [
    ("Resolved 6 concurrent performance bottlenecks under a 2M-document load test: async locking, TCP reuse, GC safety, bulk CTE deletes, connection cleanup, and logger crash fix",
     ["performance", "distributed", "postgresql", "optimization", "reliability"]),
    ("Reduced database round-trips to 3 for any batch size via bulk unnest() inserts (delete + doc + chunk/embedding in one transaction)",
     ["database", "performance", "postgresql", "optimization"]),
    ("Reduced pod restarts under load by integrating tenacity retry logic (3 attempts, exponential backoff 1s–8s) for transient 502/503/504 errors",
     ["reliability", "distributed", "backend", "performance"]),
    ("Designed and implemented pgvector retrieval backend: asyncpg, HNSW index, schema-per-business-unit multi-tenant routing, and GIN full-text index",
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
    ("Designed and implemented AI automation workflows, improving faculty productivity by ~40%",
     ["ai", "llm"]),
    ("Supported applied AI research initiatives and tooling development",
     ["ai", "llm"]),
]

PROJECTS = [
    {
        "name": "Scalable Notification Service",
        "link": "github.com/kareemadesola/scalable-notification-service",
        "date": "May 2026 – Present",
        "stack": "FastAPI · RabbitMQ · Redis · PostgreSQL · Docker · Prometheus · Grafana",
        "bullets": [
            ("Built distributed notification system using FastAPI, RabbitMQ, Redis, PostgreSQL",
             ["backend", "distributed", "rabbitmq", "redis", "architecture"]),
            ("Designed multi-channel delivery: email, SMS, push, and WebSocket",
             ["backend", "distributed", "architecture"]),
            ("Implemented retry logic, exponential backoff, and dead-letter queues",
             ["reliability", "distributed", "rabbitmq"]),
            ("Architected for high throughput (~17K notifications/sec)",
             ["performance", "distributed", "backend"]),
            ("Added observability via Prometheus and Grafana; enforced rate limiting",
             ["observability", "monitoring", "backend"]),
            ("Built TypeScript client SDK — typed request/response interfaces and npm package structure",
             ["backend", "api"]),
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
            ("Random Forest classifier on 25K+ arthritis case notes — 4 exercise classes, 100% holdout accuracy (5,045-sample test set), deployed on Render",
             ["ml", "ai", "python", "backend"]),
        ],
        "tags": ["ml", "ai", "python", "backend"],
    },
]

EDUCATION = {
    "school": "Obafemi Awolowo University",
    "degree": "BSc Computer Science with Mathematics — First Class (GPA: 4.62)",
    "date":   "2023",
}

CERTIFICATIONS_ANTHROPIC = (
    "Anthropic: Building with the Claude API, Intro to Model Context Protocol, "
    "MCP Advanced Topics, Claude Code 101, Claude Code in Action, "
    "AI Fluency: Framework & Foundations"
)
CERTIFICATIONS_HACKERRANK = "HackerRank: Java, REST API, Problem Solving, Python"


# ─────────────────────────────────────────────
# TAILORING LOGIC
# ─────────────────────────────────────────────

def build_summary(role: str, focus: list[str]) -> str:
    f = set(focus)

    return (
        "Backend Software Engineer with 3 years of Python engineering experience specializing in "
        "AI infrastructure and distributed systems. At WebMD, took ownership of three production "
        "microservices on the Athena AI platform — a content ingestion gateway, a RabbitMQ-driven "
        "vector embedding worker, and a HIPAA-compliant PII anonymization service — while "
        "contributing to an OpenAI-compatible LLM routing API, deployed across 5 environments "
        "including HIPAA."
    )


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

# ── Colours ───────────────────────────────────
_BLUE = colors.HexColor("#1F4E79")
_DARK = colors.HexColor("#1A1A1A")
_GRAY = colors.HexColor("#555555")

_LEFT_MARGIN  = 0.55 * inch
_RIGHT_MARGIN = 0.55 * inch
# Inner frame width: letter minus margins minus 6pt frame padding on each side
_CONTENT_W = 8.5 * inch - _LEFT_MARGIN - _RIGHT_MARGIN - 12


def build_styles():
    return {
        "name": ParagraphStyle(
            "Name", fontSize=22, fontName="Helvetica-Bold",
            alignment=TA_CENTER, leading=27, spaceAfter=2,
            textColor=_BLUE,
        ),
        "contact": ParagraphStyle(
            "Contact", fontSize=8, fontName="Helvetica",
            alignment=TA_CENTER, leading=11, spaceAfter=1,
            textColor=_GRAY,
        ),
        "section": ParagraphStyle(
            "Section", fontSize=10, fontName="Helvetica-Bold",
            spaceBefore=5, spaceAfter=0,
            textColor=_BLUE,
        ),
        "body": ParagraphStyle(
            "Body", fontSize=8.5, fontName="Helvetica",
            spaceAfter=1, leading=11,
            textColor=_DARK,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontSize=8.5, fontName="Helvetica",
            spaceAfter=0.8, leftIndent=12, leading=11,
            textColor=_DARK,
        ),
        "job_title": ParagraphStyle(
            "JobTitle", fontSize=9.5, fontName="Helvetica-Bold",
            spaceAfter=0, spaceBefore=0, leading=12,
            textColor=_DARK,
        ),
        "job_date": ParagraphStyle(
            "JobDate", fontSize=8.5, fontName="Helvetica",
            alignment=TA_RIGHT, spaceAfter=0, spaceBefore=0, leading=12,
            textColor=_GRAY,
        ),
        "job_company": ParagraphStyle(
            "JobCompany", fontSize=8.5, fontName="Helvetica-Oblique",
            spaceAfter=1, leading=10,
            textColor=_GRAY,
        ),
        "job_meta": ParagraphStyle(
            "JobMeta", fontSize=7.5, fontName="Helvetica-Oblique",
            spaceAfter=1, leading=9,
            textColor=_GRAY,
        ),
    }


def section_rule():
    return HRFlowable(width="100%", thickness=0.75, color=_BLUE, spaceAfter=2, spaceBefore=0)


def job_row(title: str, date: str, s: dict) -> Table:
    """Job title left (bold dark), date right-aligned (gray) — same line."""
    t = Table(
        [[Paragraph(title, s["job_title"]), Paragraph(date, s["job_date"])]],
        colWidths=[_CONTENT_W - 1.4 * inch, 1.4 * inch],
        spaceBefore=5,
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
        leftMargin=_LEFT_MARGIN, rightMargin=_RIGHT_MARGIN,
        topMargin=0.4 * inch, bottomMargin=0.4 * inch,
    )
    s = build_styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────
    story.append(Paragraph(CONTACT["name"], s["name"]))
    story.append(Paragraph(CONTACT["line1"], s["contact"]))
    story.append(Paragraph(CONTACT["line2"], s["contact"]))

    # ── Summary ─────────────────────────────────────────────────────────
    story.append(Paragraph("SUMMARY", s["section"]))
    story.append(section_rule())
    story.append(Paragraph(build_summary(role, focus), s["body"]))

    # ── Skills ──────────────────────────────────────────────────────────
    story.append(Paragraph("TECHNICAL SKILLS", s["section"]))
    story.append(section_rule())
    for label, value in reorder_skills(focus):
        story.append(Paragraph(f"<b>{label}:</b> {value}", s["body"]))

    # ── Work Experience ──────────────────────────────────────────────────
    story.append(Paragraph("EXPERIENCE", s["section"]))
    story.append(section_rule())

    story.append(job_row("Backend Software Engineer", "Mar 2025 – Present", s))
    story.append(Paragraph("WebMD (Internet Brands)", s["job_company"]))
    for b in select_bullets(WEBMD_BULLETS, focus, min_count=6, max_count=7):
        story.append(Paragraph(f"• {b}", s["bullet"]))

    story.append(job_row("Software Engineer", "Nov 2023 – Feb 2024", s))
    story.append(Paragraph("Nomba (Fintech)", s["job_company"]))
    for b in select_bullets(NOMBA_BULLETS, focus, min_count=2, max_count=2):
        story.append(Paragraph(f"• {b}", s["bullet"]))

    story.append(job_row("Research Assistant", "Mar 2024 – Jan 2025", s))
    story.append(Paragraph("Precious Cornerstone University", s["job_company"]))
    for b in PCU_BULLETS:
        story.append(Paragraph(f"• {b[0]}", s["bullet"]))

    # ── Projects ─────────────────────────────────────────────────────────
    story.append(Paragraph("PROJECTS", s["section"]))
    story.append(section_rule())
    for p in select_projects(focus, max_projects=1):
        story.append(Paragraph(
            f'<b>{p["name"]}</b>  <font color="#555555" size="8">— {p["link"]}</font>',
            s["job_title"],
        ))
        for b in p["bullets"]:
            story.append(Paragraph(f"• {b[0]}", s["bullet"]))

    # ── Education ────────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", s["section"]))
    story.append(section_rule())
    story.append(job_row(EDUCATION["degree"], EDUCATION["date"], s))
    story.append(Paragraph(EDUCATION["school"], s["job_company"]))

    # ── Certifications ───────────────────────────────────────────────────
    story.append(Paragraph("CERTIFICATIONS", s["section"]))
    story.append(section_rule())
    story.append(Paragraph(CERTIFICATIONS_ANTHROPIC, s["body"]))
    story.append(Paragraph(CERTIFICATIONS_HACKERRANK, s["body"]))

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
