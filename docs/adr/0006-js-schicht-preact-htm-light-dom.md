# ADR-0006: JS-Schicht = Preact + htm, Light DOM, no-build

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Meta-Ziel: mit einem KI-Assistenten mega-einfach und fehlerarm erweiterbar. Kandidaten: vanilla JS, Preact+htm, Lit/Web Components, Svelte. Gewichtung: (a) robust/fehlerarm für KI-Edits, (b) wenig Abhängigkeiten/Langlebigkeit, (c) e-ink/schwache CPU.

## Entscheidung
**Preact + htm**, gerendert in **Light DOM**, **no-build** (Import Map → lokal vendored ESM in `web/vendor/`).

**Ausschlaggebender, projektspezifischer Grund:** Unser Design-System ist **global-CSS-basiert** (Every-Layout-Primitive als globale Klassen, CUBE). Preact rendert in den normalen DOM → globale Klassen + Tokens greifen direkt, 1:1 passend. **Lit/Web Components rendern per Default in Shadow DOM**, der globales CSS abschottet — die Primitive-Klassen kämen dort nicht an. Light-DOM + globale Primitive gehören strukturell zusammen.

Dazu: htm = native Tagged Templates → **echter Null-Build-Pfad ohne Transform** (Lit bräuchte mindestens eine Import-Map). React-API-kompatible Ergonomie = großer Trainingskorpus → Claude generiert/ändert Komponenten zuverlässiger. ~5,5 kB gzip, extrem stabil.

## Konsequenzen
- Komponenten komponieren die governte globale Foundation; sie führen **kein** eigenes Skin/CSS ein.
- Preact + htm werden lokal vendored (committed) → LAN-only/offline, kein CDN zur Laufzeit.
- Die JS-Wahl berührt den Anti-Drift-Anker nicht — der sitzt im CSS-Governance (strict-value-Lint + ADR-Gate), siehe ADR-0007/0008.

## Alternativen
- **Lit/Web Components:** philosophisch sauberster Anker (reiner Web-Standard, kein Framework). Verworfen wegen Shadow-DOM-vs-globale-Foundation-Konflikt + Import-Map-Pflicht. *Falls je gewechselt:* bewusst **Light-DOM-Lit** (`createRenderRoot` überschreiben) + Import-Map.
- **Vanilla JS:** vom Prototyp als zu fehleranfällig belegt (globaler State + `innerHTML`-Vollrender, e-ink-feindlich).
- **Svelte 5:** Compiler erzwingt Build-Step → kollidiert mit no-build/KI-Robustheit. Verworfen.
- Belege: [`docs/STACK-FINDINGS.md`](../STACK-FINDINGS.md).
