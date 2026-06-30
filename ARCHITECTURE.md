# Sonos-Controller — Architektur & HA-Readiness

**Stand:** 2026-06-29 · **Reife:** Entwurf · Recherche-Basis: HA REST + WebSocket API.

Ziel: heute auf SoCo bauen, später **mit minimalem Aufwand** auf Home Assistant umstellen *und* um Geräte (Hue-Licht) erweitern — ohne Rewrite.

## HA spricht ein einfaches Muster

- **Entities** mit `entity_id` (`media_player.wohn`, `light.kueche`), `state` (`playing`/`paused`/`idle`/`on`/`off`) + `attributes` (`volume_level` 0–1, `media_title`/`media_artist`, `entity_picture` = Cover, `source`/`source_list` = Sonos-Favoriten, `group_members`).
- **Lesen:** REST `GET /api/states`. **Echtzeit:** WebSocket `subscribe_events`(state_changed) → Push.
- **Steuern:** Service-Call `<domain>.<service>` + `service_data{entity_id,…}` (REST `POST /api/services/<d>/<s>` oder WS `call_service`). Auth: Header `Authorization: Bearer <Long-Lived-Token>`.
- **Sonos-Services:** `media_play`/`media_pause`/`media_next_track`/`media_previous_track`, `volume_set`, `volume_mute`, `join`/`unjoin` (Gruppen), `select_source` (= Sonos-Favoriten), `play_media`/`search_media`.
- **Hue-Services:** `light.turn_on` (brightness/color) / `turn_off` / `toggle`.

## Bauregeln (damit Umstieg + Erweiterung billig bleiben)

1. **UI ↔ nur Adapter (Port).** UI/HTTP-Schicht ruft *nie* SoCo direkt, sondern ein Interface. Zwei Implementierungen: `SocoBackend` (jetzt), `HaBackend` (später). Wechsel = eine Config-Zeile.
2. **Domänenmodell HA-förmig.** Eigene, UI-freundliche Typen, die sich 1:1 auf HA-Entities mappen lassen: `Player{id,name,state,volume(0–100),mute,now{title,artist,album,artUrl},groupMembers[],sources[]}`, später `Light{id,name,on,brightness}`. Volumen/State-Strings normalisiert (Adapter rechnet 0–1 ↔ 0–100 um).
3. **Stabile IDs = Raum-Slugs** (`wohn`, `spielzimmer`). Beide Backends mappen darauf (SoCo: Raumname/UID; HA: `entity_id`). So überleben Szenen + Config einen Backend-Wechsel.
4. **Unsere Konzepte in UNSERER Config**, backend-agnostisch: Szenen, gespeicherte Gruppen/Namen, Schnellquellen — referenzieren nur Raum-Slugs, leben nie in SoCo/HA. Bleiben über jeden Wechsel gültig.
5. **State als Strom denken.** Unsere API liefert einen `state`-Snapshot (jetzt per Poll dahinter), aber so strukturiert, dass später ein Push-Kanal (SSE/WS) ergänzbar ist. `HaBackend` abonniert HA-WebSocket → echtes Push; `SocoBackend` pollt intern. UI merkt keinen Unterschied.
6. **Capabilities/Feature-Flags.** Adapter meldet, was er kann; UI blendet nicht unterstützte Aktionen sauber aus.
7. **Config extern** (welcher Adapter; HA-URL + Token bzw. SoCo-Seed-IPs).

## Adapter-Interface (Skizze)

```python
class Backend(Protocol):
    def get_state(self) -> StateSnapshot: ...   # players (+ später lights), Gruppen, now-playing
    def play(self, room): ...
    def pause(self, room): ...
    def next(self, room): ...
    def previous(self, room): ...
    def set_volume(self, room, level): ...      # 0–100, rastet auf 5%
    def set_mute(self, room, on): ...
    def group(self, room, into_room): ...
    def ungroup(self, room): ...
    def list_sources(self, room) -> list[Source]: ...
    def play_source(self, room, source_id): ...
    # später:
    def set_light(self, light_id, on=None, brightness=None): ...
```

`SocoBackend` füllt das via SoCo; `HaBackend` via REST/WebSocket-Service-Calls. Die UI kennt nur `Backend`.

## Der Licht-Hebel (wichtig)

SoCo kann **nur Sonos** — Licht geht damit nicht. Genau **Hue ist der Moment, HA drunterzuschieben:** HA steuert Sonos *und* Hue über dieselbe API. Weil unser Adapter die `set_light`-Fähigkeit von Anfang an kennt, schaltet der `HaBackend` Hue quasi mit frei — die UI bekommt nur eine „Licht"-Zeile dazu, kein neuer Unterbau. (Alternative ohne HA: ein separater kleiner Hue-Adapter gegen die lokale Bridge-API — möglich, aber mehr Eigenpflege.)

## Fazit

HA-Umstieg = `SocoBackend` → `HaBackend` tauschen (UI + Szenen + Config bleiben). Hue = Fähigkeit war schon vorgesehen. **Kein Rewrite, kein From-Scratch.**
