"""Niche Clustering Agent.

Groups related keywords into `niches` using co-occurrence: if two keywords
were both extracted from the same underlying signal (the same Hacker News
title, the same Stack Exchange question, ...) they're linked. Connected
components of size >= 2 become a niche. This is a real, auditable signal of
relatedness with no external dependency - not a hand-curated taxonomy and
not semantic clustering (no embedding model is available yet; see
ROADMAP.md for the planned Ollama-embeddings upgrade).

Package-name artifacts (npm identifiers like "@editorjs/checklist") are
excluded from clustering for the same reason product_agent excludes them
from ideation - they're not market topics.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import now_iso
from agents.keyword_agent import terms_per_signal
from agents.product_agent import _looks_like_package_name
from core.db import get_connection, init_db

MIN_NICHE_SIZE = 2


class UnionFind:
    def __init__(self):
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def build_clusters(run_id: int) -> list[list[str]]:
    conn = get_connection()
    kw_rows = conn.execute(
        """SELECT DISTINCT k.term FROM keyword_run_stats krs
           JOIN keywords k ON k.id = krs.keyword_id WHERE krs.run_id = ?""",
        (run_id,),
    ).fetchall()
    conn.close()

    allowed_terms = {r["term"] for r in kw_rows if not _looks_like_package_name(r["term"])}
    groups = terms_per_signal(run_id, allowed_terms)

    uf = UnionFind()
    for term in allowed_terms:
        uf.find(term)  # ensure every eligible keyword exists as its own node
    for group in groups:
        for i in range(1, len(group)):
            uf.union(group[0], group[i])

    clusters: dict[str, list[str]] = {}
    for term in allowed_terms:
        root = uf.find(term)
        clusters.setdefault(root, []).append(term)

    return [terms for terms in clusters.values() if len(terms) >= MIN_NICHE_SIZE]


def run(run_id: int) -> list[int]:
    init_db()
    clusters = build_clusters(run_id)

    conn = get_connection()
    cur = conn.cursor()
    ts = now_iso()
    niche_ids = []

    for terms in clusters:
        scored = cur.execute(
            f"""SELECT term, latest_score FROM keywords
                WHERE term IN ({','.join('?' for _ in terms)})
                ORDER BY latest_score DESC""",
            terms,
        ).fetchall()
        if not scored:
            continue
        name = " + ".join(r["term"] for r in scored[:3]).title()

        existing = cur.execute("SELECT id FROM niches WHERE name = ?", (name,)).fetchone()
        if existing:
            niche_id = existing["id"]
        else:
            cur.execute(
                "INSERT INTO niches (name, description, created_at) VALUES (?, ?, ?)",
                (name, f"Co-occurrence cluster discovered in run {run_id}: "
                       f"{', '.join(r['term'] for r in scored)}", ts),
            )
            niche_id = cur.lastrowid
        niche_ids.append(niche_id)

        for r in scored:
            kw = cur.execute("SELECT id FROM keywords WHERE term = ?", (r["term"],)).fetchone()
            cur.execute(
                "INSERT OR IGNORE INTO niche_keywords (niche_id, keyword_id) VALUES (?, ?)",
                (niche_id, kw["id"]),
            )

    conn.commit()
    conn.close()
    print(f"[niche_agent] run_id={run_id} niches_found={len(niche_ids)}")
    return niche_ids


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 agents/niche_agent.py <run_id>")
        sys.exit(1)
    run(int(sys.argv[1]))
