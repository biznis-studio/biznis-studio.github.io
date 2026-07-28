# Biznis — Autonomous Digital Business Engine

**Live at https://biznis-studio.github.io/**

A modular, self-improving pipeline that discovers demand signals from free
public APIs, scores them, and proposes original digital-product ideas
(ebooks, checklists, templates, calculators, prompt packs) with a documented
rationale for each. No paid APIs, no scraping against terms of service, no
fabricated traffic or reviews — every signal is traceable back to a public,
no-auth-required source.

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for how it fits together and
[ROADMAP.md](docs/ROADMAP.md) for what's built vs. planned.

## Quickstart

```bash
pip install -r requirements.txt
python3 core/db.py                 # initialize SQLite schema
python3 scripts/run_pipeline.py    # run one full loop iteration
```

Output:
- `db/biznis.sqlite3` — all runs, signals, keywords, scores, product ideas
- `data/exports/run_XXXX.json` — full machine-readable report for that run
- `data/exports/run_XXXX_ideas.csv` — product ideas + generated file paths
- `data/exports/products/*.{html,md,csv}` — the actual generated product files

## The loop (current implementation)

```
Market Research → Keyword Discovery → Niche Clustering → Demand Scoring (1)
      → Competition Analysis → Demand Scoring (2, re-blend) → Product Ideas
      → Content Generation → Landing Pages → SEO Enhancement
```

| Stage | Agent | File |
|---|---|---|
| Market research + trend detection | Market Research Agent | [agents/market_research_agent.py](agents/market_research_agent.py) |
| Keyword discovery | Keyword Agent | [agents/keyword_agent.py](agents/keyword_agent.py) |
| Niche clustering (co-occurrence) | Niche Agent | [agents/niche_agent.py](agents/niche_agent.py) |
| Demand scoring (2 passes) | Demand Scoring Agent | [agents/demand_scoring_agent.py](agents/demand_scoring_agent.py) |
| Competition analysis (top-20 shortlist) | Competitor Agent | [agents/competitor_agent.py](agents/competitor_agent.py) |
| Product ideation | Product Agent | [agents/product_agent.py](agents/product_agent.py) |
| Content generation | Content Agent | [agents/content_agent.py](agents/content_agent.py) |
| Landing pages (static site) | Landing Page Agent | [agents/landing_page_agent.py](agents/landing_page_agent.py) |
| SEO enhancement (schema.org/OG/FAQ/internal links) | SEO Agent | [agents/seo_agent.py](agents/seo_agent.py) |
| Orchestration | — | [scripts/run_pipeline.py](scripts/run_pipeline.py) |

Output also includes:
- `site/index.html` + `site/products/*.html` — a static site, one page per
  "ready" product, each with schema.org JSON-LD + OG tags + a genuine FAQ.
  Deployed live via GitHub Pages (see below).
- `site/sitemap.xml` + `site/feed.xml` — generated once `SITE_BASE_URL` is
  set (the deployed pipeline sets this automatically; running locally
  without it skips both, since a sitemap for a URL that isn't real would
  be misleading).

Everything past "SEO Enhancement" (analytics, conversion feedback loop) is
not yet built — see the roadmap.

## Data sources (all free, public, no API key)

- Hacker News front page — [Algolia HN Search API](https://hn.algolia.com/api)
- Wikipedia top pageviews — [Wikimedia REST API](https://wikimedia.org/api/rest_v1/)
- npm registry search popularity — [npm public search API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)
- Stack Exchange active questions — [Stack Exchange API v2.3](https://api.stackexchange.com/docs)
- GitHub recently-created trending repos — [GitHub REST search API](https://docs.github.com/en/rest/search)

## Running on a schedule

Repo: **https://github.com/biznis-studio/biznis-studio.github.io** (public).
`.github/workflows/pipeline.yml` runs the loop daily via GitHub Actions
(free, unlimited minutes on public repos), commits the updated database +
reports + site back to the repo, then deploys `site/` to GitHub Pages via
`actions/deploy-pages`. Demand history accumulates over time, so the
growth-scoring component and the live site both get more accurate/complete
with every run.

## Docker

```bash
docker compose up --build
```

## Principles

- Legal, ethical, GDPR-respecting, copyright-respecting by construction.
- Every claim an agent makes is traceable to a specific public data point.
- No stubs pretending to be finished features — see ROADMAP.md for what's
  honestly not built yet.
