# ADR-0005: E-Ink-Touch-Steuerung geparkt; interaktive App zuerst

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Faces: Handy, Tablet, Browser jetzt; evtl. browserfähiges E-Ink-Touch-Gerät später. Die Recherche zeigt: echtes E-Ink läuft eine interaktive SPA schlecht (Voll-Refresh 0,6–1,3 s s/w, Farb-E-Ink 15–19 s; Ghosting; schwache CPUs). Erfolgreiche E-Ink-Projekte rendern **serverseitig zu einem Bild** (TRMNL-Muster).

## Entscheidung
Die **interaktive Web-App** (Preact+htm) ist das primäre Ziel und läuft auf **Handy/Tablet/Touch-TFT**. **E-Ink-Touch-Steuerung wird geparkt.** Falls später ein E-Ink-Wandpanel kommt: **separater, serverseitig gerenderter „Glance"-View** (statisches Bild, alle paar Minuten), Steuerung bleibt auf Handy/Tablet — **nicht** die SPA aufs E-Ink zwingen.

## Konsequenzen
- Design-Grundgesetze (kein Abdunkeln, Blättern statt Scrollen, flacher Hochkontrast) gelten weiter — sie sind durch die E-Ink-Recherche validiert und schaden den interaktiven Faces nicht.
- Kein Aufwand jetzt für E-Ink-Subscription/Refresh-Firmware.

## Alternativen
- **Interaktive SPA direkt auf E-Ink:** verworfen (Physik: Refresh, Ghosting, CPU). Belege: [`docs/2026-06_ui-foundation-vergleich.md`](../2026-06_ui-foundation-vergleich.md).
