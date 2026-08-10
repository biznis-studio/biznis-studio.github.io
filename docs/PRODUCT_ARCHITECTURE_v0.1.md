# Product Architecture v0.1 — AI-assisted complaint investigation

> ## ⛔ STATUS: REJECTED FOR IMPLEMENTATION — 2026-08-10
>
> Owner's audit against current Microsoft documentation. Verdict accepted.
>
> **The load-bearing decision C-3 was wrong as stated.** "Agent knowledge =
> files, not list items" is false as a claim about the Microsoft agent platform:
> Copilot Studio documents SharePoint Lists as a knowledge source (that page is
> marked **preview**). It is narrowly true only for the **declarative agent**,
> whose knowledge-source list does not include SharePoint Lists and whose
> SharePoint capability searches *"files, folders, or sites"*. **Two runtimes
> were conflated.**
>
> **C-2 was too absolute.** "The agent cannot write" describes *our* configuration,
> which ships no `actions`. Manifest 1.8 supports API plugins, and Microsoft
> documents agents performing real-time operations through them. An implementation
> choice was presented as a platform limit.
>
> **F3 "blocks closure" is not achievable as written.** A flow reacts to a change;
> it cannot refuse one. Correct formulation: *validates closure conditions and
> prevents a case from remaining in an invalid closed state* — by revert,
> approval gate, column validation, or permissions. Which of those, a PoC decides.
>
> **C-6 stands technically but is not accepted architecturally.** Unscoped means
> the whole organisation's SharePoint and OneDrive. Least privilege argues for a
> dedicated site.
>
> **§6 "Copilot cannot be [2],[3a],[4],[5]" is overbroad** and follows from C-2.
>
> ### The finding that supersedes the argument, verified 2026-08-10
>
> The declarative-agent knowledge documentation states that for **structured,
> frequently changing content** the correct mechanism is an **API plugin backed
> by an OpenAPI specification**, which *"allows the agent to query the underlying
> data source directly"* — explicitly instead of relying on indexed content.
>
> A case register is exactly that. So the storage question is not
> *file vs list*; it is **knowledge vs action**, and Microsoft's own guidance
> answers it: **action**.
>
> This removes component **[3b]** entirely and removes the reason for
> "case = document". It also re-binds the old constraint **A8**: an API plugin's
> `spec.url` is fixed in the package, so a plugin pointing at each customer's own
> SharePoint **cannot be distributed** — it is viable only in a per-tenant
> deployment.
>
> **Nothing below is to be implemented.** The runtime decision comes first:
> Microsoft 365 declarative agent (Agents Toolkit) vs Copilot Studio agent. Their
> knowledge, action and workflow capabilities differ, and v0.1 was drawn around
> the limits of one of them without having chosen it.
> Superseded by `PRODUCT_ARCHITECTURE_v0.2.md` once that decision is made.

---

**Status:** first technical architecture. Every component names its technology,
its owner, where its data sits, and how it talks to the others. Where a human is
required because the platform provides no path, that is drawn as a component, not
hidden.

**Scope:** one use case. Not a QMS.

**All platform facts referenced here were verified 2026-08-09/10 and are recorded
in `ENTERPRISE_COPILOT_PRODUCT_ARCHITECTURE.md` §4, §22, §29.**

---

## 0. The question this document must answer

> What exactly do we deliver beyond the customer's existing Copilot, and why can
> Copilot not do it alone?

**Answer, stated up front and defended by §6:**

| We deliver | Copilot cannot, because |
|---|---|
| A **case model** — identity, state, evidence, decisions, history | The agent has no storage. It prints text and forgets. |
| A **discriminating knowledge model** — not a list of causes but what separates each from the one that looks the same | Copilot answers from probability. Nothing in it holds "how to tell these apart". |
| **Governance** — a case cannot close without a confirmed cause and a list of what was excluded | The agent cannot enforce anything. It has no write path and no ability to block. |
| **Time** — deadlines, reminders, effectiveness checks at +90 days | Manifest 1.8 has no trigger, no schedule, no event. The agent never acts first. |
| **Knowledge evolution** — each closed case can add a cause with its discriminator, under approval | A15 = FAIL. The agent cannot write to any store. |

**The reasoning is the small part. The spine is state, time and governance.**

---

## 1. Constraints that shaped every decision below

| # | Constraint | Consequence in this architecture |
|---|---|---|
| C-1 | Agent has **no trigger/schedule/event** (DA-1.8 schema) | Nothing is ever started by the agent. Flows start things; the agent is opened by a human. |
| C-2 | Agent **cannot write** except mail/calendar (A15 FAIL, A16) | Every persisted fact is written by a flow or a person. |
| C-3 | Agent knowledge = **files, not list items** (F2) | **The case is a document in a library, not a row in a list.** This is the single most load-bearing decision here. |
| C-4 | Power Automate **as an agent action** is unreliable, no workaround (F1) | Flows are never invoked by the agent. They trigger on item/file change. |
| C-5 | `instructions` ≤ **8,000 chars** (A3) | Procedure in the manifest; catalogue in knowledge files. |
| C-6 | Unscoped knowledge is the **prescribed** multi-tenant pattern (A4) | No per-customer site enumeration. Cuts onboarding. |
| C-7 | Non-WebSearch capabilities need a **Copilot licence** (B8) | Prerequisite, not a feature. Silent failure if absent (F3). |
| C-8 | Purview-encrypted files may be **invisible** (B4) | Mandatory probe at deployment. |

