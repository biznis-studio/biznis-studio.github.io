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

## Operating mode (owner, 2026-08-16)

**Run continuously. Do not wait for the owner on anything reversible.**

- **Architecture and marketing advance together.** They are independent branches
  with no edge between them — running one while the other waits is a fake edge.
  Every architecture change should have a marketing consequence in the same
  stretch of work, and vice versa.
- **When stuck, consult ChatGPT** (open in the owner's Chrome, tab
  `chatgpt.com`). Paste the design, ask for hard criticism, name your own
  objections and ask it to confirm or refute them. **It is a second opinion, not
  an authority** — record what you accepted, what you rejected, and why.
  It already corrected two real errors this way.
- **Stop and ask the owner only for:** anything outward-facing (publishing,
  sending, posting), anything that costs money, anything that creates an
  obligation, and any decision about what the business should be.
- Everything else — build, verify, measure, record, prepare — proceed.

**Nikdy neukončuj správu vyhlásením zámeru.** Vety typu „ďalej overím…",
„idem na to", „teraz pozriem…" na konci ťahu sú zakázané. Ak je ďalší krok
známy, sprav ho v tom istom ťahu. Ak sa spraviť nedá, napíš **prečo sa nedá**
— nie čo by si spravil. Majiteľ na to upozornil trikrát (2026-08-18) a stop
hook to nevyrieši: vynúti jednu jednotku navyše a potom pustí. Toto je návyk
vo výstupe, nie chýbajúca brána, takže sa opravuje pravidlom, ktoré sa číta
každú reláciu.

**Every asset carries a promise and a review date.** No exceptions: an asset
that cannot state how it will be judged cannot later be killed, and the system
grows forever. `state/promises.json`, checked by `scripts/check_promises.py`.

## What is enforced vs advisory

Everything above is advisory. These are **enforced** and cannot be talked around:

| Mechanism | Blocks |
|---|---|
| Stop hook `.claude/hooks/verify_before_stop.sh` | ending a turn while the site audit fails · **ending a turn while the queue still has `(stroj)` work** · **ending a turn while `test_beh.py` or `test_vyklad.py` fails** — added 2026-08-30 after a column added by hand to the local database (and not to `MIGRACIE`) broke CI for eight consecutive runs; the site audit could not see it, because the site was fine and the schema was not |
| `tests/test_beh.py` (CI, blocking) | a run that crashes mid-node leaving partial writes, or budgets that don't stop a run |
| `scripts/kontrola_repozitara.py` (CI, blocking) | **new customer data reaching the repo** — names and case identifiers. Does *not* check git history: a published record stays published. |
| `scripts/kontrola_jazyka_odkazov.py` (CI, blocking) | **an odkaz in prose that carries the reader into the other language** — the promise is in the reader's language, the page it opens is not. The language switcher is exempt: it lives in `nav`/`header`/`footer` or carries `hreflang`. |
| `scripts/kontrola_dosiahnutelnosti.py` (CI, blocking) | **a built page no internal link points to** — a search engine discovers by following links, so an unlinked page is an island even though it returns 200 and sits in the sitemap. Six were, on 2026-08-30, including `work.html`. |
| `scripts/kontrola_slovenciny.py` (CI, blocking · also in `build_site.py`) | **a Slovak typo reaching `/sk/`** — runs `aspell --lang=sk` over the built pages; ~90 words it does not know (names, anglicisms) are in an approved list. A new word is not an error, it is a word someone must read once. Fails loudly if aspell or the Slovak dictionary is missing. |

If a rule matters and is not in that table, either enforce it or accept it will be
skipped under pressure.

**A row in that table must name the path it actually guards.** Until
2026-08-18 the table named `quality-packs/build/build_pack.py --check` as what
blocked customer data from *the repo*. That script is real and it works — it
lives in the sibling project `~/Desktop/quality-packs/` and its `--check`
verifies catalogue consistency and refuses customer names in the **pack
source**. What it never did is look at *this* repository, and nothing in this
repository's CI ran it. So the row was true about the pack and false about the
repo, which is how 13 lines naming customers reached the public `origin/main`
while the table read as covering them.

