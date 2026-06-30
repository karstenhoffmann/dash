# ADR-0003: UI-Foundation = Tokens + Every-Layout-Primitive + CUBE + Utopia

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Der Prototyp rechnete responsive Layouts per View von Hand (`--ph: clamp(720px,100svh,1000px)`, `--pd: calc(...)`, überall `calc(8px + var(--pd)*0.0357)`). Das ist genau das per-View-Gefrickel, das wir loswerden wollen. Meta-Ziel: neue Screens = **Komposition**, ohne an Layout/Responsive zu frickeln.

## Entscheidung
Vier Schichten adoptieren (nicht ersetzen):
1. **Design-Tokens** als CSS Custom Properties — eine Quelle der Wahrheit (`web/tokens/`).
2. **Utopia**-`clamp()`-Scales für fluide Typo/Space — systematisiert die per-View-clamp-Mathematik; Output ist statisches CSS.
3. **Every-Layout-Primitive** als **globale CSS-Klassen**: `.cover .center .stack .cluster .grid .frame` (bei Bedarf `.switcher .sidebar`). Responsive **ohne `@media`-Breakpoints**.
4. **CUBE-CSS**-Schichtung: Composition trägt **kein** Skin; Skin = dünne Token-Schicht zuletzt.

Anker = die gepflegte Boilerplate von Andy Bell (CUBE-Autor / Every-Layout-Mitautor) bzw. `cu.css` (Harry Cresswell): spezifizierter, zero-dep, no-build Standard auf genau dieser Methodik. Daraus einen minimalen Satz **einfrieren**, nicht von grüner Wiese starten.

## Konsequenzen
- „Neuer Screen = Komposition" wird strukturell möglich.
- Flach + winzig + statisch = e-ink-/schwache-CPU-freundlich.
- Disziplin wird per Lint erzwingbar (siehe ADR-0007, ADR-0008).

## Alternativen
- **Tailwind:** Delivery-Schicht, kein Layout-out-of-the-box; Build nötig. Verworfen als Fundament.
- **React-Komponenten-Libs (MUI/Chakra/Mantine):** schwer (~45 kB React + ~140 kB Lib), „soft modern"-Look gegen S/W, e-ink-feindlich, Breaking Majors. Verworfen.
- Belege: [`docs/2026-06_ui-foundation-vergleich.md`](../2026-06_ui-foundation-vergleich.md), [`docs/STACK-FINDINGS.md`](../STACK-FINDINGS.md).
