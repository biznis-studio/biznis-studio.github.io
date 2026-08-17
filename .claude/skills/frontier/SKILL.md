---
name: frontier
description: Nasnímať globálnu špičku AI a marketingu a premeniť ju na poznatky so zdrojom. Použi na začiatku pracovného behu, alebo keď treba vedieť, čo sa vo svete AI zmenilo od minule.
---

# Snímanie špičky

Dve dráhy, lebo majú rôzne obmedzenia. Nemiešaj ich.

## Dráha 1 — automatická (vie ju spustiť aj CI)

```bash
python3 -c "import sys; sys.path.insert(0,'.'); from agents import frontier_agent as f; f.run()"
```

Štrnásť zdrojov overených naživo 2026-08-17. Zapíše do `signals_raw` s prefixom
`frontier:`. Fronta na výklad:

```bash
python3 -c "import sys; sys.path.insert(0,'.'); from agents import frontier_agent as f; [print(p['source'], '|', p['term'][:90], '|', p['url']) for p in f.na_vyklad(20)]"
```

## Dráha 2 — X (potrebuje prihlásený Chrome majiteľa)

X nemá použiteľné free API, takže **toto CI nikdy nespustí**. Účty sú v
`state/x_watchlist.json`. Otvor v Chrome dotaz `from:` cez tie účty
(`&f=live`) a vytiahni ich týmto — nie `read_page`, ktorý minie 15 kB
stromu na tri príspevky:

```js
[...document.querySelectorAll('article')].slice(0,15).map(a=>{
  const h=a.querySelector('a[href^="/"][role="link"]')?.getAttribute('href')||'';
  const t=a.querySelector('[data-testid="tweetText"]')?.innerText||'';
  const l=[...a.querySelectorAll('a[href*="/status/"]')]
      .map(x=>x.getAttribute('href')).find(x=>/status\/\d+$/.test(x))||'';
  return (h.split('/')[1]||'?')+' :: '+t.replace(/\s+/g,' ').slice(0,180)+' :: '+l;
}).join('\n')
```

Zahoď príspevky kratšie než ~60 znakov bez odkazu — sú to odpovede, nie obsah.
Otvorené vyhľadávanie podľa kľúčových slov nepoužívaj: dotaz `agent` vrátil
futbalových agentov a agenta FBI.

## Výklad — jediný krok, kde vzniká poznatok

Fronta je skládka, kým nad každou položkou nepadne úsudok. Pri každej odpovedz:

1. **Čo to zlacňuje?** 2. **Čo to umožňuje, čo predtým nešlo?**
3. **Čo to ruší?** 4. **Posilňuje alebo oslabuje to našu pozíciu?**

Až potom zápis — a `FAKT` ani `VYSLEDOK` neprejde bez poľa `dokaz`:

```python
from core.db import get_connection
from core import evolution as ev
conn = get_connection(); ev.priprav(conn)
ev.zapis_poznatok(conn,
    tvrdenie="…", druh="POZOROVANIE",   # POZOROVANIE | ODVODENIE | HYPOTEZA | VYSLEDOK | FAKT
    zdroj="https://…",                  # otvorený, nie z výsledkov vyhľadávania
    typ_zdroja="model",                 # model 60 dní | nastroj 90 | trh 180 | zakaznik 365 | vlastne 365
    dosah="čo to zlacňuje/umožňuje/ruší")
```

## Čo tu nehľadať

Zdroje, ktoré vyzerajú živé a nie sú: LangChain `/rss/` vracia Webflow HTML,
Papers with Code API vracia HTML, Meta AI blog 404, Reddit 403. Anthropic nemá
RSS ani na `/news/rss.xml`, ani na `/engineering/rss.xml` — sníma sa ručne.
**HTTP 200 nie je dôkaz, že je to zdroj.** Pozri, čo prišlo.
