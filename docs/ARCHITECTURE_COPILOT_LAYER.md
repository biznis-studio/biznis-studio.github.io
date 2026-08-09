# AI Workforce Layer for Microsoft 365 Copilot — architecture findings

## CRITICAL ASSUMPTIONS REGISTER

Built before the architecture, per the research protocol. Status is
**VERIFIED** (quoted Microsoft docs), **UNKNOWN** (docs do not answer),
or **FAIL** (documented as not possible). UNKNOWN is never read as YES.

| # | Assumption | Why critical | Status | Consequence |
|---|---|---|---|---|
| A1 | One package distributable to many tenants via marketplace | G3, G9, G10 | **VERIFIED** — but only via Agents Toolkit; Agent Builder & Copilot Studio declarative are org-catalog only | Low-code paths excluded from a product |
| A2 | Package can be tenant-agnostic (no per-customer build) | G3, G8 | **VERIFIED** — omitting `items_by_url`/`items_by_sharepoint_ids`/`connections` searches the whole tenant | Unscoped default is the productisable design |
| A3 | Copilot enforces the user's existing permissions | **G2 — the entire security proposition** | **VERIFIED** — *"only surfaces organizational data to which individual users have at least view permissions"*; *"Semantic Index honors the user identity-based access boundary"* | Permission-aware retrieval is a platform guarantee, not our build |
| A4 | Connector content is also permission-trimmed | G2 | **VERIFIED** — *"Data from Graph connectors can be returned… if the user has permission to access that information"* | External data inherits the same model |
| A5 | Customer data is not used to train models | enterprise sale | **VERIFIED** — *"Prompts, responses, and data accessed through Microsoft Graph aren't used to train foundation LLMs"* | Strong, quotable procurement argument |
| A6 | Enough room for domain methodology in the agent | product substance | **FAIL** — `instructions` capped at **8,000 characters** | Methodology must live in knowledge or actions, not the agent |
| A7 | Manifest can be parameterised per tenant | G3 | **FAIL** — only localization keys `[[key]]`, and unknown properties invalidate the document | No templating; unscoped or per-customer build, nothing between |
| A8 | Action endpoint bindable per tenant | G2 + G7 together | **FAIL** — `spec.url` fixed in package; MCP URL *"MUST be a valid absolute URL"* | **G2 and G7 cannot both pass** — see §4 fork |
| A9 | Credentials configurable per tenant | G2 | **VERIFIED** — `OAuthPluginVault`/`ApiKeyPluginVault` + `reference_id`, explicitly so secrets stay out of the manifest | Per-tenant auth is fine; per-tenant endpoints are not |
| A10 | Human-in-the-loop must be built by us | scope | **FAIL (in our favour)** — native `confirmation` + AdaptiveCard + `isNonConsequential` | Do not build; use the platform |
| A11 | Copilot licence needed by every user | market size | **VERIFIED** — non-WebSearch capabilities need a Copilot licence or metered usage | Market limited to Copilot-licensed orgs |
| A12 | EU data stays in the EU | EU B2B sale | **VERIFIED WITH EXCEPTION** — Copilot is an EU Data Boundary service, **but** *"Models provided by Anthropic as a subprocessor are currently excluded from the EU Data Boundary"* | Must be disclosed, not glossed. A German or Slovak enterprise will ask |
| A13 | Our agent is inside Microsoft's trust boundary | procurement | **FAIL** — Microsoft tells customers *"check the privacy statement and terms of use of the agent"*; admins see required permissions and data access before enabling | The agent is a **separate** trust boundary and will be scrutinised. Favours Option C (no egress) |
| A14 | The agent can read all tenant content | product value | **FAIL** — *"For content accessed through agents… encryption can exclude programmatic access, thus limiting the agent from accessing the content"* | **Purview-labelled/encrypted documents may be invisible to the agent** — and quality/HR documents are exactly what gets labelled |
| A15 | Agent can write knowledge back into the tenant without a backend | **G6 — the "know-how stays" promise** | **FAIL — STRUCTURAL BLOCKER** | The closed knowledge loop is not buildable today as a distributable, in-tenant product |
| A16 | Captured knowledge needs human validation before publication | avoids "digital landfill" | **DESIGN REQUIREMENT, not a platform question** | Must exist in any version; see below |
| A17 | Custom engine agents are a viable alternative marketplace path | fallback for A15 | **FAIL** — not supported in Outlook, Word, Excel, PowerPoint or Edge; *"Sensitivity labels aren't supported"*; no proactive notifications | Teams/Copilot chat only — loses the Office surface entirely |
| A18 | Public sector is addressable | market size | **FAIL** — in Microsoft 365 Government tenants, publishing via Agents Toolkit and authenticated custom actions are unsupported | Government excluded from the market |

