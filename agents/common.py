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
