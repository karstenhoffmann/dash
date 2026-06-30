# Stack-Findings — Projekt „dash"

**Stand:** 2026-07-01 · **Zweck:** Kritische Gegenprüfung des im `REBUILD-BRIEF.md` vorgeschlagenen Stacks, bevor gebaut wird. **Methode:** Mehrquellige Web-Recherche, Behauptungen adversarial verifiziert (3-Stimmen-Verfahren, 25 Claims geprüft, 25 bestätigt, 0 gekippt). **Adressat:** Karsten (+ Claude Cowork). **Status:** Entwurf zur Freigabe — **es wurde nichts gebaut.**

> **TL;DR:** Der Brief liegt **im Kern richtig**. Drei Korrekturen: (1) „Lit ODER Preact+htm" ist **keine** Gleichung — für das Top-Ziel „robuste, toolchain-freie KI-Edits" gewinnt **Preact + htm** klar. (2) **Vite ist nicht das Herzstück** — die Guardrails (stylelint) sind es; starte **no-build**, Bundler nur bei gemessenem Bedarf. (3) **Open Props** eher **nein** (Tokens selbst schreiben → null externe Abhängigkeit). Backend **FastAPI bestätigt**. Design-System (Every Layout + CUBE + Utopia + Tokens) **unverändert adoptieren** — es ist exakt die gepflegte Produktions-Boilerplate des CUBE/Every-Layout-Autors.

---

## 1. Empfehlung je Schicht (Entscheid + Begründung)

| Schicht | Entscheid | Begründung (1–2 Sätze) |
|---|---|---|
| **JS / Komponenten** | **Preact + htm** (no-build) | Einziger Pfad mit Komponenten-Modell **und** vom Hersteller offiziell dokumentiertem **Null-Build-Workflow** (~5,5 kB gzip) — keine Toolchain, die driften kann, vertraute React-Ergonomie → am robustesten für KI-generierte inkrementelle Edits. |
| **Layout** | **Every Layout Primitive** (Stack, Cluster, Cover, Grid, Center, Frame, Switcher, Sidebar…) | Fester Katalog von 13 Primitiven, die responsive Layouts **ohne `@media`-Breakpoints** erzeugen → „neuer Screen = Komposition" ist genau das, was diese Schicht liefert. Aktiv gepflegt (3. Auflage). |
| **CSS-Methodik** | **CUBE CSS** | Composition trägt **kein** Skin; Skin/Utility/Block-Schichten getrennt → erzwingt die im Brief geforderte Layout↔Skin-Trennung als Methodik. |
| **Scales** | **Utopia-`clamp()`-Generator** (fluide Typo/Space) | Systematisiert exakt die per-View-`clamp()`-Mathematik, die der Prototyp von Hand rechnete (`--ph`/`--pd`/`calc(8px + var(--pd)*0.0357)`). Generator läuft zur Build-Zeit/einmalig, Output ist statisches CSS. |
| **Tokens** | **Hand-geschriebene CSS Custom Properties** (eine Datei) | Volle Eigentümerschaft, null externe Abhängigkeit, trivial für Claude zu lesen/erweitern. **Open Props nur optional** (s. Abweichung D3). |
| **Skin (S/W)** | **Dünne Token-Schicht zuletzt** | S/W = Tausch weniger Skin-Tokens; e-ink-Skin als alternativer Token-Satz. |
| **Lint-Guardrails** | **stylelint** (`declaration-strict-value` + `declaration-property-value-disallowed-list` + `declaration-property-unit-disallowed-list`) + **prettier** + **CI** | Verbietet **mechanisch** rohe px-Werte / Nicht-Token-`clamp()` in Komponenten (in Shopify Polaris produktiv erprobt) → die Disziplin hängt nicht am guten Willen. **Load-bearing.** |
| **Build/Bundler** | **Start: no-build** (Import Maps + vendored ESM); Bundler **optional, später** | Für ein kleines, von FastAPI ausgeliefertes Dashboard ist no-build am wartungsärmsten. Vite/esbuild erst, wenn Minify/Bündelung messbar nötig wird (s. Abweichung D2). |
| **Backend** | **Python + FastAPI** mit **Backend-Adapter** (`SocoBackend`→`HaBackend`) | FastAPI empfiehlt **offiziell** plain `def` für blockierende Sync-Libs wie SoCo (läuft im Threadpool, Event-Loop bleibt frei) und ist async-nativ für die HA-WebSocket-Zukunft. **Unverändert bestätigt.** |
| **Hosting** | **Docker** auf Mele, **Caddy** Reverse-Proxy, Middleware **IP-Whitelist + Passwort/Cookie** | Wie im Brief — durch die Recherche nicht berührt, kein Änderungsbedarf. |

