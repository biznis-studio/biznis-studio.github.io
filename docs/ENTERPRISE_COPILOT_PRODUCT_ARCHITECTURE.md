# Enterprise Copilot Product Architecture

**Status:** register agreed 2026-08-09; architecture derived from it.
Part I (§1–6, §14a) is evidence and constraint. Part II (§7–19) is design, and
every decision cites the assumptions it follows from. Anything not derivable is
labelled **DESIGN ASSUMPTION** and carries no factual status.

Supersedes nothing. `ARCHITECTURE_COPILOT_LAYER.md` remains the evidence log;
this document is the product decision record built on top of it.

---

## 1. Executive decision — what we know and what we do not

**What is settled (verified against Microsoft Learn, 2026-08-09):**

- The distribution unit is fixed: **one app package carries exactly one agent.**
- **Cross-publisher agent-to-agent calling is explicitly permitted** by store
  policy, which assigns liability for it.
- **A thin orchestrator is not publishable.** Both a parent agent and every worker
  it references must independently meet a value bar.
- **Shipping knowledge inside the package is not available to a distributed
  product** — file embedding is line-of-business only. Customer-side knowledge
  configuration is therefore irreducible.
- **Native write actions exist** (email, calendar) with no backend, and
  consequential actions have a prescribed confirmation contract.
- **The store enforces "differentiated value beyond Copilot" as a Must-fix gate.**
  Better instructions alone do not qualify.

**What we do not know, and must not assume:**

- Whether declaring native write capabilities changes review depth (U3 residue).
- Whether publisher-side telemetry exposes anything beyond adoption counts.
- Whether the value proposition survives contact with buyers — no customer has
  been asked, and one internal user's positive experience is not evidence.
- **Whether onboarding can be held under the economic ceiling in §14a.** This is
  now the largest single risk to the business, larger than any technical
  question remaining.

**Decision status:** not BUILD, not KILL. **CONDITIONAL — proceed to derive
architecture; the go/no-go depends on §14a and on buyer evidence, neither of
which is a desk exercise.**

---

## 2. Product thesis

> The smallest productisable layer a company installs into its own Microsoft 365
> tenant that demonstrably increases Copilot's usefulness in repeatable
> professional and administrative work, without moving company data outside the
> tenant.

Three commitments follow from that sentence and constrain everything below:

1. **Inside the tenant.** No customer content is processed by infrastructure we
   operate. This is the sellable proposition; it is also what makes procurement
   tractable.
2. **Repeatable work, not questions.** The unit of value is a *process run to a
   defined end state*, not an answer.
3. **Demonstrable.** A claim of improvement must be measurable by the customer,
   with a baseline taken before deployment.

**What the product is not:** a chatbot, a general assistant, a prompt library, a
Copilot training course, or a consulting practice with software attached.

---

## 3. Architecture principles — invariant

These are not preferences. Violating one invalidates the thesis.

| # | Principle | Why it is invariant |
|---|---|---|
| P1 | **Use Microsoft before extending it; extend before building.** | Every component we build is a component we must certify, secure, host and maintain at 99.9%. |
| P2 | **No customer content leaves the tenant.** | §2 commitment; also the only cheap answer to procurement. |
| P3 | **The agent proposes; a human disposes on anything consequential.** | Store policy requires it for mutating actions; our own claim discipline requires it everywhere else. |
| P4 | **Every distributed artefact must stand alone commercially.** | Forced by store policy (A9, A10). Also good business hygiene. |
| P5 | **No number we cannot show the source of.** | Applies to marketing, to the product's own output, and to internal claims. |
| P6 | **Customer configuration is priced, never wished away.** | A12 closed the zero-configuration route permanently. |
| P7 | **Preview features may be planned for, never depended on.** | A7 is preview; the MVP must work without it. |

---

## 4. Critical Assumptions Register

Status vocabulary: **FACT** (official documentation, quoted) · **INFERENCE**
(logical consequence of facts, labelled as such) · **UNKNOWN** (documentation
silent — never read as yes or no) · **PREVIEW** (documented, not dependable).

All sources verified **2026-08-09** unless stated. Abbreviations: *DA-1.8* =
declarative agent manifest schema 1.8; *SVG* = Agent Store Validation Guidelines
(marketplace policy 1140.9); *APP* = Microsoft 365 app manifest schema;
*REG* = Agent Registry admin documentation.

### A. Platform