### A15 — the evidence, and why no workaround is proposed

Microsoft's own Known Issues page (updated 2026-07-29), under the heading
**"Power Automate Flows aren't fully supported as actions in declarative
agents"**:

> "Power Automate Flows as actions in declarative agents might not run
> reliably and might not return results."
>
> **Workaround:** "Currently, no workaround for the issue that the flows
> might not return results is available."

Power Automate was the only path that kept writes **inside** the tenant.
The remaining options both fail a requirement:

| Write path | In-tenant | Distributable | Reliable |
|---|---|---|---|
| Power Automate flow | ✅ | ❌ tenant-specific trigger URL | ❌ per Microsoft |
| Our backend | ❌ data leaves | ✅ | ✅ |
| Native agent capability | — | — | **does not exist** — every declarative capability is read-only |

Per the stop rule: this is a **STRUCTURAL BLOCKER**, recorded rather than
engineered around.

### What this does to the product definition

The hoped-for loop — *existing know-how → Copilot finds and uses it →
user solves the task → result is stored → next user benefits* — cannot be
delivered today as one distributable product that keeps data in the
tenant. The last two steps are the ones that break.

**What survives is the first half**, and it is still a product:
intelligent work *with existing* know-how — retrieval, classification,
comparison against similar past cases, drafting to the company's own
standards. Capture becomes a **human-in-the-loop** step: the agent
proposes the record, a person saves it through normal Microsoft 365 means.

That is weaker than the original vision and must be said plainly to any
customer. It is also honest, buildable, and exactly what the website
currently promises.

**A16 is unaffected by this and remains mandatory.** Even in the
human-save version, no AI output may become "company knowledge" without
validation. The lifecycle stays: *proposal → human validation →
classification → approval → publication → reuse*. Without it the product
manufactures a digital landfill with an authoritative tone, which is
worse than no product.

**Two findings here change the sales story, not just the architecture:**

- **A14** is the most under-appreciated risk in this whole document. The
  documents most worth reasoning over — procedures, customer
  requirements, HR material — are the ones an enterprise is most likely
  to have encrypted with sensitivity labels. If programmatic access is
  excluded, the agent cannot see them. This must be tested against a real
  labelled tenant before promising anything.
- **A13** means our own privacy terms become a procurement artifact. An
  agent that provably moves nothing out of the tenant (Option C) clears
  that review trivially. Option A does not.

---


Decision document. **Scope of verification is deliberately narrow and deep
rather than broad and shallow**: the load-bearing questions that decide
product-vs-consultancy were verified against Microsoft's own current
documentation; the rest is explicitly marked UNKNOWN rather than filled
with plausible prose.

Evidence status is marked throughout: **FACT** (Microsoft docs),
**INFERENCE** (reasoning from facts), **UNKNOWN** (needs validation).

Sources read: `microsoft-365/copilot/extensibility/publish` (updated
2026-07-29), `declarative-agent-manifest-1.5` (updated 2026-07-29),
`extensibility/agents-overview`, `copilot/connectors`.

**Caveat, stated up front:** the manifest schema read in detail was 1.5.
Microsoft's own page states *"The latest version of the declarative agent
manifest schema is version 1.8. Use the latest schema version for new
agents."* Findings below may be stale in detail. Re-verify against 1.8
before building.

---

## 1. Distribution — decides G3, G9, G10

**FACT.** Only two build paths can reach the Microsoft Commercial
Marketplace:

