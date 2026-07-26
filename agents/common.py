"""Shared HTTP + logging helpers for all agents.

Every agent in this system only calls public, documented, no-auth-required
APIs (Hacker News/Algolia, Wikimedia, npm registry, Stack Exchange, GitHub
REST) strictly within their published rate limits and terms of use. No
scraping of pages that forbid it, no bypassing of auth walls, no synthetic
traffic.
"""
import html
import re
import time
import warnings
from datetime import datetime, timezone
from typing import Any, Optional

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import requests

USER_AGENT = "biznis-market-research-agent/0.1 (contact: jozefrusnak4@gmail.com)"
DEFAULT_TIMEOUT = 15
DEFAULT_HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


MARKETING_BLURBS = {
    "calculator": "Get an instant answer for {term} - no signup, no spreadsheet, works right in your browser.",
    "checklist": "A clear, repeatable checklist for {term} - know exactly what to do next, in the right order.",
    "template": "Skip the blank page. A ready-to-use {term} template with the right structure already in place.",
    "prompt_pack": "Ready-to-paste AI prompts for {term} - works with ChatGPT, Claude, or Gemini.",
}
MARKETING_BLURB_EBOOK_FREE = "A fast, practical guide to {term} - no fluff, just what actually works."
MARKETING_BLURB_EBOOK_PAID = "A focused guide to {term} you can read in about 15 minutes and put to use today."
MARKETING_BLURB_FALLBACK = "A practical {format} for {term}."

# When the keyword IS the format word itself (e.g. term="checklist" for a
# checklist product), using it verbatim reads as an accidental repeat
# ("A clear, repeatable checklist for Checklist"). Swap in a generic
# subject that still fits the sentence template.
GENERIC_SUBJECT_BY_FORMAT = {
    "calculator": "your numbers",
    "checklist": "your next project",
    "template": "your work",
    "prompt_pack": "everyday tasks",
    "ebook": "getting started",
    "sop": "getting started",
}

# term.title() mangles acronyms ("xlsx" -> "Xlsx" instead of "XLSX").
# Small, explicit override list rather than general acronym detection.
ACRONYM_OVERRIDES = {
    "xlsx": "XLSX", "csv": "CSV", "pdf": "PDF", "seo": "SEO", "ai": "AI",
    "api": "API", "sql": "SQL", "css": "CSS", "html": "HTML", "url": "URL",
    "json": "JSON",
}


def display_term(term: str) -> str:
    override = ACRONYM_OVERRIDES.get(term.strip().lower())
    return override if override else term.title()


def marketing_blurb(term: str, format_: str, monetized: bool = False) -> str:
    """Visitor-facing copy for a product page - deliberately separate from
    `product_ideas.rationale`, which is an internal audit trail ("why the
    agent picked this") and reads like an engineering log, not marketing
    (e.g. "Keyword implies users want to compute something quickly
    online."). Real copy, but still 100% honest - no fabricated numbers,
    testimonials, or urgency that isn't true."""
    if term.strip().lower() == format_:
        subject = GENERIC_SUBJECT_BY_FORMAT.get(format_, term)
    else:
        subject = display_term(term)

    if format_ in ("ebook", "sop"):
        template = MARKETING_BLURB_EBOOK_PAID if monetized else MARKETING_BLURB_EBOOK_FREE
    else:
        template = MARKETING_BLURBS.get(format_, MARKETING_BLURB_FALLBACK)
    return template.format(term=subject, format=format_.replace("_", " "))


def markdown_lite_to_html(md_text: str) -> str:
    """Minimal renderer for the specific Markdown subset content_agent.py
    produces: #/## headings, "- [ ] " checklist items, "- " list items,
    "> " blockquotes, "---" rules, and plain paragraphs. Shared by
    landing_page_agent.py (web pages) and scripts/export_pdf.py (PDF
    downloads) so both never drift into two different parsers."""
    lines = md_text.splitlines()
    out = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if stripped == "---":
            continue
        if stripped.startswith("### "):
            out.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            out.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            out.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("- [ ] "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>☐ {html.escape(stripped[6:])}</li>")
        elif stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{html.escape(stripped[2:])}</li>")
        elif stripped.startswith("> "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<blockquote>{html.escape(stripped[2:])}</blockquote>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{html.escape(stripped)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def http_get(url: str, params: Optional[dict] = None, retries: int = 2,
             backoff: float = 1.5, headers: Optional[dict] = None) -> Optional[Any]:
    """GET a URL and return parsed JSON, or None on failure (never raises)."""
    hdrs = {**DEFAULT_HEADERS, **(headers or {})}
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=hdrs, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 403) or resp.status_code >= 500:
                time.sleep(backoff * (attempt + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(backoff * (attempt + 1))
    return None
