"""SEO Agent.

Enhances each already-built page under site/products/ in place with:
  - schema.org JSON-LD (SoftwareApplication for the calculator - including
    a genuine $0 Offer, since it really is free; HowTo for the checklist,
    built from its *actual* rendered steps; CreativeWork for template/
    prompt_pack) - no AggregateRating/Review schema anywhere, since there
    are no real reviews and fabricating one would violate the project's
    no-fake-reviews rule.
  - Open Graph + meta description tags mirroring the real page content.
  - A short, generic, honestly-answerable FAQ section (also mirrored as
    FAQPage JSON-LD, matching Google's guidance that FAQ markup must match
    visible page content).
  - A handful of internal links to other real product pages, so pages
    aren't SEO-orphaned.

sitemap.xml and feed.xml are only generated when the SITE_BASE_URL
environment variable is set - both formats assert "this is live at this
URL", which isn't true before there's an actual deployed site. Once set
(see .github/workflows/pipeline.yml, which sets it to the real GitHub
Pages URL), canonical link tags, sitemap.xml and feed.xml all start being
emitted with real, absolute URLs.
"""
import html
import json
import os
import re
import secrets
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from core.db import get_connection, init_db

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "").rstrip("/")

# Persisted outside site/ so it survives the directory getting rebuilt -
# the filename IS the IndexNow key by convention, so it has to stay stable
# across runs, not be regenerated every time.
INDEXNOW_KEY_FILE = ROOT / "db" / "indexnow_key.txt"

FAQS_BY_FORMAT = {
    "calculator": [
        ("Do I need to install anything?",
         "No - it runs directly in your browser. Nothing is uploaded or stored."),
        ("Is my data saved anywhere?",
         "No. All calculations happen locally in your browser; nothing is sent to a server."),
        ("Is it free to use?", "Yes, with no signup required."),
    ],
    "checklist": [
        ("Is this checklist free?", "Yes - download it directly, no signup required."),
        ("What format is it in?",
         "Plain Markdown, so you can paste it into Notion, a PDF, or any note-taking app."),
        ("Can I edit or reuse it?", "Yes, it's yours to adapt for your own use."),
    ],
    "template": [
        ("What file format is the template?",
         "CSV, which opens directly in Excel, Google Sheets, or Numbers."),
        ("Is it free?", "Yes, no signup required."),
        ("Can I customize the columns?",
         "Yes - it's a starting point. Add, remove, or rename columns as needed."),
    ],
    "prompt_pack": [
        ("Which AI tool do these prompts work with?",
         "Any general-purpose chat AI (e.g. ChatGPT, Claude, Gemini) - paste one in and "
         "fill the bracketed placeholders with your own details."),
        ("Is this free?", "Yes, no signup required."),
        ("Can I modify the prompts?",
         "Yes - they're a starting point to adapt to your exact situation."),
    ],
    "swipe_file": [
        ("Is this free?", "Yes, no signup required."),
        ("What format is it in?",
         "Plain Markdown - copy the text straight into an email, Slack message, or document."),
        ("Do I need to use the exact wording?",
         "No - these are starting points. Adjust the tone and details to match your own situation."),
    ],
}


def _abs_url(relative_path: str) -> Optional[str]:
    return f"{SITE_BASE_URL}/{relative_path}" if SITE_BASE_URL else None


def extract_checklist_steps(page_html: str) -> list[str]:
    """Pull the actual rendered checklist <li> items out of the page so the
    HowTo schema reflects real content instead of inventing steps. The page
    HTML has these HTML-escaped (&quot;, &#x27;, ...) for correct rendering,
    but JSON-LD text values must hold the literal characters, not markup -
    otherwise a rich-snippet renderer would show "&quot;" verbatim."""
    items = re.findall(r"<li>☐ (.*?)</li>", page_html)
    return [html.unescape(re.sub(r"<.*?>", "", item)) for item in items]