| Build path | Marketplace |
|---|---|
| Declarative agent via **Agents Toolkit** | ✅ |
| **Custom engine agent** via Agents Toolkit | ✅ |
| Declarative agent via **Agent Builder** | ❌ org catalog only |
| Declarative agent via **Copilot Studio** | ❌ org catalog only |
| SharePoint agents | ❌ |
| Custom agent via Copilot Studio | ✅ but multi-tenant is **PREVIEW** |
| Copilot connectors | ✅ only if packaged as a Microsoft 365 (Teams) app, by verified publishers |

**Consequence:** if the goal is a distributable product, the low-code
paths are out. It must be built with **Microsoft 365 Agents Toolkit** and
shipped as a Microsoft 365 app package through Partner Center. Copilot
Studio's multi-tenant route is preview and therefore excluded from MVP
per the "no preview in production" rule.

---

## 2. Tenant-agnostic packaging — this reverses an earlier conclusion

An earlier reading suggested knowledge sources are hardcoded per tenant,
which would have meant every customer is a custom build and G3/G8/G9 all
fail. **That was wrong.** The schema says the opposite:

**FACT**, declarative agent manifest 1.5:

> "If you omit both the `items_by_sharepoint_ids` and the `items_by_url`
> properties, the declarative agent can access **all OneDrive and
> SharePoint sources in the organization**."

> [GraphConnectors] "If you omit this property, the declarative agent can
> access **all Copilot connectors in the organization**."

> [TeamsMessages] "Omitting this property allows an unscoped search
> through all of channels, meetings, 1:1 chats, and group chats."

**Consequence.** One package can install into any tenant and immediately
work against whatever that tenant has, without a per-customer build. The
real design decision is therefore not *possible vs impossible* but a
genuine trade-off:

| | Unscoped (omit properties) | Scoped (explicit IDs/URLs) |
|---|---|---|
| Distributable as one package | ✅ | ❌ per-tenant build |
| Retrieval precision | lower — searches everything | higher |
| Setup effort per customer | none | mapping work |

**INFERENCE.** The productisable design is unscoped-by-default, with
precision recovered through *instructions* and *actions* rather than
through hardcoded knowledge scoping.

---

## 3. The real constraint nobody would guess: 8,000 characters

**FACT.** `instructions` is *"Required… 8,000 characters or less."*

That is the entire budget for domain methodology inside a declarative
agent — roughly 1,200–1,500 words. A full 8D methodology, defect
taxonomy, decision rules and output templates do **not** fit.

