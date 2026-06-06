#!/usr/bin/env python3
"""
Resume generator for Adesola Kareem.
Generates a one-page tailored PDF using the Google Docs resume structure.

Usage:
    python3 generate_resume.py --company "Acme Corp" --role "Backend Engineer"
    python3 generate_resume.py --company "Acme Corp" --role "Backend Engineer" --focus "python fastapi llm"
    python3 generate_resume.py  # generates base resume
"""

import argparse
import os
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors


# ─────────────────────────────────────────────
# MASTER CONTENT — edit this section to update
# ─────────────────────────────────────────────

CONTACT = {
    "name": "ADESOLA KAREEM",
    "location": "Lagos, Nigeria",
    "phone": "+2349070708811",
    "email": "kareemadesola1999@gmail.com",
    "linkedin": "linkedin.com/in/adesola-kareem-686541181",
    "github": "github.com/kareemadesola",
}

SUMMARY = (
    "Backend Software Engineer with 2+ years of production Python experience, specializing in "
    "distributed pipelines, high-throughput data systems, and LLM-powered platforms. "
    "At WebMD, owned the full Athena vector ingestion pipeline — designed pgvector storage, "
    "resolved 6 performance bottlenecks under a 2M-document load test, and drove deployments "
    "across DevInt, QA, Staging, Production, and HIPAA environments. "
    "Strong foundation in system design, API architecture, and observability."
)

SKILLS = [
    ("Languages", "Python (5+ yrs), JavaScript/Node.js, Java"),
    ("Backend", "FastAPI, REST APIs, Pydantic, JSON Schema, Express.js, Microservices, Event-Driven Architecture"),
    ("Data", "PostgreSQL (pgvector), Redis, MongoDB, Solr"),
    ("Infra", "RabbitMQ, Docker, GCP, GitLab CI/CD, JWT/OAuth2"),
    ("AI/LLM", "LLM routing, embeddings (OpenAI, Azure, Anthropic, Vertex, Cohere), RAG, FAISS, PII anonymization"),
]

# Each bullet has tags for focus-based filtering
WEBMD_BULLETS = [
    # Performance & Scale
    ("Resolved 6 concurrent performance bottlenecks under a 2M-document load test: async double-checked locking, TCP connection reuse (eliminating per-request TLS handshakes), background task GC safety, bulk DELETE CTE, connection reference cleanup, and logger crash fix", ["performance", "distributed", "postgresql", "optimization", "reliability"]),
    ("Reduced DB round-trips to 3 for any batch size via bulk unnest() inserts (bulk delete + doc insert + chunk+embedding insert)", ["database", "performance", "postgresql", "optimization"]),
    ("Integrated tenacity retry logic (3 attempts, exponential backoff 1s–8s) for transient 502/503/504 errors from embeddings API — eliminated pod restarts under load", ["reliability", "distributed", "backend", "performance"]),
    # Architecture & Pipeline
    ("Built pgvector storage backend from scratch: asyncpg, HNSW index, schema-per-business-unit multi-tenant routing, and GIN full-text index on chunk content", ["database", "postgresql", "architecture", "backend"]),
    ("Implemented batch processing pipeline: in-memory buffer with configurable flush on BATCH_SIZE or interval; dedup key across 6 composite fields for idempotent processing", ["distributed", "backend", "architecture", "rabbitmq", "performance"]),
    ("Designed multi-backend storage routing (pgvector + Solr) by business unit via env config, with per-backend failure isolation", ["distributed", "database", "backend", "architecture"]),
    ("Implemented retrieval_mode field (chunk | segment | document) stored across pgvector and Solr — controls how chunks surface at query time", ["backend", "database", "api", "architecture"]),
    ("Implemented delete flag on ingest payload routing to composite-key deletion across all storage backends", ["backend", "api", "distributed", "architecture"]),
    # LLM / AI
    ("Implemented multi-provider LLM + embedding routing (OpenAI, Azure, Anthropic, Vertex, Cohere) with model-aware batching grouped by embedding model", ["llm", "ai", "embeddings", "ml", "performance"]),
    ("Built PII anonymization service (FastAPI + Presidio + spaCy) deployed to HIPAA Kubernetes cluster — patched CVEs and resolved security vulnerabilities for compliance", ["llm", "ai", "security", "fastapi", "hipaa"]),
    # Ops & Observability
    ("Drove end-to-end deployments across DevInt, QA, Staging, Production, and HIPAA environments for athena-vector-processor and athena-ingestion-service", ["devops", "backend", "reliability"]),
    ("Built Grafana dashboards for production monitoring; designed structured logging spec with document/chunk identifiers across the vector processor", ["observability", "monitoring", "backend"]),
    ("Built JWT-secured REST APIs with Helios OAuth2 for authenticated multi-tenant content processing", ["api", "security", "backend", "auth"]),
]

