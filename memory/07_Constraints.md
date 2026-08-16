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

## Verification

- **A check you have not seen fail is not a check.** Break it deliberately,
  watch it go red, then restore.
- **Parsing is not correctness.** `node --check` once passed a calculator that
  computed the wrong answer.
- **A green gate covers only what we control.** External links, live URLs and
  third-party behaviour are outside it.
- **Whoever produced the work does not grade it.** Fresh context, given only the
  output and the criteria.

## Tooling

- **Never install third-party agent tooling (skills, MCP servers, plugins) on
  the owner's say-so alone.** This machine's Chrome holds a live corporate
  Microsoft 365 session and credentials for our GitHub. A skill list on X is a
  claim, not a verification — "live-verified" is the author's word, and our own
  rule is to re-check against the primary source before acting.
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