---

## 2. Vergleichstabellen der Alternativen

### 2.1 JS / Komponenten-Schicht

| Kriterium | **Vanilla JS** | **Preact + htm** ✅ | **Lit / Web Components** | **Svelte 5** |
|---|---|---|---|---|
| Runtime min+gzip | 0 kB | **~5,47 kB** (12,95 kB min) — *bundlejs, preact 10.29.3 + htm 3.1.1* | ~6,02 kB (15,46 kB min) — *Bundlephobia, lit 3.3.3* | kleiner Runtime, aber **Compiler-Output** — keine verifizierte Zahl (⚠️) |
| Läuft ohne Build-Step? | Ja | **Ja — offiziell dokumentiert** (htm = native Tagged Templates, kein Transform) | Nur via **Import Maps** (Bare-Specifier-Transform sonst nötig); Import Maps seit 2025-09 „Baseline Widely Available" (~95 %) | **Nein** — Svelte *kompiliert*, Build-Step Pflicht |
| Komponenten-Modell | ❌ keins (Prototyp: full-`innerHTML`-Re-Render) | ✅ Funktionskomp. + Hooks/Signals, React-vertraut | ✅ Web-Components/Shadow DOM (Web-Standard) | ✅ Komponenten, aber eigene Sprache (`.svelte`) |
| KI-Edits (Robustheit) | mittel — viel Boilerplate, leicht inkonsistent | **hoch** — bekanntes Modell, kein Toolchain-Drift, gezielte DOM-Updates | hoch — aber Import-Map/Specifier-Detail kann KI stolpern | mittel — Compiler-Magie + Runes-Syntax, weniger Trainingsdaten, Build muss grün bleiben |
| e-ink / schwache CPU | ⚠️ full re-render = Vollflackern | ✅ VDOM-Diff → **gezielte** DOM-Updates (gut für Teilrefresh) | ✅ lit-html Template-Parts → gezielte Updates | ✅ kompilierte, gezielte Updates |
| Langlebigkeit / Churn | maximal (nur Web-Standards) | hoch — winzig, stabil, React-kompatibel | sehr hoch — auf Web-Standards (Custom Elements) | mittel — größere Versionssprünge (Runes = Bruch 4→5) |
| **Eignung „dash"** | Belegt schmerzhaft (Ist-Prototyp) | **Beste Gesamtbilanz** | Starker Zweitplatz | Bestes für klassische Apps, aber Build-Zwang kollidiert mit no-build-Ziel |

> **Begründung des Entscheids:** Priorität (a) = robuste KI-Edits, (b) = wenig Abhängigkeiten/Zukunftssicherheit. Preact+htm ist der **einzige** Kandidat, der ein echtes Komponenten-Modell mit einem **vom Hersteller gesegneten Null-Build-Pfad** verbindet. Vanilla hat der Prototyp als zu fehleranfällig widerlegt (globaler State + `innerHTML`-Vollrender, e-ink-feindlich). Lit ist technisch ebenbürtig und als Web-Standard sogar langlebiger — aber der Import-Map/Bare-Specifier-Schritt ist genau die Art Detail, an der KI-Edits scheitern. Svelte scheidet wegen Build-Zwang aus (⚠️ unverifiziert, s. §5).

### 2.2 Design-System-Bausteine

