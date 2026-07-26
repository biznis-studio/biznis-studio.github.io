"""Demand Scoring Agent.

Scores every keyword touched in a given run on three transparent components:

  - frequency_component: how strongly it showed up this run (per-run weight,
    itself a percentile rank within source - see keyword_agent).
  - breadth_component: how many *independent* free sources mentioned it.
    Cross-source agreement is the strongest signal that demand is real
    rather than a single-source artifact.
  - growth_component: this run's occurrence count vs. the historical average
    occurrence count for the same keyword (0 for brand-new keywords, since
    there is no baseline yet - they instead score highly on novelty, tracked
    separately so first-run output isn't misleadingly flat).

Final score = weighted sum, written to `demand_scores` and mirrored onto
`keywords.latest_score` for fast lookup by downstream agents.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import now_iso
from core.db import get_connection, init_db

WEIGHTS = {"frequency": 0.4, "breadth": 0.4, "growth": 0.2}
MAX_BREADTH = 5  # number of distinct sources in the whole system


def score_run(run_id: int) -> list[dict]:
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    stats = cur.execute(
        """SELECT krs.keyword_id, krs.occurrences, krs.weight, krs.sources_json, k.term
           FROM keyword_run_stats krs JOIN keywords k ON k.id = krs.keyword_id
           WHERE krs.run_id = ?""",
        (run_id,),
    ).fetchall()

    results = []
    for s in stats:
        breadth = len(json.loads(s["sources_json"] or "[]"))
        breadth_component = min(1.0, breadth / MAX_BREADTH)

        history = cur.execute(
            """SELECT AVG(occurrences) AS avg_occ, COUNT(*) AS n
               FROM keyword_run_stats WHERE keyword_id = ? AND run_id != ?""",
            (s["keyword_id"], run_id),
        ).fetchone()
        if history["n"] and history["avg_occ"]:
            growth_component = min(1.0, s["occurrences"] / history["avg_occ"] / 2.0)
            is_new = False
        else:
            growth_component = 0.5  # neutral prior for brand-new keywords
            is_new = True

        frequency_component = min(1.0, s["weight"])  # weight is already ~0-few from rank sums

        score = (WEIGHTS["frequency"] * frequency_component
                 + WEIGHTS["breadth"] * breadth_component
                 + WEIGHTS["growth"] * growth_component)

        components = {
            "frequency_component": round(frequency_component, 4),
            "breadth_component": round(breadth_component, 4),
            "growth_component": round(growth_component, 4),
            "is_new": is_new,
            "breadth_count": breadth,
        }

        cur.execute(
            """INSERT INTO demand_scores
               (keyword_id, run_id, score, frequency_component, growth_component,
                breadth_component, components_json, scored_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (s["keyword_id"], run_id, score, frequency_component, growth_component,
             breadth_component, json.dumps(components), now_iso()),
        )
        cur.execute("UPDATE keywords SET latest_score = ? WHERE id = ?", (score, s["keyword_id"]))
        results.append({"keyword_id": s["keyword_id"], "term": s["term"], "score": score, **components})

    conn.commit()
    conn.close()
    results.sort(key=lambda r: r["score"], reverse=True)
    print(f"[demand_scoring_agent] run_id={run_id} scored={len(results)} keywords")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 agents/demand_scoring_agent.py <run_id>")
        sys.exit(1)
    for r in score_run(int(sys.argv[1]))[:15]:
        print(f"  {r['score']:.3f}  breadth={r['breadth_count']}  new={r['is_new']}  {r['term']}")