---

## 2. Component map

```
                        CUSTOMER TENANT
  ┌───────────────────────────────────────────────────────────┐
  │                                                           │
  │   [1] Microsoft 365 Copilot + declarative agent           │
  │       reads ──────────────┐        ▲ opened by human      │
  │       prints text ────────┼────────┘                      │
  │                           │                               │
  │                           ▼ (files only, C-3)             │
  │   ┌────────────────────────────────────────────────┐      │
  │   │ [2] "Pripady" — SharePoint DOCUMENT LIBRARY    │      │
  │   │     file  : case dossier (.md)  ← agent reads  │      │
  │   │     columns: stav, vlastnik, terminy, pricina  │      │
  │   └───────────────┬────────────────────────────────┘      │
  │                   │ change triggers                        │
  │                   ▼                                        │
  │   ┌────────────────────────────────────────────────┐      │
  │   │ [4] Power Automate — lifecycle, sync, approval │      │
  │   └───────┬───────────────────────┬────────────────┘      │
  │           │ regenerates            │ writes                │
  │           ▼                        ▼                        │
  │   ┌──────────────────┐   ┌──────────────────────────┐     │
  │   │ [3a] Katalog     │   │ [3b] katalog.docx        │     │
  │   │  LIST (govern.)  │──▶│  generated ← agent reads │     │
  │   └──────────────────┘   └──────────────────────────┘     │
  │                                                           │
  │   [5] Human — the only writer of judgement                │
  └───────────────────────────────────────────────────────────┘
```

---

## 3. Components in detail

### [1] Declarative agent — the reasoning component

| | |
|---|---|
| **What it is** | Copilot agent carrying the investigation procedure |
| **Technology** | Declarative agent, manifest 1.8, `OneDriveAndSharePoint` unscoped (C-6), `default_response_mode: Think deeper`, `editorial_answers`, **no `actions`** |
| **Owner** | **Us** — this is IP |
| **Data** | Holds none. Reads tenant files under the signed-in user's permissions (B1) |
| **Interfaces** | Reads [2] and [3b]. Output is text in chat. **Writes nothing** (C-2) |
| **Standard vs IP** | Runtime is Microsoft; the procedure, discriminator method, refusal rules and output contract are ours |
| **Customer config** | None if unscoped. Licence required (C-7) |
| **Auto-deployable** | **Yes** — app package upload |

### [2] `Pripady` — case library

| | |
|---|---|
| **What it is** | One SharePoint **document library**. Each case = one dossier file + metadata columns |
| **Why a library and not a list** | C-3: the agent reads files, not list items. A library gives both — the file the agent reads, and the columns the flows and views need. **A plain list would be invisible to the agent.** |
| **Technology** | SharePoint Online document library |
| **Owner** | **Customer** |
| **Data** | Customer tenant, customer-owned |
| **Interfaces** | Read by [1]; written by [4] and by people; changes trigger [4] |
| **Dossier file** | Markdown, sections fixed: *Popis · Pozorovania · Vylúčené príčiny a čím · Potvrdená príčina a dôkaz · Opatrenie · Overenie účinnosti · Otvorené body* |
| **Columns** | `Stav` (D0…D8, Overenie, Uzavrete) · `Zakaznik` · `Kategoria` · `Vlastnik` · `TerminPricina` · `TerminFormular` · `TerminUcinnosti` · `PotvrdenaPricina` (lookup → [3a]) · `NovaZnalost` (Y/N) |
| **Standard vs IP** | Library is standard; **the dossier structure and the column model are ours** |
| **Customer config** | Owners, deadline offsets, their category list if it differs |
| **Auto-deployable** | **Yes** — provisioning template |

### [3a] `KatalogPricin` — knowledge, governed

| | |
|---|---|
| **What it is** | SharePoint list, one item per cause. 121 at delivery |
| **Technology** | SharePoint list |
| **Owner** | **Content is ours at delivery; everything added later is the customer's** |
| **Data** | Customer tenant |
| **Interfaces** | Written by [4] on approval; source for [3b] |
| **Key columns** | `Rozlisenie` (**the discriminator — the core IP**) · `Mechanizmus` · `Prevencia` · `Detekcia` · `Stav` (Schvalene/Navrhnute/Zamietnute) · `ZdrojPripad` (lookup → [2]) |
| **Standard vs IP** | List is standard; **the 121 causes and their discriminators are our IP** |
| **Customer config** | Their own terminology; their additions |
| **Auto-deployable** | **Yes** — template + CSV import |

### [3b] `katalog.docx` — the agent-readable projection