| Baustein | Verdikt | Größe / Abhängigkeit | Bemerkung |
|---|---|---|---|
| **Every Layout Primitive** | **adoptieren** | nur CSS, ~0 Runtime | 13 Primitive, keine `@media`-Breakpoints; aktiv (3. Auflage), genutzt von BBC/web.dev. |
| **CUBE CSS** | **adoptieren** | Methodik, 0 kB | Vom Autor (Andy Bell) in seiner Produktions-Boilerplate aktiv gepflegt (Stand 2024). |
| **Utopia (clamp-Scales)** | **adoptieren** | Generator → statisches CSS | Ersetzt das hand-gerollte `--pd`-Gerechne des Prototyps 1:1. |
| **Design Tokens (CSS Custom Properties)** | **adoptieren, selbst schreiben** | 1 Datei, 0 Abhängigkeit | SSoT für Spacing/Typo/Sizes/Skin. |
| **Open Props** | **optional — Default: nein** | 4,0 kB Brotli core (self-reported ⚠️), reine Custom Properties, no-build via CDN, **niedriger Lock-in** | Sicher und klein, aber für ein deps-armes, KI-gepflegtes Projekt bringt eine selbst geschriebene Token-Datei mehr Kontrolle. |
| **cu.css** | **als Skelett erwägen** | zero-dep, no-build | Fertige Boilerplate **auf** CUBE+Utopia, Tokens eng an CSS gekoppelt (keine JSON-Token-Abstraktion) — guter Startpunkt statt grüner Wiese. |

> **Begründung:** Diese vier Schichten sind nicht nur solide — sie sind exakt die kombinierte Boilerplate von Andy Bell (CUBE-Autor, Every-Layout-Mitautor): CUBE + Every-Layout-Kompositionen + „Utopia-like clamp"-Generator + Token-Custom-Properties. Höchste Konfidenz, dass der Brief hier richtig liegt. **Adoptieren, nicht ersetzen.**

### 2.3 Build / Lint-Guardrails

| Werkzeug | Verdikt | Rolle |
|---|---|---|
| **stylelint** | **Pflicht (load-bearing)** | Verbietet rohe px / Nicht-Token-Werte. Drei Mechanismen, alle bestätigt (s.u.). |
| **prettier** | **Pflicht** | Einheitliche Formatierung → KI-Diffs bleiben klein/sauber. |
| **CI** (Lint + Format-Check + Boot/Routen-Smoke) | **Pflicht** | Der Durchsetzungs-Mechanismus, nicht der gute Wille. |
| **Vite** | **Optional / später** | Für no-build Preact+htm zunächst **overkill**. Erst bei gemessenem Minify-/Bündel-Bedarf — dann ggf. simpler: esbuild. |

**stylelint kann die Disziplin mechanisch erzwingen — bestätigt:**
- `stylelint-declaration-strict-value` → erzwingt `var()`/Funktion/erlaubter Wert pro Property (`color:#FFF` warnt, `color:var(--color-white)` ok; greift auch für `font-size:20px`). *Das* mandatiert Tokens.
- `declaration-property-value-disallowed-list` → Regex gegen den **ganzen** Wert (z. B. `/\bpx\b/` flaggt rohe px).
- `declaration-property-unit-disallowed-list` → verbietet Einheiten pro Property (z. B. `font-size:[px,em]`); in **Shopify Polaris** produktiv (verbietet hart-kodierte px/em/rem in `border`).
- **Caveat:** Keine Regel prüft *out of the box* — jede Property/Regex muss **explizit** aufgelistet werden. Einheiten-Verbot allein erzwingt noch keine Token-Pflicht → dafür `strict-value` nötig.

### 2.4 Backend-Adapter

| Kriterium | **FastAPI** ✅ | **Flask** | **Node / TypeScript** |
|---|---|---|---|
| SoCo (synchron) heute | ✅ plain `def` → **Threadpool**, offiziell empfohlen | ✅ synchron nativ | ⚠️ SoCo ist Python — Node bräuchte separaten Sonos-Client |
| HA-WebSocket-Zukunft (async push) | ✅ **async-nativ** | ⚠️ async nachrüstbar, aber nicht nativ | ✅ async-nativ |
| Adapter-Wiederverwendung | ✅ SoCo-Code bleibt Python (Prototyp-Logik als Spec migrierbar) | ✅ dito | ❌ Sprachwechsel, Logik neu |
| Sprach-Einheitlichkeit | ✅ ein Stack (Python) | ✅ | ❌ zwei Sprachen (JS Front + … ) |
| Reife async-Ökosystem | ✅ | mittel | ✅ |

