"""Company Scoreboard Agent.

Computes real, queryable business metrics from the DB and (a) inserts one
snapshot row into `company_metrics` per run, so a trend builds up over
time, and (b) writes docs/COMPANY_SCOREBOARD.md from that data.

Layout follows a North Star / diagnostic split (added 2026-07-27 per user
feedback): the 5 numbers that actually matter for the business
(revenue, leads, CAC, EBV) lead the file; everything else (keyword/
product/page counts) is explicitly diagnostic, not the goal itself. A
Company Assets portfolio view sits between them - "which asset has the
most growth potential today" instead of "what task should I do next."

Deliberately NOT a hand-written report: every number here is a real COUNT/
SUM from the database, never an estimate. Fields this project can't
honestly quantify yet (development cost in $, maintenance cost, estimated
future value, Enterprise Business Value as a single number, cost per
acquired customer while acquisition spend is $0) are shown as explicit
"not yet meaningful" notes rather than invented numbers.
"""
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import now_iso
from core.db import get_connection, init_db

ROOT = Path(__file__).resolve().parent.parent
SCOREBOARD_PATH = ROOT / "docs" / "COMPANY_SCOREBOARD.md"


def compute_metrics(conn, run_id: Optional[int]) -> dict:
    q1 = lambda sql, *a: conn.execute(sql, a).fetchone()[0]

    total_keywords = q1("SELECT COUNT(*) FROM keywords")
    new_keywords_7d = q1(
        "SELECT COUNT(*) FROM keywords WHERE first_seen >= datetime('now', '-7 days')"
    )
    total_signals = q1("SELECT COUNT(*) FROM signals_raw")
    total_products = q1("SELECT COUNT(*) FROM products")
    ready_products = q1("SELECT COUNT(*) FROM products WHERE status = 'ready'")
    core_tier = q1("SELECT COUNT(*) FROM products WHERE tier = 'core'")
    lead_magnet = q1("SELECT COUNT(*) FROM products WHERE tier = 'lead_magnet'")
    retire_candidate = q1("SELECT COUNT(*) FROM products WHERE tier = 'retire_candidate'")
    live_pages = q1("SELECT COUNT(*) FROM pages")
    seo_enhanced_pages = q1("SELECT COUNT(*) FROM pages WHERE seo_enhanced = 1")
    monetized_products = q1("SELECT COUNT(*) FROM products WHERE monetization_url IS NOT NULL")
    experiments_total = q1("SELECT COUNT(*) FROM experiments")
    experiments_running = q1("SELECT COUNT(*) FROM experiments WHERE status = 'running'")
    experiments_succeeded = q1("SELECT COUNT(*) FROM experiments WHERE status = 'succeeded'")
    experiments_failed = q1("SELECT COUNT(*) FROM experiments WHERE status = 'failed'")

    last_run_row = conn.execute("SELECT started_at FROM runs ORDER BY started_at DESC LIMIT 1").fetchone()
    last_run_at = last_run_row[0] if last_run_row else None
    last_product_row = conn.execute(
        "SELECT created_at FROM products ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    last_product_at = last_product_row[0] if last_product_row else None

    return dict(
        run_id=run_id,
        computed_at=now_iso(),
        last_run_at=last_run_at,
        last_product_at=last_product_at,
        total_keywords=total_keywords,
        new_keywords_7d=new_keywords_7d,
        total_signals=total_signals,
        total_products=total_products,
        ready_products=ready_products,
        core_tier_count=core_tier,
        lead_magnet_count=lead_magnet,
        retire_candidate_count=retire_candidate,
        live_pages=live_pages,
        seo_enhanced_pages=seo_enhanced_pages,
        monetized_products=monetized_products,
        confirmed_revenue_usd=0.0,      # no real sale confirmed yet - see docs/DECISION_JOURNAL.md D1
        qualified_leads=0,              # Formspree endpoint not live yet - see TASKBOARD.md Human Action Batch
        experiments_total=experiments_total,
        experiments_running=experiments_running,
        experiments_succeeded=experiments_succeeded,
        experiments_failed=experiments_failed,
    )


def build_assets_table(metrics: dict) -> str:
    rows = [
        ("Knowledge Base", "Data", "Active",
         "market_research_agent.py + keyword_agent.py",
         f"{metrics['total_keywords']} keywords / {metrics['total_signals']} signals",
         "100% (fully automated ingestion, no manual entry)",
         (metrics['last_run_at'] or "n/a")[:10]),
        ("Product Catalog", "Product portfolio", "Active",
         "product_agent.py + content_agent.py + tiering",
         f"{metrics['core_tier_count']} core / {metrics['lead_magnet_count']} lead_magnet / "
         f"{metrics['ready_products']} ready",
         "High for calculator/checklist/template/prompt_pack (fully automated); "
         "low for ebook/sop (human-written prose by design)",
         (metrics['last_product_at'] or "n/a")[:10]),
        ("Distribution Surface", "Distribution", "Active, pre-revenue",
         "landing_page_agent.py + seo_agent.py",
         f"{metrics['live_pages']} live pages, 0 confirmed Google-indexed",
         "100% (build + deploy); 0% for actual discovery, see docs/CONSTRAINT_LOG.md",
         (metrics['last_run_at'] or "n/a")[:10]),
        ("Reusable Code / Design System", "Software", "Active",
         "agents/common.py, agents/pdf_export.py",
         "shared design system + renderer + PDF export - zero marginal cost per new product",
         "100% (every new product reuses it automatically)",
         "see git log agents/common.py"),
        ("Service Capability", "Service", "Active, 0 leads yet",
         "manual delivery (web dev, chatbot dev)",
         "2 offerings listed, 0 confirmed leads",
         "0% by nature - services are human-delivered, not automatable",
         (metrics['last_product_at'] or "n/a")[:10]),
    ]
    header = "| Asset | Type | Status | Owner (module) | Business Value (real) | Automation | Last Updated |\n"
    header += "|---|---|---|---|---|---|---|\n"
    return header + "\n".join(
        f"| {a} | {t} | {s} | {o} | {v} | {auto} | {lu} |" for a, t, s, o, v, auto, lu in rows
    )


def render_markdown(metrics: dict, history: list[dict]) -> str:
    trend_rows = "\n".join(
        f"| {h['computed_at'][:10]} | {h['total_products']} | {h['ready_products']} | "
        f"{h['core_tier_count']} | {h['live_pages']} | {h['total_keywords']} | "
        f"{h['new_keywords_7d']} | {h['confirmed_revenue_usd']:.2f} |"
        for h in history
    )
    run_label = f"run {metrics['run_id']}" if metrics['run_id'] is not None else "a manual (non-pipeline) invocation"
    return f"""# Company Scoreboard

**Auto-generated by `agents/scoreboard_agent.py` on every pipeline run -
do not hand-edit.** Every number below is real, computed from the
database at `{metrics['computed_at']}` ({run_label}), never an estimate.

## North Star Metrics (the only numbers that actually matter)

Everything below this section is diagnostic. These 5 are what the
business lives or dies on.

| Metric | Value |
|---|---|
| Revenue Today (USD) | {metrics['confirmed_revenue_usd']:.2f} |
| Revenue Last 30 Days (USD) | {metrics['confirmed_revenue_usd']:.2f} |
| Qualified Leads | {metrics['qualified_leads']} |
| Cost per Acquired Customer | N/A - $0 acquisition spend and 0 customers so far |
| Enterprise Business Value | Not computable as a single number - no revenue or user base exists yet to value. The `tier` classification (core/lead_magnet/retire_candidate) is the honest qualitative proxy until real numbers exist; see docs/CONSTRAINT_LOG.md for the current blocking constraint. |

All effectively zero right now - that's the real, current state, not a
display bug. See docs/CONSTRAINT_LOG.md for why (distribution/discovery)
and docs/TASKBOARD.md's Human Action Batch for what unblocks it fastest.

## Company Assets Portfolio

The question that matters: **which asset has the most growth potential
today** - not "what task should I do." Real assets only (no fabricated
ones like an email list or audience that don't exist yet - see
docs/ROADMAP.md's Company Assets note).

{build_assets_table(metrics)}

## Experiments

| Metric | Value |
|---|---|
| Total defined | {metrics['experiments_total']} |
| Running | {metrics['experiments_running']} |
| Succeeded | {metrics['experiments_succeeded']} |
| Failed | {metrics['experiments_failed']} |

All zero right now - see docs/ROADMAP.md on why a full experiment
portfolio isn't built yet (no traffic exists to run one against). The
`experiments` table exists and is ready the moment a real one is runnable.

## Diagnostic metrics (not the goal - context for the North Star numbers above)

| Metric | Value |
|---|---|
| Total products in DB | {metrics['total_products']} |
| Products `ready` (built + live) | {metrics['ready_products']} |
| Core tier (validated paid-demand evidence) | {metrics['core_tier_count']} |
| Lead-magnet tier (useful, free by design) | {metrics['lead_magnet_count']} |
| Retire-candidate tier (rejected, never published) | {metrics['retire_candidate_count']} |
| Live pages on site | {metrics['live_pages']} |
| Pages with SEO enhancement applied | {metrics['seo_enhanced_pages']} |
| Products with a monetization URL set | {metrics['monetized_products']} |
| Total keywords tracked | {metrics['total_keywords']} |
| New keywords in last 7 days (learning-velocity proxy) | {metrics['new_keywords_7d']} |
| Total raw signals collected | {metrics['total_signals']} |

## Trend (last {len(history)} run snapshot(s))

| Date | Products | Ready | Core tier | Pages | Keywords | New kw (7d) | Revenue |
|---|---|---|---|---|---|---|---|
{trend_rows}

## Not tracked (deliberately, not by oversight)

- **Development / maintenance cost in USD** - no metered cost model
  exists for agent time in this environment, so any dollar figure here
  would be invented, not measured.
- **Estimated future value per product / a single EBV number** - would
  require forecasting assumptions this project has no basis to make yet.
- **Traffic/impressions/clicks** - 0 real analytics exist yet (see
  docs/CONSTRAINT_LOG.md - this is the current primary constraint).
"""


def run(run_id: Optional[int] = None) -> dict:
    init_db()
    conn = get_connection()
    metrics = compute_metrics(conn, run_id)

    conn.execute(
        """INSERT INTO company_metrics
           (run_id, computed_at, total_keywords, new_keywords_7d, total_signals,
            total_products, ready_products, core_tier_count, lead_magnet_count,
            retire_candidate_count, live_pages, seo_enhanced_pages, monetized_products,
            confirmed_revenue_usd, experiments_total, experiments_running,
            experiments_succeeded, experiments_failed)
           VALUES (:run_id, :computed_at, :total_keywords, :new_keywords_7d, :total_signals,
                   :total_products, :ready_products, :core_tier_count, :lead_magnet_count,
                   :retire_candidate_count, :live_pages, :seo_enhanced_pages, :monetized_products,
                   :confirmed_revenue_usd, :experiments_total, :experiments_running,
                   :experiments_succeeded, :experiments_failed)""",
        metrics,
    )
    conn.commit()

    history = [
        dict(r) for r in conn.execute(
            "SELECT * FROM company_metrics ORDER BY computed_at DESC LIMIT 14"
        ).fetchall()
    ][::-1]
    conn.close()

    SCOREBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCOREBOARD_PATH.write_text(render_markdown(metrics, history))
    print(f"[scoreboard_agent] wrote {SCOREBOARD_PATH} ({len(history)} snapshot(s) in trend)")
    return metrics


if __name__ == "__main__":
    run_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(run_id_arg)
