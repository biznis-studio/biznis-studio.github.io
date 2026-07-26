"""Market Research + Trend Agent.

Pulls current demand/attention signals from five free, public, no-auth-key
APIs and stores them as raw rows in `signals_raw`. This is stage 1 of the
loop (Market Research -> Keyword Discovery -> ...).

Sources:
  - Hacker News front page (Algolia HN Search API)
  - Wikipedia top pageviews (Wikimedia REST API)
  - npm registry search popularity (npm public search API)
  - Stack Exchange active questions (Stack Exchange API v2.3)
  - GitHub trending repos (GitHub REST search API, unauthenticated)
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import http_get, now_iso
from core.db import get_connection, init_db

# Broad, non-niche-specific seed terms used only for the npm popularity signal
# (npm's search API requires a query; it has no "trending now" endpoint).
NPM_SEED_TERMS = [
    "productivity", "automation", "ai", "notion template", "seo tool",
    "spreadsheet", "invoice", "checklist", "calculator",
]

STACKEXCHANGE_SITES = ["stackoverflow", "productivity", "workplace", "pm"]


def fetch_hackernews(limit: int = 50) -> list[dict]:
    data = http_get("https://hn.algolia.com/api/v1/search", params={
        "tags": "front_page", "hitsPerPage": limit,
    })
    if not data:
        return []
    out = []
    for hit in data.get("hits", []):
        title = hit.get("title")
        if not title:
            continue
        out.append({
            "source": "hackernews",
            "signal_type": "discussion",
            "term": title,
            "metric_value": float(hit.get("points") or 0),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            "payload": hit,
        })
    return out


def fetch_wikipedia_top_pageviews(limit: int = 50) -> list[dict]:
    # Pageview data typically lags 1-2 days; walk backwards until we get a hit.
    for days_back in (2, 3, 4, 5):
        d = datetime.now(timezone.utc) - timedelta(days=days_back)
        url = (
            "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
            f"en.wikipedia/all-access/{d.year}/{d.month:02d}/{d.day:02d}"
        )
        data = http_get(url)
        if data and data.get("items"):
            articles = data["items"][0].get("articles", [])[:limit]
            out = []
            for a in articles:
                title = a.get("article", "").replace("_", " ")
                if not title or title.startswith(("Main Page", "Special:", "Wikipedia:")):
                    continue
                out.append({
                    "source": "wikipedia_pageviews",
                    "signal_type": "pageview",
                    "term": title,
                    "metric_value": float(a.get("views") or 0),
                    "url": f"https://en.wikipedia.org/wiki/{a.get('article')}",
                    "payload": a,
                })
            return out
    return []


def fetch_npm_popularity(limit_per_term: int = 5) -> list[dict]:
    out = []
    for term in NPM_SEED_TERMS:
        data = http_get("https://registry.npmjs.org/-/v1/search", params={
            "text": term, "size": limit_per_term,
        })
        if not data:
            continue
        for obj in data.get("objects", []):
            pkg = obj.get("package", {})
            name = pkg.get("name")
            if not name:
                continue
            score = obj.get("score", {}).get("final", 0)
            out.append({
                "source": "npm_downloads",
                "signal_type": "package_popularity",
                "term": f"{name} ({term})",
                "metric_value": round(float(score or 0) * 100, 2),
                "url": pkg.get("links", {}).get("npm"),
                "payload": {"seed_term": term, **pkg},
            })
    return out


def fetch_stackexchange_active(limit_per_site: int = 20) -> list[dict]:
    out = []
    for site in STACKEXCHANGE_SITES:
        data = http_get("https://api.stackexchange.com/2.3/questions", params={
            "order": "desc", "sort": "activity", "site": site,
            "pagesize": limit_per_site, "filter": "!9_bDDxJY5",
        })
        if not data:
            continue
        for q in data.get("items", []):
            title = q.get("title")
            if not title:
                continue
            title = re.sub(r"&#?\w+;", " ", title)  # strip basic HTML entities
            out.append({
                "source": "stackexchange",
                "signal_type": "question",
                "term": title,
                "metric_value": float(q.get("score", 0)) + float(q.get("view_count", 0)) / 100.0,
                "url": q.get("link"),
                "payload": {"site": site, **{k: q[k] for k in q if k not in ("body",)}},
            })
    return out


def fetch_github_trending(limit: int = 30) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")
    data = http_get("https://api.github.com/search/repositories", params={
        "q": f"created:>{since}", "sort": "stars", "order": "desc", "per_page": limit,
    })
    if not data:
        return []
    out = []
    for repo in data.get("items", []):
        name = repo.get("full_name")
        if not name:
            continue
        term = repo.get("description") or name
        out.append({
            "source": "github",
            "signal_type": "repo",
            "term": term[:200],
            "metric_value": float(repo.get("stargazers_count") or 0),
            "url": repo.get("html_url"),
            "payload": {"full_name": name, "stars": repo.get("stargazers_count"),
                        "language": repo.get("language")},
        })
    return out


FETCHERS = [
    fetch_hackernews,
    fetch_wikipedia_top_pageviews,
    fetch_npm_popularity,
    fetch_stackexchange_active,
    fetch_github_trending,
]


def run() -> int:
    """Fetch all sources and persist to signals_raw. Returns the run_id."""
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO runs (started_at, stage, status) VALUES (?, 'market_research', 'running')",
        (now_iso(),),
    )
    run_id = cur.lastrowid
    conn.commit()

    total = 0
    per_source_counts = {}
    try:
        for fetcher in FETCHERS:
            signals = fetcher()
            for s in signals:
                cur.execute(
                    """INSERT INTO signals_raw
                       (run_id, source, signal_type, term, metric_value, url, fetched_at, payload_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (run_id, s["source"], s["signal_type"], s["term"], s["metric_value"],
                     s.get("url"), now_iso(), json.dumps(s.get("payload", {}), default=str)),
                )
            per_source_counts[fetcher.__name__] = len(signals)
            total += len(signals)
        conn.commit()
        cur.execute(
            "UPDATE runs SET finished_at = ?, status = 'success', notes = ? WHERE id = ?",
            (now_iso(), json.dumps(per_source_counts), run_id),
        )
    except Exception as exc:  # pragma: no cover - defensive top-level guard
        cur.execute(
            "UPDATE runs SET finished_at = ?, status = 'failed', notes = ? WHERE id = ?",
            (now_iso(), str(exc), run_id),
        )
        conn.commit()
        conn.close()
        raise
    conn.commit()
    conn.close()
    print(f"[market_research_agent] run_id={run_id} total_signals={total} by_source={per_source_counts}")
    return run_id


if __name__ == "__main__":
    run()
