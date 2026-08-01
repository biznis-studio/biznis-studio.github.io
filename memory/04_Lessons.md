# Lessons (reusable only, max 10 lines each)

**Rebuilding a page wipes its SEO markup.** `build_page()` resets to pre-`seo_agent` state.
Always: `pages.seo_enhanced=0` then re-run `seo_agent`. `build_site.py` does this — never hand-roll.

**`git rebase --ours` is UPSTREAM, not your commit** (opposite of merge). Discarded new DB rows once.
Use `--theirs` when replaying your own work in a rebase; verify row counts after.

**Deploy success ≠ live.** A concurrent push once failed the pipeline silently; site sat stale for hours
while local build looked fine. Never report "done" from a local build — `scripts/deploy.py` verifies the live URL.

**Apostrophes inside single-quoted JS strings break the whole inline `<script>` silently.**
The page renders, the widget just does nothing. Verify by driving the tool and reading output, not by "it built".

**Subagent research must be re-verified on primary sources before acting.** One fan-out claimed a github.io
site ranked page-1 on Google; it was DuckDuckGo-only and didn't replicate. Always spot-check load-bearing claims.

**Don't confuse "not lying" with "advertising your own weakness."** Both are wrong in opposite directions.
State what's true; frame risk-transfer (fixed price, written scope) as a guarantee, not a confession.

**Calculator page bypasses `page_shell()`** — has its own `<style>` block, silently drifts from site-wide changes.
Any global template/CSS change must also touch `inject_intro_into_calculator()`.

**Fake-edge test for pipeline stages:** for any two sequential steps, ask if the second actually needs
the first's output. `market_research_agent`'s 5 source fetchers (+ npm/StackExchange's internal per-term
loops) had none — fanned out with `ThreadPoolExecutor`, ~8.98s→4.21s avg (noisy, measured not assumed).
DB writes stay single-threaded (sqlite3 isn't thread-safe). Apply this test before adding new pipeline stages.
