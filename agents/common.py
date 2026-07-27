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


# Shared visual design system for every generated page (landing_page_agent.py's
# non-calculator pages + index, and content_agent.py's calculator tool) so
# the whole site reads as one product, not a pile of separately-styled
# documents. Rewritten after direct feedback that the design looked
# "extremely bland and unprofessional," then again to be "ultra-modern":
# gradient accents, glow/lift hover states, gradient text on the hero.
SITE_CSS = """
  :root {
    color-scheme: light dark;
    --bg: #ffffff;
    --bg-alt: #fafaff;
    --surface: #f6f7fc;
    --border: #e4e7ef;
    --text: #14161f;
    --text-muted: #5b6072;
    --brand: #4f46e5;
    --brand2: #7c3aed;
    --brand-hover: #4338ca;
    --brand-contrast: #ffffff;
    --shadow: 0 1px 2px rgba(20, 22, 31, 0.04), 0 8px 24px rgba(20, 22, 31, 0.07);
    --shadow-lg: 0 4px 10px rgba(79, 70, 229, 0.12), 0 16px 40px rgba(20, 22, 31, 0.10);
    --radius: 16px;
    --gradient: linear-gradient(135deg, var(--brand), var(--brand2));
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0a0b12;
      --bg-alt: #0d0e17;
      --surface: #151723;
      --border: #262a3a;
      --text: #f1f2f9;
      --text-muted: #9a9fb5;
      --brand: #818cf8;
      --brand2: #a78bfa;
      --brand-hover: #a5b0fb;
      --brand-contrast: #0a0b12;
      --shadow: 0 1px 2px rgba(0, 0, 0, 0.35), 0 8px 24px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 4px 14px rgba(129, 140, 248, 0.18), 0 20px 48px rgba(0, 0, 0, 0.45);
    }
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0; background: var(--bg); color: var(--text); line-height: 1.65;
    -webkit-font-smoothing: antialiased;
    background-image: radial-gradient(60rem 30rem at 15% -10%, rgba(124, 58, 237, 0.10), transparent 60%),
                       radial-gradient(50rem 26rem at 100% 0%, rgba(79, 70, 229, 0.10), transparent 55%);
    background-repeat: no-repeat;
  }
  .site-header {
    display: flex; align-items: center; justify-content: space-between;
    max-width: 960px; margin: 0 auto; padding: 1.75rem 1.25rem 0;
  }
  .site-header a.brand {
    font-weight: 800; font-size: 1.2rem; color: var(--text); text-decoration: none;
    letter-spacing: -0.03em;
  }
  .site-header a.brand span {
    background: var(--gradient); -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .site-header nav { display: flex; gap: 1.5rem; align-items: center; }
  .site-header nav a {
    color: var(--text-muted); text-decoration: none; font-size: 0.9rem; font-weight: 600;
    transition: color 0.15s ease;
  }
  .site-header nav a:hover { color: var(--brand); }
  .site-header nav a.nav-cta {
    background: var(--gradient); color: #fff !important; padding: 0.5rem 1.1rem; border-radius: 999px;
    font-weight: 700; box-shadow: var(--shadow);
  }
  main { max-width: 720px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
  main.wide { max-width: 1080px; }
  h1 {
    font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; margin: 0 0 0.5rem;
    line-height: 1.15;
  }
  h2 { font-size: 1.3rem; font-weight: 750; margin-top: 2.25rem; letter-spacing: -0.015em; }
  h3 { font-size: 1.05rem; font-weight: 700; }
  .subtitle { color: var(--text-muted); margin: 0 0 1.75rem; font-size: 1.08rem; }
  .card {
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.6rem 1.85rem; margin: 1.5rem 0; box-shadow: var(--shadow);
  }
  a.button {
    display: inline-block; background: var(--gradient); color: var(--brand-contrast) !important;
    padding: 0.85rem 1.75rem; border-radius: 12px; text-decoration: none; font-weight: 700;
    box-shadow: var(--shadow-lg); transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  a.button:hover { transform: translateY(-2px) scale(1.015); }
  a.button.secondary {
    background: var(--surface); color: var(--text) !important; border: 1px solid var(--border);
    box-shadow: none;
  }
  a.button.secondary:hover { border-color: var(--brand); }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.92rem; }
  th, td { border: 1px solid var(--border); padding: 0.65rem 0.75rem; text-align: left; }
  th { background: var(--bg-alt); font-weight: 700; }
  blockquote {
    background: var(--bg-alt); border-left: 3px solid var(--brand); margin: 0.9rem 0;
    padding: 0.7rem 1.15rem; border-radius: 0 10px 10px 0;
  }
  ul { padding-left: 1.3rem; }
  li { margin-bottom: 0.55rem; }
  .badge {
    display: inline-block; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.05em;
    text-transform: uppercase; color: #fff; padding: 0.3rem 0.7rem; border-radius: 999px;
    margin-bottom: 0.85rem; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }
  .section-title {
    font-size: 0.82rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-muted); margin: 3rem 0 0.25rem;
  }
  .product-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1.15rem; margin-top: 1.25rem;
  }
  .product-card {
    display: block; background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.5rem 1.6rem; text-decoration: none; color: var(--text);
    box-shadow: var(--shadow); transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  }
  .product-card:hover { transform: translateY(-3px); border-color: var(--brand); box-shadow: var(--shadow-lg); }
  .product-card h3 { margin: 0.55rem 0 0.4rem; font-size: 1.08rem; }
  .product-card p { margin: 0; color: var(--text-muted); font-size: 0.9rem; }
  .service-card {
    display: block; text-decoration: none; color: var(--text);
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.75rem 2rem; box-shadow: var(--shadow); position: relative; overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .service-card::before {
    content: ""; position: absolute; inset: 0 0 auto 0; height: 4px; background: var(--gradient);
  }
  .service-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
  .service-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.15rem; margin-top: 1.25rem;
  }
  .hero { max-width: 680px; }
  .hero .subtitle { font-size: 1.15rem; }
  .hero h1 {
    background: var(--gradient); -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; display: inline-block;
  }
  footer {
    max-width: 960px; margin: 3rem auto 0; padding: 1.5rem 1.25rem 2.5rem;
    font-size: 0.82rem; color: var(--text-muted); border-top: 1px solid var(--border);
  }
  footer a { color: var(--text-muted); }
"""