def schema_for(fmt: str, title: str, description: str, url: Optional[str], page_html: str) -> dict:
    base = {"@context": "https://schema.org", "name": title, "description": description}
    if url:
        base["url"] = url

    if fmt == "calculator":
        return {**base, "@type": "SoftwareApplication",
                "applicationCategory": "UtilitiesApplication",
                "operatingSystem": "Any (runs in a web browser)",
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    if fmt == "checklist":
        steps = extract_checklist_steps(page_html)
        if steps:
            return {**base, "@type": "HowTo",
                    "step": [{"@type": "HowToStep", "text": s} for s in steps]}
    return {**base, "@type": "CreativeWork"}


def faq_block(fmt: str, term: str) -> tuple[str, Optional[dict]]:
    faqs = FAQS_BY_FORMAT.get(fmt)
    if not faqs:
        return "", None
    items_html = "\n".join(
        f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in faqs
    )
    section_html = f'<div class="card"><h2>FAQ</h2>\n{items_html}</div>'
    schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }
    return section_html, schema


def related_links_html(current_url: str, all_pages: list[dict], limit: int = 3) -> str:
    others = [p for p in all_pages if p["url"] != current_url][:limit]
    if not others:
        return ""
    items = "\n".join(
        f'<li><a href="{html.escape(Path(p["url"]).name)}">{html.escape(p["title"])}</a></li>'
        for p in others
    )
    return f'<div class="card"><h2>More free tools</h2><ul>{items}</ul></div>'


def generate_sitemap(pages: list[dict]) -> None:
    """Standard sitemap.xml. Only called when SITE_BASE_URL is set - a
    sitemap for a URL that doesn't exist yet would be actively misleading."""
    urls = [f"{SITE_BASE_URL}/"] + [_abs_url(p["url"]) for p in pages]
    lastmods = [datetime.now(timezone.utc).strftime("%Y-%m-%d")] + [
        (p["created_at"] or "")[:10] for p in pages
    ]
    entries = "\n".join(
        f"  <url><loc>{html.escape(u)}</loc><lastmod>{lm}</lastmod></url>"
        for u, lm in zip(urls, lastmods)
    )
    xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n')
    (SITE_DIR / "sitemap.xml").write_text(xml)


def _rfc822(iso_timestamp: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_timestamp)
    except (ValueError, TypeError):
        dt = datetime.now(timezone.utc)
    return format_datetime(dt)


def generate_rss(pages: list[dict]) -> None:
    """Standard RSS 2.0 feed, newest first. Only called when SITE_BASE_URL
    is set, for the same reason as the sitemap."""
    items = []
    for p in sorted(pages, key=lambda p: p["created_at"] or "", reverse=True):
        pub_date = _rfc822(p["created_at"])
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(p['title'])}</title>\n"
            f"    <link>{html.escape(_abs_url(p['url']))}</link>\n"
            f"    <description>{html.escape(p['meta_description'])}</description>\n"
            f"    <pubDate>{html.escape(pub_date)}</pubDate>\n"
            "  </item>"
        )
    rss = (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
           f"  <title>Biznis - Free Digital Products</title>\n"
           f"  <link>{html.escape(SITE_BASE_URL)}/</link>\n"
           f"  <description>Free checklists, templates, calculators and prompt packs "
           f"generated from real demand signals.</description>\n"
           + "\n".join(items) + "\n</channel></rss>\n")
    (SITE_DIR / "feed.xml").write_text(rss)


def get_or_create_indexnow_key() -> str:
    """The IndexNow key file's *name* has to be the key itself, hosted at
    the site root, so it must stay stable across runs - persisted outside
    site/ (which gets wiped and rebuilt) rather than regenerated."""
    if INDEXNOW_KEY_FILE.exists():
        return INDEXNOW_KEY_FILE.read_text().strip()
    key = secrets.token_hex(16)
    INDEXNOW_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEXNOW_KEY_FILE.write_text(key)
    return key


