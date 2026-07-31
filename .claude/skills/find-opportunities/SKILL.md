---
name: find-opportunities
description: Check whether search queries are realistically winnable before writing content for them. Use before creating any SEO-targeted page.
---
Assess real search demand and, more importantly, whether we could actually
rank. The pipeline's own demand scoring measures *interest* and calls it
opportunity — it has no idea who already owns the page.

For each candidate query in $ARGUMENTS (or propose 5-10 yourself):

1. Fetch the live SERP and read who actually ranks:
   `https://www.google.com/search?q=<url-encoded query>&num=15`

2. Classify the first page:
   - **Not winnable** — an established brand or funded SaaS holds it
     (Harvest, Asana, HubSpot and similar). A new domain with no backlinks
     does not displace these. Skip.
   - **Winnable** — Reddit threads, small blogs, personal sites, or content
     that misses the angle. Google flagging "Chýba: X" / "Missing: X" on a
     top result is a strong signal the query is underserved.
   - **Commercial proof** — paid ads on the query mean somebody is already
     buying these customers. Demand is proven, not assumed.

3. Record what the "People also ask" box lists. Those are the exact
   questions to use as section headings.

4. Report a short table: query, verdict, who holds it, and why.

Two patterns already established for this project, worth re-testing rather
than assuming:
- English *tool/calculator* queries are saturated; *conversational* ones
  ("what do I say when…") are not, and are what a script catalogue answers.
- Slovak SERPs for the same services are contested only by small local
  agencies — far weaker competition, and the market we can actually serve.

Only write content for queries that pass. Do not write for a query because
it sounds relevant.
