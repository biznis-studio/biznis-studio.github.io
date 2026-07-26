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

## In progress / next
- [ ] Competitor/Competition Analysis Agent
- [ ] Niche clustering (populate `niches` / `niche_keywords`)

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
