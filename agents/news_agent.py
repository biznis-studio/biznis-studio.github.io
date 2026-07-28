"""Autonomous News Agent.

Runs unattended on every scheduled pipeline run and keeps a curated news
digest current - AI, technology, quantum computing/chips, and economics -
sourced *only* from a fixed allowlist of high-trust publishers and
primary institutions (research preprints, central banks, established
science/technology press). There is no open-web crawling and no
user-suggested sources: the allowlist below is the entire universe this
agent will ever fetch, which is what keeps "trustworthy sources only"
an enforced property rather than a hope.

Copyright/ethics stance, deliberately conservative:
  - Stores and displays ONLY the headline, the publisher name, the date,
    and a link to the original. Article bodies and feed summaries are
    never copied, stored, or republished - this is a link index with
    attribution (the same shape as any feed reader), not a content mirror.
  - Every headline links straight back to the publisher, so traffic goes
    to them, not away from them.
  - Fetches published RSS/Atom feeds only - the mechanism publishers
    provide precisely for syndication - with a descriptive User-Agent and
    a hard cap of one poll per source per run.

Failure of any single source is non-fatal by design: a news page that is
one source short is fine, a pipeline that dies because a publisher had a
bad gateway is not.
"""
import html as html_mod
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import now_iso
from core.db import get_connection, init_db

USER_AGENT = ("biznis-news-agent/1.0 (+https://biznis-studio.github.io; "
              "headline+link index, no content reproduction)")
TIMEOUT = 15

# The complete allowlist. Each entry: (source name, topic, feed URL).
# Chosen for editorial standards and/or primary-source status - research
# preprint servers, central banks, and established science/technology
# publications. Nothing here is a content farm, aggregator, or blog
# network, and no source is added at runtime.
SOURCES = [
    # --- AI -------------------------------------------------------------
    ("arXiv (cs.AI)", "ai",
     "http://export.arxiv.org/api/query?search_query=cat:cs.AI"
     "&sortBy=submittedDate&sortOrder=descending&max_results=8"),
    ("arXiv (cs.LG)", "ai",
     "http://export.arxiv.org/api/query?search_query=cat:cs.LG"
     "&sortBy=submittedDate&sortOrder=descending&max_results=8"),
    ("MIT Technology Review", "ai", "https://www.technologyreview.com/feed/"),
    # --- Technology -----------------------------------------------------
    ("IEEE Spectrum", "technology", "https://spectrum.ieee.org/feeds/feed.rss"),
    ("Ars Technica", "technology", "https://feeds.arstechnica.com/arstechnica/index"),
    ("Nature", "technology", "https://www.nature.com/nature.rss"),
    # --- Quantum computing / chips --------------------------------------
    ("arXiv (quant-ph)", "quantum",
     "http://export.arxiv.org/api/query?search_query=cat:quant-ph"
     "&sortBy=submittedDate&sortOrder=descending&max_results=8"),
    ("Phys.org (Quantum)", "quantum",
     "https://phys.org/rss-feed/physics-news/quantum-physics/"),
    # --- Economics ------------------------------------------------------
    ("European Central Bank", "economy", "https://www.ecb.europa.eu/rss/press.html"),
    ("US Federal Reserve", "economy", "https://www.federalreserve.gov/feeds/press_all.xml"),
]

TOPICS = [
    ("ai", "Artificial intelligence"),
    ("quantum", "Quantum computing &amp; chips"),
    ("technology", "Technology"),
    ("economy", "Economy &amp; markets"),
]

# Keep the page focused rather than exhaustive.
PER_TOPIC_ON_PAGE = 12
MAX_PER_SOURCE_PER_RUN = 6

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _clean_title(raw: str) -> str:
    """Feed titles occasionally carry markup or entity escapes; normalize
    to plain text. (Titles only - no summaries are ever processed.)"""
    text = html_mod.unescape(_TAG_RE.sub("", raw or ""))
    return _WS_RE.sub(" ", text).strip()


