---
name: ship
description: Build, audit, deploy and verify the change is actually live. Use whenever site content or templates changed.
disable-model-invocation: true
---
Ship the current changes end to end. Do not report success until the change
is verified on the live site.

$ARGUMENTS is a short distinctive phrase that must appear on the live page
after deploying. If it is empty, pick one yourself from what changed.

1. Rebuild everything:
   ```bash
   python3 scripts/build_site.py
   ```
   Required env vars: SITE_BASE_URL, FORMSPREE_ENDPOINT,
   GOOGLE_SITE_VERIFICATION, PEXELS_API_KEY. The script ends with the crawl
   audit and exits non-zero if it fails. **A non-zero exit means stop** -
   fix the reported issue, do not deploy around it.

2. Commit with a message that says what changed and why.

3. Rebase onto origin. If `db/biznis.sqlite3` or any `site/` file conflicts,
   resolve with `--theirs` (during a rebase that means YOUR commit, not
   upstream — getting this backwards has silently deleted product rows
   before), then confirm nothing was lost:
   ```bash
   sqlite3 db/biznis.sqlite3 "SELECT COUNT(*) FROM products WHERE format='service';"
   ```

4. Push, then deploy and verify in one step:
   ```bash
   python3 scripts/deploy.py --expect "<the phrase>"
   ```
   Add `--url` if the change is not on the homepage.

5. Report the deploy script's actual output. Exit 0 means verified live.
   Anything else means the site was NOT updated — say so plainly rather
   than reporting the local build as success.
