# dash — Verfassung (vor jeder Arbeit zuerst lesen)

> Kanonische Regel-Datei dieses Repos. Claude Code lädt sie automatisch. **Substanz lebt nur hier → kein Drift.**

Projekt **dash** = lokales Wohnungsinterface. Jetzt: Sonos S1. Später: Hue, Kalender, Todos, Wetter, Status. LAN-only, kein Login. Hosting: Mele (Docker).

## Vor jeder Änderung lesen
Pflicht: [`DESIGN.md`](docs/DESIGN.md) (Grundgesetze, Screens, Flows, Edge Cases) · [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) (Backend-Adapter / HA-Readiness) · [`STACK-FINDINGS.md`](docs/STACK-FINDINGS.md) (Stack-Entscheid je Schicht) · [`docs/adr/`](docs/adr/) (verbindliche Entscheidungen). Davon nur **bewusst per ADR** abweichen, nie als Einzelfall hinbiegen. Der Prototyp in [`reference/`](reference/) ist **read-only Spezifikation** — nie recyceln.

## Der Stack (gelockt, siehe ADRs)
| Schicht | Wahl |
|---|---|
| JS/Komponenten | **Preact + htm**, **Light DOM**, **no-build** (Import Map → lokal vendored ESM in `web/vendor/`) — [ADR-0006](docs/adr/0006-js-schicht-preact-htm-light-dom.md) |
| Layout | **Every Layout**-Primitive als **globale CSS-Klassen** (`.cover .center .stack .cluster .grid .frame`) — [ADR-0003](docs/adr/0003-ui-foundation-tokens-primitive-cube.md) |
| Methodik | **CUBE CSS** (Composition trägt kein Skin) |
| Scales | **Utopia**-`clamp()` (fluide Typo/Space), Output statisches CSS |
| Tokens | **geschlossenes, eingefrorenes** CSS-Custom-Property-Set, ADR-gated — [ADR-0007](docs/adr/0007-tokens-governed-frozen.md) |
| Skin (S/W) | dünne Token-Schicht **zuletzt** (`web/tokens/skin-bw.css`) |
| Guardrails | **stylelint** (strict-value + disallowed-list) + **prettier** + **CI**, strikt ab Commit 1 — [ADR-0008](docs/adr/0008-no-build-start-guardrails-ab-tag-1.md) |
| Backend | **Python + FastAPI** + Backend-Adapter (`SocoBackend`→`HaBackend`) — [ADR-0002](docs/adr/0002-backend-adapter-ha.md) |

## Non-negotiables (mechanisch geprüft, wo möglich)
1. **Tokens zuerst. Nur Primitive fürs Layout. Skin zuletzt.**
2. **KEINE Magic-Numbers.** Kein rohes `px`/`clamp()` außerhalb der Scale-Tokens, kein Inline-Style, kein per-View-CSS. → **stylelint erzwingt** (CI rot bei jedem Nicht-Token-Wert).
3. **Tokens sind leicht zu *lesen*, bewusst schwer zu *erweitern*.** Neuer Token **nur per ADR**. Ein kleines, geschlossenes Set ist der Anti-Drift-Anker — nicht „schnell einen Wert dazu". (Governance schlägt Token-Quelle.)
4. **UI spricht nur das `Backend`-Interface** — nie SoCo/HA direkt. Eigene Konzepte (Szenen/Namen/Schnellquellen) backend-agnostisch über **Raum-Slugs**.
5. **Neue Screens = Komposition** aus Primitiven + Komponenten-Katalog. Neue Werte **nur als Token** (per ADR).
6. **Komponenten rendern in Light DOM** (kein Shadow DOM), damit die globalen Primitive-Klassen + Tokens greifen.
7. **Icons:** nur Lucide-SVG, **nie Emoji**. **Touch:** Ziele **≥ 64 px**. **Kein Scrollen → Blättern. Kein Abdunkeln** (Popover statt Modal). Portrait **und** Landscape als eigene Layouts. E-Ink-nativ (tap-getrieben, kein Auto-Poll im Endausbau).
8. **Verifizieren vor „fertig":** `npm run lint` grün, App bootet, Routen geprüft — keine ungetesteten Behauptungen.
9. **Jede Abweichung = explizite Exception** (ADR/Kommentar), nie still hinbiegen.

## Definition of Done (pro Änderung)
Komponiert aus Primitiven/Komponenten · nutzt nur Tokens · **keine neuen Magic-Numbers** · `stylelint`+`prettier` grün · App bootet · Routen geprüft · ggf. ADR/Exception dokumentiert.
**Bei sichtbaren Änderungen zusätzlich:** Sichttest über alle vier Viewports (sehen **und** messen) nach [`docs/VISUAL-QA.md`](docs/VISUAL-QA.md) — Befunde **systemisch** fixen (Token/Primitiv/Komponente), nie per-View-Quickfix.

## Arbeitsweise
Dev am MacBook, Deploy auf Mele (Docker) später. `git` = Meilensteine, `main` getrackt auf GitHub (`origin`). Branch für Feature-Arbeit, dann Merge nach `main`.