| ID | Assumption | Status | Source | Consequence |
|----|-----------|--------|--------|-------------|
| A1 | One app package = exactly one declarative agent | **FACT** — `declarativeAgents` `minItems:1, maxItems:1`, *"Currently, only one declarative agent per application is supported"*, identical across manifest **1.19 → prev** | APP `root.copilotAgents` | The packaging atom is the agent. Domain packs are separate products, not SKUs. |
| A2 | An app declares declarative **or** custom-engine agents, never both | **FACT** — `oneOf` | APP | No hybrid package. |
| A3 | `instructions` capped at **8,000 characters** | **FACT** — unchanged in 1.5 and 1.8 | DA-1.5, DA-1.8 | Procedure fits; corpora never do. This single limit creates the CORE/configuration split. |
| A4 | Agent knowledge can be left **unscoped** to reach all tenant sources | **FACT** — omitting `items_by_url`/`items_by_sharepoint_ids`/`connections` searches the whole organisation; SVG makes it the **required** multi-tenant pattern (*"leave the nodes for them empty"*, Must fix) | DA-1.8, SVG | A tenant-agnostic manifest is not a trick — it is the prescribed design. |
| A5 | Manifest cannot be parameterised per tenant | **FACT** — only localisation keys `[[key]]`; unrecognised properties invalidate the document | DA-1.8 | No templating. Either unscoped, or a per-customer build (which A-econ forbids). |
| A6 | `actions` array holds **1–10** plugins; plugin manifest may be inlined | **FACT** | DA-1.8 | Action surface is bounded; fewer files to ship. |
| A7 | `worker_agents` — agent-to-agent delegation, brokered by Copilot Chat | **PREVIEW** — added in schema 1.6; DA-1.8 states *"This capability is in preview"* | DA-1.8, connected-agent doc | Plan for it (P7). MVP must not require it. |
| A8 | A parent agent may reference a worker **published by a different publisher** | **FACT** — *"If a parent agent references a worker agent published by a different publisher, the parent agent publisher remains responsible for handling integration issues, user experience gaps, and graceful failure behavior."* | SVG | Federation may span publishers. We can orchestrate agents we did not write — and inherit responsibility for the seams. |
| A9 | A parent agent must have **standalone value** without any worker | **FACT** — Must fix | SVG | A shell orchestrator is unpublishable. |
| A10 | **Each** worker must independently meet the value bar | **FACT** — Must fix | SVG | Domain packs cannot be passive knowledge containers. |
| A11 | Prompts depending on a worker must **fail gracefully** when it is absent | **FACT** — Must fix | SVG | Degradation is a build requirement. Ties to §17. |
| A12 | Knowledge can be embedded **in the package** (`EmbeddedKnowledge`, 10 files × 1 MB) | **FACT that it exists** (DA-1.8) — **FACT that we may not use it**: *"Dataverse, file embedding, sensitivity label, and scenario model capabilities are restricted to be used in the LOB scenario only"*, Must fix | DA-1.8, SVG | **Zero-configuration distribution is closed.** Customer-side knowledge setup is permanent, and must be priced (P6). |
| A13 | Agent-to-agent communication is **text only** | **FACT** — no files, no images | connected-agent doc | A worker cannot return a structured record. Delegation passes prompts, not objects. |
| A14 | Adaptive cards raised by a worker are **not shown to the user**; the parent receives only their data | **FACT** | connected-agent doc | **Human approval cannot be delegated.** Confirmation UX must live in the agent the user is talking to. |
| A15 | Workers may be declarative agents only | **FACT** — *"Custom engine agents are currently not supported"* | SVG | No Copilot Studio agent inside a federation. |
| A16 | Native **write** capabilities exist without a backend — `EmailActions` (triage, supervised send, delete, inbox rules, auto-reply, folders), `MeetingActions` (scheduling, polls) | **FACT** (DA-1.8) | DA-1.8 | The old "security XOR automation" fork is narrowed: real actions with no egress, *where Microsoft shipped one*. |
| A17 | `editorial_answers` — up to 300 curated Q&A pairs, semantic match with tunable thresholds | **FACT** | DA-1.8 | A governance primitive. USE MICROSOFT (P1). |
| A18 | `default_response_mode` (`Auto` / `Quick response` / `Think deeper`) is declarable | **FACT** | DA-1.8 | Reasoning depth is a product setting, not a user's lucky guess. Directly addresses the observed "only reliable on the strongest model". |
| A19 | Marketplace distribution requires Agents Toolkit; Agent Builder and Copilot Studio declarative agents are org-catalog only | **FACT** (2026-08-08) | prior log | Low-code authoring is a prototyping tool, never the shipping path. |

### B. Security and data boundary

