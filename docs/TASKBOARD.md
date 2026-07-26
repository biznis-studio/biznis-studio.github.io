# Task Board

## Done (iteration 1)
- [x] Project scaffold, docs, `.gitignore`, `requirements.txt`
- [x] SQLite schema (`db/schema.sql`) covering the full intended loop
- [x] Market Research + Trend Agent (5 free, no-auth APIs)
- [x] Keyword Discovery Agent (n-gram extraction, per-source rank normalization)
- [x] Demand Scoring Agent (frequency/breadth/growth components)
- [x] Product Idea Generation Agent (rule-based format matching)
- [x] Orchestrator (`scripts/run_pipeline.py`) + JSON/CSV export
- [x] Dockerfile + docker-compose.yml
- [x] GitHub Actions workflow for a daily scheduled run (activated in iteration 5)
- [x] First real end-to-end run producing 12 product ideas from live data

## Done (iteration 2)
- [x] Filtered npm package-name artifacts out of product ideation (e.g.
      "@editorjs/checklist", "react-spreadsheet" aren't market topics)
- [x] Content/Template Agent: real files for calculator/checklist/template/
      prompt_pack, outline-only drafts for ebook/sop
- [x] Verified the generated calculator actually computes correctly and
      fixed a dark-mode contrast bug found during manual browser testing
- [x] Wired Content Agent into the orchestrator; report now includes each
      idea's product file path/status

## Done (iteration 3)
- [x] Competitor Analysis Agent (`agents/competitor_agent.py`): checks
      npm/GitHub/Stack Exchange/Wikipedia supply for the run's top 20
      keywords, bounded by GitHub's 10 req/min unauthenticated search limit
- [x] Demand Scoring Agent split into two passes; pass 2 re-blends the
      checked shortlist's score with a 25%-weighted opportunity component
- [x] Found and documented a real limitation: the competition signal
      saturates trivially (1.0) for generic single-word keywords like
      "checklist"/"calculator" since GitHub code-repo density isn't the
      same thing as consumer-content market saturation — logged in
      ROADMAP.md rather than presented as solved

## Done (iteration 4)
- [x] Niche Clustering Agent (`agents/niche_agent.py`): union-find over
      keywords that co-occurred in the same underlying signal
- [x] Verified the clustering + DB-insertion logic is correct with a
      synthetic co-occurring pair on a scratch DB copy
- [x] Confirmed 0 niches on the real run is an honest data-sparsity result
      (single-word keywords, ~230 signals/run), not a bug — documented in
      ROADMAP.md rather than papered over

## Done (iteration 5)
- [x] Installed GitHub CLI, authenticated, pushed repo to
      https://github.com/fwwk4pb868-afk/biznis (public)
- [x] Verified the scheduled Action end-to-end: manual `workflow_dispatch`
      run succeeded and the bot commit landed back on `main`
- [x] Decided: ebook/sop prose will be written using Claude directly by the
      user, not an automated Ollama/OpenRouter call — updated ROADMAP.md
- [x] Landing Page Agent (`agents/landing_page_agent.py`): real static
      pages under `site/` for "ready" products only; found and fixed a
      real bug (intro blurb rendering above the calculator's own title)
      during manual browser verification

## Done (iteration 6)
- [x] SEO Agent (`agents/seo_agent.py`): schema.org JSON-LD (no fake
      ratings/reviews - explicitly excluded per project rules), Open Graph
      tags, a genuine FAQ mirrored as FAQPage schema, internal "more free
      tools" links - injected idempotently via new `pages.seo_enhanced` column
- [x] Added a lightweight DB migration mechanism (`core/db.py::MIGRATIONS`)
      since `CREATE TABLE IF NOT EXISTS` doesn't add columns to existing tables
- [x] Found and fixed a real bug: HowTo step text was pulled from
      already-HTML-escaped page content, so JSON-LD literally contained
      `&quot;` instead of a real quote character
- [x] Deliberately did NOT build sitemap.xml/RSS yet - both assert "this is
      live at this URL", not true until `SITE_BASE_URL` is set at deploy time

## In progress / next
- [ ] Decide: deploy `site/` to Cloudflare Pages or GitHub Pages (needs your go-ahead)

## Backlog (see ROADMAP.md for detail and ordering rationale)
- [ ] Analytics Agent
- [ ] Conversion analysis + feedback loop back into demand scoring

## Milestones
- **M1 — Discovery loop proven with real data** ✅ (iteration 1)
- **M2 — First real product file exists and is reviewable by the user** ✅ (iteration 2 — see `data/exports/products/`)
- **M2.5 — Pipeline runs autonomously on a schedule, not just locally** ✅ (iteration 5 — see the Actions tab on the repo)
- **M3 — First page published and receiving organic traffic**
- **M4 — First measured lead or sale attributed to the pipeline**
