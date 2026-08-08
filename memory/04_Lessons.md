# Lessons (reusable only, max 10 lines each)

**Rebuilding a page wipes its SEO markup.** `build_page()` resets to pre-`seo_agent` state.
Always: `pages.seo_enhanced=0` then re-run `seo_agent`. `build_site.py` does this — never hand-roll.

**`git rebase --ours` is UPSTREAM, not your commit** (opposite of merge). Discarded new DB rows once.
Use `--theirs` when replaying your own work in a rebase; verify row counts after.

**Deploy success ≠ live.** A concurrent push once failed the pipeline silently; site sat stale for hours
while local build looked fine. Never report "done" from a local build — `scripts/deploy.py` verifies the live URL.

**Apostrophes inside single-quoted JS strings break the whole inline `<script>` silently.**
The page renders, the widget just does nothing. Verify by driving the tool and reading output, not by "it built".

**Subagent research must be re-verified on primary sources before acting.** One fan-out claimed a github.io
site ranked page-1 on Google; it was DuckDuckGo-only and didn't replicate. Always spot-check load-bearing claims.

**Don't confuse "not lying" with "advertising your own weakness."** Both are wrong in opposite directions.
State what's true; frame risk-transfer (fixed price, written scope) as a guarantee, not a confession.

**Calculator page bypasses `page_shell()`** — has its own `<style>` block, silently drifts from site-wide changes.
Any global template/CSS change must also touch `inject_intro_into_calculator()`.

**STRATEGY (2026-08-08, supersedes data-moat goal):** build a profitable AI-enabled service where
proprietary WORKFLOW, execution and customer integration are the moat — not owning public data.
Sequence: `PROBLEM → PAYMENT → WORKFLOW → AI AUTOMATION → PRODUCTISATION`. Opening question is
"what repeated corporate work does someone already pay for that AI can standardise with far better
economics?" Every candidate must pass the 8-point BUSINESS GATE in `docs/RESEARCH_LOG.md` — Q8
("why not just use ChatGPT directly?") is the hardest; "better prompt" is not an answer.
**AI is not the product, AI is the production mechanism.**

**Q5 and Q6 are in tension (RL-3).** A dataset moat requires nobody else holds the history; a
business case requires someone would pay for it. But series get collected BECAUSE they have
recognised value — so anything worth paying for is usually already sold (verified across 8 state
classes: Wayback, CT logs, Shodan, SecurityTrails, self-archiving registers, flight/hotel price
APIs, Semrush/Ahrefs, governments). A proprietary-dataset flagship is structurally unavailable to
us. Don't reopen without a specific system that passes the Q0 7-point test on evidence.

**Order of work (RL-1, binding).** Not `topic → content → tool → SEO → look for evidence`.
Instead: `observable property → population → measurement → falsification → dataset → product`.
A measurable property and a defensible route to the data must exist BEFORE any thesis, article,
tool or business model. Flagship candidates must pass the 7-point filter in `docs/RESEARCH_LOG.md`.

**Never publish a number without a mandatory UNKNOWN category and pre-registered thresholds.**
RL-1 nearly shipped "64% of manufacturers' documentation is unavailable" — false, driven by
marketing PDFs and our own classifier defects. Segmentation only happened because the protocol
forced it. Classifier defects produce confident wrong output without ever crashing.

**Machinery Regulation is OUT as a flagship candidate** (RL-1, 2026-08-02) — no cheap, open,
representative data source exists. The existing free tool stays and is correct; do not add any
claim about industry behaviour to it. Do not turn RL-1's negative results into site content.

**`node --check` proves a script PARSES, never that it's RIGHT.** The Machinery tool computed the
Art. 10(7) window as `life + 10` for weeks — the law says lifetime AND ≥10y, both from placing on
market, so it's `max(life, 10)`. Overstated a 15y machine by a decade and the cost by 67%. The page
quoted the law correctly the whole time; only the calculator misread the sentence above it.
**Quoting a source correctly ≠ implementing it correctly.** Test calculators by executing them
against a stubbed DOM with hand-computed expected values, including boundaries.

**Build gates fail only on what WE control.** External-link checking lives in
`scripts/check_links.py`, never in `audit_site.py` — a gate that fails because someone else's server
is briefly down gets routed around. Treat its output as advisory: 403 usually = bot-blocking
(Pexels), 502 = transient (indiehackers). Confirm with 2+ clients before changing a citation; a
correct source we can't reach is still better than a worse one we can.

**`page_shell(is_index=True)` means "root-level + wide layout", NOT "is the homepage".**
`work.html`/`credits.html` share it and once inherited the homepage's canonical (= "don't index me")
and its hreflang. Pass `canonical_path="work.html"` for any new root-level page that isn't `/`.

**All absolute URLs go through `agents.common.canonical_url()`** — directory form (`/sk/`, not
`/sk/index.html`). Four call sites (sitemap, RSS, canonical tags, IndexNow) built them by hand and
drifted; the sitemap ended up advertising a URL the page itself disclaimed.

**When adding an audit check, run it against the BROKEN site first.** A green run on already-fixed
output proves nothing. Doing this caught a bug in the check itself (unconditional `index.html` slice
mangled shorter filenames, hiding the very bug it was written for).

**hreflang must be reciprocal or Google ignores it entirely.** Google: "if two pages don't both
point to each other, the tags will be ignored." `/sk/` carried it alone for weeks = dead markup.
Only `/` ↔ `/sk/` are annotated as alternates; SK articles correctly have none (no EN counterpart —
hreflang naming a non-existent alternate is worse than none). Never auto-redirect by browser
language: Google prefers an explicit selector, and it can hide a version from Googlebot.

**Slovak quotes: `„text“`, never `„text"`.** All 5 SK articles shipped with a straight ASCII
closing quote (13 occurrences) before anyone noticed. Grep `content/sk/*.md` for `"` before shipping —
zero is the only correct count. Watch for quotes spanning a line break; scripted fixes miss those.

**Measure the internal link graph, don't assume it.** Every SK article had 1 inbound link and 0
links to each other — five dead ends, not a cluster. `blog_agent._sk_related_html()` now generates
"Ďalej čítajte" from a curated `SK_RELATED` map (+ newest-first fallback). Pages generated by
`landing_page_agent` (e.g. the e-faktúra tool) are NOT covered by it — link those by hand.

**`audit_site.py` only checked `products/*.html` + `index.html` for years.** Every `site/sk/`,
`site/tools/`, `site/blog/`, `site/news/` page shipped unaudited despite the gate "passing".
Widened to `site/**/*.html` (iteration 70) — immediately caught 2 real over-length meta
descriptions. Any new site directory needs the audit's glob updated, not just the build script.

**Fake-edge test for pipeline stages:** for any two sequential steps, ask if the second actually needs
the first's output. `market_research_agent`'s 5 source fetchers (+ npm/StackExchange's internal per-term
loops) had none — fanned out with `ThreadPoolExecutor`, ~8.98s→4.21s avg (noisy, measured not assumed).
DB writes stay single-threaded (sqlite3 isn't thread-safe). Apply this test before adding new pipeline stages.