def submit_to_indexnow(urls: list[str], key: str) -> bool:
    """Ask Bing/Yandex/Seznam/Naver/Yep (not Google - IndexNow isn't a
    Google protocol) to (re)crawl these URLs. Free, no account needed -
    just the key file hosted at the site root for ownership proof. This
    is a best-effort courtesy ping, not something the pipeline should ever
    fail over if the API is briefly unreachable."""
    if not urls or not SITE_BASE_URL:
        return False
    host = SITE_BASE_URL.split("://", 1)[-1].split("/", 1)[0]
    try:
        resp = requests.post(
            "https://api.indexnow.org/indexnow",
            json={"host": host, "key": key, "keyLocation": f"{SITE_BASE_URL}/{key}.txt",
                  "urlList": urls},
            timeout=15,
        )
        return resp.status_code in (200, 202)
    except requests.RequestException:
        return False


def inject(page_path: Path, head_extra: str, body_extra: str) -> None:
    text = page_path.read_text()
    head_close = re.search(r"</head>", text, re.IGNORECASE)
    if head_close:
        text = text[:head_close.start()] + head_extra + text[head_close.start():]
    footer_open = re.search(r"<footer>", text, re.IGNORECASE)
    if footer_open:
        text = text[:footer_open.start()] + body_extra + text[footer_open.start():]
    page_path.write_text(text)


def run(run_id: Optional[int] = None) -> int:
    init_db()
    conn = get_connection()
    all_rows = conn.execute(
        """SELECT pg.id, pg.url, pg.title, pg.meta_description, pg.created_at,
                  p.format, k.term
           FROM pages pg
           JOIN products p ON p.id = pg.product_id
           JOIN product_ideas pi ON pi.id = p.idea_id
           JOIN keywords k ON k.id = pi.target_keyword_id""",
    ).fetchall()
    pending_ids = {r["id"] for r in conn.execute(
        "SELECT id FROM pages WHERE seo_enhanced = 0"
    ).fetchall()}

    all_pages = [dict(p) for p in all_rows]  # used for related-links across ALL pages, not just pending
    processed = 0

    for p in all_pages:
        if p["id"] not in pending_ids:
            continue
        page_path = SITE_DIR / p["url"]
        if not page_path.exists():
            continue
        current_html = page_path.read_text()
        url = _abs_url(p["url"])

        schema = schema_for(p["format"], p["title"], p["meta_description"], url, current_html)
        faq_html, faq_schema = faq_block(p["format"], p["term"])
        links_html = related_links_html(p["url"], all_pages)

        head_parts = [f'<meta property="og:title" content="{html.escape(p["title"])}">',
                      f'<meta property="og:description" content="{html.escape(p["meta_description"])}">',
                      '<meta property="og:type" content="website">']
        if url:
            head_parts.append(f'<link rel="canonical" href="{html.escape(url)}">')
        head_parts.append(f'<script type="application/ld+json">{json.dumps(schema)}</script>')
        if faq_schema:
            head_parts.append(f'<script type="application/ld+json">{json.dumps(faq_schema)}</script>')

        body_extra = (faq_html or "") + (links_html or "")
        inject(page_path, "\n".join(head_parts) + "\n", body_extra + "\n")
        conn.execute("UPDATE pages SET seo_enhanced = 1 WHERE id = ?", (p["id"],))
        processed += 1

    conn.commit()
    conn.close()

    indexnow_ok = None
    if SITE_BASE_URL:
        generate_sitemap(all_pages)
        generate_rss(all_pages)
        key = get_or_create_indexnow_key()
        (SITE_DIR / f"{key}.txt").write_text(key)
        urls = [f"{SITE_BASE_URL}/"] + [_abs_url(p["url"]) for p in all_pages]
        indexnow_ok = submit_to_indexnow(urls, key)

    print(f"[seo_agent] enhanced {processed} pages"
          + ("" if SITE_BASE_URL else " (SITE_BASE_URL unset - no canonical URLs, sitemap/RSS skipped)")
          + (f", indexnow_submit={'ok' if indexnow_ok else 'failed'}" if indexnow_ok is not None else ""))
    return processed


if __name__ == "__main__":
    run_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(run_id_arg)
