# Project

- **Objective:** digital studio + product catalogue, autonomous pipeline, first paying customer.
- **Live:** https://biznis-studio.github.io (EN) · /sk/ (Slovak)
- **Repo:** github.com/biznis-studio/biznis-studio.github.io
- **Stack:** Python 3, SQLite (`db/biznis.sqlite3`), static HTML → GitHub Pages via Actions (`.github/workflows/pipeline.yml`), daily cron + manual dispatch.
- **Mechanism:** `scripts/build_site.py` (rebuild), `scripts/deploy.py --expect "<text>"` (ship + verify live), `.claude/hooks/verify_before_stop.sh` (Stop hook, blocks turn end if `audit_site.py` fails), `.claude/skills/ship`, `.claude/skills/find-opportunities`, `scripts/check_links.py` (advisory external-link check, deliberately NOT in the build gate).
- **Monetization:** Gumroad (5 products, $0 revenue). 5 services (web, automation, custom digital products, design/branding, chatbots) — the real target, sold via outreach/portfolio not SEO.
- **Version:** iteration 78 (see 01_Decisions.md for the log going forward; full history in `docs/TASKBOARD.md`).
