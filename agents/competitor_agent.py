"""Competitor / Competition Analysis Agent.

For a shortlist of the run's top-scoring keywords, checks how much free
supply already exists for that topic, across four free no-auth sources:

  - npm registry: how many packages already match this term (developer-tool
    saturation)
  - GitHub: how many repositories already match this term (open-source
    saturation)
  - Stack Exchange: how many already-answered questions exist (the problem
    is already solved for free, in public)
  - Wikipedia: does a dedicated article already exist (topic is already
    comprehensively covered as free reference content)

Only the top `TOP_N_TO_CHECK` keywords per run are checked, not the full
~60 discovered per run: GitHub's unauthenticated Search API is capped at
10 requests/minute, so checking everything isn't feasible without an API
key. This runs *after* the Demand Scoring Agent's first pass (which ranks
by frequency/breadth/growth alone) and then asks demand_scoring_agent to
re-blend the top candidates' scores with an "opportunity" component
(1 - saturation).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import http_get, now_iso
from core.db import get_connection, init_db

TOP_N_TO_CHECK = 20
GITHUB_MIN_INTERVAL = 6.5  # seconds; keeps us under GitHub's 10 req/min unauthenticated cap


def npm_supply(term: str) -> int:
    data = http_get("https://registry.npmjs.org/-/v1/search", params={"text": term, "size": 1})
    return int(data.get("total", 0)) if data else 0


def github_supply(term: str) -> int:
    data = http_get("https://api.github.com/search/repositories", params={"q": term, "per_page": 1})
    return int(data.get("total_count", 0)) if data else 0


def stackexchange_supply(term: str) -> int:
    data = http_get("https://api.stackexchange.com/2.3/search/advanced", params={
        "q": term, "site": "stackoverflow", "answers": 1, "pagesize": 30,
    })
    if not data:
        return 0
    return sum(1 for item in data.get("items", []) if item.get("is_answered"))


def wikipedia_dedicated_article(term: str) -> bool:
    data = http_get("https://en.wikipedia.org/w/api.php", params={
        "action": "query", "list": "search", "srsearch": term, "format": "json", "srlimit": 1,
    })
    if not data:
        return False
    results = data.get("query", {}).get("search", [])
    if not results:
        return False
    top_title = results[0].get("title", "").strip().lower()
    return top_title == term.strip().lower()


def _normalize(count: int, saturating_at: int) -> float:
    """0 at count=0, ~1 once count reaches `saturating_at`."""
    return min(1.0, count / saturating_at) if saturating_at else 0.0


def check_keyword(term: str) -> dict:
    npm_count = npm_supply(term)
    time.sleep(GITHUB_MIN_INTERVAL)
    github_count = github_supply(term)
    se_count = stackexchange_supply(term)
    has_wiki = wikipedia_dedicated_article(term)

    components = [
        _normalize(npm_count, saturating_at=50),
        _normalize(github_count, saturating_at=200),
        _normalize(se_count, saturating_at=15),
        1.0 if has_wiki else 0.0,
    ]
    saturation_score = sum(components) / len(components)

    return {
        "npm_package_count": npm_count,
        "github_repo_count": github_count,
        "stackexchange_answered_count": se_count,
        "wikipedia_dedicated_article": int(has_wiki),
        "saturation_score": round(saturation_score, 4),
    }


def run(run_id: int) -> list[int]:
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    shortlist = cur.execute(
        """SELECT ds.keyword_id, k.term FROM demand_scores ds
           JOIN keywords k ON k.id = ds.keyword_id
           WHERE ds.run_id = ? ORDER BY ds.score DESC LIMIT ?""",
        (run_id, TOP_N_TO_CHECK),
    ).fetchall()

    checked_ids = []
    ts = now_iso()
    for row in shortlist:
        result = check_keyword(row["term"])
        cur.execute(
            """INSERT OR REPLACE INTO competition_checks
               (keyword_id, run_id, npm_package_count, github_repo_count,
                stackexchange_answered_count, wikipedia_dedicated_article,
                saturation_score, checked_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (row["keyword_id"], run_id, result["npm_package_count"], result["github_repo_count"],
             result["stackexchange_answered_count"], result["wikipedia_dedicated_article"],
             result["saturation_score"], ts),
        )
        checked_ids.append(row["keyword_id"])

    conn.commit()
    conn.close()
    print(f"[competitor_agent] run_id={run_id} checked={len(checked_ids)} keywords")
    return checked_ids


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 agents/competitor_agent.py <run_id>")
        sys.exit(1)
    run(int(sys.argv[1]))
