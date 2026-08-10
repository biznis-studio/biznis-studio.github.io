# Competitive audit v1 — 2026-08-10

**Answers question (b) differentiation and question (c) IP.** Needs no tenant.
Done because we were blocked on the least likely reason for this to fail.

**Method limitation, stated first:** vendor sites, product pages and industry
writing. No hands-on evaluation, no demos, no pricing calls. Enough to falsify
our claims. **Not** enough to confirm a gap.

---

## 1. What existing eQMS/CAPA platforms already do

| Capability we planned | Already shipping | Evidence |
|---|---|---|
| Case management, D0–D8 workflow, owners, deadlines | **Yes** | CAPA record structures map D1–D8 to workflow phases |
| Structured RCA — fishbone, 5-Why, fault tree, TapRooT | **Yes** | Intelex, ETQ |
| Rule causes **in or out** against evidence | **Yes** | "add contributing factors under each category with evidence, **rule them in or out**" |
| Centralised RCA log, tagging, pattern spotting for recurring issues | **Yes** | ETQ |
| Effectiveness checks, audit trail, compliance | **Yes** | core eQMS function |
| **AI retrieving similar historical cases on logging** | **Yes** | "when a deviation is logged, AI automatically tags it and **retrieves similar deviations from the past**" |
| **AI proposing probable root causes from history** | **Yes** | "presents the **top three most probable contributing factors** within seconds" |
| **AI recommending corrective actions that worked before** | **Yes** | "suggests actions that have proven most effective for similar issues" |

**In 2026 this is described as moving from innovation project to everyday
practice** in regulated manufacturing.

---

## 2. What this kills

**"The system tells you a similar case happened before"** — shipping.
**"AI helps find the cause"** — shipping.
**"Knowledge accumulates across cases"** — shipping.
**"Case state, deadlines, effectiveness, audit trail"** — shipping, for twenty years.

Every capability we listed in `PRODUCT_ARCHITECTURE_v0.1.md` §0 as *"what Copilot
cannot do"* exists in products a quality department can buy today. We were
comparing ourselves to Copilot. **The customer compares us to their eQMS.**

---

## 3. The one difference that survives — and it is narrow

Their AI presents **the top three most probable** contributing factors.
Ours **refuses to rank by probability** and asks the observation that separates
candidates — and will not conclude without it.

| | Existing AI-eQMS | Ours |
|---|---|---|
| Output | ranked probable causes | one discriminating question |
| Basis | statistical correlation across history | recorded mechanism and how to tell it apart |
| Failure mode | plausible cause, unconfirmed → wrong corrective action | slower; may frustrate someone who wants an answer |
| Evidence | tested 2026-08-09: plain Copilot did exactly the ranking thing; with our procedure it refused | |

**This is a feature-level difference, not a category.** It is defensible as an
argument about *quality of investigation*. It is not a moat, and it sits inside
products that already own the workflow.

---

## 4. Where this actually leaves the market position

**Companies with a modern eQMS:** we are redundant or a very hard sell. Their
platform already holds the spine and is adding the AI.

**Companies without one** — and this is most mid-size manufacturers — run quality
on **Excel, email and SharePoint**. They will not buy a six-figure eQMS. They
already pay for Microsoft 365.

**That is the only segment where any of this makes sense**, and it reframes the
product from what we have been saying:

> Not *"an enterprise AI productivity layer over Copilot"*.
> **Complaint investigation for manufacturers who run quality on Excel and email
> and will never buy an eQMS.**

The Microsoft-native argument finally has a real basis — not *"they already have
Copilot"*, but **"they already have Microsoft 365 and nothing else"**.

**This also changes who we compete with:** not Intelex and ETQ, but the
spreadsheet — and the eQMS vendors' entry-level tiers, which are unexamined.

---

## 5. What this does to the gates

| Gate | Before | Now |
|---|---|---|
| G8 differentiation vs plain Copilot | argued | **wrong comparison** — the bar is the eQMS, or the spreadsheet |
| IP | three hypotheses | **two of three fall** — similar-case retrieval and knowledge accumulation ship today. Only the discriminating-procedure claim survives, and it is a feature |
| Market | "companies with Copilot" | **companies without an eQMS** — narrower, poorer, and possibly right |

---

## 6. What must be checked before anything else is built

1. **Entry-level eQMS pricing.** If a small CAPA module costs €200/month, our
   price ceiling is set by it and every economic assumption in §14a is wrong.
2. **Do those entry tiers include the AI features?** If yes, the segment closes.
3. **Do the target companies even want software here**, or is the complaint
   process deliberately informal because volume is low?
4. **Is the discriminating procedure actually better** — measurably, on real
   cases, against an AI that ranks probabilities? Untested. It is now the single
   claim the product rests on.

**Point 4 is the whole product.** It is also the one thing we have partial
evidence for, from three real complaints on 2026-08-10.

---

## 7. Honest summary

The technical blocker we were stuck on — a tenant — was never the risk. **The
risk was that most of what we planned to build already exists and ships.**

Nothing here says stop. It says the product is smaller, the segment is narrower,
and the single surviving claim is about *how* an investigation is conducted
rather than *that* it is assisted.
