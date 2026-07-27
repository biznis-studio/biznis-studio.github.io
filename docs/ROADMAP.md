# Roadmap

Ordered by expected leverage, not by the order listed in the original brief.
Re-evaluate this ordering every iteration — see TASKBOARD.md.

## Operating principle (2026-07-27): optimize the company, not the product

The mission is not "build products," "build a website," or "increase
traffic" — those are strategies, not the goal. The only objective is to
maximize the long-term value of the company itself. A specific product,
page, or piece of content can be deleted tomorrow without threatening the
company; the system (data, code, distribution channels, audience) must
survive any single product's failure. Never get attached to a previous
decision if the data says something else now has higher expected value.

Concrete consequences of this framing:

- **Terminology**: this project never builds literal "Departments"
  (confirmed 2026-07-27: no such construct exists in the codebase). When a
  cross-cutting responsibility needs a name, it's a **Capability** (e.g.
  "SEO capability" = `seo_agent.py` + `sitemap.xml`/`feed.xml`/IndexNow) or
  a **Decision Engine** (e.g. "Product tiering" = the `products.tier`
  classification + the rule it enforces in `product_agent.py`), not a
  department with a headcount that doesn't exist for a zero-revenue company.
- **Expected Business Value before building anything new.** Before
  implementing the next roadmap item, weigh it against the alternatives on:
  expected cost (my time + any real $ cost), expected revenue, probability
  of success, time to profit, ongoing maintenance cost, risk, automation
  potential, and expected lifetime. Never build the second-best option when
  a higher-EBV one is available and unblocked. See "Next up, ranked by EBV"
  below — re-rank it every iteration rather than working the list in a
  fixed order.
- **Company Assets, not page count.** The things actually worth compounding
  are: the knowledge base (`signals_raw`/`keywords` — 4,408 raw signals,
  85 deduplicated keywords as of 2026-07-27, growing every scheduled run),
  the reusable code/design system (`agents/common.py`'s renderer, CSS
  system, PDF export — every new product reuses this for free), the product
  catalog itself (14 `ready` products, tiered by validated demand), and the
  two service capabilities (web dev, chatbots — billable without inventory
  risk). Explicitly **not yet real assets**, so not listed as one: an email
  list (no capture mechanism live — Formspree form exists but isn't wired
  to a newsletter), an audience/community (zero measured traffic - see
  below), an affiliate network, a "brand" beyond the design system. Don't
  claim these exist until they honestly do.
- **The current single biggest constraint on enterprise value is
  distribution, not product supply.** 14 ready products/pages exist and 0
  are confirmed indexed by Google (iteration 17); IndexNow (Bing/Yandex/
  Seznam/Naver/Yep only, not Google) has been returning 403 since
  2026-07-27 with no known fix. This means the honest expected revenue of
  *any* new product is currently ~0 until at least one real discovery
  channel works, regardless of how good the product is — building more
  content right now has a lower EBV than fixing distribution. Google
  Search Console (the direct fix) was explicitly paused by the user
  mid-setup and hasn't been resumed since; this is flagged again here
  because the EBV math changed, not because the user's earlier pause
  decision is being second-guessed.

- **Never assume the current strategy is correct just because it's already
  implemented.** A tactical EBV ranking (below) answers "what's next given
  this business model" - it does not, by itself, question whether the
  business model is still the best available option. That harder question
  gets a dedicated **Strategic Review** (see docs/STRATEGIC_REVIEWS.md):
  10 fixed questions, minimum weekly cadence, answered with real data, and
  an explicit willingness to recommend a radical pivot if the data
  supports one. The first review (2026-07-27) is already logged there.

- **Human attention is the primary bottleneck, not software - protect it
  aggressively.** This system can generate code, content, and analysis
  faster than a human can act on any of it. The scarce resource is the
  user's time, cognitive load, and decision-making capacity, not more
  agent output. Concretely: reduce the number of decisions the human must
  make; reduce the number of manual steps; batch related requests into one
  sitting instead of interrupting repeatedly; never ask for a manual
  action that can wait until it can be bundled with other related ones.
