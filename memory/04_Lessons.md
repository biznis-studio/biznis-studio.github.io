> **This file is the ARCHIVE, not the loaded memory.** It is read only when a
> specific incident matters. The operative rules live in `07_Constraints.md`
> (loaded every session) or, better, in the gate — see `CLAUDE.md`.
> Discovered 2026-08-16: 47 lessons had been written here while nothing read
> the file at session start. A constraint that is not loaded is not a constraint.

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

**Customer interviews confirm whatever you hope.** "Sounds interesting / send me info" = ZERO
evidence. Only these count: a named recurring task with an estimated time cost given unprompted,
money already spent on it, a named know-how holder, a named budget owner. Ask about the PAST
(last time it happened), never the future ("would you use..."). Never describe the concept before
they describe the work — after the pitch everything is contaminated. Thresholds pre-registered in
`docs/RESEARCH_LOG.md` so warm responses can't be rationalised into validation.

**A/B tests need their confounds fixed BEFORE running** (same discipline as RL-1's pre-registration):
same person doing the task twice is faster regardless of tool (learning effect → between-subjects or
counterbalanced with equivalent cases); whoever scores must not know which condition produced the
output; with n=5–10 there is no significance, so pre-register a DECISION threshold (e.g. "wins on
time in ≥7 of 10 pairs, no worse on the rubric"), not a p-value.

**ARCHITECTURE PRINCIPLE (adopted 2026-08-08):** *Copilot generates and prepares. The human
decides. Microsoft 365 stores.* No customer data owned, no AI infra run, no backend for sensitive
content. Ollama / customer-hosted runtimes are OUT — they solve inference while the blocker is the
write path, and they reintroduce per-customer endpoints and infra, forfeiting the licence,
security approval, marketplace distribution and zero-infra economics that justified the idea.
**The 8k instruction cap means agents must be PER-PROCESS, not per-department** — a Domain Pack is
a set of narrow agents. ROI claims need a baseline measured AT that customer (that's what the paid
assessment is for); never generalise one customer's time saving.

**A15 FAIL — the closed knowledge loop is NOT buildable today.** Every declarative agent capability
is read-only. Writing needs actions; the only in-tenant write path (Power Automate) is documented by
Microsoft as *"might not run reliably and might not return results"* with *"no workaround available"*.
Our backend works but data then leaves the tenant. Custom engine agents (the other marketplace path)
don't run in Outlook/Word/Excel/PowerPoint and don't support sensitivity labels. Government tenants
can't publish via Agents Toolkit at all. **What survives: intelligent work with EXISTING know-how;
capture becomes a human-save step.** Say this plainly to customers — it is less than "AI builds your
knowledge base".

**Copilot: two risks that change the SALES story, not just architecture (verified 2026-08-08).**
(1) Purview-encrypted content may be INVISIBLE to agents — *"encryption can exclude programmatic
access, thus limiting the agent from accessing the content"*. The documents worth reasoning over
(procedures, customer requirements, HR) are exactly what enterprises label. Test on a real labelled
tenant before promising anything. (2) Our agent is a SEPARATE trust boundary — Microsoft tells
customers to check the agent's own privacy terms, and admins see its required permissions before
enabling. An agent that moves nothing out of the tenant clears that review; one with a backend
does not. Full register in `docs/ARCHITECTURE_COPILOT_LAYER.md`.

**Copilot extensibility facts (verified 2026-08-08, docs updated 2026-07-29).** Marketplace
distribution ONLY via Agents Toolkit (declarative or custom engine); Agent Builder and Copilot
Studio declarative are org-catalog only; Copilot Studio multi-tenant is PREVIEW. Omitting
`items_by_url`/`items_by_sharepoint_ids`/`connections` makes the agent search the WHOLE tenant —
so one package installs anywhere, no per-customer build. `instructions` capped at **8,000 chars**
(the whole methodology budget). No manifest parameterisation except localization keys. Details in
`docs/ARCHITECTURE_COPILOT_LAYER.md`; schema read was 1.5, latest is 1.8 — re-verify.

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

**A11 (Copilot licence gate) confirmed in the field, 2026-08-08.** Without an M365 Copilot licence,
Agent Builder offers *only* "Add specific URL" — SharePoint/OneDrive grounding is a paid capability.
So the free Copilot Chat tier cannot carry a knowledge-backed agent at all: the product's addressable
market is licensed tenants only, not "anyone with M365". Two consequences worth remembering:
(a) the 8,000-char `instructions` cap makes an instructions-only fallback structurally limited — the
34 compressed decision trees are 13.5k chars, so ALL of them never fit, regardless of how terse the
procedure gets. A fallback must therefore carry the *universal* procedure and openly disclaim the
per-case catalogue, not silently cover a subset (5 of 34 fit — confident on 5, blind on 29).
(b) the one available option (public URL) is a data-exfiltration path for internal engineering
know-how, never a workaround. Say so explicitly when a customer hits this.


**Pattern transfer is the failure mode the procedure exists to prevent — and Claude did it, 2026-08-10.**
Diagnosed Žilina/2853 as a possible design-stiffness limit and prescribed a two-measurement test, on the
basis of **two lines** in a morning report. The pattern came from AMARI/2650, where 12 of 16 pieces were
borderline. Owner rejected it in one sentence: if the section were at its stiffness limit the profile
could not be produced at all — it would fail constantly, not intermittently, and would have been caught
at first-article. Correct, and the deeper error was carrying a pattern from a case with data to a case
without any. **When a defect description is two lines, the honest output is "not enough to diagnose",
not a hypothesis that happens to fit a neighbouring case.** This is exactly what plain Copilot does and
exactly what the procedure is supposed to block.


**A structural gate cannot catch a missing decision rule — 2026-08-14, quality-packs v0.2.0.**
Adding the category "Nevhodné balenie" next to the existing "Poškodené balenie" passed every gate check
(each cause covered by a tree step, no invented causes, no duplicates) and was still broken: a technician
with a packaging complaint faced two valid trees and nothing said which to enter. **The gate guards
consistency; only the acceptance set guards behaviour.** Fixed with a ROZCESTNÍK first step in both trees
(damaged packaging / damaged profiles / both), scenario S12, and a gate check that cross-category
references point at a category that exists (verified by deliberately breaking one).
Corollary, and it cost a rejected design: a heuristic gate for "confusably named categories" fires 7 times
on this catalogue with 1 true positive. **A gate people learn to ignore is worse than no gate** — do not
ship a check whose false positives outnumber its finds.
Also recorded: `tests/vysledky/` was empty, i.e. the 12-scenario acceptance set has never been run once,
and 0.2.0 shipped without it despite the CI reminder. Claude must not run it — it tests the customer's
Copilot with the pack attached, so a Claude-side "12/12" would be an invented number.


**"Not in the catalogue" is not an answer — owner's rule, 2026-08-15, quality-packs v0.3.0.**
Until 0.2.1 the pack said "neuvedieš príčinu, ktorá nie je v tomto dokumente" and S7 treated the dead
end as the correct response. Owner overruled it: when the catalogue has no match, propose the most
probable explanation from professional/scientific knowledge of aluminium extrusion, **say plainly that
it is outside the catalogue**, and if information is missing, define the **cheapest** questions.
Implemented as KROK 4 with a mandatory label — `HYPOTÉZA MIMO KATALÓGU — … Opiera sa o: … Mechanizmus: …
Rozhodne to: … Vyvráti to: …` — so it can never be mistaken for a catalogue cause. **The confirmation bar
did not move: only an observation confirms, never probability.** Fabricated citations, studies, authors
or figures stay banned; name the mechanism instead.
The non-obvious part was a **rule collision** the change created: KROK 0 forbids diagnosing without a
discriminating observation, KROK 4 demands always offering something. Resolution, now scenario S13
(blocking): with an observation → offer the labelled hypothesis; without one → offer **questions, not
causes**. Without S13 the new rule would have silently disabled the old one.


**Novice and expert fail in opposite directions — 2026-08-15, quality-packs v0.4.0.**
Owner's requirement: the tool must correctly guide an experienced AND an inexperienced quality engineer.
The gap was not "explain more". It was that **a decision tree only knows YES and NO, so "I don't know"
has nowhere to go** — and an inexperienced user will guess rather than admit it, producing a cause
resting on nothing. Rule added: "neviem" never branches, the cause is marked **NEOVERENÁ** and stays in
play (not excluded), every question states **where the answer is found**, and unfamiliar terms
(nedolisok, bearing, puller, PCG) are explained inside the question. 8D must list what stayed unverified —
unverified is not excluded.
The expert's risk is the mirror image: **they already have an answer and are looking for confirmation**
(this is what AMARI/2650 was). So skipped steps must be named along with the basis for skipping — a
silently skipped step is an assumption wearing the costume of a fact — and the tool offers the observation
that would **refute** their hypothesis, not confirm it.
Scenarios S14 (blocking) and S15 cover the two directions; threshold now 15/15.


**The acceptance set found a real design defect on its first proper run — 2026-08-15, v0.4.0 → v0.4.1.**
S7 failed: given an anodising defect, the model listed four out-of-catalogue causes, tagged them
`NEOVERENÁ`, and **never said they were not from the catalogue**. Cause was the pack's design, not the
model: v0.4.0 introduced two labels side by side without distinguishing them — `NEOVERENÁ` (is in the
catalogue, not yet verified) and `MIMO KATALÓGU` (not in the catalogue at all). The model reached for the
wrong one, defeating the whole point of labelling. Fixed in 0.4.1 with an explicit contrast section, the
combined form `MIMO KATALÓGU, NEOVERENÁ`, and a standing rule that one does not substitute for the other.
Re-run passed.
**Second finding, about the test set itself:** S7's original input was one sentence practically identical
to S13's but with the opposite expected output, so S7 could never have passed. When a rule is added, its
scenario must be re-checked against neighbouring scenarios — **a scenario for the new rule must contain a
genuinely discriminating observation, or it silently tests the older rule instead.**
Run status: 6 of 15, all five blocking scenarios pass on model "Automaticky" (not GPT-5.6). S1/S2 passed
on 0.2.1 and do not carry over — the pack changed materially since.


**A verifier may say something is broken; it must never decide what gets built — 2026-08-16.**
Owner's frustration ("točíme sa v bludnom kruhu") was correct and Andrew Ng's *AI Engineering Skills Map*
(14 Aug 2026) names the missing skill precisely: **shaping the build** — when agents deliver to a spec,
the engineering work moves to deciding what belongs in the spec. Between 12 and 16 Aug the quality pack
went through five versions while `source/` — the actual knowledge — never changed once, because a working
verifier was allowed to generate the work: gate → scenario → rule collision → new rule → new scenario.
It looks like progress because every step is correct and ends green.
**The same post also validates the product thesis and exposes a real gap.** Ng: AI differs from ordinary
software in having unpredictable output, so the craft is measuring and governing behaviour via disciplined
evals and error-analysis loops. That is our differentiator stated from the other side — but our acceptance
set is **not an eval**: single manual run, binary pass/fail, no error taxonomy, no trend. A scenario that
passed once on a nondeterministic model means "it worked at least once", which is weaker than what we
recorded. Fix specified in `docs/EVAL_DISCIPLINA.md`: repeat runs with a pass *rate* (blocking = 5/5),
error codes Z1–Z6 instead of free text, model-assisted grading with mandatory human sampling.


**Topology does not buy truth — you need anchors. 2026-08-16, Kopadze "Graph Engineering".**
The article's own opening claim is that most people use AI at 5–10% of its capability — i.e. the product
thesis is a widely held view in the field, not our insight. Commercially good news: the market does not
need convincing that the problem exists.
Its deepest point lands on what we built: a system where every node checks another node, all reading from
the same source, is **consistent and unverified** — it fails like a single loop, later and with more green
ticks. Our pack, gate, scenarios and grading were all authored by Claude, so most of the acceptance set
**catches regression but does not prove correctness**. Only anchors prove correctness: closed complaints
whose real cause is independently known, an intervention that actually stopped (AMARI/2650), an expert
objection from the shop floor, and CW35–36 switching to original packaging.
**Three practices we were violating, now fixed:** (1) whoever ran a scenario also graded it in one context
— grading now runs in a clean context given only the transcript and criteria; (2) the 15 scenarios have no
edges between them yet ran serially — they fan out, which is what makes Ng's repeat runs affordable
(15 × 5 = 75); (3) a truncated response was almost graded as complete — returned answers are now counted
against expected.
Also recorded: three **frozen rules** (no cause without a discriminating observation · always label
out-of-catalogue · never invent sources) — frozen because they are exactly what an optimiser would bend to
look more helpful.
**Where a graph would be wrong for us:** building a pack (exploratory, sequential, approval each step) and
diagnosing one case (the cost-ordered sequence is a real chain). Diagnosis is a loop, and a loop is correct.


**LLMs automate what you can VERIFY, not what you can specify — 2026-08-16, research across 5 sources.**
Karpathy's verifiability thesis, and Ng, Huyen, Raschka and Kopadze say the same thing from other angles.
This sharpens the product claim: companies are stuck at 5% **not because AI is weak but because their work
is not in verifiable form**. We do not sell knowledge into AI — we sell the conversion of company
decision-making into verifiable form. Falls out as a **sales qualification filter**: *can we say in advance
what would prove the answer wrong?* If not, don't sell the pack — it can be neither handed over nor defended.
Diagnosing a defect passes; "write a nice reply to the customer" does not.
**Raschka gives the mechanism the pack was missing — ablation.** Harnesses shrink as models improve, so a
rule written today to compensate for a weakness may be dead weight in six months. Turn one rule off, re-run
the set; if nothing degrades, **delete the rule**. Until now the pack could only grow, which is exactly how
five versions appeared with no change to the knowledge.
**Huyen: four of her six pitfalls are ones we fell into** — premature complexity, over-indexing on early
success (LinkedIn: 1 month to 80%, four more to 95% — tell customers this before a pilot), abandoning human
evaluation (judge quality depends on judge model, prompt and use case, so a manual sample must always run
and be correlated), and collecting use cases without strategy ("a million Slack bots") — which is the ready
answer to how a process gets chosen at a customer: not by survey.
Also missing: we only have **failure-mode** eval sets. Huyen wants one that matches the **real production
distribution** — an ordinary Tuesday — otherwise we never learn if the tool is over-cautious on routine work.
Full notes with sources and honest coverage gaps: `docs/RESEARCH_12_UCTOV.md`.


**A template that fills in a name produces pages nobody wrote — 2026-08-17.**
All 19 product/service pages shared seven generated sentences; four templates and four swipe files
differed by a single word ("X, scoped and quoted for your actual project"). It looked correct at the
source (`MARKETING_BLURBS` keyed by format) and unbearable on the page. **A per-format template is a
defect generator: it scales one weak sentence across every page and nobody reads them side by side.**
Fixed with per-slug dictionaries written from each product's own file.
**Second, worse lesson from the same fix:** the copy lives in code but is *served* from the `pages`
table, which the pipeline rewrites — so `git checkout --theirs db/biznis.sqlite3` silently reverted it
twice in one hour. `scripts/apply_blurbs.py` now rewrites them from code and exits non-zero if any
template sentence survived; it runs after every merge, before the build.
