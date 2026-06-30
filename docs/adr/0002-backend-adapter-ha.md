# ADR-0002: Backend-Adapter (SoCo jetzt → Home Assistant später)

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Heute steuern wir Sonos S1 lokal via SoCo (UPnP/SOAP). Später kommt Hue dazu — der Moment, HA als Hub unterzuschieben (HA steuert Sonos *und* Hue über dieselbe API). Ein Rewrite soll vermieden werden.

## Entscheidung
Die UI spricht **ausschließlich** ein `Backend`-Interface (Port). Zwei Implementierungen: `SocoBackend` (jetzt), `HaBackend` (später). Wechsel = eine Config-Zeile. Domänenmodell **HA-förmig** (Player/Light), Volumen/State normalisiert. **Stabile IDs = Raum-Slugs** (`wohn`, `bad`). Eigene Konzepte (Szenen, gespeicherte Gruppen, Schnellquellen) leben in **unserer** Config, backend-agnostisch.

## Konsequenzen
- SoCo→HA-Umstieg + Hue-Erweiterung ohne Rewrite (Details: [`ARCHITECTURE.md`](../ARCHITECTURE.md)).
- State als Snapshot strukturiert, später um Push-Kanal (SSE/WS) ergänzbar; `HaBackend` abonniert HA-WebSocket.
- Capabilities/Feature-Flags: Adapter meldet Fähigkeiten, UI blendet Nicht-Unterstütztes aus.

## Alternativen
- **UI direkt gegen SoCo:** verworfen — bindet die UI an ein Backend, HA-Umstieg = Rewrite.
- **Separater Hue-Adapter statt HA:** möglich, aber mehr Eigenpflege; HA bündelt Sonos+Hue.
