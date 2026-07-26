"""Demand Scoring Agent.

Runs in two passes:

1. `score_run()` - scores every keyword touched in a run on three
   transparent components: frequency (per-run weight), breadth (how many
   independent free sources mentioned it), and growth (this run vs. its
   own history). This is what ranks the full candidate pool and produces
   the shortlist the Competitor Analysis Agent then checks.
2. `apply_competition()` - for the keywords the Competitor Analysis Agent
   actually checked, re-blends the score to include an "opportunity"
   component (1 - saturation: how much free supply already exists).
   Keywords that weren't checked (rate-limit-bounded shortlist) keep their
   pass-1 score - this is recorded in `components_json` so it's never
   ambiguous which score a given row is.

Final score is written to `demand_scores` and mirrored onto
`keywords.latest_score` for fast lookup by downstream agents.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import now_iso
from core.db import get_connection, init_db

WEIGHTS = {"frequency": 0.4, "breadth": 0.4, "growth": 0.2}
WEIGHTS_WITH_COMPETITION = {"frequency": 0.3, "breadth": 0.3, "growth": 0.15, "opportunity": 0.25}
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


def apply_competition(run_id: int) -> list[dict]:
    """Re-blend scores for keywords the Competitor Analysis Agent checked
    this run, folding in an opportunity component (1 - saturation)."""
    conn = get_connection()
    cur = conn.cursor()

    checks = cur.execute(
        """SELECT cc.keyword_id, cc.saturation_score, cc.npm_package_count,
                  cc.github_repo_count, cc.stackexchange_answered_count,
                  cc.wikipedia_dedicated_article, ds.id AS demand_score_id,
                  ds.components_json, k.term
           FROM competition_checks cc
           JOIN demand_scores ds ON ds.keyword_id = cc.keyword_id AND ds.run_id = cc.run_id
           JOIN keywords k ON k.id = cc.keyword_id
           WHERE cc.run_id = ?""",
        (run_id,),
    ).fetchall()

    results = []
    for row in checks:
        components = json.loads(row["components_json"])
        opportunity_component = round(1.0 - row["saturation_score"], 4)
        w = WEIGHTS_WITH_COMPETITION
        score = (w["frequency"] * components["frequency_component"]
                 + w["breadth"] * components["breadth_component"]
                 + w["growth"] * components["growth_component"]
                 + w["opportunity"] * opportunity_component)

        components["opportunity_component"] = opportunity_component
        components["saturation_score"] = row["saturation_score"]
        components["competition_checked"] = True

        cur.execute(
            "UPDATE demand_scores SET score = ?, components_json = ? WHERE id = ?",
            (score, json.dumps(components), row["demand_score_id"]),
        )
        cur.execute("UPDATE keywords SET latest_score = ? WHERE id = ?", (score, row["keyword_id"]))
        results.append({"keyword_id": row["keyword_id"], "term": row["term"], "score": score, **components})

    conn.commit()
    conn.close()
    results.sort(key=lambda r: r["score"], reverse=True)
    print(f"[demand_scoring_agent] run_id={run_id} re-scored {len(results)} keywords with competition data")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 agents/demand_scoring_agent.py <run_id> [--apply-competition]")
        sys.exit(1)
    run_id_arg = int(sys.argv[1])
    if "--apply-competition" in sys.argv:
        for r in apply_competition(run_id_arg)[:15]:
            print(f"  {r['score']:.3f}  saturation={r['saturation_score']:.2f}  {r['term']}")
    else:
        for r in score_run(run_id_arg)[:15]:
            print(f"  {r['score']:.3f}  breadth={r['breadth_count']}  new={r['is_new']}  {r['term']}")
