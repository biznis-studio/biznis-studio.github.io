#!/usr/bin/env python3
"""Orchestrator: runs one full iteration of the discovery + creation loop -

    Market Research -> Keyword Discovery -> Demand Scoring (pass 1)
        -> Competition Analysis -> Demand Scoring (pass 2, re-blend)
        -> Product Ideas -> Content Generation

and exports a JSON + CSV report to data/exports/. This is the single
entrypoint used both locally and by the GitHub Actions schedule.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents import (competitor_agent, content_agent, demand_scoring_agent,
                     keyword_agent, market_research_agent, product_agent)
from agents.common import now_iso
from core.db import get_connection


def export_report(run_id: int) -> Path:
    conn = get_connection()

    run_row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    top_keywords = conn.execute(
        """SELECT k.term, ds.score, ds.breadth_component, ds.growth_component, k.sources_json
           FROM demand_scores ds JOIN keywords k ON k.id = ds.keyword_id
           WHERE ds.run_id = ? ORDER BY ds.score DESC LIMIT 25""",
        (run_id,),
    ).fetchall()
    ideas = conn.execute(
        """SELECT pi.id, pi.title AS title, pi.format AS format, pi.demand_score AS demand_score,
                  pi.rationale AS rationale, pi.status AS status,
                  p.file_path AS product_file_path, p.status AS product_status
           FROM product_ideas pi LEFT JOIN products p ON p.idea_id = pi.id
           WHERE pi.run_id = ? ORDER BY pi.demand_score DESC""",
        (run_id,),
    ).fetchall()
    signal_counts = conn.execute(
        "SELECT source, COUNT(*) AS n FROM signals_raw WHERE run_id = ? GROUP BY source",
        (run_id,),
    ).fetchall()
    conn.close()

    report = {
        "run_id": run_id,
        "generated_at": now_iso(),
        "run_status": run_row["status"] if run_row else None,
        "signals_by_source": {r["source"]: r["n"] for r in signal_counts},
        "top_keywords": [dict(r) for r in top_keywords],
        "product_ideas": [dict(r) for r in ideas],
    }

    exports_dir = ROOT / "data" / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    json_path = exports_dir / f"run_{run_id:04d}.json"
    csv_path = exports_dir / f"run_{run_id:04d}_ideas.csv"

    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "format", "demand_score", "rationale", "product_file_path", "product_status"])
        for idea in ideas:
            writer.writerow([idea["title"], idea["format"], idea["demand_score"], idea["rationale"],
                              idea["product_file_path"], idea["product_status"]])

    return json_path


def main() -> int:
    run_id = market_research_agent.run()
    keyword_agent.run(run_id)
    demand_scoring_agent.score_run(run_id)
    competitor_agent.run(run_id)
    demand_scoring_agent.apply_competition(run_id)
    product_agent.run(run_id)
    content_agent.run(run_id)
    report_path = export_report(run_id)
    print(f"[run_pipeline] run_id={run_id} report={report_path}")
    return run_id


if __name__ == "__main__":
    main()
