#!/bin/bash
# Stop hook: refuse to end a turn while the site is in a broken state.
#
# Exists because of a real failure: work was reported as done while the
# live site was several changes behind and the crawl audit was failing.
# CLAUDE.md says "verify against the live URL" but an instruction is
# advisory — this is deterministic.
#
# Blocks only on a genuinely broken build, so it is silent during normal
# work and never produces a false positive.

INPUT=$(cat)

# Required: without this the hook can block itself in a loop.
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active' 2>/dev/null)" = "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
[ -f scripts/audit_site.py ] || exit 0

AUDIT=$(SITE_BASE_URL="https://biznis-studio.github.io" python3 scripts/audit_site.py 2>&1)
if [ $? -ne 0 ]; then
  echo "The site audit is failing, so the site must not be shipped in this state:" >&2
  echo "$AUDIT" >&2
  echo "Fix the reported issues, then rebuild with scripts/build_site.py." >&2
  exit 2
fi
exit 0
