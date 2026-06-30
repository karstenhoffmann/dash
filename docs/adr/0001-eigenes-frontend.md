# ADR-0001: Eigenes Front-End statt HA-Lovelace

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
dash braucht ein minimalistisch-flaches S/W-Interface mit großen Tippzielen, Blättern statt Scrollen, kein Abdunkeln, e-ink-tauglich. Home Assistant bietet mit Lovelace ein fertiges Dashboard.

## Entscheidung
Eigenes Front-End bauen. HA wird **Backend/Integrations-Schicht** (ab Hue), **nicht** die UI.

## Konsequenzen
- Volle Kontrolle über Design-Decke, Touch-Größen, Refresh-Choreografie.
- Mehr Eigenbau, aber genau das ist der Projektzweck (bewusst „kein Content-Bloat").
- Custom-Front-End über HA-WS/REST ist ein offiziell unterstütztes Muster (Long-Lived-Token).

## Alternativen
- **Lovelace + Mushroom + card-mod:** verworfen — Design-Decke, und card-mod bricht bei HA-Frontend-Updates (dokumentiert 2025.1, 2026.3; hängt an undokumentiertem internem DOM). Siehe `docs/2026-06_ui-foundation-vergleich.md`.