NOMBA_BULLETS = [
    ("Reduced GCP infrastructure costs by 25% via caching and service optimization", ["cloud", "backend", "performance", "optimization"]),
    ("Built a CSV export pipeline using MongoDB and Redis", ["backend", "database", "python"]),
]

PCU_BULLETS = [
    ("Trained faculty on AI tools (ChatGPT, Claude), improving team productivity by ~40%", ["ai", "llm"]),
]

PROJECTS = [
    {
        "name": "Scalable Notification Service",
        "link": "github.com/kareemadesola/scalable-notification-service",
        "date": "Apr 2026 – Present",
        "stack": "FastAPI · RabbitMQ · Redis · PostgreSQL · Docker · Prometheus · Grafana",
        "bullets": [
            ("Production-grade multi-channel notification system (email, SMS, push, WebSocket) with independent channel scaling", ["backend", "distributed", "rabbitmq", "architecture"]),
            ("Implemented exponential backoff retry + dead-letter queues for fault tolerance", ["distributed", "reliability", "backend"]),
            ("Built Redis rate limiting and Prometheus + Grafana observability (latency, throughput, error tracking)", ["performance", "monitoring", "observability", "redis"]),
            ("Designed for ~17K notifications/sec throughput with horizontal scaling strategy", ["performance", "distributed", "architecture", "scalability"]),
        ],
        "tags": ["backend", "distributed", "rabbitmq", "redis", "performance", "architecture"],
    },
    {
        "name": "AI Investigation & Research Assistant",
        "link": "github.com/kareemadesola/ai-investigation-assistant",
        "date": "Apr 2026",
        "stack": "Python · FAISS · RAG · Agentic pipeline",
        "bullets": [
            ("Agentic RAG system combining vector search, multi-step reasoning, and structured evaluation", ["ai", "llm", "rag", "ml"]),
            ("Built hallucination detection and response consistency evaluation layer", ["ai", "llm", "rag", "ml"]),
        ],
        "tags": ["ai", "llm", "rag", "ml", "python"],
    },
]

EDUCATION = {
    "school": "Obafemi Awolowo University, Ile-Ife, Nigeria",
    "degree": "BSc Computer Science with Mathematics — First Class Honours",
    "date": "Aug 2023",
    "extra": "Coursework: Data Structures & Algorithms, Operating Systems, Computer Networks, Software Engineering, AI",
}

CERTIFICATIONS = "HackerRank: Java (2024), REST API (2023), Problem Solving (2023), Python (2022)"


# ─────────────────────────────────────────────
# TAILORING LOGIC
# ─────────────────────────────────────────────

def score_bullet(bullet_tags, focus_keywords):
    """Score a bullet by how many focus keywords match its tags."""
    if not focus_keywords:
        return 1  # no filter — include all
    return sum(1 for kw in focus_keywords if any(kw in tag for tag in bullet_tags))


def select_bullets(bullet_list, focus_keywords, min_count=3, max_count=5):
    """Select the most relevant bullets based on focus keywords."""
    if not focus_keywords:
        return [b[0] for b in bullet_list[:max_count]]
    scored = [(score_bullet(b[1], focus_keywords), b[0]) for b in bullet_list]
    scored.sort(reverse=True)
    # Always include at least min_count, up to max_count
    selected = [b for score, b in scored if score > 0]
    if len(selected) < min_count:
        # pad with remaining bullets
        remaining = [b for score, b in scored if score == 0]
        selected.extend(remaining[:min_count - len(selected)])
    return selected[:max_count]


def select_projects(focus_keywords, max_projects=2):
    """Select most relevant projects."""
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
    name_style = ParagraphStyle("Name", fontSize=17, fontName="Helvetica-Bold",
                                alignment=TA_CENTER, spaceAfter=3)
    contact_style = ParagraphStyle("Contact", fontSize=8.5, fontName="Helvetica",
                                   alignment=TA_CENTER, spaceAfter=6)
    section_style = ParagraphStyle("Section", fontSize=10.5, fontName="Helvetica-Bold",
                                   spaceBefore=7, spaceAfter=2, textColor=colors.black)
    body_style = ParagraphStyle("Body", fontSize=9, fontName="Helvetica",
                                spaceAfter=2, leading=13)
    bullet_style = ParagraphStyle("Bullet", fontSize=9, fontName="Helvetica",
                                  spaceAfter=1.5, leftIndent=10, leading=13)
    job_header_style = ParagraphStyle("JobHeader", fontSize=9.5, fontName="Helvetica-Bold",
                                      spaceAfter=1, spaceBefore=5)
    job_meta_style = ParagraphStyle("JobMeta", fontSize=8.5, fontName="Helvetica-Oblique",
                                    spaceAfter=2)
    return {
        "name": name_style,
        "contact": contact_style,
        "section": section_style,
        "body": body_style,
        "bullet": bullet_style,
        "job_header": job_header_style,
        "job_meta": job_meta_style,
    }


