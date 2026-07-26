# Architecture

## Status legend
✅ implemented and tested · 🚧 partially implemented · ⬜ not started

## Loop graph (from the project brief) vs. current implementation

```
Market Research        ✅ agents/market_research_agent.py
      ↓
Keyword Discovery       ✅ agents/keyword_agent.py
      ↓
Demand Scoring (pass 1) ✅ agents/demand_scoring_agent.py::score_run()
      ↓                   (ranks the full pool so we know which ~20 to
      ↓                    spend GitHub's 10 req/min budget checking)
Competition Analysis    ✅ agents/competitor_agent.py (top-20 shortlist only -
      ↓                   see known limitations in ROADMAP.md)
Demand Scoring (pass 2) ✅ agents/demand_scoring_agent.py::apply_competition()
      ↓
Product Ideas           ✅ agents/product_agent.py
      ↓
Product Creation        ✅ agents/content_agent.py (calculator/checklist/template/
      ↓                   prompt_pack ship "ready"; ebook/sop are outline-only "draft")
Landing Page            ⬜ not started
      ↓
SEO Optimization        ⬜ not started
      ↓
Publishing              ⬜ not started
      ↓
Traffic Collection      ⬜ not started
      ↓
Analytics               ⬜ not started (schema exists: pages, analytics_events)
      ↓
Conversion Analysis     ⬜ not started
      ↓
User Feedback           ⬜ not started
      ↓
Product Improvement     ⬜ not started
      ↓
New Product Ideas       🔁 loop closes back to Product Ideas once analytics exist
```

## Why these 4 stages first

A discovery engine that can't tell "real demand" from "noise" will poison
every downstream stage (you'll write SEO content for a movie title nobody
will buy a product about). So the highest-leverage first slice was: prove
we can pull real signals from free APIs, extract genuine keyword candidates,
score them defensibly, and turn the winners into concrete (not vague)
product briefs — end to end, no mocked data. That's what's built.

## Data flow

```
5 free public APIs
   │  (agents/market_research_agent.py)
   ▼
signals_raw (SQLite)  — one row per raw hit, full payload kept for audit
   │  (agents/keyword_agent.py: stopword-filtered n-gram extraction,
   │   per-source percentile-rank normalization so no source's raw units
   │   (pageviews in the 100k range vs. HN points in the hundreds) dominate)
   ▼
keywords + keyword_run_stats (SQLite) — cumulative candidate list + per-run snapshot
   │  (agents/demand_scoring_agent.py::score_run(): frequency 40% + breadth 40% + growth 20%)
   ▼
demand_scores (SQLite, pass 1)
   │  (agents/competitor_agent.py: checks top 20 by pass-1 score against
   │   npm/GitHub/Stack Exchange/Wikipedia supply - GitHub's unauthenticated
   │   10 req/min search limit is why this is a shortlist, not all ~60)
   ▼
competition_checks (SQLite)
   │  (agents/demand_scoring_agent.py::apply_competition(): re-blends the
   │   checked 20 to frequency 30% + breadth 30% + growth 15% + opportunity 25%)
   ▼
demand_scores (SQLite, pass 2 for the checked subset)
   │  (agents/product_agent.py: regex format-matching, excludes
   │   Wikipedia-only keywords and npm package-name artifacts as
   │   non-commercial/non-topic noise)
   ▼
product_ideas (SQLite)
   │  (agents/content_agent.py: deterministic per-format generators -
   │   calculator/checklist/template/prompt_pack are genuinely usable
   │   output; ebook/sop are outline skeletons, status='draft')
   ▼
products (SQLite) + data/exports/products/*.{html,md,csv}
   → data/exports/run_XXXX.json + _ideas.csv
```

## Database schema

See [db/schema.sql](../db/schema.sql) — the single source of truth. Summary:

| Table | Purpose |
|---|---|
| `runs` | One row per pipeline execution; tracks stage/status/timing |
| `signals_raw` | Raw hits from the 5 free APIs, full JSON payload kept |
| `keywords` | Deduplicated, cumulative keyword candidates |
| `keyword_run_stats` | Per-run occurrence/weight snapshot (powers growth scoring) |
| `competition_checks` | Per-run npm/GitHub/Stack Exchange/Wikipedia supply check, top-20 shortlist only |
| `demand_scores` | Per-run score + components per keyword (re-blended for the checked shortlist) |
| `niches` / `niche_keywords` | Manual/future-automated keyword clustering (not yet populated) |
| `product_ideas` | Generated product briefs (title, format, rationale, target keyword) |
| `products` | Actually-built product files (path, format, status ready/draft) |
| `pages` | Landing pages (empty until a Landing Page Agent exists) |
| `analytics_events` | Traffic/conversion events (empty until publishing exists) |

## Design decisions worth knowing

- **No LLM dependency yet.** No local Ollama install or OpenRouter key was
  present in this environment, so both Product Idea Generation and Content
  Generation are rule-based/template-based, not LLM-generated. This keeps
  the system 100% free and fully deterministic/auditable, at the cost of
  creativity. Formats that can be genuinely useful without free-text
  writing (calculator, checklist, template, prompt_pack) ship as "ready";
  formats that need real prose (ebook, sop) are intentionally left as
  reviewable outline skeletons at status='draft' rather than faking
  finished content. First thing to upgrade once a model is wired in (see
  ROADMAP).
- **SQLite lives in git**, not `.gitignore`d. For a single-writer, low-volume
  pipeline this is simpler and freer than standing up Supabase/Turso, and it
  gives free version history of the whole business's memory for nothing.
  Revisit if the file grows large or multiple writers appear.
- **Per-source percentile-rank normalization** in the keyword agent, not raw
  log-scaling — otherwise Wikipedia's 100k+ pageviews would always outrank
  HN's ~500-point stories regardless of actual relative significance.
- **Wikipedia is kept but fenced off from product ideation.** It's a decent
  general zeitgeist/timely-content signal but a poor proxy for "a problem
  someone would pay to have solved" (top pageviews skew celebrity/movie/
  sports). It stays in `keywords` for a future SEO/content-timing use case.
