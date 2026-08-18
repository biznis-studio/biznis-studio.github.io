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

# --- druhá brána: nekončiť ťah, kým je vo fronte práca pre stroj ------------
#
# Majiteľ 2026-08-18: "zas si sa zasekol, toto je systemovy problem." Mal
# pravdu. Po každej hotovej jednotke som napísal správu a ťah ukončil, hoci
# fronta mala ďalšie kroky označené (stroj) — teda také, na ktoré nikoho
# nepotrebujem. Prevádzkový režim v CLAUDE.md hovorí "bež ďalej", ale to je
# rada, a rada sa pod tlakom preskočí. Toto je deterministické.
#
# Neblokuje donekonečna: pri druhom pokuse je stop_hook_active=true a hook
# skončí hneď na začiatku. Vynúti teda ešte jednu jednotku práce, nie väzenie.
# Kroky označené (MAJITEĽ) sa zámerne nepočítajú — tie čakať majú.

[ -f scripts/evolve.py ] || exit 0

# Bez `timeout`: na macOS ten príkaz neexistuje a vracia 127, čím sa výstup
# stratí a brána mlčky nezaberie. Časový strop hooku je v .claude/settings.json.
KROKY=$(python3 scripts/evolve.py 2>/dev/null | grep -F "(stroj)" | head -3)

# Budík ako podmienka ukončenia. Ak je vo fronte práca, ťah smie skončiť len
# vtedy, keď je naplánované pokračovanie — inak sa loop zastaví a majiteľ musí
# písať "pokracuj". Presne to sa 2026-08-18 stalo opakovane: skôr v relácii som
# budík po každom ťahu nastavoval a loop bežal sám, potom som na to prestal
# a zastavil som sa po každej úlohe. Marker píše ScheduleWakeup cez state/.
BUDIK="state/dalsi_budik.txt"
BUDIK_CERSTVY=0
if [ -f "$BUDIK" ]; then
  # čerstvý = zapísaný za posledných 10 minút, teda v tomto ťahu
  if [ -n "$(find "$BUDIK" -mmin -10 2>/dev/null)" ]; then
    BUDIK_CERSTVY=1
  fi
fi

if [ -n "$KROKY" ] && [ "$BUDIK_CERSTVY" = "1" ]; then
  echo "Fronta má prácu, ale pokračovanie je naplánované ($(cat "$BUDIK")) — ťah smie skončiť." >&2
  exit 0
fi

if [ -n "$KROKY" ]; then
  echo "Fronta má prácu, ktorú smieš spraviť sám — ťah sa nekončí:" >&2
  echo "$KROKY" >&2
  echo "Vezmi prvý krok, sprav ho celý vrátane overenia meraním, commitni." >&2
  echo "Zastavuj sa len pri peniazoch, odosielaní, záväzkoch a rozhodnutiach" >&2
  echo "o tom, čím má byť biznis." >&2
  echo "" >&2
  echo "Ak prácu spraviť nevieš, NAPLÁNUJ POKRAČOVANIE cez ScheduleWakeup a zapíš" >&2
  echo "čas do state/dalsi_budik.txt — inak sa loop zastaví a majiteľ ho musí" >&2
  echo "spúšťať ručne." >&2
  exit 2
fi
exit 0
