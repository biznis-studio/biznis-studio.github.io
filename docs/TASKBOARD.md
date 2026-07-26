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
- [x] GitHub Actions workflow for a daily scheduled run (not yet active — no remote pushed)
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

## In progress / next
- [ ] Decide: push repo to GitHub + enable the scheduled Action (needs your go-ahead)

## Backlog (see ROADMAP.md for detail and ordering rationale)
- [ ] LLM-assisted ideation (Ollama or OpenRouter — needs your decision)
- [ ] Landing Page Agent
- [ ] SEO Agent
- [ ] Publishing (Cloudflare Pages / GitHub Pages — needs remote repo)
- [ ] Analytics Agent
- [ ] Conversion analysis + feedback loop back into demand scoring

## Milestones
- **M1 — Discovery loop proven with real data** ✅ (iteration 1)
- **M2 — First real product file exists and is reviewable by the user** ✅ (iteration 2 — see `data/exports/products/`)
- **M3 — First page published and receiving organic traffic**
- **M4 — First measured lead or sale attributed to the pipeline**