> **Begründung:** FastAPI deckt **beide** Phasen sauber ab. SoCo synchron → plain `def` (FastAPI-Doku wörtlich: läuft im externen Threadpool, blockiert den Server nicht) — genau der SoCo-Fall. HA ist async-first (empfiehlt `aiohttp` für Libs); FastAPI ist async-nativ. Bonus: SoCo bringt ein opt-in `events_asyncio`-Modul (für später, ⚠️ historisch weniger reif als der Thread-Default). **Threadpool-Worker sind endlich** (früher 40, heute CPU-basiert) — bei Single-Apartment-Last irrelevant.

---

## 3. Abweichungen vom Brief-Vorschlag

### D1 — „Lit ODER Preact+htm" ist keine Gleichung → **Preact + htm** (statt offener Wahl)
Der Brief behandelt beide als austauschbar. Auf der Achse, die der Brief am höchsten gewichtet (robuste, toolchain-freie KI-Edits), sind sie **nicht** symmetrisch: Preact+htm braucht **null** Transform (offiziell dokumentierter no-build-Pfad), Lit braucht mindestens eine Import-Map. Lit bleibt ein starker, langlebiger Zweitplatz (Web-Standard) — aber als **Default** empfehle ich Preact+htm. *Konfidenz: hoch.*

### D2 — Vite ist **nicht** das Herzstück → **Guardrails ja, Bundler optional/später**
Der Brief stellt „Vite + stylelint + prettier + CI" als Einheit dar. Tatsächlich ist nur die **Guardrail-Hälfte** (stylelint/prettier/CI) load-bearing; der **Bundler** ist für no-build Preact+htm zunächst überflüssig. Empfehlung: **no-build starten** (Import Maps + lokal vendored ESM), stylelint/prettier/CI von Tag 1, Vite/esbuild erst bei gemessenem Minify-Bedarf. Reduziert Abhängigkeiten und Drift-Fläche (Priorität b). *Konfidenz: mittel-hoch — Abwägung, kein Faktenstreit.*

### D3 — Open Props → **Default: nein** (Tokens selbst schreiben)
Der Brief lässt Open Props offen. Für ein bewusst deps-armes, KI-gepflegtes Projekt empfehle ich eine **hand-geschriebene Token-Datei** statt Open Props: volle Kontrolle, null externe Abhängigkeit, trivial für Claude zu lesen. Open Props ist **sicher** (klein, niedriger Lock-in) und bleibt eine valide Option, falls du eine fertige Palette willst. *Konfidenz: mittel — Geschmack/Trade-off.*

> Keine Abweichung bei: Design-System-Schichten (Every Layout/CUBE/Utopia/Tokens), Backend (FastAPI + Adapter), Hosting (Docker/Caddy/IP-Whitelist), Verfassung/Lint-Disziplin. Alles bestätigt.

---

## 4. Offene Entscheidungen / Rückfragen an Karsten

1. **Svelte endgültig streichen?** Kein verifizierter Claim überlebte; Svelte **kompiliert** (Build-Step Pflicht) → kollidiert mit dem no-build-/KI-Robustheit-Ziel. *Empfehlung: streichen.* OK?
2. **JS-Schicht final:** **Preact + htm** (mein Default, D1) — oder doch **Lit** (Web-Standard, dafür Import-Map)? 
3. **Tokens:** selbst schreiben (D3, mein Default) · **Open Props** (fertige Palette) · **cu.css**-Skelett als Start? 
4. **Build-Strategie:** OK, **voll no-build** zu starten (Import Maps + vendored ESM) und einen Bundler (esbuild/Vite) erst bei messbarem Bedarf nachzuziehen (D2)?
5. **HA-Phase (später):** Client-Ansatz noch offen — roher FastAPI-WebSocket-Client gegen die HA-WS-API vs. fertige Lib. *Bewusst vertagt bis Hue real wird.*
6. **e-ink-Verhalten ist unbelegt:** Re-Render-Verhalten (Preact-VDOM vs. Lit-Template-Parts) wurde **nicht auf Zielhardware** gemessen — Aussagen sind aus Architektur/Bundle abgeleitet. Auf echtem e-ink-Gerät validieren, sobald vorhanden.

---