# One accent color per product format, used for the small badge shown on
# product cards/pages - purely a scannability aid, not a claim about
# quality or popularity.
FORMAT_BADGE_COLORS = {
    "calculator": "#2563eb",
    "checklist": "#059669",
    "template": "#d97706",
    "swipe_file": "#7c3aed",
    "prompt_pack": "#0891b2",
    "ebook": "#db2777",
    "sop": "#4b5563",
    "service": "#0d9488",
}

# Public contact address for the "service" format's Get in touch CTA
# (custom website/chatbot development - not an automated digital
# download). Using the site owner's real email, so it's the one that
# should change first if a dedicated business address is set up later.
CONTACT_EMAIL = "jozefrusnak4@gmail.com"

# A small monogram favicon (inline SVG data URI - no external request).
FAVICON_DATA_URI = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' rx='14' fill='%234f46e5'/%3E"
    "%3Ctext x='32' y='44' font-family='Arial,sans-serif' font-size='34' "
    "font-weight='800' fill='white' text-anchor='middle'%3EB%3C/text%3E%3C/svg%3E"
)


def format_badge_html(fmt: str) -> str:
    color = FORMAT_BADGE_COLORS.get(fmt, "#4b5563")
    label = fmt.replace("_", " ")
    return f'<span class="badge" style="background:{color}">{label}</span>'


def site_header_html(active_is_index: bool = False) -> str:
    home_href = "index.html" if active_is_index else "../index.html"
    services_href = "#services" if active_is_index else "../index.html#services"
    return f"""<header class="site-header">
<a class="brand" href="{home_href}">Biznis<span>.</span></a>
<nav>
<a href="{home_href}">Free products</a>
<a href="{services_href}">Services</a>
<a class="nav-cta" href="mailto:{CONTACT_EMAIL}">Hire us</a>
</nav>
</header>"""


MARKETING_BLURBS = {
    "calculator": "Get an instant answer for {term} - no signup, no spreadsheet, works right in your browser.",
    "checklist": "A clear, repeatable checklist for {term} - know exactly what to do next, in the right order.",
    "template": "Skip the blank page. A ready-to-use {term} template with the right structure already in place.",
    "prompt_pack": "Ready-to-paste AI prompts for {term} - works with ChatGPT, Claude, or Gemini.",
    "swipe_file": "Ready-to-send scripts for {term} - copy, adjust the details, send.",
    "service": "{term}, scoped and quoted for your actual project - get in touch to start.",
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
    "swipe_file": "that conversation",
    "ebook": "getting started",
    "sop": "getting started",
}

