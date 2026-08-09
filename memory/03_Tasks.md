# Active tasks

## IN PROGRESS
- Measuring whether the SK pricing/free-kit strategy converts (review 2026-09-29, D13/D14).
- Machinery Regulation tool: buyer-side demand unverified — watching for organic traffic/enquiries.

## BLOCKED (user action, not re-raised every session — see docs/TASKBOARD.md Human Action Batch)
- Gumroad payout: identity verification failed (does not block sales, only payout).

## TODO (next highest-EBV, unblocked)
- **Step 3 DONE 2026-08-08 — first narrow agent built.** 8D/diagnostics declarative agent (Option C: knowledge + instructions, no backend, no actions) in `~/Desktop/8D-Agent`. Built from a defect/cause table the owner and Claude produced together in this project days earlier — **it is our own artefact, not Constellium material**, so it carries no IP or conflict-of-interest constraint (an earlier note claiming otherwise was wrong). Design proof: procedure in `instructions` (4,213 of 8,000 chars), 34 decision trees in `knowledge` (19 kB — could never fit instructions). Confirms A6 splits the product cleanly into CORE PLATFORM (procedure) vs CUSTOMER CONFIGURATION (knowledge docs).
- **FIRST FIELD VALIDATION 2026-08-08 — the agent works.** Owner ran it in their own Copilot at Constellium. Licence-free path: no knowledge grounding available (A11 confirmed — Agent Builder offers only "Add specific URL" without a Copilot licence), so the catalogue is hand-attached to each conversation and the instructions were rewritten to detect an attachment and quote it verbatim. **Caveat the owner reported unprompted: reliable only when GPT-5.6 is selected.** That is a property of the instructions, not the model — a distributable product cannot dictate which model a customer's tenant serves. Next: harden instructions so they hold on a weaker model (this is what the local Ollama test was for; the field gave the signal cheaper).
- **STILL BLOCKED ON USER — steps 1/2/4 need a real company with Copilot.** Measure baseline → A/B vs vanilla Copilot. Pre-registered metrics: steps-to-confirmed-cause, and count of *unnecessary expensive tests ordered* (the latter converts to €). Verify A14 (Purview-encrypted quality docs may be invisible to the agent) on one document before building any process on it. **Claim rule: no "saves X%" before a pilot, ever.**
- **BLOCKED ON USER — B10 customer interviews (5–10).** Working concept: AI Operational Knowledge System (Copilot as our stack, not competitor; Quality/8D as first workflow). Protocol, pre-registered pass criteria and thresholds in `docs/RESEARCH_LOG.md`. Claude cannot do this step. Nothing else in this direction should be built until it returns evidence.
- Data-moat flagship search is CLOSED (RL-3, negative). Do not reopen by relaxing Q0.
- No new verified opportunity in hand (iteration 66 fan-out found none worth building). Don't force one — watch existing assets (Machinery Reg tool, the 5 SK articles) for real signal before the next fan-out. NB: 5 articles ≠ full service coverage — "Digitálny produkt na mieru" (290 €) has no article **on purpose** (iteration 66 SERP-rejected custom-tool pricing as incumbent-held). Don't "close" that gap without re-checking the SERP first.
- Sitemap "Couldn't fetch" persisted through a 2nd submission (2026-08-02, 24h after resubmit). Every documented cause ruled out (iteration 69); Page Indexing still "Processing data". Nothing further to do — stop re-checking until GSC has real data.
- Watch Search Console for first real *organic* impression/click data — first data point appeared (iteration 68) but was a manual `site:` check, still not real signal. Sitemap "Couldn't fetch" is confirmed NOT a site defect (iteration 69 ruled out every documented cause) — no more action to take there, just wait.
- External directory listing (DatabázaFiriem.com) researched and offered — user declined 2026-08-01, don't re-raise.

## DONE (one-line, chronological — full detail in docs/TASKBOARD.md)
- 46 iterations: pipeline, SEO, 5 monetized products, redesign, blog, Signals news bot, free tools, SK market entry, mechanism (build/deploy/hooks/skills), global opportunity research.
- Iteration 65: closed last SK content gap (design/branding) — SERP-verified, shipped, live-verified.
- Iteration 66: 12-candidate opportunity fan-out, all honestly rejected with primary-source evidence — no new build this round.
- Iteration 67: applied graph/fan-out engineering pattern to market_research_agent (parallel API fetchers), lint pass on operating memory.
- Iteration 68: found+fixed all 5 SK article CTAs linking to bare index.html instead of #kontakt/#cennik.
