# ADR-0008: No-build-Start; Guardrails (stylelint/prettier/CI) strikt ab Tag 1

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Der Brief schlug „Vite + stylelint + prettier + CI" als Einheit vor. Die Recherche zeigt: load-bearing ist die **Guardrail-Hälfte** (stylelint), nicht der Bundler. Für no-build Preact+htm ist Vite zunächst overkill.

## Entscheidung
1. **No-build starten:** Import Map + lokal vendored ESM (`web/vendor/`). Kein Bundler im Auslieferungspfad. FastAPI liefert `web/` statisch aus.
2. **Guardrails strikt ab Commit 1:**
   - **stylelint** mit `stylelint-declaration-strict-value` (erzwingt `var(--token)` für Farb-/Maß-Properties) + `declaration-property-value-disallowed-list` + `declaration-property-unit-disallowed-list` (verbieten rohe `px`/`clamp()`).
   - **prettier** für einheitliche Formatierung.
   - **CI** (GitHub Actions): Lint + Format-Check + Boot/Routen-Smoke. **CI rot bei jedem Nicht-Token-Wert.**
3. **Ausnahme nur per ADR** (oder dokumentierter stylelint-`disable`-Kommentar mit Begründung).
4. **Bundler (esbuild/Vite) erst bei gemessenem Bedarf** (Minify/Bündelung) — dann als minimaler Build-Schritt, nicht als Fundament.

## Konsequenzen
- Minimale Abhängigkeits- und Drift-Fläche; node-Toolchain nur dev-time (Lint/Format), nicht runtime.
- Disziplin hängt nicht am guten Willen, sondern am roten CI.
- stylelint-Regeln prüfen **nicht** out-of-the-box — jede Property/Regex wird explizit konfiguriert.

## Alternativen
- **Vite als Fundament:** verworfen (overkill für no-build). Bleibt Option für später.
- **Nur prettier, kein stylelint:** verworfen — dann fehlt der mechanische Anti-Drift-Anker.
- Belege: [`docs/STACK-FINDINGS.md`](../STACK-FINDINGS.md).
