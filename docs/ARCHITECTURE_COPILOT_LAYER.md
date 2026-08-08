# AI Workforce Layer for Microsoft 365 Copilot — architecture findings

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

**UNKNOWN — requires technical validation.** Whether an API plugin's
server URL can be bound per tenant at install time, or whether it is
fixed in the package. This decides whether "our backend" and "data stays
in tenant" can both be true. **This is now the single most important open
question.**

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
| G2 Data security | ⚠️ CONDITIONAL | holds for knowledge (stays in tenant); undecided for actions (§4) |
| G3 Distribution | ✅ PASS | marketplace via Agents Toolkit; unscoped manifest installs anywhere |
| G4 Tenant isolation | ✅ PASS | agent runs in tenant, retrieval is permission-trimmed |
| G5 More than plain Copilot | ⚠️ UNPROVEN | plausible via instructions+actions, but 8k limit is severe; no evidence yet |
| G6 Knowledge value | ❓ UNKNOWN | knowledge capture back into tenant not yet verified |
| G7 Real automation | ⚠️ DEPENDS ON §4 | without actions it is retrieval + drafting only |
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

### Open questions blocking a full design

1. Can an API plugin's server URL be bound per tenant? (§4 — decides G2/G7)
2. Can the agent write knowledge back into the tenant? (decides G6)
3. Does schema 1.8 change any of the above?
