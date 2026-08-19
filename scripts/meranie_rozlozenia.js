/* Meranie rozloženia stránky. Vlož do javascript_tool v prehliadači.
 *
 * Vzniklo z 2026-08-19, keď som to isté meral trikrát a zakaždým inak — a
 * štyrikrát som z toho vyvodil chybu, ktorá neexistovala. Metóda je tu
 * zafixovaná, aby sa tie omyly nedali zopakovať:
 *
 *  - znaky na riadok cez VÝŠKU / line-height, nikdy cez obdĺžniky Range:
 *    každý <a> alebo <strong> v odstavci pridá obdĺžnik a riadkov vyjde viac
 *    (na domovskej 9 namiesto 5)
 *  - bunky tabuliek sa nemerajú vôbec: sú roztiahnuté na najvyššiu bunku
 *    riadku, takže ich výška nie je výška ich textu
 *  - 35-45 znakov na riadok je pri 375 px FYZICKÉ MAXIMUM, nie chyba;
 *    pravidlo 45-75 platí pre desktop
 *  - img.complete v tomto kontexte klame — pri vizuálnej otázke rozhoduje
 *    snímka obrazovky, nie odvodené číslo
 *
 * Použitie: nastav šírku (375 / 768 / 1280), načítaj stránku, spusti.
 */
(() => {
  const d = document, de = d.documentElement;
  const out = { url: location.pathname, sirka: innerWidth };

  // 1. Horizontálne pretečenie a čo ho spôsobuje
  out.prekrocenie = de.scrollWidth - innerWidth;
  const trcia = [];
  d.querySelectorAll("*").forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right > innerWidth + 1 || r.left < -1)) {
      trcia.push(el.tagName.toLowerCase() + "." +
                 (el.className || "").toString().split(" ")[0]);
    }
  });
  out.trcia = [...new Set(trcia)].slice(0, 6);

  // 2. Znaky na riadok — len blokové odstavce, cez výšku
  const ps = [...d.querySelectorAll("main p, article p")]
    .filter(p => p.textContent.trim().length > 90 && !p.closest("td,th"))
    .slice(0, 15);
  const cpl = ps.map(p => {
    const lh = parseFloat(getComputedStyle(p).lineHeight);
    const n = Math.max(1, Math.round(p.getBoundingClientRect().height / lh));
    return Math.round(p.textContent.trim().length / n);
  }).sort((a, b) => a - b);
  out.znakovNaRiadok = cpl.length
    ? { min: cpl[0], median: cpl[Math.floor(cpl.length / 2)],
        max: cpl[cpl.length - 1], n: cpl.length,
        poznamka: innerWidth <= 480 ? "pri 375 px je 35-45 maximum, nie chyba"
                                    : "cieľ 45-75" }
    : "žiadne dostatočne dlhé odstavce";

  // 3. Nadpisy so zdedenou riadkovou výškou (telo má 1.65, nadpis chce ~1.2)
  out.nadpisySprawl = [...d.querySelectorAll(
      "main h1,main h2,main h3,article h1,article h2,article h3")]
    .map(h => {
      const cs = getComputedStyle(h);
      const r = parseFloat(cs.lineHeight) / parseFloat(cs.fontSize);
      return r > 1.4 ? `${h.tagName} lh=${r.toFixed(2)} "${h.textContent.trim().slice(0, 28)}"` : null;
    }).filter(Boolean).slice(0, 6);

  // 4. Dotykové ciele mimo prózy (odkazy vo vete 44 px mať nemusia)
  out.maleCiele = [...d.querySelectorAll("a,button")].filter(a => {
    const r = a.getBoundingClientRect();
    const vProze = a.closest("p") && !a.closest("nav,header,footer");
    return r.height > 0 && r.height < 40 && !vProze;
  }).map(a => `${(a.textContent || "").trim().slice(0, 20) || "?"} ${Math.round(a.getBoundingClientRect().height)}px`)
    .slice(0, 8);

  // 5. Tabuľky — len či sa vojdú a či majú kam scrollovať
  out.tabulky = [...d.querySelectorAll("table")].map(t => ({
    sirka: Math.round(t.getBoundingClientRect().width),
    stlpcov: t.rows[0] ? t.rows[0].cells.length : 0,
    rodicOverflowX: getComputedStyle(t.parentElement).overflowX,
    poznamka: "výšky buniek NEMERAŤ — sú roztiahnuté na najvyššiu v riadku",
  }));

  out.dalsiKrok = "Ak niečo vyzerá ako chyba, sprav SNÍMKU a pozri sa. " +
                  "Štyri z dnešných nálezov boli omyl merania, nie chyba stránky.";
  return out;
})();