*(An earlier version of this paragraph claimed the file had never existed. That
was wrong — I checked only this repository. Corrected 2026-08-19.)*

Before adding a row, run the command **from where CI runs it** and watch it
fail on purpose.

## Start here (any new session)

Read **`STATE.md`** (what is open right now, and what the anchors actually say),
then `memory/06_Index.md`, then `memory/00_Project.md` through `03_Tasks.md`,
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
- `docs/TASKBOARD.md` was split at 145KB on 2026-08-19: iterations 1-49 moved
  to `docs/TASKBOARD_ARCHIVE.md`, nothing deleted. If the live file passes
  ~150KB again, move the next block of iterations the same way and say so.


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
- **Merging the pipeline's `db/biznis.sqlite3` discards hand-written copy.**
  Product descriptions live in `agents/common.py` but are *served* from the
  `pages` table, which the pipeline rewrites. After every merge with origin,
  run `python3 scripts/apply_blurbs.py` **before** the build — it rewrites them
  and exits non-zero if any template sentence survived. This bit twice in one
  hour on 2026-08-17.
- **A rebase silently discards everything written to `db/biznis.sqlite3`.**
  `.gitattributes` resolves that file with `merge=ours`, and during a rebase
  "ours" is upstream — so poznatky and rozhodnutia written this session vanish
  and the next write reuses their IDs. This is why `state/evolucia.jsonl`
  exists (`merge=union`, so it survives). **After every rebase or merge with
  origin, run `python3 scripts/obnov_z_dennika.py`** — it replays the journal
  idempotently. It recovered three poznatky on 2026-08-19; without it they
  would have been lost with no trace that anything was missing.
- **During a `git rebase`, `--ours` is UPSTREAM, not your commit.** Resolving
  `db/biznis.sqlite3` with `--ours` once discarded newly added products while
  leaving their HTML behind as orphans. Use `--theirs` when replaying your own
  work, then verify: `sqlite3 db/biznis.sqlite3 "SELECT COUNT(*) FROM products
  WHERE format='service';"`
- **Deploy failing does not look like failure.** A push landing while the
  pipeline runs used to fail the run and skip `deploy-pages`, leaving the live
  site behind while local builds looked perfect. Never report a change as done
  from a local build — verify against the live URL (`scripts/deploy.py` does).
  **And `deploy.py` builds what is on `origin`, not what is in your working
  tree.** An unpushed commit gives a run with status *success* and a live site
  that never changed (2026-08-19). Push first; then `--expect` a string from
  the page you actually changed, with `--url` pointing at that page — a default
  `--expect` against the homepage proves nothing about a `/sk/` page.
- **The calculator page bypasses `page_shell()`.** `site/products/free-online-calculator.html`
  is generated from its own file, so anything added site-wide must also be added
  in `inject_intro_into_calculator()`. It has silently missed the RSS tag and a
  whole design revision this way.

## Design rules — design carries the same weight as content

**Owner, 2026-08-16: the design of the site matters as much as what it says.**
We sell websites; ours is the reference. A page whose text is right and whose
layout is wrong loses the reader before the argument lands — and it argues
against us in the one place a prospect can check our work.

- **Both language versions get the same treatment.** Same container width, same
  type scale, same components. `/sk/` ran at 720px while `/` ran at 1080px for
  weeks and nobody noticed until the owner looked. If a fix lands on one, check
  the other in the same turn.
- **Judge design by measuring, not by reading CSS.** Container width, characters
  per line (aim 45-75), heading line-height, tap-target height at 375px,
  horizontal overflow. Every design defect found so far was invisible in the
  source and obvious in a measurement.
- **Beware the browser cache when verifying.** A measurement once said a fix had
  not applied when the deployed CSS was already correct.
- Headings are not paragraphs: give every heading level an explicit
  `line-height` (~1.15-1.25). Missing ones inherit body 1.65 and sprawl.
- A grid needs `grid-template-columns`. `display: grid` alone is one column,
  which only looks acceptable until the container gets wider.

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
