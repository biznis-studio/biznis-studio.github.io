# Constraints — read at the start of every session

Imperatives only. Each one exists because it already went wrong once.
The reasoning and the incident are in `04_Lessons.md`; this file is the short
form that actually gets loaded. **If a rule here can be mechanised, move it to
the gate and delete it from here** (`CLAUDE.md` lists what is enforced).

## Evidence

- **Re-verify subagent and web research against the primary source before
  acting.** A fan-out once reported a live page that did not exist.
- **Quoting a source correctly is not implementing it correctly.** Execute the
  thing and check the number, don't re-read the spec.
- **"Sounds interesting, send me info" is zero.** Only a paid commitment or a
  scheduled next step counts as interest.
- **No published number without a pre-registered threshold and an UNKNOWN
  category.** A guessed 85% once shipped where the real figure was 92%.
- **Say what a result does *not* prove**, every time you report one.
- **A URL from a search result is not a verified source — open it.** On
  2026-08-17 a cited source went live returning 404 because the link came
  from search output and nobody fetched it. Citing a dead source is worse
  than citing none. `scripts/check_external_links.py` now checks them all.

## Verification

- **A check you have not seen fail is not a check.** Break it deliberately,
  watch it go red, then restore.
- **Parsing is not correctness.** `node --check` once passed a calculator that
  computed the wrong answer.
- **A green gate covers only what we control.** External links, live URLs and
  third-party behaviour are outside it.
- **Whoever produced the work does not grade it.** Fresh context, given only the
  output and the criteria.
- **A guard must inspect the published artifact, not the source it came from.**
  The image check scanned `content/*.md` and never saw a page built another way;
  the Slovak source read correctly while the page carried the typo.
- **A visual question is settled by a screenshot, not by a derived number.**
  `img.complete`, `Range` rects, table-cell heights and screenshot pixels each
  produced a defect that did not exist (four in one session, 2026-08-19).

## Tooling

- **Never install third-party agent tooling (skills, MCP servers, plugins) on
  the owner's say-so alone.** This machine's Chrome holds a live corporate
  Microsoft 365 session and credentials for our GitHub. A skill list on X is a
  claim, not a verification — "live-verified" is the author's word, and our own
  rule is to re-check against the primary source before acting.
- **Validate a new gate on data it was not built from.** Seeding a gate's
  allow-list from the same pages it guards proves nothing — the improvement can
  be fitted to those pages. Keep three sets apart: what you diagnosed on, a
  held-out set for validation, and a regression set. The Slovak gate passed this
  on 2026-08-20 (6 326 held-out words, 2 non-words flagged), but only because
  someone checked.
- **Before building a substitute, check whether the real tool is already here.**
  A hand-rolled Slovak check reported "all approved" while six typos sat on the
  live site; `aspell --lang=sk` was installed the whole time and found them all.
  A substitute that looks like a check is worse than no check.
- **Fix a capability gap by hand before shopping for it.** Most of what these
  tools sell — context discipline, session memory, verification — we have
  either already built or can build in an afternoon, and then we understand it.

## Context discipline

- **Never dump a whole page or file into context to read one part of it.**
  Extract the slice (JS on the DOM, `grep`, a range read). Whole-page reads have
  repeatedly cost tens of thousands of tokens for a paragraph of signal.
- **Re-read only the delta.** After sending a message, read what changed, not
  the whole transcript.

## Autonomy needs a leash made of measurement

- **A measurable success condition is what licenses a long unattended run.**
  *"Improve it"* drifts by step forty; *"cut p95 by 30% without changing the
  outputs"* can run for hours because the agent can check itself at every step.
  If the condition cannot be stated, work in short supervised steps instead.
- **Set a budget before starting: steps, wall-clock, cost.** Running out of
  budget is information, not failure — report the partial result and what it
  would take to finish.
- **Produce auditable artifacts, not assurances:** what was run, the diff, the
  test output, the cost. "It's done" is not a result.

## Can it take done back?

- **A system that can only promote is a burndown chart with extra steps.**
  For every gate we build, ask what un-does a pass — not only what blocks one.