# term.title() mangles acronyms ("xlsx" -> "Xlsx" instead of "XLSX"). Small,
# explicit override list rather than general acronym detection - applied
# per-word so it also fixes multi-word terms like "eu digital seller
# compliance" -> "EU Digital..." not just single-word terms.
ACRONYM_OVERRIDES = {
    "xlsx": "XLSX", "csv": "CSV", "pdf": "PDF", "seo": "SEO", "ai": "AI",
    "api": "API", "sql": "SQL", "css": "CSS", "html": "HTML", "url": "URL",
    "json": "JSON", "eu": "EU", "vat": "VAT", "kyc": "KYC", "gdpr": "GDPR",
}


def display_term(term: str) -> str:
    return " ".join(ACRONYM_OVERRIDES.get(w.lower(), w.title()) for w in term.split())


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


_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")


def _inline_emphasis(escaped_text: str) -> str:
    """Convert **bold** and *italic* to <strong>/<em>, applied *after*
    html.escape() so the asterisks (not HTML-special) are untouched by
    escaping but the tags we insert are real markup, not escaped text.
    Found this gap by shipping content that used *italic* emphasis and
    seeing literal asterisks on the live page."""
    escaped_text = _BOLD_RE.sub(r"<strong>\1</strong>", escaped_text)
    escaped_text = _ITALIC_RE.sub(r"<em>\1</em>", escaped_text)
    return escaped_text


def markdown_lite_to_html(md_text: str) -> str:
    """Minimal renderer for the specific Markdown subset content_agent.py
    produces: #/## headings, "- [ ] " checklist items, "- " list items,
    "> " blockquotes, "---" rules, plain paragraphs, and inline **bold**/
    *italic* emphasis. Shared by landing_page_agent.py (web pages) and
    scripts/export_pdf.py (PDF downloads) so both never drift into two
    different parsers.

    Every block type here is hand-wrapped across multiple physical lines
    in the source (for readable line lengths), so this has to merge wrapped
    lines back into one logical block before emitting a tag - line-by-line
    classification alone would (and once did) break a wrapped list item
    into a <li> plus a stray sibling <p>, and a wrapped blockquote into
    several separate <blockquote> tags instead of one."""
    lines = md_text.splitlines()
    out: list[str] = []
    in_list = False
    buffer_type: Optional[str] = None  # 'p' | 'li' | 'li_checked' | 'blockquote'
    buffer_text: list[str] = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def flush():
        nonlocal buffer_type, buffer_text
        if buffer_text:
            text = _inline_emphasis(html.escape(" ".join(buffer_text).strip()))
            if buffer_type == "li":
                out.append(f"<li>{text}</li>")
            elif buffer_type == "li_checked":
                out.append(f"<li>☐ {text}</li>")
            elif buffer_type == "blockquote":
                close_list()
                out.append(f"<blockquote>{text}</blockquote>")
            else:  # 'p'
                close_list()
                out.append(f"<p>{text}</p>")
        buffer_text = []
        buffer_type = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped == "---":
            flush()
            close_list()
            continue
        if stripped.startswith("### "):
            flush()
            close_list()
            out.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            flush()
            close_list()
            out.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            flush()
            close_list()
            out.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("- [ ] "):
            flush()
            if not in_list:
                out.append("<ul>")
                in_list = True
            buffer_type, buffer_text = "li_checked", [stripped[6:]]
        elif stripped.startswith("- "):
            flush()
            if not in_list:
                out.append("<ul>")
                in_list = True
            buffer_type, buffer_text = "li", [stripped[2:]]
        elif stripped.startswith("> "):
            if buffer_type == "blockquote":
                buffer_text.append(stripped[2:])  # same quote, wrapped across lines
            else:
                flush()
                buffer_type, buffer_text = "blockquote", [stripped[2:]]
        else:
            # Continuation of whatever block is open (li/blockquote/p), or
            # the start of a new paragraph if nothing is open.
            if buffer_type is None:
                buffer_type = "p"
            buffer_text.append(stripped)

    flush()
    close_list()
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
