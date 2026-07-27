# Decision Journal

Every *strategic* decision (not routine bug fixes - those live in
TASKBOARD.md) gets recorded here: what was decided, why, what it assumes,
what was rejected instead, how we'll know it worked, and when to revisit
it. When new evidence shows up (a Strategic Review, a Constraint Log
update, real traffic/revenue data), come back to the relevant entry
explicitly instead of quietly re-deciding or drifting - the company should
learn from its own recorded reasoning, not rely on someone re-reading the
whole conversation history. Populated retroactively 2026-07-27 with the
real decisions made so far, then kept current going forward.

---

### D1 — Gumroad as the monetization platform (2026-07-26)
- **Decision**: Sell digital products through Gumroad rather than a direct
  Stripe integration, an affiliate-link model, or a newsletter/subscription
  platform.
- **Reasoning**: Gumroad acts as merchant of record and handles EU VAT
  automatically - removes a real compliance burden from a solo,
  non-company seller. Needs only a free account, no payment infrastructure
  to build.
- **Assumptions**: The user can pass Stripe's underlying KYC (Gumroad's
  payout processor) as an individual seller; Gumroad's cut is acceptable
  at expected volume.
- **Alternatives rejected**: Direct Stripe integration (more compliance
  work, no VAT handling); affiliate links (no product ownership, lower
  margin, still needs an account/network); newsletter/subscription
  platform (deferred - needs an audience that doesn't exist yet).
- **Expected outcome**: At least one product generating real payments
  within weeks of listing.
- **Metrics to validate**: Gumroad account active, ≥1 completed sale
  (currently: account + 1 listing done, 0 confirmed sales).
- **Correction (2026-07-27, via an Opportunity Scan)**: this entry
  previously assumed Stripe KYC blocks *sales*, not just *payouts* - that
  assumption was never verified and turned out to be wrong. Real research
  (see D12) confirms Gumroad lets an account make sales before Stripe
  verification completes; only receiving the payout is delayed. This
  means listing/pricing the remaining `core`-tier products was never
  actually blocked on KYC - it was just mis-filed as blocked. The Ko-fi
  fallback idea is correspondingly deprioritized (see D12) - it would
  have solved a problem (blocked sales) that doesn't exist.
- **Review date**: Revisit payout-specific status once Stripe
  verification completes; sales-enablement is no longer waiting on it.

### D2 — GitHub Pages over Cloudflare Pages for publishing (2026-07-26)
- **Decision**: Deploy the generated site to GitHub Pages.
- **Reasoning**: Zero new accounts needed (repo already lives on GitHub);
  Cloudflare Pages would have required the user to sign up there first,
  which the Human Cost Analysis principle now explicitly weighs against.
- **Assumptions**: GitHub Pages' free tier and `*.github.io` subdomain are
  sufficient for now; a custom domain isn't required for the current stage.
- **Alternatives rejected**: Cloudflare Pages (extra account cost, no
  clear benefit at this stage); Netlify/Vercel (same account-cost issue,
  not evaluated in depth since GitHub Pages already satisfied the need).
- **Expected outcome**: A working, automatically-deployed live site with
  no manual publishing step.
- **Metrics to validate**: Site live and auto-updating on every pipeline
  run (confirmed working since iteration 7).
- **Review date**: Revisit only if the `*.github.io` subdomain itself
  turns out to hurt trust/credibility enough to matter (flagged as a
  possibility, not yet evidenced, in the first Strategic Review) - a
  custom domain has a real $ cost so needs its own EBV case first.

### D3 — IndexNow for free instant indexing (2026-07-26)
- **Decision**: Implement the IndexNow protocol to ping Bing/Yandex/
  Seznam/Naver/Yep whenever new pages publish.
- **Reasoning**: Free, no-account, and (in theory) faster than waiting for
  organic crawling - a genuine no-cost distribution lever if it works.
- **Assumptions**: A subdirectory `keyLocation` proof of ownership would
  be trusted the same as a domain-root one on a shared `*.github.io` host.
- **Alternatives rejected**: None directly - this was additive, not a
  replacement for Google discovery, which IndexNow never covers anyway.
- **Expected outcome**: Faster (re)crawling by the covered search engines.
- **Metrics to validate**: Submission returns `ok=True`. Result: worked
  once, then started returning 403 `UserForbiddedToAccessSite`
  consistently from 2026-07-27 with no public fix found - logged as a
  known limitation rather than kept silently "working" in the docs.
- **Review date**: Low priority to revisit - it fails gracefully and costs
  nothing while broken; check again only if Bing's own systems change or a
  public fix surfaces.

### D4 — Diversify beyond single-keyword ebooks (2026-07-26/27)
- **Decision**: Stop treating "ebook from a scraped keyword" as the
  default product shape; do real (web) research on what digital products
  actually have paid demand, and build originals from that research
  instead (swipe files, checklists, templates, tracker CSVs).
- **Reasoning**: User pushback plus direct research showed narrow,
  validated audience+problem intersections outsell generic broad guides -
  the opposite of what the keyword-frequency pipeline was producing by
  default.
- **Assumptions**: Manually-researched product ideas (tagged
  `manual_research` in `keywords.sources_json`) are worth the extra human/
  Claude time versus letting the automated scorer pick ideas alone.
- **Alternatives rejected**: Keep scaling the same keyword-driven ebook
  pattern (rejected outright - this is precisely what D5 later formalized
  as the `retire_candidate` tier).
- **Expected outcome**: A small number of higher-conviction products
  (freelancer swipe-file "systems") replacing a larger number of
  low-conviction generic ebooks.
- **Metrics to validate**: Real competitor pricing evidence found for the
  new products ($19-79 category, iteration 18) - validated. Actual sales
  - not yet measurable (see D1/Constraint Log).
- **Review date**: Reassess once the `core`-tier products are actually
  priced and selling - see D1.

### D5 — Product tiering + retire the generic-ebook fallback (2026-07-27)
- **Decision**: Classify all products into `core`/`lead_magnet`/
  `retire_candidate`, reject the 14 `retire_candidate` ideas, and remove
  `product_agent.py`'s fallback that turned any unmatched keyword into a
  generic "Practical Guide to X" ebook idea.
- **Reasoning**: The fallback was the direct, provable source of all 14
  low-value products (confirmed via `pages` table: 0 of them ever got a
  live page) - continuing to run it would keep manufacturing the same
  clutter on every future scheduled run.
- **Assumptions**: Removing the fallback (skip unmatched keywords
  entirely) doesn't meaningfully reduce the pipeline's useful output,
  since matched-pattern ideas (calculator/checklist/template/prompt_pack/
  sop) plus manual research (D4) are enough to keep the product pipeline
  fed.
- **Alternatives rejected**: Keep the fallback but deprioritize its ideas
  in scoring (rejected - doesn't stop the clutter from accumulating in the
  DB, just hides it); keep it and manually reject each new one as it
  appears (rejected - pure ongoing toil for a pattern already proven weak).
- **Expected outcome**: No new generic single-keyword ebook ideas appear
  in future scheduled runs.
- **Metrics to validate**: Checked runs 18-19 (already executed with the
  old code before this fix landed) - produced 0 new fallback ebooks
  regardless, and no new ones appeared after the fix in run history
  reviewed so far. Recheck after the next scheduled run actually exercises
  the new code path.
- **Review date**: Confirm after the next 1-2 scheduled runs that no
  `format='ebook'` idea appears without a `manual_research` source tag.

### D6 — Add website design/development and chatbot development as service offerings (2026-07-27)
- **Decision**: Add two custom, quote-based services alongside the
  productized digital downloads.
- **Reasoning**: User request, framed as "if you can pull it off" -
  services can generate revenue without waiting on a product to find an
  audience, using the skills already demonstrated by this very project as
  informal proof of capability.
- **Assumptions**: A visitor will trust a services page with no case
  studies or track record enough to reach out.
- **Alternatives rejected**: None seriously considered - added directly on
  request, but flagged honestly in the first Strategic Review
  (2026-07-27) that this assumption is weak and worth revisiting.
- **Expected outcome**: At least one inbound inquiry once the contact form
  is live (see D7).
- **Metrics to validate**: 0 leads so far - contact form isn't live yet
  (Formspree endpoint pending, see Constraint Log/Human Action Batch).
- **Review date**: Revisit in the next Strategic Review once the contact
  form is live for at least 1-2 weeks - if there are still 0 leads,
  consider the "separate trust-building track / case study" alternative
  raised in the first Strategic Review instead of just waiting longer.

### D7 — Formspree contact form instead of a visible mailto (2026-07-27)
- **Decision**: Replace mailto links (which expose the owner's real email
  in page source) with a real `<form>` posting to Formspree.
- **Reasoning**: Direct, explicit user requirement - the email must never
  appear in page source.
- **Assumptions**: Formspree's free tier (~50 submissions/month) is
  sufficient at current traffic levels.
- **Alternatives rejected**: Keep mailto (violates the explicit
  requirement - not seriously considered); self-hosted form backend
  (unnecessary infrastructure for the current scale).
- **Expected outcome**: Zero occurrences of the email address in generated
  HTML once the endpoint is set; working lead capture for the services.
- **Metrics to validate**: Verified zero-occurrence with the endpoint set,
  exactly one (fallback mailto) without it - confirmed both directions
  work. Real endpoint still pending from the user (Human Action Batch).
- **Review date**: Close out once the real endpoint is wired in - no
  further review needed unless volume approaches the free-tier cap.

### D8 — Resume Google Search Console verification (2026-07-27)
- **Decision**: Resume the Search Console setup that had been explicitly
  paused mid-way at the user's earlier request.
- **Reasoning**: The Constraint Log and first Strategic Review both
  independently identified discovery as the current primary constraint -
  the EBV of resolving it now outweighs the earlier reason for pausing.
- **Assumptions**: The user is willing to spend the ~3 minutes this needs;
  verification will actually lead to indexing within a reasonable time
  once submitted.
- **Alternatives rejected**: Continue waiting/deferring (rejected - no
  new information favors staying paused, and every week of delay has a
  real opportunity cost across all 14 live pages).
- **Expected outcome**: Verified property, submitted sitemap, pages
  beginning to appear in Google's index.
- **Metrics to validate**: Verification status, then impressions/clicks in
  Search Console once available.
- **Review date**: Re-check in the Constraint Log as soon as verification
  completes and again once ~1 week of impression data exists.

### D9 — Adopt EBV / Strategic Review / Human Cost Analysis / Constraint-Driven Management as standing operating principles (2026-07-27)
- **Decision**: Reframe the whole project's operating model around
  maximizing enterprise value (not product/content output), with four
  concrete mechanisms: EBV-ranking the backlog, a recurring Strategic
  Review that can challenge the business model itself, a Human Cost
  Analysis gate before requesting manual action from the user, and a
  Constraint Log that names one current bottleneck per iteration.
- **Reasoning**: Direct user feedback across several turns, converging on
  a single failure mode to avoid: an autonomous agent that keeps
  optimizing whatever it's already building, never questioning the
  business model, and treating the human's time as free.
- **Assumptions**: These mechanisms are worth the ongoing overhead of
  maintaining 4 living documents (ROADMAP, STRATEGIC_REVIEWS,
  CONSTRAINT_LOG, this journal) - if they start feeling like ceremony
  rather than changing real decisions, that's itself a signal to simplify.
- **Alternatives rejected**: A single combined doc (rejected for now -
  the four serve genuinely different cadences: constraint log per
  iteration, strategic review weekly, decision journal on strategic
  decisions only, roadmap as the living backlog); doing this only
  informally in conversation (rejected - the whole point was that
  conversation history doesn't survive context resets, these docs do).
- **Expected outcome**: Future iterations default to this framing without
  the user having to re-explain it; visibly fewer "why did it build that"
  or "why did it interrupt me for that" moments.
- **Metrics to validate**: Qualitative for now - judged by whether future
  sessions actually reference these docs unprompted (they should, since
  it's also saved to persistent memory outside this repo).
- **Review date**: Revisit in the next Strategic Review (~1 week) - check
  whether the four documents are actually being kept current or have
  started to rot, which would itself be a constraint worth logging.

### D11 — Stop adding principle docs, build a real measured scoreboard instead (2026-07-27)
- **Decision**: Per direct user feedback, stopped adding new
  principle/manifesto documents (this project now has ROADMAP,
  STRATEGIC_REVIEWS, CONSTRAINT_LOG, OPPORTUNITY_QUEUE, and this journal -
  enough). Built `company_metrics` + `experiments` DB tables and
  `agents/scoreboard_agent.py`, which computes real numbers from the DB
  every run and writes docs/COMPANY_SCOREBOARD.md - a generated data
  artifact, not hand-written prose.
- **Reasoning**: The user correctly identified that more documentation
  has diminishing returns and risks becoming the exact over-engineering
  this whole operating-principle layer was meant to prevent. The real gap
  wasn't another policy - it was the absence of any queryable, trending,
  quantified record of what the business actually has and produces.
- **Assumptions**: Real, computed counts (products/tiers/pages/keywords/
  confirmed revenue) are more useful right now than an economic model
  with invented dollar figures for a solo project with no metered agent-
  time cost - so the scoreboard deliberately omits Development Cost/
  Maintenance Cost/Estimated Future Value rather than fabricating them.
- **Alternatives rejected**: Assigning made-up dollar costs/values per
  asset just to satisfy the "quantify everything" request literally -
  rejected as fabricated data, which this project's rules explicitly
  forbid (no fake traffic/reviews/data, extended here to no fake
  financials). Building a full experiment-portfolio scheduler (parallel
  hypotheses, auto-kill, auto-scale) right now - rejected as premature:
  there is currently no real traffic to run any experiment against, so a
  scheduler would have nothing real to manage yet. The `experiments`
  table exists so this is a one-line addition once it's actually needed,
  not a rebuild.
- **Expected outcome**: Every future session opens on real trend data
  instead of re-deriving business state from conversation history or
  prose docs; the scoreboard's "Not tracked" section makes the honesty
  boundary explicit instead of silently pretending precision that
  doesn't exist.
- **Metrics to validate**: The `company_metrics` trend actually
  accumulates real, distinct snapshots run over run (not fabricated), and
  future sessions consult docs/COMPANY_SCOREBOARD.md before restating
  numbers from memory.
- **Review date**: Check in the next Strategic Review whether the
  scoreboard is actually being consulted, and whether the deliberately
  excluded fields (cost/future-value estimates) are still the right call
  once real revenue or traffic data exists.

### D12 — First real Opportunity Scan: caught myself assuming instead of scanning (2026-07-27)
- **Decision**: Before acting on a previous turn's assumption ("next step
  is researching Ko-fi"), ran an actual Opportunity Scan per the user's
  new rule instead - re-ranked live candidates for "fastest path to a
  first paying customer" rather than proceeding on the un-scanned plan.
- **Reasoning**: The user caught a real violation of this project's own
  Strategic Review principle: I'd picked Ko-fi as the next action without
  verifying the premise (that Gumroad KYC blocks *sales*, not just
  *payouts*). That premise was never actually checked.
- **What the scan found**: A real web search confirmed Gumroad allows an
  account to make sales before Stripe verification finishes - only the
  payout is delayed, not the sale itself. This changes the ranking
  materially: the 4 core-tier freelancer-system files
  (Scope Creep Kit + Change Request Log; Retainer Renewal Kit + Tracker)
  were sitting un-listed on Gumroad, incorrectly filed as "blocked on
  KYC" when they were never actually blocked from being listed and sold.
- **Alternatives considered and re-ranked**:
  1. **List the 2 already-validated product bundles on Gumroad now**
     (highest EBV - directly enables a first sale; low human cost since
     the account/workflow already exists from D1; PDFs for the two
     swipe_file components generated immediately as prep so the human
     only has to upload + set a price, not also convert files).
  2. Resume Search Console (already in progress) - a multiplier on #1,
     not a substitute for it.
  3. Ko-fi research - **deprioritized**, not abandoned: it would solve a
     problem (blocked sales) that this scan showed doesn't exist. Revisit
     only if real Gumroad sales attempts hit an actual blocker the search
     didn't surface.
  4. B2B service outreach - kept in the queue behind #1, since it still
     needs Formspree live first and more direct human effort per lead.
- **Expected outcome**: A real Gumroad listing attempt for both bundles
  this week, independent of whether Stripe KYC has resolved yet.
- **Metrics to validate**: Whether Gumroad in fact accepts new listings
  and processes a test/real sale pre-KYC as the research suggested - this
  is itself still an assumption from secondary sources, not first-hand
  confirmed, so treat it as a hypothesis to verify by trying, not a
  guarantee.
- **Review date**: As soon as the user attempts the listing - if Gumroad
  actually does block something unexpected, log it here and re-open the
  Ko-fi option immediately rather than assuming this scan's finding was
  complete.

### D10 — Consulted an independent AI (ChatGPT) for a second opinion, adopted some findings and explicitly rejected others (2026-07-27)
- **Decision**: At the user's request, explained the full system to ChatGPT
  (via the user's own logged-in browser session) and asked for
  optimization suggestions, specifically asking for an independent view
  rather than confirmation of what's already being done.
- **Reasoning**: An external model with no stake in this system's prior
  decisions is a cheap way to surface real blind spots that accumulated
  context can hide - the same reason docs/STRATEGIC_REVIEWS.md exists,
  applied via a genuinely different reasoning process instead of just
  another pass of my own.
- **What was adopted as genuinely new and real** (not already covered by
  the existing EBV/Constraint/Decision-Journal layer):
  - **Customer Discovery Layer**: the pipeline currently only reads
    keyword *frequency*, never actual customer language ("I wish...",
    "I'm tired of...", "does anyone know..."). Added to
    docs/OPPORTUNITY_QUEUE.md, scoped honestly: Reddit (public JSON,
    no-account), GitHub Issues (already-used API), HN *comments* (not
    just titles - same Algolia API), and Stack Exchange *comments* (same
    API already in use) are genuinely free/no-auth extensions of the
    current stack. Product Hunt, IndieHackers, and Discord were also
    suggested but need a new account/API token each - correctly gated
    behind the Human Action Batch/Human Cost Analysis, not treated as
    equally "free" just because ChatGPT listed them together.
  - **Expected Learning Value** as a companion to EBV: some low-EBV tasks
    are worth doing anyway because they resolve real uncertainty cheaply
    (e.g. a tiny paid distribution test that answers "do people even
    click" regardless of whether it sells anything). Added to ROADMAP.md
    as an explicit second axis alongside EBV, not a replacement for it.
  - **Kill Switch**: no rule currently exists for retiring a *published*
    product that isn't performing, only for rejecting ideas before
    they're built (the `retire_candidate` tier). Logged as a real gap;
    can't fully implement the trigger conditions (impressions/clicks/
    conversions) until Analytics exists, but the rule itself is recorded
    now so it's not forgotten once that data exists.
  - **An 11th Strategic Review question** ("if Google stopped sending
    traffic tomorrow, would this survive?") - a sharper, more falsifiable
    version of a concern the first Strategic Review already raised in
    softer form; added directly to docs/STRATEGIC_REVIEWS.md.
  - **GitHub repo discoverability** was genuinely just missing and free to
    fix: `homepageUrl` was empty and there were zero topics on the public
    repo. Set both immediately (`gh repo edit`) - a real, unblocked,
    zero-cost distribution surface that had simply been overlooked.
- **What was explicitly NOT adopted, and why**:
  - The claim that most of the pipeline (Competition Analysis, Demand
    Scoring, Niche Clustering) is "engineering comfort" that doesn't
    move revenue. Rejected: the competition/demand scoring work directly
    produced this session's product tiering decision (D5) - it's not
    decorative, it materially changed what got built and what got
    retired. Logged the pushback rather than silently ignoring or
    silently complying with an external opinion that didn't match the
    evidence in hand.
  - Migrating off SQLite-in-git or off GitHub Pages right now - both are
    reasonable *future* considerations (already independently flagged in
    D2 and ARCHITECTURE.md's design decisions) but premature at 28
    products and 0 measured traffic; re-platforming now would cost real
    engineering time against a constraint (distribution) that doesn't
    require it.
  - A full "Problem Statement" pipeline stage (keyword -> problem ->
    solution -> product) as new infrastructure: the `core`-tier products
    already implicitly went through exactly this reasoning via
    `manual_research`-sourced ideas (D4) - the gap is only in the
    *rule-based* `FORMAT_RULES` path used for lower-conviction ideas, so
    this is a refinement to note, not a new system to build.
- **Expected outcome**: A slightly larger, better-scoped Opportunity
  Queue and two new standing principles (Expected Learning Value, Kill
  Switch), without importing untested claims wholesale just because they
  came from a second AI.
- **Metrics to validate**: Whether the Customer Discovery Layer additions
  (once built) surface product ideas with a qualitatively different,
  more specific rationale than the current keyword-frequency approach.
- **Review date**: Revisit in the next Strategic Review - check whether
  Customer Discovery signals actually produced a better idea than the
  keyword pipeline would have, or whether it was a detour.
