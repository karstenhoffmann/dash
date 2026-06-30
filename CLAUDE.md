# Sonos-Controller — Projekt-Regeln (vor jeder Arbeit hier zuerst lesen)

> Kanonische Regel-Datei dieses Projekts. Wird beim späteren `git init` zur **Repo-Root-`CLAUDE.md`** (Claude Code lädt sie dann automatisch beim Arbeiten im Repo).
> In **Cowork** wird sie über einen VOR-Trigger in der Workspace-Root-`CLAUDE.md` referenziert (Cowork zieht verschachtelte `CLAUDE.md` nicht automatisch). **→ Dieser Trigger ist bei Repo-Extraktion aus der Root-`CLAUDE.md` zu entfernen.** Substanz lebt nur hier → kein Drift.

## Vor jeder Änderung lesen
Pflicht: `DESIGN.md` (Grundgesetze, Screens, Flows, Edge Cases) + `ARCHITECTURE.md` (Backend-Adapter / HA-Readiness). Davon nur **bewusst** abweichen, nie als Einzelfall hinbiegen.

## Non-negotiables
- **Primitive statt Sonderlocken:** auf geteilten Komponenten bauen (`btn`, `iconbtn`, `segbar`, `tab`, `overlay`). Verhalten/Präsentation an *einer* Stelle (z.B. `OVERLAY_VARIANT`); Abweichung nur als explizite Variante/Fork.
- **Icons:** nur Lucide-SVG, **nie Emoji**.
- **Touch:** grobe Ziele **≥ 64 px**, nie pfriemelig.
- **Responsiv:** Portrait UND Landscape als eigene, durchdachte Layouts; **kein Scrollen/Overflow** (E-Ink!). Moderne CSS-Mittel (dvh, clamp, min, Container-Queries).
- **Entkoppelt:** UI spricht nur das `Backend`-Interface (SoCo jetzt, HA später); eigene Konzepte (Szenen/Namen/Schnellquellen) backend-agnostisch über Raum-Slugs.
- **E-Ink-nativ:** tap-getrieben, optimistisch, Sleep/Wake; kein erzwungenes Auto-Poll im Endausbau.
- **Verifizieren vor „fertig":** Syntax/Boot/Routen prüfen (`node --check`, Test-Client) — keine ungetesteten Behauptungen.

## Arbeitsweise
Dev am MacBook (`scripts/run-local-macbook.sh`), Deploy auf Mele später (rsync/Mutagen). GitHub nur für Meilensteine. Status-SSoT: `memory/projects/2026-06_sonos-controller.md`.