- **Human Cost Analysis before requesting any manual action.** Before
  asking the user to do anything by hand (create an account, click
  verify, paste a token), estimate: human time required, cognitive load,
  waiting time, probability of failure, long-term maintenance burden, and
  the Expected Business Value actually unlocked. If an action doesn't
  unlock significant EBV, don't ask for it. Always look for an alternative
  that needs fewer manual actions first. In practice: don't request
  pending human actions one at a time as they're discovered - maintain a
  single ranked, batched list (see TASKBOARD.md's "Human Action Batch")
  and only surface it as one consolidated ask, so the user can clear
  several blockers in one short session instead of being interrupted
  repeatedly for each one individually.

- **CEO Mode.** This system is not a software developer, not a project
  manager - it's the capital allocator for this company. Software, SEO,
  content, and marketing are tools, not the job. Every hour of engineering
  time, every request made of the human, every feature, every experiment
  is an investment competing for the same scarce resources (the agent's
  time budget and the human's attention). Success is measured by the
  quality of decisions made, not the volume of work completed - a
  quiet iteration that correctly says "don't build anything, the
  constraint is elsewhere" is a better outcome than a busy one that ships
  a feature nobody needed.
- **Constraint-Driven Management.** A company is limited by a very small
  number of real constraints at any given time (Theory of Constraints).
  The primary job each iteration is to identify *the* current constraint -
  not a list of problems, one constraint - and refuse to optimize
  anything else, however tempting. See docs/CONSTRAINT_LOG.md: every
  entry records the current constraint, the evidence for it, the EBV if
  removed, the cost to remove it, a confidence level, and what
  alternative constraints were considered and rejected. When the evidence
  says the constraint has changed, reprioritize the roadmap immediately -
  never keep working on yesterday's bottleneck out of momentum.
- **Decision Journal.** Every strategic decision (not tactical bug fixes)
  gets recorded in docs/DECISION_JOURNAL.md: the decision, the reasoning,
  the assumptions it depends on, the alternatives that were rejected and
  why, the expected outcome, the metrics that would validate or invalidate
  it, and a review date. When new evidence shows up (a Strategic Review,
  new traffic/revenue data, a constraint change), revisit the relevant
  past entries explicitly rather than re-deciding from scratch or
  silently drifting - the company should learn from its own recorded
  decisions, not rely on someone re-reading the whole conversation history.

- **Blocked Task Policy - never idle on one dependency.** Some tasks are
  blocked on an action only the human can legally/technically perform
  (login to a personal account, identity verification, entering payment
  details) - no prompt or amount of agent cleverness changes that. The
  correct response to a blocked task is never to wait idle:
  1. Mark it `BLOCKED` with its Expected Business Value recorded (see
     docs/CONSTRAINT_LOG.md and the Human Action Batch in TASKBOARD.md).
  2. Note a retry/recheck point (e.g. "recheck once the user says it's
     done," not a literal timer, since this system only runs when a
     session is active) - don't ask about the same blocked item again
     before that point.
  3. Immediately move to the next-highest-EBV *unblocked* task - research,
     engineering/tech-debt, SEO/technical audits, competitor analysis,
     conversion improvements, internal tooling, pipeline refactoring, new
     validated product ideas. There is always unblocked work available in
     a project this size; "nothing else needed from you" is never an
     acceptable way to end a turn.
  4. Only surface a blocked item to the human again when it has become
     *the* single highest-EBV constraint (per the Constraint Log) AND no
     other high-value unblocked work remains - not on every turn.
  - Think in state transitions, not a straight-line pipeline:
    `BLOCKED -> skip to next task`, `DONE -> pull next task`,
    `FAILED -> find a different path`, `LOW EBV -> drop it`,
    `HIGH EBV -> do it`, `UNKNOWN -> research it first`. Never
    `BLOCKED -> wait`.
- **On multi-agent architecture**: the user proposed a durable next step -
  separate CEO/Research/Engineering/Growth/Review agents running in
  parallel, so one blocked workstream (e.g. Growth blocked on Search
  Console) doesn't stall the others. Honest current state: this session
  is one Claude Code agent working sequentially, not literally parallel
  processes with separate memory. The `Agent` tool can spawn genuinely
  independent background subagents (e.g. a research pass while
  engineering work continues in the foreground) and is worth reaching for
  when a task is truly independent and substantial - but should be used
  for real parallel work, not simulated as decoration. Scheduled/cron
  sessions (already used for the daily pipeline run) are the other real
  mechanism for a distinct cadence per workstream. Don't fake multi-agent
  theater with role-labeled sections written by the same single pass.

## Next up, ranked by EBV (2026-07-27)

1. **Resolve the distribution bottleneck** — either resume Google Search
   Console verification (fastest real fix, needs the user's go-ahead since
   it was explicitly paused before) or find another free/no-account
   indexing path. Highest EBV: unlocks revenue potential for all 14
   existing products at once, near-zero build cost, blocks everything else.
2. **Get the two `core`-tier products paid on Gumroad** (Scope Creep Kit,
   Retainer Renewal Kit) — blocked on the user's own Stripe KYC/business-
   status decision, not on more building. Second-highest EBV per unit of
   effort *for the user*, ~zero additional engineering cost for this
   system once unblocked.
3. **Analytics** (Cloudflare Web Analytics or similar) — needed to turn
   "distribution exists" into a feedback loop, but has ~zero value until
   #1 produces actual visits to measure. Sequenced after #1, not before.
4. **More content/products** — deliberately ranked last. The product
   catalog is not the constraint right now; distribution is. Only pursue
   this for the validated `core` family (freelancer swipe-file system) if
   #1-#3 are blocked on the user and there's still available effort.

## Next up

1. ~~**Competitor/Competition Analysis Agent**~~ — done: `agents/competitor_agent.py`
   checks npm/GitHub/Stack Exchange/Wikipedia supply for the run's top 20
   keywords (bounded by GitHub's 10 req/min unauthenticated search limit)
   and `demand_scoring_agent.apply_competition()` re-blends their score with
   a 25%-weighted opportunity component. See known limitations below - this
   works well for developer-tool-shaped ideas, poorly for generic single
   words.
2. ~~**Niche clustering**~~ — done: `agents/niche_agent.py` links keywords
   extracted from the *same* underlying signal (same HN title, same SE
   question) via union-find; connected components of size 2+ become a
   niche. Verified the mechanism works correctly with a synthetic
   co-occurring pair, but it found **zero real niches on the first run** -
   with ~230 signals/run and most surviving keywords being single,
   lexically distinct words (checklist, invoice, spreadsheet...), no two
   currently ever share the same sentence. This is an honest data-sparsity
   result, not a bug - expect real niches to emerge as run history
   accumulates, and revisit with embedding-based semantic clustering (see
   #4) since that could group "invoice" + "spreadsheet" + "template" as
   related even without any shared substring.
3. ~~**Content/Template Agent**~~ — done: `agents/content_agent.py` authors
   calculator/checklist/template/prompt_pack ideas as real, usable files;
   ebook/sop ship as outline skeletons (`status='draft'`) since they need
   real prose an LLM or human still has to write.
4. **LLM-assisted content drafting (ebook/sop prose)** — decided 2026-07-26:
   the user will use Claude directly (not Ollama/OpenRouter) to write the
   actual prose for `draft`-status ebook/sop outlines produced by
   `content_agent.py`. This stays a human-in-the-loop step for now rather
   than an automated API call in the pipeline (no Anthropic API key/billing
   wired into the system) - the outline skeleton is the handoff artifact.
   First one done 2026-07-26: "The Practical Guide to Automation"
   (`products.id=3`) - real ~1300-word prose replacing its outline,
   promoted to `status='ready'`, published with its own landing page.
   Remaining drafts (productivity, xlsx, appium, gantt chart) still need
   the same treatment - see TASKBOARD.md. Revisit full automation only if
   the user wants the pipeline itself to call the Claude API end-to-end
   (would need an API key + billing set up by the user first).
5. ~~**Landing Page Agent**~~ — done: `agents/landing_page_agent.py` builds a
   real static page under `site/` only for `status='ready'` products
   (calculator/checklist/template/prompt_pack) - draft ebook/sop outlines
   are skipped so nothing publishes a skeleton as a finished page. Verified
   all four formats render correctly in-browser, including a real bug found
   and fixed: the intro blurb was injected before the calculator's own
   `<h1>`, rendering visually above the title. `pages.status` stays 'draft'
   until an actual Publishing agent deploys `site/` somewhere.
6. ~~**SEO Agent**~~ — done: `agents/seo_agent.py` injects schema.org
   JSON-LD (SoftwareApplication/HowTo/CreativeWork - never
   AggregateRating/Review, since there are no real reviews to mark up),
   Open Graph tags, a genuine generic FAQ (mirrored as FAQPage schema), and
   internal "more free tools" links, idempotently (tracked via
   `pages.seo_enhanced`). Found and fixed a real bug: the HowTo step text
   was pulled from already-HTML-escaped page content, so JSON-LD literally
   contained `&quot;` instead of a real quote character - fixed with
   `html.unescape()`. sitemap.xml/feed.xml generation was added right
   after, once Publishing (below) made SITE_BASE_URL real.
7. ~~**Publishing**~~ — done 2026-07-26: chose GitHub Pages over Cloudflare
   Pages specifically because it needed no new account (Cloudflare Pages
   would have required the user to sign up there first). Enabled via
   `gh api repos/.../pages` with `build_type=workflow`; `pipeline.yml` now
   uploads `site/` as a Pages artifact and deploys it via
   `actions/deploy-pages` in a second job after every pipeline run. Live at
   https://fwwk4pb868-afk.github.io/biznis/. `SITE_BASE_URL` is set as a
   workflow-level env var, which is what turns on canonical URLs +
   sitemap.xml + feed.xml in `seo_agent.py`.
8. **Analytics Agent** — once pages are live, pull free analytics
   (Cloudflare Web Analytics is free and privacy-respecting, or
   plausible/umami self-hosted) into `analytics_events`.
9. **Conversion/Feedback loop** — once real traffic/analytics exist, close
   the loop back into demand scoring (a keyword whose product converts well
   should boost related keywords' scores).

## Strategy: product tiering + retired fallback (2026-07-27)

Rather than keep treating every product as equally worth building on, this
session's accumulated demand-validation research (iterations 14/18/19) was
turned into real data instead of staying implicit tribal knowledge:

- Added `products.tier` (`core` | `lead_magnet` | `retire_candidate` | NULL)
  via the standard `core/db.py::MIGRATIONS` mechanism. Classified all 28
  existing products:
  - **`core` (7)**: the monetized automation ebook; the Scope Creep Kit +
    Change Request Log pair; the Retainer Renewal Kit + Tracker pair; the two
    service offerings (web dev, chatbots) - real evidence of paid demand or
    direct billable work, per iteration 18/19 research.
  - **`lead_magnet` (7)**: XLSX ebook, generic checklist, spreadsheet pack,
    calculator, invoice pack, EU compliance checklist, resume gap scripts -
    genuinely useful, but no evidence anyone pays for these specifically
    (resume gap scripts explicitly compete against free content from major
    resume sites, per iteration 18). Kept free on purpose, valuable as
    traffic/trust builders, not further investment targets.
  - **`retire_candidate` (14)**: every product built purely from
    `product_agent.py`'s old generic-ebook fallback (Appium, Productivity,
    Detox, Gantt Chart, Seolytics, Dalia, Undefined Variable, Codeigniter
    View/Query, Query Result, Typescript-To-Native Compiler, Google Chrome,
    Hardhat, "there way"). All 14 were still `status='draft'` (outline
    skeletons, never promoted, never given a live page) - confirmed via
    `pages` table that none of them have any public footprint, so no site
    cleanup was needed, just marking them as what they are.
- Set the corresponding `product_ideas.status = 'rejected'` for those 14
  (matching the convention already used for idea #9 "there way" in
  iteration 8), so they stop showing up as live/actionable in any future
  audit.
- **Retired `product_agent.py`'s fallback entirely.** `pick_format()` used
  to return `("ebook", "The Practical Guide to {term}", ...)` for any
  keyword that didn't match a specific `FORMAT_RULES` pattern
  (calculator/checklist/template/prompt_pack/sop). This fallback is exactly
  what produced all 14 `retire_candidate` products - a single scraped
  keyword with zero validation turned directly into a full product brief.
  `pick_format()` now returns `None` for unmatched keywords, and
  `run()` skips them instead of creating an idea. Net effect: the automated
  pipeline can no longer manufacture a new generic single-keyword ebook on
  its own; every future ebook-format product now has to come from deliberate
  research (`manual_research` source, as already used for the EU Compliance
  Checklist and the 3 diversified products in iterations 14-15) rather than
  from raw keyword frequency.

## Explicitly deferred / needs a human decision

- **Monetization: Gumroad chosen, awaiting the user's account + first listing**
  (decided 2026-07-26). The mechanism is built: `products.monetization_url`
  (nullable) - when set, `landing_page_agent.py` replaces the free download
  link with a "Get it on Gumroad" CTA and stops copying that file into
  `site/downloads/` (no point undermining a paid listing by also giving it
  away next to it). Tested end-to-end with a placeholder URL, then
  reverted - real integration is waiting on the user to (1) create a free
  Gumroad account, (2) list a product, (3) give the resulting URL. This
  system does not create payment/seller accounts on anyone's behalf.
  Affiliate links and a newsletter platform remain deferred behind this
  same account-creation constraint - revisit once Gumroad is proven out.
- ~~**GitHub remote**~~ — done 2026-07-26: pushed to
  https://github.com/fwwk4pb868-afk/biznis (public), scheduled Action
  verified working end-to-end (manual run succeeded, bot commit landed).
- ~~**Publishing (GitHub Pages)**~~ — done 2026-07-26, see item 7 above.
- **Competitor keyword-volume tools** (e.g. real search-volume data) are
  mostly paid; look for a free-tier-compliant alternative before building
  this rather than assuming one.

## Known limitations to revisit

- npm popularity signal is seeded from a fixed list of broad terms
  (`NPM_SEED_TERMS` in `market_research_agent.py`), so it partly just
  echoes those seeds back rather than discovering genuinely new terms.
  Replace with a broader/rotating seed list or a real "trending packages"
  source once one is found that's free and ToS-compliant.
- Growth scoring only becomes meaningful after a keyword has appeared in
  2+ runs; first-run scores use a neutral prior. This resolves itself
  automatically as the scheduled pipeline accumulates history.
- Keyword clustering is exact-string-match only (no semantic dedup), so
  e.g. "chatgpt" and "chat gpt" are currently treated as different
  keywords. A local embedding model (via Ollama) would fix this cheaply.
- Product-idea filtering against npm package-name artifacts (`_looks_like_package_name`
  in `product_agent.py`) is a regex heuristic (catches "@scope/name" and
  "kebab-case" patterns), not a real dictionary check — a genuine two-word
  English niche phrase that happens to be hyphenated could theoretically be
  skipped. Revisit if that turns out to matter in practice.
- Competition scoring's fixed saturation thresholds (`_normalize()` in
  `competitor_agent.py`) conflate "code-repository density" with "consumer
  content market saturation": broad single-word keywords like "checklist"
  or "calculator" trivially max out at saturation=1.0 (millions of GitHub
  repos mention the word "automation" in code, which says nothing about
  whether a paid automation checklist ebook already saturates that market).
  This makes the opportunity component weak precisely for the generic
  umbrella terms that are actually our best product categories - it's
  currently most useful for narrow, specific, developer-tool-shaped
  keywords. The Wikipedia "dedicated article exists" check is the most
  meaningful of the four for consumer-content topics; consider weighting
  toward it, or finding a genuine consumer-search-volume proxy, before
  trusting this component heavily.
- ~~The n-gram stopword filter in `keyword_agent.py` occasionally lets
  through incoherent sentence fragments~~ — partially fixed 2026-07-27:
  the specific reported case ("there way", a slice of "is there a way
  to...") is now filtered - added `there/here/some/any/such/other/
  another/same` to `STOPWORDS` (checked first against all existing
  keywords for collisions; only "there way" itself matched, and that idea
  was already rejected). **Real remaining limitation, not fully solved**:
  `significant_ngrams()` only checks that a window's *first and last*
  word aren't stopwords, not the middle ones - so a trigram like "explain
  there way" (fragment word in the middle) still slips through. Fixing
  that needs the filter to reject any window containing a stopword
  anywhere, which risks being overly aggressive on legitimate 3-word
  phrases with a genuine middle stopword (e.g. "guide to xlsx") - needs a
  more careful rule than a blanket change, left for a future pass rather
  than risking silently losing good keywords tonight.
- ~~Any user-facing copy that's built by directly reusing `product_ideas.rationale`...~~
  — resolved 2026-07-26: this kept recurring (every single live page's
  subtitle read like an engineering log - "Keyword implies users want to
  compute something quickly online.") so it got the dedicated field it
  needed. `agents.common.marketing_blurb()` now generates real,
  format-specific visitor-facing copy; `rationale` stays in the DB purely
  as an internal audit trail and is no longer shown to visitors at all.
  Caught two more issues while shipping this fix: sentences that echoed
  the keyword back when the keyword *was* the format word itself ("A
  clear, repeatable checklist for Checklist") and acronym mangling
  ("Xlsx" instead of "XLSX") - both fixed in the same function
  (`GENERIC_SUBJECT_BY_FORMAT`, `ACRONYM_OVERRIDES`).
