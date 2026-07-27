-- Core schema for the autonomous digital business pipeline.
-- SQLite. Safe to re-run: all statements are CREATE TABLE IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    stage TEXT NOT NULL,          -- e.g. 'market_research', 'keyword_discovery', 'demand_scoring', 'product_ideation'
    status TEXT NOT NULL DEFAULT 'running', -- running | success | failed
    notes TEXT
);

-- Raw signals pulled from free/no-auth public APIs (Market Research + Trend Agent).
CREATE TABLE IF NOT EXISTS signals_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    source TEXT NOT NULL,         -- hackernews | wikipedia_pageviews | npm_downloads | stackexchange | github
    signal_type TEXT NOT NULL,    -- 'discussion' | 'pageview' | 'download_count' | 'question' | 'repo'
    term TEXT NOT NULL,           -- extracted candidate term/title
    metric_value REAL,            -- points, views, downloads, stars, score...
    url TEXT,
    fetched_at TEXT NOT NULL,
    payload_json TEXT             -- raw JSON for traceability/reprocessing
);
CREATE INDEX IF NOT EXISTS idx_signals_raw_run ON signals_raw(run_id);
CREATE INDEX IF NOT EXISTS idx_signals_raw_term ON signals_raw(term);

-- Deduplicated keyword candidates (Keyword Discovery Agent).
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL UNIQUE,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    times_seen INTEGER NOT NULL DEFAULT 0,
    sources_json TEXT,             -- json list of distinct sources that mentioned it
    latest_score REAL
);

-- Per-run occurrence/weight snapshot per keyword, used to compute the
-- growth component in demand scoring (this run vs. historical average).
CREATE TABLE IF NOT EXISTS keyword_run_stats (
    keyword_id INTEGER NOT NULL REFERENCES keywords(id),
    run_id INTEGER NOT NULL REFERENCES runs(id),
    occurrences INTEGER NOT NULL,
    weight REAL NOT NULL,
    sources_json TEXT,
    created_at TEXT NOT NULL,
    PRIMARY KEY (keyword_id, run_id)
);

-- Competition/saturation check per keyword per run (Competitor Analysis
-- Agent). Only computed for a top shortlist per run (not every keyword) -
-- GitHub's unauthenticated Search API caps at 10 req/min, so checking all
-- ~60 keywords discovered per run isn't feasible without an API key.
CREATE TABLE IF NOT EXISTS competition_checks (
    keyword_id INTEGER NOT NULL REFERENCES keywords(id),
    run_id INTEGER NOT NULL REFERENCES runs(id),
    npm_package_count INTEGER,
    github_repo_count INTEGER,
    stackexchange_answered_count INTEGER,
    wikipedia_dedicated_article INTEGER, -- 0/1
    saturation_score REAL NOT NULL,      -- 0 (wide open) .. 1 (heavily saturated)
    checked_at TEXT NOT NULL,
    PRIMARY KEY (keyword_id, run_id)
);

-- Demand scores per keyword per run (Demand Scoring Agent).
CREATE TABLE IF NOT EXISTS demand_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER NOT NULL REFERENCES keywords(id),
    run_id INTEGER NOT NULL REFERENCES runs(id),
    score REAL NOT NULL,
    frequency_component REAL,
    growth_component REAL,
    breadth_component REAL,        -- number of distinct independent sources
    components_json TEXT,
    scored_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_demand_scores_keyword ON demand_scores(keyword_id);

-- Niches: manually or automatically grouped clusters of related keywords.
CREATE TABLE IF NOT EXISTS niches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS niche_keywords (
    niche_id INTEGER NOT NULL REFERENCES niches(id),
    keyword_id INTEGER NOT NULL REFERENCES keywords(id),
    PRIMARY KEY (niche_id, keyword_id)
);

-- Product Idea Generation Agent output.
CREATE TABLE IF NOT EXISTS product_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    title TEXT NOT NULL,
    format TEXT NOT NULL,          -- ebook | checklist | template | calculator | sop | prompt_pack | ...
    target_keyword_id INTEGER REFERENCES keywords(id),
    niche_id INTEGER REFERENCES niches(id),
    demand_score REAL,
    rationale TEXT,
    status TEXT NOT NULL DEFAULT 'proposed', -- proposed | approved | rejected | built
    created_at TEXT NOT NULL
);

-- Built products (Content/Book/Template/Spreadsheet Agents write here in later stages).
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL REFERENCES product_ideas(id),
    title TEXT NOT NULL,
    format TEXT NOT NULL,
    file_path TEXT,
    status TEXT NOT NULL DEFAULT 'draft', -- draft | ready | published
    monetization_url TEXT, -- set once a product is listed for sale (e.g. Gumroad); NULL = free download
    tier TEXT, -- core | lead_magnet | retire_candidate | NULL (not yet classified) - see docs/ROADMAP.md
    created_at TEXT NOT NULL,
    published_at TEXT
);

-- Landing pages (Landing Page Agent / SEO Agent write here).
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id),
    url TEXT,
    title TEXT,
    meta_description TEXT,
    status TEXT NOT NULL DEFAULT 'draft', -- draft | published
    seo_enhanced INTEGER NOT NULL DEFAULT 0, -- 0/1, set by seo_agent.py so re-runs don't double-inject
    created_at TEXT NOT NULL
);

-- Analytics events (Analytics Agent writes here once traffic exists).
CREATE TABLE IF NOT EXISTS analytics_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL REFERENCES pages(id),
    event_type TEXT NOT NULL,     -- pageview | click | lead | sale
    count INTEGER NOT NULL DEFAULT 0,
    period_start TEXT,
    period_end TEXT,
    source TEXT,
    recorded_at TEXT NOT NULL
);

-- One snapshot row per pipeline run (scoreboard_agent.py). Real, computed
-- numbers only - no estimated/fabricated dollar figures. This is what
-- lets docs/COMPANY_SCOREBOARD.md show a trend over time instead of a
-- single point-in-time report.
CREATE TABLE IF NOT EXISTS company_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES runs(id),
    computed_at TEXT NOT NULL,
    total_keywords INTEGER,
    new_keywords_7d INTEGER,       -- learning-velocity proxy: real, computable from keywords.first_seen
    total_signals INTEGER,
    total_products INTEGER,
    ready_products INTEGER,
    core_tier_count INTEGER,
    lead_magnet_count INTEGER,
    retire_candidate_count INTEGER,
    live_pages INTEGER,
    seo_enhanced_pages INTEGER,
    monetized_products INTEGER,
    confirmed_revenue_usd REAL,    -- 0 until a real sale is confirmed by the user - never estimated
    experiments_total INTEGER,
    experiments_running INTEGER,
    experiments_succeeded INTEGER,
    experiments_failed INTEGER
);

-- Real experiments (not ideas, not products) - a hypothesis with a
-- defined success metric that either passes or fails. Structure only for
-- now: see docs/ROADMAP.md on why a full experiment-portfolio scheduler
-- isn't being built yet (no traffic exists to run experiments against -
-- building the harness before that would itself be premature
-- over-engineering). This table exists so the first real experiment has
-- somewhere honest to live the moment one becomes runnable.
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    success_metric TEXT NOT NULL,
    budget TEXT,                   -- human-readable time/resource budget - no metered $ cost exists to assign
    status TEXT NOT NULL DEFAULT 'proposed', -- proposed | running | succeeded | failed | abandoned
    started_at TEXT,
    ended_at TEXT,
    result TEXT,
    created_at TEXT NOT NULL
);