| ID | Assumption | Status | Source | Consequence |
|----|-----------|--------|--------|-------------|
| B1 | Copilot enforces the user's existing permissions; the semantic index honours the identity boundary | **FACT** | prior log (2026-08-08) | Permission-trimmed retrieval is a **platform guarantee we inherit**, not code we write or warrant. |
| B2 | Connector content is permission-trimmed the same way | **FACT** | prior log | External data inherits the model. |
| B3 | Prompts and Graph-accessed data are not used to train foundation models | **FACT** | prior log | Quotable in procurement. |
| B4 | Purview-encrypted content may be **invisible** to an agent | **FACT** — encryption *"can exclude programmatic access, thus limiting the agent from accessing the content"* | prior log | The most under-appreciated deployment risk: quality/HR/legal documents are exactly what gets labelled, and failure is **silent**. Onboarding must test it explicitly. |
| B5 | Our agent is a **separate trust boundary**; admins review its permissions and data access before enabling | **FACT** | prior log | Our privacy policy and terms are procurement artefacts from day one, not launch paperwork. |
| B6 | Copilot is an EU Data Boundary service, **but** models supplied by Anthropic as subprocessor are currently excluded | **FACT WITH EXCEPTION** | prior log | Must be disclosed unprompted to EU buyers. Concealment costs the deal and the relationship. |
| B7 | Any action backend must meet: HTTPS TLS 1.2+, no URL redirection, and be *"served from the same domain or subdomain as the root domain verified for the developer"* | **FACT** | SVG | Constrains hosting topology if we ever ship an action endpoint. |
| B8 | Non-`WebSearch` capabilities require a Copilot licence or metered usage | **FACT** | DA-1.8 note | Addressable market = licensed tenants. Confirmed in the field 2026-08-08 (unlicensed Agent Builder offers only "Add specific URL"). |
| B9 | Government tenants: Agents Toolkit publishing and authenticated custom actions unsupported | **FACT** | prior log | Public sector excluded. |

### C. Distribution, deployment, discoverability

| ID | Assumption | Status | Source | Consequence |
|----|-----------|--------|--------|-------------|
| C1 | Admin can **publish** (who may install) and **deploy** (who gets it **preinstalled**) as separate choices | **FACT** — *"Under Deploy (optional), select the users or groups who will have the agent preinstalled"* | REG | Silent fleet-wide rollout is possible. An earlier note claiming every user must install manually was wrong. |
| C2 | Admins may pin at most **three** agents; beyond three, lower-priority agents are **not seen** by the user | **FACT** | REG | This is a **discoverability** limit, not an installation limit. See §7's five-layer separation — do not conflate them. |
| C3 | Users must acquire a worker agent before prompts depending on it work; the parent's description must instruct them to | **FACT** | connected-agent doc, SVG | Acquisition friction is a product surface, not an afterthought. |
| C4 | Store requires **differentiated value beyond Copilot**: workflows not easily achieved via Copilot, *or* significant time reduction, *or* specialised orchestration / fine-tuned models | **FACT** — Must fix | SVG | Our G8 is Microsoft's entry condition. "Better instructions" is absent from the qualifying list. |
| C5 | Publisher attestation, Microsoft 365 App Compliance, and Responsible AI validation apply; RAI failure blocks publication | **FACT** | certification policies, RAI validation doc | Compliance is a build input. |
| C6 | Operational bars: 99.9% availability; response time ≤9 s p99, ≤5 s p75, ≤2 s p50 | **FACT** | SVG | Applies to anything we host. An argument for hosting nothing. |
| C7 | Whether declaring `EmailActions`/`MeetingActions` raises review depth | **UNKNOWN** | — | Not "no". Assume equivalent disclosure duty; verify before relying on write features commercially. |

### D. Automation and control

| ID | Assumption | Status | Source | Consequence |
|----|-----------|--------|--------|-------------|
| D1 | Consequential (system-mutating) actions **must** require explicit user permission before execution | **FACT** — Must fix | SVG | Human-in-the-loop is mandated, not optional. |
| D2 | Mechanism is prescribed: plugin → `isConsequential: true`; MCP → `readOnlyHint: false`; or a custom CTA stating the action | **FACT** | SVG | USE MICROSOFT (P1) — do not build an approval framework. |
| D3 | Confirmation wording must name the operation (*"Do you want to proceed with creating a new order?"* passes; *"Do you want to proceed?"* fails) | **FACT** | SVG | Copy is a compliance surface. |
| D4 | Completion must be reported as a card containing action details, way forward, and a **source link or tracking ID** | **FACT** — Must fix | SVG | Auditability is required output, not a feature we may skip. |
| D5 | *"Highly consequential tasks such as bulk delete mustn't be supported"* | **FACT** (Good-to-fix) | SVG | Bulk destructive operations are out of scope by policy and by P3. |
| D6 | Native confirmation objects and Adaptive Cards exist for human-in-the-loop | **FACT** | prior log | Do not build; consume. |
| D7 | Arbitrary write-back of new knowledge into the tenant (SharePoint list, Dataverse) without a backend | **UNKNOWN**, previously recorded as a structural blocker; A16 shows Microsoft is shipping capability-by-capability | — | Knowledge capture stays **human-saved** in the MVP. Revisit each schema release. |

### E. Measurement

| ID | Assumption | Status | Source | Consequence |
|----|-----------|--------|--------|-------------|
| E1 | Tenant-side agent usage reporting exists and belongs to the **customer's** admin | **FACT** | Copilot agents usage report | We do not own it and cannot require it. |
| E2 | Publisher-side analytics exist (Developer Portal Analytics; Partner Center Insights → Usage), showing active usage by host product | **FACT** | those docs | We can see adoption. |
| E3 | Granularity, latency, per-tenant vs aggregate | **UNKNOWN** | — | Do not design reporting commitments on it. |
| E4 | Platform telemetry measures **outcome** (time saved, error rate, task completion) | **INFERENCE — NO.** Every documented metric is an adoption metric | — | **Value proof cannot be automated from telemetry.** It must be a customer-executed measurement, which is human work per customer — precisely what §14a limits. |