def _parse_date(raw: Optional[str]) -> str:
    """Best-effort date normalization to YYYY-MM-DD across RSS (RFC-822)
    and Atom (ISO 8601). Falls back to today rather than dropping an item
    over a formatting quirk."""
    if raw:
        raw = raw.strip()
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(raw).strftime("%Y-%m-%d")
        except (TypeError, ValueError, IndexError):
            pass
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except ValueError:
            pass
        m = re.search(r"(\d{4}-\d{2}-\d{2})", raw)
        if m:
            return m.group(1)
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def fetch_feed(url: str) -> list[dict]:
    """Fetch and parse one RSS or Atom feed into {title, link, date}.
    Returns [] on any network/parse failure - never raises."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as exc:
        print(f"[news_agent] fetch failed {url}: {type(exc).__name__}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"[news_agent] parse failed {url}: {exc}")
        return []

    items = []
    for node in root.iter():
        if _strip_ns(node.tag) not in ("item", "entry"):
            continue
        title = link = date_raw = None
        for child in node:
            tag = _strip_ns(child.tag)
            if tag == "title" and not title:
                title = "".join(child.itertext())
            elif tag == "link" and not link:
                # RSS puts the URL in text, Atom in an href attribute.
                link = (child.get("href") or child.text or "").strip()
            elif tag in ("pubDate", "published", "updated", "date") and not date_raw:
                date_raw = child.text
        title = _clean_title(title or "")
        if not title or not link or not link.startswith("http"):
            continue
        items.append({"title": title, "link": link.strip(), "date": _parse_date(date_raw)})
        if len(items) >= MAX_PER_SOURCE_PER_RUN:
            break
    return items


def collect() -> int:
    """Poll every allowlisted source once and store new headlines.
    Dedupes on the article URL, so re-running is safe and the table
    accumulates a real archive over time."""
    init_db()
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE,
            source TEXT NOT NULL,
            topic TEXT NOT NULL,
            published TEXT,
            fetched_at TEXT
        )""")
    conn.commit()

    added = 0
    for source, topic, url in SOURCES:
        for item in fetch_feed(url):
            cur = conn.execute(
                """INSERT OR IGNORE INTO news_items
                   (title, link, source, topic, published, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (item["title"], item["link"], source, topic, item["date"], now_iso()),
            )
            added += cur.rowcount
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM news_items").fetchone()[0]
    conn.close()
    print(f"[news_agent] {added} new headlines ({total} in archive)")
    return added


def recent_by_topic(limit: int = PER_TOPIC_ON_PAGE) -> dict[str, list[dict]]:
    conn = get_connection()
    exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='news_items'"
    ).fetchone()
    if not exists:
        conn.close()
        return {}
    out = {}
    for topic, _label in TOPICS:
        rows = conn.execute(
            """SELECT title, link, source, published FROM news_items
               WHERE topic = ? ORDER BY published DESC, id DESC LIMIT ?""",
            (topic, limit),
        ).fetchall()
        out[topic] = [dict(r) for r in rows]
    conn.close()
    return out


def build_page() -> bool:
    """Render site/news/index.html. Imported lazily inside the function so
    this module stays importable without pulling the page builders in."""
    from agents.landing_page_agent import OG_IMAGE_TAGS, SITE_BASE_URL, page_shell

    by_topic = recent_by_topic()
    if not any(by_topic.values()):
        print("[news_agent] no stored headlines yet - page not built")
        return False

    tabs = "".join(
        f'<a class="topic-tab" href="#{t}">{label}</a>' for t, label in TOPICS if by_topic.get(t)
    )
    sections = []
    for topic, label in TOPICS:
        rows = by_topic.get(topic) or []
        if not rows:
            continue
        items = "\n".join(
            f'<div class="news-item"><span class="news-src">{html_mod.escape(r["source"])}</span>'
            f'<a href="{html_mod.escape(r["link"])}" target="_blank" rel="noopener">'
            f'{html_mod.escape(r["title"])}</a>'
            f'<span class="news-date" style="margin-left:auto">{r["published"]}</span></div>'
            for r in rows
        )
        sections.append(
            f'<h2 id="{topic}" class="section-title">{label}</h2>\n'
            f'<div class="news-list">{items}</div>'
        )

    updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    sources_line = ", ".join(sorted({s for s, _t, _u in SOURCES}))
    body = f"""<div class="hero">
<span class="eyebrow">Fresh headlines</span>
<h1>Signals</h1>
<p class="subtitle">What is happening in AI, quantum computing, technology and the economy -
gathered daily from a fixed list of primary sources and established publications.</p>
</div>
<div class="topic-tabs">{tabs}</div>
{"".join(sections)}
<div class="card">
<h2>How this page works</h2>
<p>Every run, the pipeline polls a fixed list of trusted feeds and records new headlines.
No open-web crawling and no user-submitted sources - these are the publishers' own headlines,
unedited, linking straight back to the people who wrote them.</p>
<p>We deliberately show only the headline, the publisher, and the date. Article text is never
copied or republished here: every link goes to the original source, where it belongs.</p>
<p class="form-note"><strong>Sources:</strong> {html_mod.escape(sources_line)}.<br>
Last checked {updated}.</p>
</div>"""

    title = "Signals - AI, quantum, technology &amp; economy news"
    desc = ("A daily digest of AI, quantum computing, technology and economics headlines "
            "from primary sources and established publications.")
    page = page_shell(title, desc, body, is_index=False)
    if SITE_BASE_URL:
        url = f"{SITE_BASE_URL}/news/index.html"
        extras = (
            f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{html_mod.escape(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:type" content="website">\n' + OG_IMAGE_TAGS
        )
        idx = page.lower().find("</head>")
        if idx != -1:
            page = page[:idx] + extras + page[idx:]

    out_dir = Path(__file__).resolve().parent.parent / "site" / "news"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page)
    print(f"[news_agent] built news page ({sum(len(v) for v in by_topic.values())} headlines shown)")
    return True


def run() -> int:
    added = collect()
    build_page()
    return added


if __name__ == "__main__":
    run()
