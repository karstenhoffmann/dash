# Visual QA — Sichttest bei jeder UI-Änderung

Verbindliche Routine für jede sichtbare Änderung (Teil der Definition of Done, [`CLAUDE.md`](../CLAUDE.md)).
Ziel: Layout **sehen und messen**, Inkonsistenzen erkennen und **das System optimieren — nicht in Einzelfall-Quickfixes driften**.

## 1. Viewport-Matrix (immer alle vier)
| Ziel | Größe (CSS-px) |
|---|---|
| iPhone 16 — Hochformat | 393 × 852 |
| iPhone 16 — Querformat | 852 × 393 |
| iPad mini | 744 × 1133 |
| Desktop | 1280 × 800 |

Portrait **und** Landscape sind eigene, durchdachte Layouts (DESIGN §3) — nicht nur skaliert.

## 2. Methode (pro Viewport)
1. `preview_start` → `preview_resize` (Größe) → `preview_screenshot` (**Gestalt sehen**) → `preview_eval` (**Geometrie messen**).
2. Konsole muss **fehlerfrei** sein (`preview_console_logs` level=error).

## 3. Checkliste — sehen UND messen
- **Kein Clipping:** `cover.scrollHeight ≤ innerHeight` (Body ist `overflow:hidden` → Überlauf verschwindet *unsichtbar*, kein Scrollbalken warnt). Kein Element außerhalb des Viewports.
- **Sichtachse:** Content-Zentren fluchten mit App-/Tab-Bar (`cx ≈ innerWidth/2`). Vertikale/horizontale Linien aligned.
- **Balance:** keine kippende Kante; zusammengehörige Gruppen symmetrisch; kein „schwebendes" Einzelelement.
- **Rhythmus:** Abstände stammen aus der Space-Scale; keine Ausreißer.
- **Touch:** Ziele ≥ `var(--hit)`; nichts pfriemelig.
- **Ruhe/glanceable:** keine „zappeligen" Muster (z. B. viele dünne Elemente auf schmaler Breite).

## 4. Fix-Disziplin (Anti-Drift — der eigentliche Punkt)
Bei jedem Befund zuerst die Ebene bestimmen, dann **dort** fixen:
- **Token** (Scale/Rhythmus/Maß falsch) → Token anpassen/ergänzen (nur per ADR, [ADR-0007](adr/0007-tokens-governed-frozen.md)).
- **Primitiv** (Layout-Verhalten falsch/überladen) → Primitive/Komposition korrigieren.
- **Komponente** (ein Baustein wirkt falsch) → Komponente überarbeiten.

Verboten: per-View-`@media`-Quickfix, Magic-Number, Inline-Style, ein Wert „nur für diesen einen Screen". Wiederkehrendes Layoutmuster → Primitive/Komponente, nicht kopieren.

> Leitfrage: „Ist das *ein* Symptom oder ein *System*-Defekt?" Immer das System reparieren, damit derselbe Fehler nirgends wieder auftritt.
