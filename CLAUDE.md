# Biznis — working notes

## What this business is (read before proposing anything)

**LLMs automate what you can verify, not what you can specify.** Companies use AI
at ~5% not because it is weak but because **their work is not in verifiable form**.
We sell that conversion. The pack is a delivery format, not the product.
Full reasoning: `docs/KONCEPT.md`, `docs/RESEARCH_12_UCTOV.md`.

**Qualification filter — apply before building anything for anyone:**
*can we say in advance what would prove the answer wrong?* If not, don't build it.

**Four rules that override enthusiasm:**

1. **A verifier may say something is broken. It must never decide what gets built.**
   Five pack versions once shipped while the knowledge never changed, because the
   gate and the test set were allowed to generate the work.
2. **Never author domain content.** Derive it from the expert's own file. Every
   time Claude invented decision content it had to be rewritten from scratch.
3. **Whoever produced the work does not grade it.** Grading runs in a clean
   context given only the output and the criteria.
4. **Most of our test set proves stability, not correctness.** Only *anchors*
   prove correctness — closed cases with an independently known outcome, an
   intervention that actually stopped, an expert objection from the shop floor.

**Deleting is allowed and required — ablation:** turn a rule off, re-run the set;
if nothing degrades, delete the rule. Without this the pack can only grow.

## What is enforced vs advisory

Everything above is advisory. These are **enforced** and cannot be talked around:

| Mechanism | Blocks |
|---|---|
| Stop hook `.claude/hooks/verify_before_stop.sh` | ending a turn while the site audit fails |
| `quality-packs/build/build_pack.py --check` (local + CI) | catalogue inconsistency · **a frozen rule missing from the pack** · **customer data in the repo** · **a VERSION with no eval record naming it and stating `DÔVOD ZMENY:`** |

If a rule matters and is not in that table, either enforce it or accept it will be
skipped under pressure.

## Start here (any new session)

Read `memory/06_Index.md`, then `memory/00_Project.md` through `03_Tasks.md`,
then **`memory/07_Constraints.md`** — the short imperative list of what has
already gone wrong. `04_Lessons.md` is the archive behind it and is read only
when a specific incident matters. That is the whole current state —
do not read `docs/*.md` unless the task needs the specific detail those
files hold (full history, full decision reasoning).

**Update `memory/` after any substantive change**, same turn, not later:
- New/changed strategic decision → append ≤5 lines to `01_Decisions.md`
- New reusable gotcha → append ≤10 lines to `04_Lessons.md`
- Task state changed → edit `03_Tasks.md` in place (done items become one line)
- Never duplicate into a new file. Update an existing section instead.
- If `docs/TASKBOARD.md` exceeds ~150KB, propose archiving older iterations
  to `docs/TASKBOARD_ARCHIVE.md` and say so — don't do it silently.


A digital studio site (services + a product catalogue) published to GitHub
Pages by a scheduled pipeline. Live at https://biznis-studio.github.io

## Commands

```bash
python3 scripts/build_site.py            # rebuild everything (use this, not ad-hoc python)
python3 scripts/build_site.py --fast     # skip network work (images, news fetch)
python3 scripts/audit_site.py            # crawl-readiness check; non-zero = do not ship
python3 scripts/deploy.py --expect "text that must appear live"
```

Required env vars for any build (CI sets them in `.github/workflows/pipeline.yml`):
`SITE_BASE_URL`, `FORMSPREE_ENDPOINT`, `GOOGLE_SITE_VERIFICATION`, `PEXELS_API_KEY`.
Without `SITE_BASE_URL` the build silently skips canonicals, sitemap and RSS.

## Mechanism

- `scripts/build_site.py` is the only correct way to rebuild. It ends with
  the crawl audit and exits non-zero on failure.
- `scripts/deploy.py --expect "<text>"` is the only way to call something
  shipped: it waits for the run and then checks the live URL.
- A **Stop hook** (`.claude/hooks/verify_before_stop.sh`) runs the audit
  before any turn can end and blocks with the failure if the site is
  broken. CLAUDE.md rules are advisory; this one is enforced.
- `/ship` and `/find-opportunities` skills encode the two repeated
  procedures. Use them instead of retyping the steps.

## Gotchas that have actually bitten

- **Rebuilding a page wipes its SEO markup.** `build_page()` resets a published
  page to its pre-`seo_agent` state. Any rebuild must set
  `pages.seo_enhanced = 0` and re-run `seo_agent`. `build_site.py` does this;
  hand-rolled rebuilds forget it and strip canonicals from every page.
- **During a `git rebase`, `--ours` is UPSTREAM, not your commit.** Resolving
  `db/biznis.sqlite3` with `--ours` once discarded newly added products while
  leaving their HTML behind as orphans. Use `--theirs` when replaying your own
  work, then verify: `sqlite3 db/biznis.sqlite3 "SELECT COUNT(*) FROM products
  WHERE format='service';"`
- **Deploy failing does not look like failure.** A push landing while the
  pipeline runs used to fail the run and skip `deploy-pages`, leaving the live
  site behind while local builds looked perfect. Never report a change as done
  from a local build — verify against the live URL (`scripts/deploy.py` does).
- **The calculator page bypasses `page_shell()`.** `site/products/free-online-calculator.html`
  is generated from its own file, so anything added site-wide must also be added
  in `inject_intro_into_calculator()`. It has silently missed the RSS tag and a
  whole design revision this way.

## Content rules — these are not style preferences

- **Never invent evidence.** No testimonials, client logos, review counts or
  ratings we do not have. This has been enforced since day one; breaking it
  would invalidate the site's whole positioning.
- **Never publish an unverified number.** A hardcoded "85% of runs succeeded"
  was guessed once (real figure: 92%). Either compute it from a real source or
  link to where the reader can see it themselves.
- **Do not advertise weakness either.** "We are new, we have no clients" is not
  honesty, it is bad marketing. State what is true and demonstrable; frame risk
  handling (fixed price, written scope) as the guarantee it is.
- **State the boundaries — but never as a list of what the customer will not get**
  (owner, 2026-08-16: nobody is won over by being told what they are missing).
  Same substance, positive form: *"we work with the licences you already have"*,
  not *"we don't sell licences"*. The section is called
  **"Rozsah máte napísaný ešte pred podpisom"**.
- **Do not mention that any of this is AI-generated or automated.** Not a
  selling point; the owner has asked for it to stay out of visitor-facing copy.
- **Proofread Slovak before publishing.** `/sk/` and `content/sk/`. Bad Slovak
  destroys credibility faster than having no Slovak page at all.

## Strategy context

- The binding constraint is **traffic**, not conversion — Gumroad shows 0 views,
  not merely 0 sales. Design and copy polish sit downstream of a gate that has
  not opened.
- English tool/calculator queries are owned by incumbents (Harvest et al).
  **Conversational** queries ("what do I say when…") are not, and are what the
  script catalogue answers. See `docs/CONSTRAINT_LOG.md`.
- The strongest opportunity found: **Slovak SERPs for our services are held only
  by small local agencies**, with paid ads running — proven demand, servable
  market, deals worth 100x a $29 product.
- Decisions with reasoning and review dates: `docs/DECISION_JOURNAL.md`.
  Iteration history: `docs/TASKBOARD.md`. Do not add new governance docs.
