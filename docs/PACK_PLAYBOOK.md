# Interné know-how — ako stavať pack lacno a s najväčším prínosom

2026-08-16. Nie je to teória. Každý bod má za sebou konkrétnu chybu alebo
konkrétny zásah z reálneho stavania quality packu (12.–16. 8. 2026).

---

## Rebríček podľa pomeru prínos / cena

Zoradené podľa toho, čo sa skutočne oplatilo:

| # | Činnosť | Cena | Prínos | Dôkaz |
|---|---|---|---|---|
| 1 | **Vziať existujúcu tabuľku odborníka ako zdroj pravdy** | nulová — už existuje | najvyšší | celý katalóg 125 príčin vznikol z nej |
| 2 | **Brána na konzistenciu** | ~40 riadkov kódu, raz | veľmi vysoký | zachytila **3 skutočné chyby**, jednu vlastnú pri čistení |
| 3 | **Scenáre z reálnych prípadov** | hodina za scenár | vysoký | S11 aj S12 vznikli zo skutočných zlyhaní a obe niečo chytili |
| 4 | **Beh v Copilote zákazníka ako príloha** | minúty | vysoký | odhalil chybu návrhu štítkov, ktorú nič iné nechytilo |
| 5 | Procedúra (poradie podľa ceny overenia) | pol dňa | vysoký, ale **musí prísť od odborníka** | poradie určil QM, nie my |
| 6 | Vymyslené scenáre bez reálneho prípadu | hodina | **záporný** | pôvodný S7 sa nedal splniť — testoval iné pravidlo |
| 7 | Písanie rozhodovacích stromov vlastnou hlavou | dni | **záporný** | vymyslená príčina mimo tabuľky, stratený smer odchýlky, prepisované od nuly |

**Dva riadky sú záporné a oba majú spoločnú príčinu: obsah sme tvorili my.**

---

## Postup

### 0 · Kvalifikácia — pol dňa, zdarma

Jediná otázka, ktorá rozhoduje: **je know-how niekde zapísané?**

- **Áno**, hoci v neusporiadanej tabuľke → stavia sa pack.
- **Nie**, je v hlave dvoch ľudí → **najprv štruktúrovacia zákazka.** Pack do
  firmy bez zapísaného know-how vyrobí dokument, ktorý nikto nepoužije, a zlú
  referenciu.

Druhá otázka: **robí to rozhodnutie skúsený inak než nováčik?** Ak nie, nie je
čo vrstviť — na to stačí návod.

### 1 · Zdroj pravdy je ICH súbor. Nikdy nepíšeme obsah my

**Toto je najdrahšia chyba, akú sme spravili.** Napísali sme rozhodovacie stromy
sami; vymysleli sme príčinu, ktorá v tabuľke nebola, a stratili smer odchýlky
pri rozmerovej vade. Muselo sa to prepísať od nuly zo zdroja.

Pravidlo: **odvodzuj, nevymýšľaj.** Každý krok stromu musí ukazovať na riadok,
ktorý v ich tabuľke existuje. Kontroluje sa to strojovo, nie čítaním.

### 2 · Postav bránu skôr než čokoľvek iné

Najlacnejšia vysoko-hodnotná vec v celom projekte. Kontroluje:

- každá príčina je pokrytá aspoň jedným krokom
- žiadny krok neuvádza príčinu mimo tabuľky
- žiadna príčina nie je v strome dvakrát
- žiadne prázdne povinné pole
- odkaz na inú kategóriu mieri na existujúcu kategóriu

**Overuj bránu tým, že ju zámerne rozbiješ.** Brána, ktorú si nevidel spadnúť,
nie je overená.

**Hranica brány, ktorú treba poznať:** stráži **konzistenciu**, nie správnosť.
Keď pribudla druhá kategória o balení bez pravidla, do ktorej vojsť, brána bola
zelená a pack bol pokazený. Na to je až akceptačná sada.

### 3 · Scenáre len zo skutočných zlyhaní

Dobré scenáre nevznikli premýšľaním, ale tým, že sa niečo pokazilo:
S11 z chybnej diagnózy prenesením vzoru, S12 z kolízie dvoch kategórií,
oprava S7 z reálneho behu.

**Vymyslený scenár je záporná hodnota** — pôvodný S7 mal prakticky rovnaký vstup
ako S13 a opačné očakávanie, takže nemohol prejsť nikdy a maskoval sa ako
zlyhanie modelu.

Pri každom novom pravidle: **skontroluj scenár oproti susedným scenárom.** Nové
pravidlo vie ticho vypnúť staré.

### 4 · Pusti to v ich Copilote ako prílohu

Nevyžaduje od IT nič a odhalí veci, ktoré na papieri nevidno. Reálny beh odhalil,
že model si zlial dva štítky a nikdy nepovedal, že príčina nie je z katalógu —
to nezachytila ani brána, ani čítanie.

### 5 · Pravidlo zastavenia — bez neho to nikdy neskončí

**Toto je najdôležitejší bod celého dokumentu.**

Sada scenárov je stroj na výrobu vlastnej práce: každé pravidlo si vyžiada
scenár, každý scenár odhalí zrážku, tá si vyžiada pravidlo. Nemá to prirodzený
koniec a **vyzerá to ako postup**, lebo každý krok je správny a končí zelenou
fajkou.

Merateľný dôkaz: quality pack mal medzi 12. a 16. 8. **päť verzií, a `source/` —
teda samotná znalosť — sa nezmenil ani raz.** Menili sa pravidlá o pravidlách.

**Pravidlo: pack sa mení, len keď si to vynúti reálny prípad.** Nie hypotetická
diera, nie „toto by mohlo zlyhať". Až keď nástroj na skutočnom prípade poradí
zle alebo nevie poradiť.

---

## Čo z toho je prenosné a čo ešte nevieme

**Prenosné je všetko okrem obsahu:** postup, brána, formát scenárov, CI, pravidlo
zastavenia. To je linka.

**Neoverené:** že to zafunguje v profesii, ktorá nemá tabuľkovú povahu.
Diagnostika vady je príjemný prípad — má konečný zoznam príčin a pozorovania,
ktoré ich rozlišujú. Rozhodnutia typu „schváliť odchýlku?" alebo „ako
odpovedať zákazníkovi?" takú štruktúru nemusia mať. **Kým to neskúsime, je linka
overená na jednom type úlohy.**