| | |
|---|---|
| **What it is** | A document regenerated from [3a] whenever a cause is approved |
| **Why it exists** | C-3 again. The agent cannot read [3a]. Without this projection the catalogue is invisible to it. |
| **Technology** | File in the library, written by [4] |
| **Owner** | Derived — no separate ownership |
| **Interfaces** | Written by [4]; read by [1] |
| **Auto-deployable** | **Yes** |

### [4] Power Automate — lifecycle, sync, approvals

| | |
|---|---|
| **Technology** | Power Automate flows in the customer tenant |
| **Owner** | **Us** as templates; **customer** as running instances |
| **Interfaces** | Triggers on library/list change and on schedule. **Never called by the agent** (C-4) |
| **Auto-deployable** | **Yes** — solution import |

| Flow | Trigger | Does |
|---|---|---|
| **F1 Založenie** | new file in [2] | sets deadlines and `Stav`=D0; finds prior cases by `Kategoria`/`Zakaznik` and writes them into the dossier; sends the owner a link |
| **F2 Termíny** | daily 07:00 | reminders before deadline, escalation after |
| **F3 Uzavretie** | `Stav` → D8 | **blocks closure** if `PotvrdenaPricina` empty or *Vylúčené príčiny* section empty; else sets `TerminUcinnosti` = +90 d |
| **F4 Znalosť** | `NovaZnalost` = Yes | creates item in [3a] as `Navrhnute`, routes approval to QM; on approve → `Schvalene` **and regenerates [3b]** |
| **F5 Prehľad** | Monday 07:00 | open cases, overdue, awaiting effectiveness |

**F3 and F4 are the product.** F3 makes the evidence rule structural instead of
a matter of discipline. F4 is the only mechanism by which the catalogue grows.

### [5] The human — drawn because the platform requires it

| Step | Why a human, not automation |
|---|---|
| Opens the agent | C-1 — the agent has no trigger |
| Pastes the agent's conclusions into the dossier | C-2 — the agent cannot write |
| Confirms the cause | P3, and D1 for anything consequential |
| Approves a new cause into the catalogue | A16 — no AI output becomes company knowledge unapproved |

**This is the honest seam.** Two of these four exist only because of platform
limits and would be automated the day Microsoft ships a write path. Two are
deliberate and would remain.

---

## 4. MVP — the cycle, with the seams marked

```
person creates case file                      → [2]
  F1 sets deadlines, finds prior cases        → [4] automatic
person opens agent, describes what they see   → [1] MANUAL (C-1)
  agent asks cheapest discriminator first     → [1] automatic
  agent excludes causes, names the evidence   → [1] automatic
person pastes result into dossier             → [2] MANUAL (C-2)
person confirms cause                         → [2] MANUAL by design
  F3 blocks closure if evidence missing       → [4] automatic
  F3 schedules effectiveness at +90 days      → [4] automatic
person marks NovaZnalost if a cause was new   → MANUAL by design
  F4 routes approval, updates catalogue,
     regenerates the agent's knowledge file    → [4] automatic
```

**Out of scope for MVP:** ERP/CRM integration, Power Apps UI, connectors, mobile,
multi-domain, federation, any hosted component of ours.

---

## 5. Ownership, deployment, and what must be configured

| Layer | Ours | Customer's | Auto-deployable |
|---|---|---|---|
| Agent manifest + instructions | ✅ IP | — | ✅ |
| Dossier structure + column model | ✅ IP | — | ✅ |
| 121 causes + discriminators | ✅ IP | additions become theirs | ✅ CSV |
| Flow templates F1–F5 | ✅ IP | running instances | ✅ solution |
| Library, list, permissions | — | ✅ | ✅ template |
| Owners, approvers, deadline offsets | — | ✅ | ⚠️ wizard |
| **Their terminology and categories** | — | ✅ | ❌ **this is where the days go** |
| Their documents | — | ✅ | ✅ unscoped (C-6) |

---

## 6. Why Copilot alone cannot do this — component by component

| Component | Could plain Copilot replace it? |
|---|---|
| [1] reasoning | **Partly.** Tested 2026-08-09: plain Copilot named a cause and prescribed a fix with no evidence; with our procedure it refused and asked for the discriminator. Better instructions, honestly labelled. |
| [2] case state | **No.** No storage. |
| [3a] governed catalogue | **No.** No store, no approval, no version. |
| [4] time and enforcement | **No.** No trigger, no schedule, no ability to block (C-1). |
| [5] knowledge growth | **No.** No write path (C-2). |

**The differentiation is not the AI. It is that four of five components are
things Copilot structurally cannot be.** Which also means the competitive set is
case-management and QMS products, not Copilot consultancies — and that comparison
has not yet been made.

---

## 7. What v0.1 does not answer

1. **F2 is PARTIALLY VERIFIED.** That the agent cannot read list items comes from
   a Microsoft Q&A page, not a reference page. **The whole library-instead-of-list
   decision rests on it.** Re-verify before building.
2. Whether a flow can reliably regenerate [3b] in a format the agent indexes
   quickly enough to matter.
3. How long the agent takes to see a newly written file (indexing latency).
4. Deployment hours — unmeasured, and it decides whether this is a product.
5. Whether a customer pays for it. Unasked.