- **A pass belongs to the version it ran on and does not carry forward.**
  The artifact states its own release status; a failing blocking scenario marks
  the built pack `vydane: false` with the reason.
- **For every tool or approach adopted, name its trap** in the same breath as
  its benefit. If we cannot name the trap, we have not understood it yet.

## Building

- **Derive domain content from the expert's file. Never author it.** Every
  invented decision rule had to be rewritten from scratch.
- **Add a stop rule before adding a retry.**
- **Prefer deleting.** Turn a rule off, re-run the set; if nothing degrades, it
  goes. Without this the pack only ever grows.
- **Don't use a model for what ordinary code already knows.**

## Contact must be reachable

- **Every page a visitor can be convinced on carries the form itself** — not a
  link to it. Homepage, work page, and every article. Until 2026-08-16 the
  English homepage and the "Hire us" destination had **no form at all**.
- **"Hire us" points at the form**, never at a list of services.
- **A CTA that does not render is worse than none** — it reads as the author's
  mistake. The link syntax supports `http(s)`, `*.html`, directory paths
  (`/sk/#kontakt`) and bare anchors; anything else silently stays plain text.

## Design

- **Design carries the same weight as content** (owner, 2026-08-16). We sell
  websites; ours is the reference a prospect checks.
- **Measure, don't read CSS:** container width, characters per line (45-75),
  heading line-height, tap targets at 375px, horizontal overflow.
- **Fix both language versions in the same turn**, then verify both.

## Merateľné dizajnové minimum (namerané 2026-08-17, drž to)

- kontrast textu voči pozadiu **≥ 4,5** v tmavom aj svetlom režime
  (namerané: telo 7,48 tmavý / 6,25 svetlý — rezerva je, nezhoršovať)
- **jeden `h1`** na stránku, každý obrázok má `alt`
- dotykový terč na 375 px **≥ 40 px**
- žiadne vodorovné pretečenie: `scrollWidth == clientWidth`
- riadkovanie nadpisov 1,12-1,25, nikdy zdedené 1,65
- každý vnútorný odkaz vedie na existujúci súbor (690 overených)

## Publishing

- **A published article without a hero image is an unfinished article.**
  The image is not fetched automatically — the slug must be added to
  `agents/image_agent.QUERIES` first, and the full (non-`--fast`) build with
  `PEXELS_API_KEY` has to run. One article shipped without one for two weeks
  before anyone noticed.

- Slovak quotes are `„text“` — never straight ASCII. Five articles shipped wrong.
- Proofread Slovak before it goes out; bad Slovak costs more than no Slovak page.
- Never invent evidence: no testimonials, logos, ratings or review counts.
- Don't advertise weakness either — state what is true and demonstrable.
- **"We cannot verify demand without a customer" is almost always laziness.**
  Money already flowing is public: incumbent products, their prices, tenders,
  job ads. On 2026-08-21 I closed a question as unverifiable, was told I gave up
  too fast, and found decades of proven willingness to pay in one search.
- **A destructive test runs on a copy — always, even when it looks small.**
  On 2026-08-21 a "quick" wipe-and-restore test on the live database destroyed
  35 links from earlier sessions that were never journaled. Git saved them, not
  the journal. The journal only covers what someone wrote into it.

- **Prenos obsahu medzi / a /sk/ prenesie text, nie ciele odkazov.** Po každom takom prenose prejsť odkazy v prenesenej pasáži a overiť, že cieľ existuje v jazyku čitateľa. Audit ani stavová kontrola to nechytia — cieľ vracia 200, chybný je len jazyk. (2026-08-22: EN domovská sľubovala „our free pre-deployment record" a odkazovala na slovenský formulár.)

- **Schéma databázy sa mení v kóde, nikdy príkazom do databázy.** `ALTER TABLE`
  do lokálnej db a nie do `MIGRACIE` zhodil CI na osem behov po sebe
  (22.–30. 8. 2026) a nikto si to nevšimol, lebo lokálne fungovalo všetko.
- **Test na kópii databázy nechráni denník.** Denník je spoločný a obnova
  z neho prehrá testovacie záznamy do živej databázy. Zápis do denníka je
  odteraz viazaný na skutočnú `db/biznis.sqlite3`.
