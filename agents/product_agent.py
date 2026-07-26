"""Product Idea Generation Agent.

Turns the top-scored keywords from a run into concrete, original digital
product briefs. Rule-based (regex pattern -> format) rather than LLM-based:
there is no LLM configured yet (no local Ollama install, no OpenRouter key)
so this stays 100% free, deterministic and auditable. See ROADMAP.md for the
planned LLM-assisted upgrade once a model is wired in.

Every idea is a *brief* (title, format, target keyword, rationale) - a human
or a later Content/Book/Template Agent still has to actually author the
product. This agent never fabricates claims about a market; it only
proposes ideas and cites the keyword + demand score that triggered them.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import now_iso
from core.db import get_connection, init_db

TOP_N = 12
MIN_SCORE = 0.0  # keep permissive for MVP; tighten once score distribution is well understood

# Sources that reflect real problems/tools people are searching for or
# discussing (buyer/builder intent). Wikipedia top-pageviews mostly reflects
# celebrity/entertainment/news trivia ("Odyssey (2026 film)", "LeBron
# James") which is not a commercial digital-product niche - a keyword that
# ONLY appears via Wikipedia is excluded from product ideation (it's still
# kept in `keywords` for potential future timely-content/SEO use).
COMMERCIAL_INTENT_SOURCES = {"hackernews", "stackexchange", "github", "npm_downloads"}

# A keyword that's literally a software package identifier (scoped npm name,
# or a kebab-case dev-tool name) isn't a market topic - you can't sell a
# consumer "checklist" or "template" product branded after someone else's
# library. Filter these out rather than turning them into product ideas.
def _looks_like_package_name(term: str) -> bool:
    if "@" in term or "/" in term or "_" in term:
        return True
    # kebab-case with a dev-tool-flavored suffix, e.g. "react-spreadsheet",
    # "mjml-invoice", "automation-events"
    if re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)+", term):
        return True
    return False


def _dedupe_words(title: str) -> str:
    seen = set()
    out = []
    for word in title.split():
        key = word.lower().strip(".:")
        if key in seen:
            continue
        seen.add(key)
        out.append(word)
    return " ".join(out)


# (pattern, format, title_fn, rationale)
FORMAT_RULES = [
    (re.compile(r"\bcalculator\b"), "calculator",
     lambda t: f"Free Online {t.title()}",
     "Keyword implies users want to compute something quickly online."),
    (re.compile(r"\bchecklist\b"), "checklist",
     lambda t: f"{t.title()} (PDF + Notion)",
     "Checklist-shaped intent: users want a repeatable step list, not prose."),
    (re.compile(r"\b(template|invoice|sop|spreadsheet)\b"), "template",
     lambda t: f"{t.title()} Pack",
     "Keyword implies a reusable document/spreadsheet is the natural deliverable."),
    (re.compile(r"\b(prompt|gpt|chatgpt|ai)\b"), "prompt_pack",
     lambda t: f"{t.title()}: AI Prompt Pack",
     "AI-adjacent keyword; a curated prompt pack is a low-effort, high-value product."),
    (re.compile(r"\b(api|sdk|cli|framework|library|package)\b"), "sop",
     lambda t: f"{t.title()}: Developer Quickstart & SOP",
     "Developer-tool keyword; a standard operating procedure / quickstart guide reduces onboarding friction."),
]
FALLBACK_FORMAT = "ebook"


def pick_format(term: str):
    for pattern, fmt, title_fn, rationale in FORMAT_RULES:
        if pattern.search(term):
            return fmt, _dedupe_words(title_fn(term)), rationale
    return (FALLBACK_FORMAT, f"The Practical Guide to {term.title()}",
            "General-purpose topic; a short practical guide covers it best.")


def run(run_id: int) -> list[int]:
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    candidates = cur.execute(
        """SELECT ds.keyword_id, ds.score, k.term, k.sources_json
           FROM demand_scores ds JOIN keywords k ON k.id = ds.keyword_id
           WHERE ds.run_id = ? AND ds.score >= ?
           ORDER BY ds.score DESC""",
        (run_id, MIN_SCORE),
    ).fetchall()

    top_keywords = []
    for row in candidates:
        sources = set(json.loads(row["sources_json"] or "[]"))
        if not sources & COMMERCIAL_INTENT_SOURCES:
            continue  # Wikipedia-only trend, not a commercial niche - skip
        if _looks_like_package_name(row["term"]):
            continue  # e.g. "@editorjs/checklist", "react-spreadsheet" - not a market topic
        top_keywords.append(row)
        if len(top_keywords) >= TOP_N:
            break

    created_ids = []
    ts = now_iso()
    for row in top_keywords:
        existing = cur.execute(
            """SELECT id FROM product_ideas
               WHERE target_keyword_id = ? AND status != 'rejected'""",
            (row["keyword_id"],),
        ).fetchone()
        if existing:
            continue  # already have a live idea for this keyword; don't spam duplicates

        fmt, title, rationale = pick_format(row["term"])
        cur.execute(
            """INSERT INTO product_ideas
               (run_id, title, format, target_keyword_id, niche_id, demand_score, rationale, status, created_at)
               VALUES (?, ?, ?, ?, NULL, ?, ?, 'proposed', ?)""",
            (run_id, title, fmt, row["keyword_id"], row["score"], rationale, ts),
        )
        created_ids.append(cur.lastrowid)

    conn.commit()
    conn.close()
    print(f"[product_agent] run_id={run_id} new_ideas={len(created_ids)} (considered top {len(top_keywords)})")
    return created_ids


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 agents/product_agent.py <run_id>")
        sys.exit(1)
    run(int(sys.argv[1]))