## 5. Unsicherheiten / Flags (ehrlich)

- **Svelte 5:** keine verifizierte Bundle-/Build-Aussage überlebte die Prüfung → im Vergleich nur qualitativ geführt. Build-Zwang ist sicher; konkrete kB nicht belegt.
- **e-ink / schwache CPU:** kein On-Device-Benchmark gefunden — Bewertung aus Architektur (Compiler vs. Runtime, VDOM vs. Template-Parts) und Bundle-Größe **abgeleitet**, nicht gemessen.
- **Bundle-Zahlen sind bundler-/minifier-abhängig:** Preact+htm 5,47 kB = bundlejs/esbuild; Lit 6,02 kB = Bundlephobia 3.3.3. Eine veraltete „~8 kB"-Cache-Zahl für Lit 3.3.0 ist kein Widerspruch.
- **Open Props kB:** vom Autor selbst angegeben (intern konsistent, unwidersprochen; npm-Cross-Check 403) → leichtes Marketing-Quellen-Risiko.
- **Design-System-Claims** (cu.css, Open Props, Andy-Bell-Boilerplate) sind primäre Selbstbeschreibungen der Autoren — passend für architektonische Fakten, aber nicht unabhängig auditiert.
- **Import-Maps-Baseline (2025-09-27)** ist das, was buildless Lit von „braucht Build" zu „praktisch buildless" kippt — jung und zentral für den Lit-vs-Preact-Vergleich.
- **Dossiers fehlen im Repo:** Die im Brief referenzierten `referenzen/…`, `memory/…`, `guides/…` wurden nicht mitkopiert und lagen für diese Recherche **nicht** vor — die Foundation-Fragen wurden daher von Grund auf neu recherchiert. Falls die Dossiers existieren, lohnt ein Abgleich.

---

## 6. Quellenliste (URLs)

**JS-Schicht / Bundle-Größen**
- https://preactjs.com/guide/v10/no-build-workflows/ *(primär)*
- https://deno.bundlejs.com/?q=preact,htm *(primär, Messung)*
- https://bundlephobia.com/package/lit *(primär, Messung)*
- https://lit.dev/docs/tools/requirements/ *(primär)*
- https://dev.to/matsuuu/buildless-workflow-through-import-maps-featuring-lit-shoelace-and-more-4ill *(Blog)*
- https://mfyz.com/react-best-parts-preact-htm-5kb/ *(Blog)*
- https://github.com/sveltejs/svelte/discussions/11214 *(Forum)*
- https://eastondev.com/blog/en/posts/dev/20251124-svelte-5-guide/ *(Blog)*
- https://feature-sliced.design/blog/js-framework-benchmarks *(sekundär)*

**Design-System**
- https://every-layout.dev/layouts/ *(primär)*
- https://piccalil.li/blog/a-css-project-boilerplate/ *(primär, Andy Bell)*
- https://open-props.style/ *(primär)*
- https://cu.harrycresswell.com/ *(primär)*
- https://nerdy.dev/open-props-ui *(Blog)*

**Lint-Guardrails**
- https://github.com/AndyOGo/stylelint-declaration-strict-value *(primär)*
- https://stylelint.io/user-guide/rules/declaration-property-value-disallowed-list/ *(primär)*
- https://stylelint.io/user-guide/rules/declaration-property-unit-disallowed-list/ *(primär)*
- https://polaris-react.shopify.com/tools/stylelint-polaris/rules/border-declaration-property-unit-disallowed-list *(primär)*

**Backend**
- https://fastapi.tiangolo.com/async/ *(primär)*
- https://docs.python-soco.com/en/latest/advanced/events.html *(primär)*
- https://developers.home-assistant.io/docs/api_lib_auth/ *(primär)*
- https://leapcell.io/blog/asynchronous-vs-synchronous-functions-in-fastapi-when-to-pick-which *(Blog)*
- https://dev.to/bkhalifeh/fastapi-performance-the-hidden-thread-pool-overhead-you-might-be-missing-2ok6 *(Blog)*

*Recherche-Statistik: 5 Such-Winkel · 24 Quellen geladen · 96 Claims extrahiert · 25 adversarial verifiziert (25 bestätigt, 0 gekippt).*