def hr(color=colors.black, thickness=0.8):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4, spaceBefore=0)


def thin_hr():
    return HRFlowable(width="100%", thickness=0.4, color=colors.grey, spaceAfter=3, spaceBefore=0)


def generate_resume(company="", role="", focus_keywords=None, output_path=None):
    focus = [kw.lower() for kw in (focus_keywords or [])]

    # Output filename
    if not output_path:
        safe = lambda s: s.replace(" ", "_").replace("/", "-")
        if company and role:
            name = f"Adesola_Kareem_{safe(company)}_{safe(role)}.pdf"
        else:
            name = "Adesola_Kareem_Resume_Base.pdf"
        output_path = os.path.join(os.path.dirname(__file__), "resumes", name)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.55 * inch, bottomMargin=0.55 * inch)
    s = build_styles()
    story = []

    # ── Header ──────────────────────────────
    story.append(Paragraph(CONTACT["name"], s["name"]))
    story.append(Paragraph(
        f"{CONTACT['location']} | {CONTACT['phone']} | {CONTACT['email']} | "
        f"{CONTACT['linkedin']} | {CONTACT['github']}",
        s["contact"]
    ))
    story.append(hr())

    # ── Summary ─────────────────────────────
    story.append(Paragraph("PROFESSIONAL SUMMARY", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(SUMMARY, s["body"]))

    # ── Skills ──────────────────────────────
    story.append(Paragraph("SKILLS", s["section"]))
    story.append(thin_hr())
    for label, value in SKILLS:
        story.append(Paragraph(f"<b>{label}:</b> {value}", s["body"]))

    # ── Work Experience ──────────────────────
    story.append(Paragraph("WORK EXPERIENCE", s["section"]))
    story.append(thin_hr())

    # WebMD
    story.append(Paragraph("<b>WebMD</b> — Software Engineer (Backend)", s["job_header"]))
    story.append(Paragraph("Mar 2025 – Present | Python · FastAPI · RabbitMQ · pgvector · Redis · Docker", s["job_meta"]))
    for b in select_bullets(WEBMD_BULLETS, focus, min_count=4, max_count=6):
        story.append(Paragraph(f"• {b}", s["bullet"]))

    # Nomba
    story.append(Paragraph("<b>Nomba</b> — Software Engineer", s["job_header"]))
    story.append(Paragraph("Nov 2023 – Feb 2024 | Python · MongoDB · Redis · GCP", s["job_meta"]))
    for b in select_bullets(NOMBA_BULLETS, focus, min_count=1, max_count=2):
        story.append(Paragraph(f"• {b}", s["bullet"]))

    # PCU
    story.append(Paragraph("<b>Precious Cornerstone University (NYSC)</b> — Research Assistant", s["job_header"]))
    story.append(Paragraph("Mar 2024 – Jan 2025", s["job_meta"]))
    story.append(Paragraph(f"• {PCU_BULLETS[0][0]}", s["bullet"]))

    # ── Projects ────────────────────────────
    story.append(Paragraph("PROJECTS", s["section"]))
    story.append(thin_hr())

    selected_projects = select_projects(focus)
    for p in selected_projects:
        story.append(Paragraph(f"<b>{p['name']}</b> — {p['date']}", s["job_header"]))
        story.append(Paragraph(f"{p['stack']} | {p['link']}", s["job_meta"]))
        proj_bullets = select_bullets([(b[0], b[1]) for b in p["bullets"]], focus, min_count=2, max_count=3)
        for b in proj_bullets:
            story.append(Paragraph(f"• {b}", s["bullet"]))

    # ── Education ───────────────────────────
    story.append(Paragraph("EDUCATION", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(f"<b>{EDUCATION['school']}</b> — {EDUCATION['date']}", s["job_header"]))
    story.append(Paragraph(EDUCATION["degree"], s["body"]))

    # ── Certifications ──────────────────────
    story.append(Paragraph("CERTIFICATIONS", s["section"]))
    story.append(thin_hr())
    story.append(Paragraph(CERTIFICATIONS, s["body"]))

    doc.build(story)
    print(f"✅ Resume generated: {output_path}")
    return output_path


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a one-page tailored PDF resume")
    parser.add_argument("--company", default="", help="Company name (used in filename)")
    parser.add_argument("--role", default="", help="Role/position title (used in filename)")
    parser.add_argument("--focus", default="", help="Space-separated keywords to prioritize relevant bullets (e.g. 'python fastapi distributed llm')")
    parser.add_argument("--output", default="", help="Override output file path")
    args = parser.parse_args()

    focus_keywords = args.focus.split() if args.focus else []
    output = args.output if args.output else None

    generate_resume(
        company=args.company,
        role=args.role,
        focus_keywords=focus_keywords,
        output_path=output,
    )