---

## 5. Platform constraints — derived, not assumed

Each entry is **FACT → CONSTRAINT → DESIGN DECISION.**

**5.1 Packaging**
FACT (A1, A2): one package, one agent.
CONSTRAINT: a multi-domain offering is multiple listings, multiple approvals,
multiple update cycles.
DESIGN DECISION: **the agent is the unit of product, versioning and price.** No
concept of "suite" exists at the platform level, so any suite is a commercial
construct we maintain ourselves.

**5.2 The 8,000-character wall**
FACT (A3): instructions ≤ 8,000 characters, unchanged across schema generations.
CONSTRAINT: methodology of any depth cannot live in the manifest.
DESIGN DECISION: **procedure in `instructions` (our IP, ships with the package);
corpus in tenant knowledge (customer's, configured on site).** This is the
CORE/configuration seam, and it is imposed by the platform, not chosen.

**5.3 Federation shape**
FACT (A8, A9, A10, A11): cross-publisher delegation is allowed; parent and every
worker must stand alone; absent workers must degrade gracefully.
CONSTRAINT: "thin orchestrator + dumb knowledge packs" fails validation.
DESIGN DECISION: **every agent we ship is a complete, separately sellable
product.** Orchestration is an *additional* capability of one of them, never the
reason any of them exists.

**5.4 Approval cannot be delegated**
FACT (A14): a worker's Adaptive Card never reaches the user.
CONSTRAINT: a delegated action cannot obtain informed consent.
DESIGN DECISION: **consequential actions execute only in the agent the user is
addressing.** Workers may compute, retrieve and recommend; they may not be the
place where a user approves something.

**5.5 Structured hand-off does not exist**
FACT (A13): agent-to-agent traffic is text.
CONSTRAINT: a federation cannot pass records, only prose.
DESIGN DECISION: **define a strict text contract** (a fixed field order the
parent parses) and treat any richer integration as requiring an action, not a
worker.

**5.6 Knowledge cannot ship with the product**
FACT (A12): file embedding is LOB-only.
CONSTRAINT: every customer must have knowledge configured in their tenant.
DESIGN DECISION: **onboarding is part of the product**, with a fixed method, a
fixed artefact set and a fixed price — and it is bounded by §14a.

**5.7 Reasoning depth is ours to set**
FACT (A18): `default_response_mode` is declarable.
CONSTRAINT: reliability must not depend on the user picking a model.
DESIGN DECISION: **ship `Think deeper` for any agent that runs a procedure**, and
treat sensitivity to model choice as an instruction defect to be fixed, not a
setting to be recommended.

---

## 6. Security and data architecture

FACT (B1, B2): permission-trimmed retrieval is a platform guarantee.
CONSTRAINT: we must not build, and must not warrant, an access-control layer.
DESIGN DECISION: **the product's security statement is "we add no new access
path"** — the agent sees exactly what the signed-in user could already open. That
is provable, cheap, and stronger than anything we could implement.

FACT (B4): Purview-encrypted content may be silently invisible.
CONSTRAINT: an agent can appear healthy while being blind to the most important
documents.
DESIGN DECISION: **a labelled-content probe is a mandatory, blocking step of
onboarding**, with a documented expected answer. Never rely on the absence of an
error message.

FACT (B5, B6): we are a separate trust boundary; the Anthropic subprocessor sits
outside the EU Data Boundary.
CONSTRAINT: enterprise procurement will examine both.
DESIGN DECISION: **publish the data-handling statement before the first sales
call, and disclose the EU exception unprompted.** Disclosure costs a question;
concealment costs the account.

FACT (B7, C6): a hosted endpoint inherits TLS, no-redirect, same-domain and
99.9% obligations.
CONSTRAINT: every hosted component is a permanent operational liability.
DESIGN DECISION: **the MVP hosts nothing.** Actions, if any, use native
capabilities (A16) only.

---

## 14a. Economic gate — the binding risk

Stated separately and early because it now outranks every technical question.

> **GATE E:** if customer-specific onboarding exceeds the ceiling below, the
> product is **not scalable in its current architecture**. The response is to
> change the architecture or the offer — never to absorb the hours.

**Derivation.** Let *A* = annual recurring revenue per customer, *g* = target
gross margin, *r* = our fully loaded hourly cost, *h* = one-off onboarding hours.
Amortising onboarding over an assumed 3-year life:

```
h  ≤  3 · A · (1 − g) / r
```

**This is a parametric model, not a finding.** *A*, *g* and *r* are **BUSINESS
ASSUMPTIONS** — not facts, not derived from the register, and not yet calibrated
against any customer's willingness to pay or any timed deployment. They must be
recalibrated from real pricing and real onboarding cost before the gate binds.

**Illustrative substitution only:** A = 6 000 €/yr, g = 0.80, r = 60 €/h →
h_max ≈ 60 hours.

> **h_max is a hard ceiling, never a target.** A product that lands at 40–60
> hours has not been productised — it has had its first implementation. The
> design target is **10–20 hours**, and every decision in §10 and §12 is judged
> against that number, not against the ceiling.

That must cover: tenant assessment, the Purview probe (B4), knowledge mapping and
configuration (A12 — unavoidable), permissions, testing, baseline measurement
(E4), training, and handover.

**Why this is the real risk.** A12 made customer-side knowledge configuration
permanent. E4 made value proof a human exercise. Both land in *h*. If knowledge
mapping alone consumes the ceiling, the business is consulting with a manifest
attached — which §38 of the brief explicitly rejects.

**Two mitigations to design for, neither yet validated:**
1. **The customer performs onboarding**, guided by our method and templates; we
   review. Shifts hours off our side of the ledger.
2. **Knowledge structuring is the paid deliverable**, sold once at full price and
   deliberately not amortised into subscription.

**Measurement obligation:** *h* is recorded for every deployment from the first
one. No estimate substitutes for a timed run.

---

## 20. Gates the derived architecture must pass

| Gate | Question | Current reading |
|------|----------|-----------------|
| G1 | Microsoft compatibility | **PASS** — the whole design is native primitives |
| G2 | Data boundary | **PASS** with MVP hosting nothing (§6) |
| G3 | Repeatable distribution | **PASS** — unscoped manifest is the prescribed pattern (A4) |
| G4 | Customer IT effort | **CONDITIONAL** — bounded by §14a, unmeasured |
| G5 | Real work, not answers | **UNPROVEN** — no buyer evidence yet |
| G6 | Reusable core | **CONDITIONAL** — procedure is reusable (A3); knowledge never is (A12) |
| G7 | Acts, not only answers | **CONDITIONAL** — native actions only (A16), narrow surface |
| G8 | Differentiated vs plain Copilot | **MANDATORY** — Microsoft enforces it (C4) |
| G9 | Gross margin | **CONDITIONAL on §14a** — the decisive gate |
| G10 | 100+ customers without linear headcount | **CONDITIONAL on §14a and E4** |

**No gate reads FAIL. Four read CONDITIONAL, and three of those resolve to the
same variable: onboarding hours.**

---


---

# PART II — Architecture derived from the register

Every decision below cites the assumptions it follows from. Where a decision
cannot be derived, it is labelled **DESIGN ASSUMPTION** and carries no factual
status. Nothing here cites an assumption absent from §4.

---

## 7. Product architecture — five layers, deliberately not collapsed

**One deliberate non-decision:** the number of user-visible agents is *not* fixed
by C2. Three pinned slots is a discoverability constraint and nothing more. These
five questions are distinct and must never be conflated:

| Layer | Governed by | Cardinality |
|---|---|---|
| **L1 Commercial product** — what is bought | A1 (one package = one agent) | 1 agent = 1 listing = 1 price |
| **L2 Installed** — present in the tenant | C1 (admin *publishes* and *deploys*) | Unbounded; admin can preinstall silently |
| **L3 Visible** — what the user sees pinned | C2 (max 3 pinned; beyond that, unseen) | ≤ 3 promoted, rest discoverable on demand |
| **L4 Callable** — what a parent can invoke | A7 (PREVIEW), A8 (cross-publisher OK) | Bounded by acquisition (C3), not by slots |
| **L5 Entry point** — whom the user addresses | A14 (approval lives here) | Exactly 1 per conversation |

**FACT (C2 is about L3 only) → CONSTRAINT: installation count and visibility
count are independent → DESIGN DECISION: optimise L3 for attention and L2 for
coverage.** A tenant may hold nine installed agents while promoting one. "Three
slots" never becomes "three agents".

### Whether there is a single CORE agent — derived, not chosen

**FACT (A7): delegation is PREVIEW. FACT (P7): preview may not be depended on.
FACT (A9, A10): parent and every worker must independently carry value.**

**CONSTRAINT:** an architecture whose value requires delegation is (a) unshippable
today and (b) unpublishable even when delegation ships, because the parent would
lack standalone value.

**DESIGN DECISION:** **the MVP is exactly one agent, with no workers.** Federation
is a v2 capability added to an already-valuable agent, never the reason it exists.
Whether a dedicated "CORE orchestrator" agent is ever created remains **open** —
A9 makes a pure router unpublishable, so if one appears it must itself be a
useful agent that also routes. That is a decision for v2, on evidence.

---

## 8. CORE vs domain — and the budget nobody has costed

**FACT (A3): 8,000 characters of `instructions`, total.**
**FACT (A12): knowledge cannot ship in the package.**

**CONSTRAINT — the one that shapes the product:** CORE governance and domain
procedure **share one 8,000-character budget**. They are not separate stores.

| Element | Ships where | Owner | Reusable across customers |
|---|---|---|---|
| Governance rules, evidence discipline, output contract, escalation, refusal behaviour | `instructions` (A3) | **Us — this is the IP** | Fully |
| Domain procedure — the ordered questions, discriminators, cost ordering | `instructions` (A3) | Us | Per domain |
| Curated exact answers | `editorial_answers`, ≤300 pairs (A17) | Us or customer | Partly |
| Reasoning depth | `default_response_mode` (A18) | Us | Fully |
| Corpus — cases, SOPs, records | Tenant knowledge (A4, A12) | **Customer** | Never |

**Evidence for the budget split (measured, not estimated):** the 8D diagnostic
agent built 2026-08-08 used **4,213 characters** for governance *and* one domain
procedure combined — roughly 2,000 governance / 2,200 domain, leaving ~47 %
headroom.
**INFERENCE:** one domain per agent fits comfortably; two or three domains in one
agent would consume the budget and degrade both. This supports A1's grain
(one agent = one domain) on quality grounds, not only packaging grounds.

**DESIGN DECISION:** CORE is a **written specification plus a reusable instruction
block**, not a software component. It is versioned, tested and inserted into every
domain agent's `instructions` at build time.

---

## 9. Federation and orchestration

**FACT (A13): text only. FACT (A14): a worker's Adaptive Card never reaches the
user. FACT (A11): absent workers must degrade gracefully.**

**CONSTRAINT:** delegation is prompt-passing between context windows, not a
workflow bus, and it cannot carry consent.

**DESIGN DECISIONS:**
1. **A strict text contract.** A worker returns a fixed, ordered, labelled block
   the parent parses positionally. Anything richer requires an action (A6), not a
   worker.
2. **Workers are read-and-recommend only.** No worker may hold a consequential
   action. Derived directly from A14 — a user cannot approve what they cannot see.
3. **Degradation is specified per prompt, not global.** Each conversation starter
   that depends on a worker declares its fallback behaviour (A11).
4. **The parent's listing enumerates every worker it may call** and instructs
   acquisition (C3, SVG Must-fix).

---

## 10. Knowledge architecture — and the finding that decides the ceiling

**The single most important derivation in this document.**

**FACT (A4):** omitting the scoping nodes searches the whole organisation, and SVG
makes **leaving them empty the required multi-tenant pattern** (Must fix).

**CONSTRAINT:** enumerating SharePoint sites, libraries and connectors per
customer is **not merely unnecessary — it is contrary to the prescribed design.**

**DESIGN DECISION:** **onboarding does not map the tenant.** No one walks hundreds
of SharePoint sites. The agent is unscoped; retrieval precision is recovered
through `instructions` (A3) and `editorial_answers` (A17), not through
configuration.

This removes what looked like the dominant onboarding cost. **The remaining cost
driver is different and harder: whether the customer's knowledge exists in
written form at all.**

### The six knowledge classes

| Class | Lives | Owner | Ships with product | Update path | Onboarding cost |
|---|---|---|---|---|---|
| **K1 Our distributed IP** — governance + domain procedure | `instructions` (A3) | Us | **Yes** | Package version | **0 h** |
| **K2 Public/domain methodology** — 8D, IATF, standard practice | `instructions` if compact; else customer document | Us (as written form) | Yes, as procedure | Package version | **0 h** |
| **K3 Customer know-how** — SOPs, lessons learned, case history | Tenant (A4, A12) | Customer | **No** (A12) | Customer's own document lifecycle | **The variable** |
| **K4 Process data** — records, tickets, measurements | Tenant / connectors (A4) | Customer | No | Live | ~0 h if already in M365 |
| **K5 Dynamic sources** — external systems | Copilot connectors (A4) | Customer | No | Live | Excluded from MVP |
| **K6 Sensitive content** — labelled, encrypted | May be **invisible** (B4) | Customer | No | — | Probe, then exclude or unlabel |

**K3 is the product's real subject and its real risk.** If a customer's know-how
is written, onboarding is configuration and the 10–20 h target is plausible. If it
lives in people's heads, onboarding becomes knowledge *creation* — which is
valuable, chargeable, and **not productisable at 10–20 hours**.

**DESIGN DECISION (gating):** **a written-knowledge assessment is the first
qualifying step of every sale.** Customers whose K3 is unwritten are sold a
separate, fixed-price knowledge-structuring engagement *first*, and are not
counted as product deployments until it completes. This keeps *h* honest instead
of hiding creation work inside onboarding.

**DESIGN ASSUMPTION (not derivable, must be tested in §19):** that a useful
fraction of target customers already hold K3 in written form. If they do not, the
product is a knowledge-structuring consultancy with an agent attached, and §38 of
the brief rejects that.

---

## 11. Action architecture — two paths that must never merge

**FACT (D1): consequential actions require explicit permission before execution.
FACT (D2): mechanism prescribed — `isConsequential` / `readOnlyHint` / custom CTA.
FACT (D3): confirmation must name the operation. FACT (D4): completion needs a
tracking ID or source link. FACT (A14): worker cards are invisible to the user.**

**Path A — the only path that may change anything:**
```
retrieve (A4) → reason (A18) → draft → user confirmation (D1-D3) → native action (A16) → receipt (D4)
```
Runs **only** in the entry-point agent (L5). Uses native capabilities only; the
MVP hosts nothing (§6).

**Path B — everything a worker may do:**
```
worker → retrieve → reason → recommendation (text, A13)
```
Terminates in text. **No worker holds an action.**

**CONSTRAINT → DESIGN DECISION:** the two paths are separated at the manifest
level — worker agents ship with no `actions` array at all (A6). This makes the
rule structural rather than behavioural, so it cannot be violated by a prompt.

**FACT (D5): bulk destructive operations are not to be supported** — excluded by
policy and by P3.

---

## 12. Onboarding as a subsystem, not an implementation

**Treated as a product component with its own spec, versioning and regression
tests.** Justification: §14a makes *h* the binding variable; an uninstrumented
process cannot be held to a number.

Derived from A4 (no tenant mapping), B4 (silent failure), E4 (baseline is human),
A12 (knowledge config irreducible):

| Step | Derived from | Automatable | Target |
|---|---|---|---|
| 1. Licence + capability check | B8 | **Yes** — scripted | 0.5 h |
| 2. **Purview probe** — labelled-document retrieval test with a documented expected answer | B4 | **Yes** — fixed test prompt | 0.5 h |
| 3. Written-knowledge assessment (K3 present? in what form?) | §10 | Partly — checklist | 2 h |
| 4. Knowledge placement — customer moves K3 into M365; **no scoping** | A4, A12 | Customer-performed | 2–6 h |
| 5. Install + admin deploy + pin | C1, C2 | **Yes** — admin wizard | 0.5 h |
| 6. Acceptance test — fixed scenario set with expected discriminators | §15 | **Yes** — scripted | 1 h |
| 7. Baseline measurement | E4 | **No** — customer-executed | 3–6 h |
| 8. Handover + training | — | Partly — recorded | 2 h |

**Derived total: 11.5–18.5 h**, inside the 10–20 h design target and well under
h_max. **This is a derivation, not a measurement** — steps 4 and 7 are estimates
and are exactly where reality will differ. §19 measures them.

**DESIGN DECISION:** steps 1, 2, 5 and 6 ship as **tooling**, not as a checklist —
a script and a fixed test-prompt set. Steps 4 and 7 are **customer-performed**
under our method. Only step 3 and part of 8 are inherently ours.

**Failure of this section is failure of the business** (§14a). Any step that
cannot be automated or shifted to the customer must be priced separately and
excluded from *h*.

---

## 13. Packaging and marketplace model

**FACT (A1):** 1 agent = 1 package = 1 listing.
**FACT (C4):** must clear "differentiated value beyond Copilot" — qualifying
routes are *workflows not easily achieved via Copilot*, *significant time
reduction*, or *specialised orchestration / fine-tuned models*.
**FACT (C5):** publisher attestation, App Compliance, RAI validation; RAI failure
blocks publication.
**FACT (A19):** Agents Toolkit is the only marketplace path.

**DESIGN DECISIONS:**
- **Each domain agent is its own commercial product** with its own price. No
  suite exists at platform level; any bundle is our own commercial construct.
- **The qualifying claim is route 1** — *a workflow not easily achieved via
  Copilot*: a governed procedure that refuses to conclude without discriminating
  evidence and emits an auditable record. Route 2 (time reduction) is unavailable
  to us until §19 measures it; claiming it now would violate P5.
- **Compliance artefacts are built in sprint 1**: privacy statement, terms,
  data-handling declaration, RAI test pass.
- Agent Builder is prototyping only; the shipped artefact is Toolkit-built (A19).

---

## 15. Evaluation and ROI architecture

**FACT (E4 / INFERENCE): platform telemetry measures adoption, never outcome.**

**CONSTRAINT:** value proof cannot be automated from telemetry and is therefore
human work per customer — the cost §14a limits.

**DESIGN DECISION: a Measurement Kit, executed by the customer, sold once.**
Not a dashboard we operate. Contents:
- N closed historical cases with known outcomes
- A/B: half run with the agent, half with unmodified Copilot (the correct control
  — "before we had anything" confounds the comparison)
- Two primary metrics: **steps to a confirmed conclusion**, and **count of
  expensive verifications avoided** (the latter converts to currency)
- Secondary: escalations, rework, output completeness against the required record
- Recorded by the customer's own people, on their own cases

**Regression suite (ours, automated):** every agent version runs a fixed scenario
set asserting: correct discriminator asked first, no conclusion without evidence,
no invented item outside knowledge, graceful degradation (A11), refusal on
out-of-scope. Derived from A17 (curated pairs make expected answers testable).

**P5 binds absolutely:** no percentage is published, quoted internally, or put in
a deck before a Measurement Kit returns it.

---

## 16. Telemetry and privacy

**FACT (E1): tenant usage reporting belongs to the customer's admin.
FACT (E2): publisher analytics show adoption by host product.
UNKNOWN (E3): granularity. FACT (B3): prompts and Graph data are not training
inputs.**

**DESIGN DECISIONS:**
- **We collect nothing ourselves.** Adoption comes from Partner Center; outcome
  comes from the customer's Measurement Kit, shared only if they choose.
- **No product telemetry endpoint exists** — consistent with §6 (host nothing) and
  P2. This is also a sales asset: there is no data-flow diagram to argue about.
- Commitments in contracts reference only metrics we can actually obtain; E3 is
  UNKNOWN, so no granularity is promised.

---

## 17. Failure modes and graceful degradation

| Mode | Derived from | Behaviour required |
|---|---|---|
| Worker not acquired | A11 (Must fix) | Named fallback per prompt; state plainly what is unavailable and what remains possible |
| **Labelled content invisible** | B4 | **Silent — the dangerous one.** Probe at onboarding; agent instructed to state when it found no grounding rather than answer from model knowledge |
| Knowledge absent or stale | §10 K3 | Agent must say "not in the knowledge I have" and name what would resolve it; never infer |
| No licence | B8 | Non-WebSearch capabilities unavailable; degradation is Microsoft's, message must be anticipated in onboarding |
| Model-mode drift | A18 | `Think deeper` declared; sensitivity to model choice treated as an instruction defect, not a user setting |
| Action fails after confirmation | D4 | Receipt must still be produced, carrying the failure and the way forward |

**Cross-cutting rule, derived from B4 + P5:** the agent must distinguish *"I found
nothing"* from *"nothing exists"*. Conflating them is how silent invisibility
becomes confident error.

---

## 18. MVP architecture

Everything below is forced by the register; nothing is chosen for interest.

| Decision | Derived from |
|---|---|
| **One agent, one domain, no workers** | A7 PREVIEW + P7; A9/A10 |
| **Unscoped knowledge** | A4 (prescribed multi-tenant pattern) |
| **No hosted component, no actions in v1** | §6; B7/C6 obligations; D-path A deferred |
| **`Think deeper` declared** | A18 |
| **`editorial_answers` for the twenty highest-frequency exact questions** | A17 |
| **Governance + one domain procedure ≤ 8,000 characters** | A3, measured at 4,213 |
| **Onboarding tooling for steps 1, 2, 5, 6** | §12, §14a |
| **Measurement Kit** | E4, §15 |
| **Compliance artefacts** | C5 |

**Explicitly excluded from v1:** federation, connectors (K5), native write actions
(A16 — deferred until C7 is resolved), any dashboard, any backend.

**The MVP's single differentiating claim (C4 route 1):** a procedure that will not
conclude without discriminating evidence, and that emits an auditable record of
what was excluded and why. Plain Copilot does not do this, and cannot be made to
do it by prompting alone.

---

## 19. Validation — a falsification experiment, not a pilot

**Purpose: cheapest possible refutation of the whole model.** Not a demo. A demo
proves the agent can talk; this must prove the *business* stands.

**What it tests, traced to the register.** Nothing here is exploratory; each
dimension attacks a specific open item:

| Dimension | Tests |
|---|---|
| Onboarding time *h* | **§14a** (the binding gate) and the §12 derivation — steps 4 and 7 are estimates, and this is where they meet reality |
| Work benefit | The **DESIGN ASSUMPTION in §10** (that target customers hold K3 in written form) and **C4 route 2** (time reduction), which P5 forbids claiming until measured |
| Willingness to pay | **G5, G9** — the register cannot settle either; no documentation answers what a buyer will do |
| User acceptance | **A18/§17** — whether reliability holds without the user choosing a model, and whether degradation (A11, B4) is tolerable in practice |

**Setup:** one narrow domain agent · one real corporate knowledge corpus · real
historical tasks with known outcomes · one real tenant · timed onboarding.

**Pre-registered thresholds — set before any data is seen:**

| Dimension | Refuted if | Supported if |
|---|---|---|
| **Onboarding time** *h* | > 40 h | ≤ 20 h |
| **Work benefit** | < 10 % improvement on the §15 primary metrics | ≥ 25 % |
| **Willingness to pay** | Declines at any price covering §14a | Signs, or pays a deposit |
| **User acceptance** | Abandoned within 4 weeks | Voluntary continued use without prompting |

**The stated failure combinations — all are negative results, not setbacks:**
- Works technically, onboarding 55 h → **negative** (economics)
- Onboarding 12 h, saves 3 % → **negative** (no value)
- Saves 35 %, will not pay → **negative** (no business)
- Low onboarding **and** measurable benefit **and** willingness to pay →
  **the first real evidence the product exists**

**Order matters:** measure the baseline **before** the agent is installed.
Retrospective baselines are unfalsifiable, and P5 forbids reporting one.

**Stop rule:** if two of four dimensions refute, stop and revise the architecture
— do not re-run with adjusted thresholds. Thresholds are fixed at pre-registration.

**Honest dependency:** this requires a real organisation, real users, and a real
buying decision. It is the one part of this document that cannot be produced at a
desk, and it is the only part that can turn any of it into evidence.
