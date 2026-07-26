"""Keyword Discovery Agent.

Consumes signals_raw for a given run and extracts keyword candidates,
upserting them into the cumulative `keywords` table. No external NLP
dependency: uses stopword-filtered n-gram frequency extraction, which is
transparent, auditable and free.

Two lanes:
  - "atomic" sources (wikipedia_pageviews, npm_downloads) whose `term` is
    already a clean phrase -> used directly as a keyword.
  - "freeform" sources (hackernews, stackexchange, github) whose `term` is a
    sentence/description -> bigrams/trigrams are extracted after stopword
    removal.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import now_iso
from core.db import get_connection, init_db

ATOMIC_SOURCES = {"wikipedia_pageviews", "npm_downloads"}
FREEFORM_SOURCES = {"hackernews", "stackexchange", "github"}

STOPWORDS = set("""
a an the and or but if then else for to of in on at by with from as is are was
were be been being this that these those it its it's i you he she we they
what which who whom whose why how do does did doing not no nor so than too
very can will just should now new best top vs how-to guide show ask hn
introducing announcing release v1 v2 into your my our their his her about
one two three using use used make made get gets got know need want
""".split())

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}")


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def significant_ngrams(text: str, n_range=(2, 3)) -> list[str]:
    tokens = tokenize(text)
    grams = []
    for n in n_range:
        for i in range(len(tokens) - n + 1):
            window = tokens[i:i + n]
            if any(len(w) < 3 for w in window):
                continue
            if window[0] in STOPWORDS or window[-1] in STOPWORDS:
                continue
            if all(w in STOPWORDS for w in window):
                continue
            grams.append(" ".join(window))
    return grams


def normalize_atomic(term: str) -> str:
    term = re.sub(r"\s*\([^)]*\)\s*$", "", term)  # strip trailing "(2026 film)" etc.
    return term.strip().lower()


def _percentile_ranks(values: list[float]) -> list[float]:
    """Rank-normalize a list of raw metric values to (0, 1] within their own
    source, so no single source's units (pageviews in the 100k range vs. HN
    points in the hundreds) can dominate purely by scale."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    n = len(values)
    for pos, idx in enumerate(order):
        ranks[idx] = (pos + 1) / n
    return ranks


def extract_candidates(run_id: int) -> dict[str, dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT source, term, metric_value, url FROM signals_raw WHERE run_id = ?",
        (run_id,),
    ).fetchall()
    conn.close()

    # Normalize metric_value to a per-source percentile rank first.
    by_source: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        by_source[row["source"]].append(i)
    rank_weight = [0.0] * len(rows)
    for source, idxs in by_source.items():
        values = [rows[i]["metric_value"] or 0 for i in idxs]
        ranks = _percentile_ranks(values)
        for i, r in zip(idxs, ranks):
            rank_weight[i] = r

    candidates: dict[str, dict] = defaultdict(lambda: {
        "weight": 0.0, "sources": set(), "occurrences": 0, "sample_url": None,
    })

    for i, row in enumerate(rows):
        weight = rank_weight[i]
        if row["source"] in ATOMIC_SOURCES:
            terms = [normalize_atomic(row["term"])]
        else:
            terms = significant_ngrams(row["term"])
            if terms:
                weight = weight / len(terms)  # split signal weight across its n-grams

        for t in terms:
            if not t or len(t) < 4:
                continue
            c = candidates[t]
            c["weight"] += weight
            c["sources"].add(row["source"])
            c["occurrences"] += 1
            if c["sample_url"] is None:
                c["sample_url"] = row["url"]

    return candidates


def upsert_keywords(candidates: dict[str, dict], run_id: int, min_occurrences: int = 1) -> list[int]:
    """Upsert candidates into `keywords` and record a per-run snapshot in
    `keyword_run_stats` (used later to compute growth). Freeform n-grams
    require >=2 independent occurrences (cross-title agreement) to survive
    as real keywords; atomic terms (already single sources by construction)
    pass through at min_occurrences=1."""
    conn = get_connection()
    cur = conn.cursor()
    ts = now_iso()
    keyword_ids = []

    for term, c in candidates.items():
        is_multiword_freeform = len(term.split()) > 1
        threshold = 2 if is_multiword_freeform else min_occurrences
        if c["occurrences"] < threshold and len(c["sources"]) < 2:
            continue

        row = cur.execute("SELECT id, times_seen, sources_json FROM keywords WHERE term = ?", (term,)).fetchone()
        if row:
            existing_sources = set(json.loads(row["sources_json"] or "[]"))
            merged_sources = sorted(existing_sources | c["sources"])
            cur.execute(
                """UPDATE keywords SET last_seen=?, times_seen=times_seen+?,
                   sources_json=?, latest_score=? WHERE id=?""",
                (ts, c["occurrences"], json.dumps(merged_sources), c["weight"], row["id"]),
            )
            keyword_id = row["id"]
        else:
            cur.execute(
                """INSERT INTO keywords (term, first_seen, last_seen, times_seen, sources_json, latest_score)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (term, ts, ts, c["occurrences"], json.dumps(sorted(c["sources"])), c["weight"]),
            )
            keyword_id = cur.lastrowid
        keyword_ids.append(keyword_id)
        cur.execute(
            """INSERT OR REPLACE INTO keyword_run_stats
               (keyword_id, run_id, occurrences, weight, sources_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (keyword_id, run_id, c["occurrences"], c["weight"], json.dumps(sorted(c["sources"])), ts),
        )

    conn.commit()
    conn.close()
    return keyword_ids


def terms_per_signal(run_id: int, allowed_terms: set) -> list[list[str]]:
    """For each signal row in the run, return the subset of its extracted
    terms that are in `allowed_terms` (typically: terms that survived into
    the `keywords` table). Two terms extracted from the same signal row
    "co-occurred" - e.g. both appeared in the same Hacker News title, or
    are the same Wikipedia article - which is the raw material the Niche
    Agent uses to cluster related keywords."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT source, term FROM signals_raw WHERE run_id = ?", (run_id,),
    ).fetchall()
    conn.close()

    groups = []
    for row in rows:
        if row["source"] in ATOMIC_SOURCES:
            terms = [normalize_atomic(row["term"])]
        else:
            terms = significant_ngrams(row["term"])
        kept = [t for t in terms if t in allowed_terms]
        if kept:
            groups.append(kept)
    return groups


def run(run_id: int) -> list[int]:
    init_db()
    candidates = extract_candidates(run_id)
    keyword_ids = upsert_keywords(candidates, run_id)
    print(f"[keyword_agent] run_id={run_id} candidates={len(candidates)} kept={len(keyword_ids)}")
    return keyword_ids


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 agents/keyword_agent.py <run_id>")
        sys.exit(1)
    run(int(sys.argv[1]))
