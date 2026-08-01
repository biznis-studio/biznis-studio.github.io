# Stable context

- **Company:** solo operator, Slovak, Biznis.studiO brand (styled mark; plain "Biznis" in text/meta/RSS — see 04_Lessons).
- **Products:** 5 monetized on Gumroad + free catalogue (kits, templates, checklists, calculators). Full list: `docs/COMPANY_SCOREBOARD.md`.
- **Services (the real business):** website design/dev, process automation, custom digital products, brand/design, chatbots. Each has a published "what we do not offer" boundary — only offer what can genuinely be delivered.
- **Hard content rules:** no fabricated testimonials/logos/numbers; no unverified stats (compute or link, never guess); no advertising AI-generation to visitors; no advertising own weakness either ("we have no clients" is bad marketing, not honesty); every SK page must use SK header/footer (past bug: inherited EN nav).
- **Design system:** `agents/common.py` SITE_CSS — glassmorphism, gradient brand (#4f46e5/#7c3aed), unified card treatment across product/service/post cards.
- **Env vars required for any build:** `SITE_BASE_URL`, `FORMSPREE_ENDPOINT`, `GOOGLE_SITE_VERIFICATION`, `PEXELS_API_KEY`.