**Consequence.** Anything beyond a compact instruction set must live in:
- **knowledge** (documents in the customer's own tenant), or
- **actions** (an API plugin calling a service).

This single limit largely determines the architecture. It is also why
"we'll just write a really good prompt" is not a product.

**FACT.** There is **no parameterisation mechanism** in the manifest.
The only variable syntax is localization keys `[[key_name]]`, and only for
localizable strings (name, description, conversation starters) — not for
URLs or IDs. Further: *"Unrecognized or extraneous properties in any JSON
object make the entire document invalid."* Templating the manifest is not
an option.

---

## 4. Actions — where "data stays in the tenant" is decided

**FACT.** `actions` reference an API plugin manifest; the TypeSpec example
declares `@server("https://…")`, i.e. an external HTTP service.

**Consequence.** The moment real process logic moves into actions, it runs
on a server. If that server is ours, customer data leaves the tenant and
the central security selling point is weakened. If it is the customer's,
we are back to per-customer integration work.

**RESOLVED 2026-08-08** against plugin manifest schema 2.4 (docs updated
2026-07-01). The answer splits, and the split is the central design fork.

**FACT — the endpoint URL is fixed in the package.** There is no
per-tenant override:
- OpenAPI runtime: `spec.url` is *"The URL to fetch the OpenAPI
  specification"*, an absolute URL.
- MCP runtime: `spec.url` is *"The URL of the MCP server. **MUST be a
  valid absolute URL**"*.

**FACT — credentials, by contrast, are NOT in the package.** `auth.type`
is one of `None`, `OAuthPluginVault`, `ApiKeyPluginVault`, and:

> "The `reference_id` value is acquired independently when providing the
> necessary authentication configuration values. This mechanism exists to
> **prevent the need for storing secret values in the plugin manifest**."

So per-tenant *credentials* are supported; per-tenant *endpoints* are not.

### The fork this creates

| Option | One package for all? | Customer data leaves tenant? | G7 real automation |
|---|---|---|---|
| **A.** Actions → our multi-tenant backend | ✅ | ⚠️ yes, to us | ✅ |
| **B.** Actions → customer's own endpoint | ❌ per-customer build | ✅ no | ✅ |
| **C.** No actions at all — knowledge + instructions only | ✅ | ✅ no | ❌ retrieval + drafting only |

A and B are mutually exclusive with the two things we have been selling
simultaneously ("one product" and "your data never leaves"). **C is the
only option where both hold**, and it is also the only one needing no
backend at all.

### Two platform primitives we do not have to build

**FACT.** Human-in-the-loop is native: `confirmation` renders an
AdaptiveCard before a function runs, and `isNonConsequential` governs
whether "Always Allow" is offered. Section 27 of the brief (HITL design)
is largely a platform feature, not our work.

**FACT.** `security_info.data_handling` is a **required** declaration per
function, from `GetPublicData`, `GetPrivateData`, `DataTransform`,
`DataExport`, `ResourceStateUpdate`. Data-egress behaviour is declared and
surfaced for risk assessment by the platform itself.

**FACT.** `RemoteMCPServer` is a supported runtime type in schema 2.4, so
MCP is a first-class integration path — but bound by the same fixed-URL
constraint above.

---

## 5. Licensing dependency

**FACT.** *"Users can access declarative agents with any capabilities
other than Web search only if their tenants allow metered usage or if
they have a Microsoft 365 Copilot license."*

**Consequence.** Every user needs a Copilot licence or metered usage.
Acceptable — the target customer already has Copilot — but it is a hard
dependency and shrinks the market to Copilot-licensed organisations.

---

## 6. Gate results on evidence

| Gate | Result | Basis |
|---|---|---|
| G1 Technical feasibility | ✅ PASS | Agents Toolkit path is GA and documented |
| G2 Data security | ✅ PASS **in Option C** | knowledge stays in tenant; ❌ FAILS in Option A (data flows to our backend) |
| G3 Distribution | ✅ PASS | marketplace via Agents Toolkit; unscoped manifest installs anywhere |
| G4 Tenant isolation | ✅ PASS | agent runs in tenant, retrieval is permission-trimmed |
| G5 More than plain Copilot | ⚠️ UNPROVEN | plausible via instructions+actions, but 8k limit is severe; no evidence yet |
| G6 Knowledge value | ❓ UNKNOWN | knowledge capture back into tenant not yet verified |
| G7 Real automation | ❌ FAIL **in Option C** | no actions = retrieval + drafting only. Passes only in A or B, each of which breaks a different promise |
| G8 Core vs config | ✅ PASS | unscoped package = core; scoping/actions = config |
| G9 Economics | ⚠️ LIKELY PASS | marginal cost low *if* unscoped default is good enough |
| G10 Microsoft dependency | ❌ HIGH RISK | see §7 |

---

## 7. Microsoft dependency — the honest risk

Microsoft already ships a **Factory Operations Agent** in Copilot Studio
and AppSource already carries 8D/CAPA solutions. Microsoft controls the
schema, the limits, the distribution channel and the store. It has both
the motive and the position to absorb any generic version of this.

**INFERENCE.** What Microsoft is unlikely to ship per-vertical is the
*domain content*: defect taxonomies, process templates, validation rules,
evaluation sets for a specific industry. The defensible layer is domain
packs and deployment methodology — not the agent.

**But note the RL-3 tension applies again:** that domain content is
largely public (extrusion defect taxonomies are published by the Aluminum
Extruders Council). The moat is therefore execution and relationships,
not proprietary knowledge. That is a legitimate business, but it is a
consultancy-with-a-product, not a software moat.

---

## 7b. Architecture principle (adopted 2026-08-08)

> **Copilot generates and prepares. The human decides. Microsoft 365 stores.**

    Microsoft 365 Copilot → our domain agent → company know-how
      → structured result → human validation → SharePoint / Teams / existing M365 process

We own no customer data, run no AI infrastructure for the customer, and
need no backend for sensitive content. A15's failure is accepted rather
than engineered around; the automatic write layer is revisited only if a
real customer says the human-save step is insufficient.

**Ollama and any customer-hosted runtime are explicitly out of scope.**
Not because they are bad, but because they solve inference while the
blocker is the write path, and because a customer-hosted component
reintroduces per-customer endpoints, per-customer networking and
per-customer infrastructure — forfeiting the existing licence, the
existing security approval, marketplace distribution and zero-infra
economics that made this idea worth pursuing at all.

### The product boundary

| Layer | Contents |
|---|---|
| **CORE PLATFORM** | agent framework, process templates, knowledge governance, workflow patterns, validation, instruction architecture, evaluation, onboarding methodology |
| **DOMAIN PACKS** | Quality, HR, Maintenance, Production, Purchasing, Sales, Engineering, Finance |
| **CUSTOMER CONFIGURATION** | SharePoint sites, documents, permissions, terminology, org structure, specific workflows |

### Three consequences of today's findings that constrain this design

**1. A "department agent" will not fit. Agents must be per-process.**
`instructions` is capped at 8,000 characters (A6). A single Quality Agent
covering complaints, 8D, CAPA, FMEA, work procedures and lessons learned
has roughly 1,300 words for all six. It does not fit.

**Consequence:** a Domain Pack is **a set of narrow per-process agents**,
not one departmental agent. That is better anyway — narrower agents are
more accurate, easier to evaluate, and can be sold and adopted one at a
time — but it must be designed that way from the start, not discovered
later.

**2. The ROI claim requires a measured baseline, or it is a fabricated
number.** "This takes 47 minutes today, 12 with the agent" is exactly the
right sales argument *and* exactly the kind of figure this project's
rules forbid unless measured. The 47 must be timed at that customer,
before deployment. That is precisely what the paid assessment is for —
the entry product and the evidence-gathering step are the same activity.
Never publish a time saving measured at one customer as a general claim.

**3. UNKNOWN — packaging of multiple agents.** Whether one Microsoft 365
app package can carry several declarative agents, or whether each needs
its own marketplace listing, is not yet verified. It determines pricing
granularity (per pack vs per agent) and the admin's install burden.
Verify before designing the commercial model.

---

## 7c. Validation plan (adopted 2026-08-08) — G5 becomes an experiment

Product unit is no longer "an AI platform". It is:

> **1 process → 1 narrow agent → 1 concrete user problem → 1 measurable result**

First candidate: an **8D Agent**, not a "Quality Agent" — 8D has a
defined structure, so the output is checkable against a standard (which
is also why it suits the rubric below).

### Four steps, in order

1. **Choose one process** — by frequency, administrative burden,
   availability of company know-how, measurability, **and a checkable
   output**. Not by technical interest.
2. **Measure the baseline** — how the same task is done today, timed, at
   the customer.
3. **Build the minimal agent** — no backend, no Ollama, no database, no
   platform. Native Microsoft 365 / Copilot stack only.
4. **Run A/B** — vanilla Copilot vs our process agent.

**Stop rule:** if the agent shows no measurable advantage, it is not
rescued with more features. That would be a return to the behaviour this
project spent the day correcting.

### Three design corrections the A/B test needs

As sketched, the test would produce a result we could not trust. Three
confounds must be handled *before* running it, not explained afterwards:

**1. The same person doing the same task twice will be faster the second
time**, whatever the tool. That is a learning effect, not a product
effect. Fix: either **between-subjects** (different, experience-matched
people in A and B), or **counterbalanced order using different but
equivalent cases**. Deciding this after seeing results invalidates them.

**2. Whoever scores the output must not know which condition produced
it.** If we grade our own agent's work, the rubric measures our
expectations. Fix: a domain expert scores anonymised outputs, with the
rubric written and agreed **before** any output exists.

**3. With 5–10 participants there will be no statistical significance,
and pretending otherwise would repeat RL-1's mistake.** Fix: pre-register
a **decision** threshold rather than a p-value. For example: *the agent
must win on time in at least 7 of 10 matched pairs, and score no worse on
the quality rubric.* Written down before the first run.

### Claim discipline (binding)

| Stage | Permitted wording |
|---|---|
| Before any pilot | "We propose to measure whether the agent reduces time and administrative effort on this specific process." |
| After a pilot | "At customer X, on process Y, we measured …" |
| **Never** | "Our solution saves companies 40% of their time." |

A saving measured at one customer is not a general claim until the sample
and method support one.

### The honest dependency

Steps 1, 2 and 4 all require **a real organisation** with Copilot
licences, real cases and willing participants. Only step 3 can be done
alone. This is the same blocker as B10, and the same
conflict-of-interest boundary applies: the employer's own materials and
cases are not an input, and a direct competitor is not a safe venue.

**Packaging note.** Whether one package can carry several agents is a
cheap technical question that should be settled before pricing — but it
is not a reason to delay the first prototype. One agent for one process
is the right first build regardless of how distribution later shakes out.

---

## 8. Verdict

**PIVOT — not BUILD, not KILL.**

The mechanism works: a distributable, tenant-agnostic Copilot agent is
genuinely buildable today via Agents Toolkit, and that was the main
technical doubt. It is resolved in our favour.

**But BUILD is not yet justified**, for one reason that has nothing to do
with Microsoft: **there is still zero customer evidence.** Every gate that
failed or came out conditional above (G5, G6, G7) is about whether the
thing is worth more than plain Copilot — and that cannot be settled by
reading documentation.

### First experiment — before any development

Not a platform. Not an MVP. **One declarative agent, unscoped, built with
Agents Toolkit, for one process**, shown to real people under the B10
protocol in `RESEARCH_LOG.md`.

Its only job is to answer G5 with evidence: *does a structured agent
visibly beat what the same person gets from plain Copilot on the same
task?* If it does not, no architecture rescues it.

### What must NOT be built yet

Multi-agent orchestration, a process engine, a knowledge governance
lifecycle, domain packs, tenant management, billing, an evaluation
framework. Every one of those is justified only after G5 is proven, and
each would be a month of work spent before knowing whether anyone wants it.

### The strategic consequence of the fork

G2 and G7 **cannot both pass in one product**. That is not a gap in the
design, it is a property of the platform:

- Sell "your data never leaves your tenant" → no backend → **no real
  automation**, only retrieval and drafting.
- Sell real automation → a backend → **data leaves**, and the security
  argument that made the offer sellable weakens.

The website currently promises Option C ("we work inside your Microsoft
365, your data does not leave"). That is honest and buildable. It is also
strictly less than "AI does the work" — and the copy correctly does not
claim otherwise.

**This is the question to put to customers, not to resolve at a desk:**
is retrieval + guided drafting, with no data leaving the tenant, worth
paying for on its own? If yes, Option C is a real product with excellent
economics and no backend. If customers only value it once it *acts*, the
security proposition has a price, and that price must be quantified
before any backend is written.

### Remaining open questions

1. Can the agent write knowledge back into the tenant (SharePoint list,
   Dataverse) without a backend? Decides G6 and whether Option C can
   deliver know-how retention at all.
2. Does schema 1.8 change any of the above? (1.5/2.4 were read; 1.8 is
   current.)
3. Does Partner Center certification impose requirements that push toward
   a backend regardless?

---

## 9. RE-VERIFICATION 2026-08-09 — schema 1.8 invalidates part of this document

The register above was built against **declarative agent schema 1.5**. Versions
1.6–1.8 added primitives that bear directly on the broadened brief
(organisation-wide layer, domain packs, workflow, automation). Re-verified
against Microsoft Learn on **2026-08-09**.

| ID | Fact | Status | Source | Architectural consequence |
|----|------|--------|--------|---------------------------|
| N1 | `worker_agents` — a declarative agent can call other declarative agents; Copilot Chat brokers; the user does not pick the sub-agent | **PREVIEW** (1.8 reference says "This capability is in preview"; added in schema 1.6) | [declarative-agent-connected-agent](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/declarative-agent-connected-agent) | This is the mechanism "domain packs" needs. Preview → per §2 of the brief it may not be an MVP foundation. |
| N2 | **"Users must install each connected agent before they can use them."** | **VERIFIED** | same | **Kills "one install, many domains."** A 7-domain product is 7 installs per user, not one. Straight into deployment economics (§19). |
| N3 | Agent-to-agent communication is **text only**; no files, no images | **VERIFIED** | same | A worker agent cannot hand back a structured record. Orchestration is prompt-passing, not a workflow bus. |
| N4 | Adaptive cards from a connected agent are **not shown to the user**; the calling agent receives only the card's data | **VERIFIED** | same | **Human-in-the-loop breaks through delegation.** Approval UX must live in the agent the user is actually talking to. |
| N5 | Declarative agents can connect **only to other declarative agents** | **VERIFIED** | same | Copilot Studio / custom engine agents are not composable this way. |
| N6 | `EmbeddedKnowledge` — knowledge files shipped **inside the app package** (max 10 files, 1 MB each; docx/pptx/xlsx/txt/pdf) | **DOCUMENTED BUT NOT ENABLED** — the 1.8 `sensitivity_label` note states "Embedded Files are not enabled yet" | [declarative-agent-manifest-1.8](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/declarative-agent-manifest-1.8) | If enabled, the CORE product ships its own methodology with **zero customer configuration** — the single biggest productisation unlock available. Track this. Do not build on it yet. |
| N7 | `EmailActions` — native **write** operations: triage, supervised send, delete, inbox rules, auto-reply, folder management | **VERIFIED** (1.8) | same | **Partially reverses A15/G7.** Real actions with **no backend** — so "data stays in the tenant" and "it acts" are no longer strictly exclusive, within email/calendar. |
| N8 | `MeetingActions` — scheduling, time-finding polls, time insights | **VERIFIED** (1.8) | same | Same as N7 for calendar. |
| N9 | `editorial_answers` — up to 300 curated Q&A pairs matched by semantic similarity with tunable thresholds | **VERIFIED** (1.8) | same | A governance/accuracy primitive we would otherwise have built. USE MICROSOFT. |
| N10 | `default_response_mode` — `Auto` / `Quick response` / `Think deeper`, set in the manifest | **VERIFIED** (1.8) | same | Directly addresses the field report that the agent is "reliable only when GPT-5.6 is selected": reasoning mode is declarable, not left to the user. |
| N11 | `instructions` still capped at **8,000 characters** in 1.8 | **VERIFIED** | same | The constraint that defines the CORE/CONFIG split is unchanged. |
| N12 | `actions` array now holds **1–10** plugin objects, and a plugin manifest may be **inlined** in the agent manifest | **VERIFIED** (1.8) | same | Fewer files to distribute; action count is bounded. |

### What this does to earlier conclusions

- **A15 / G7 are no longer a clean FAIL.** They are FAIL *for arbitrary write-back
  to SharePoint/Dataverse*, but **PASS for email and calendar actions** natively.
  The honest statement is now: *the agent can act where Microsoft has shipped an
  action capability, and nowhere else.*
- **"One package, many domains" is refuted (N2).** Domain packs are separately
  installed agents. Deployment economics must be recomputed per domain, not per
  customer.
- **N4 is the most under-appreciated new risk.** A product whose whole safety
  story is "human approves before anything happens" cannot route approvals
  through a worker agent — the user never sees the card.
- **N6 is the one to watch.** If embedded knowledge ships, the customer-
  configuration burden for the CORE product drops to near zero and G4/G9/G10
  改善 materially. It is not available today.

### Still UNKNOWN after this pass

1. Whether one app package may declare **multiple** declarative agents (distinct
   from N2, which is about *installing* connected agents).
2. Whether `worker_agents` works across **publishers/tenants** or only within
   agents the same user installed.
3. Marketplace/Partner Center certification requirements for an agent that
   declares `EmailActions` (write scope is likely to raise review bar).
4. Cross-tenant usage telemetry for §23 observability without data egress.
