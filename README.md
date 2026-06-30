# Sonos-Controller — Working-Folder

Eigenbau-Steuerung für die 5× Gen-1/S1-Sonos. **Projekt-SSoT (Status, Entscheidungen):** `memory/projects/2026-06_sonos-controller.md`. **Recherche:** `referenzen/sonos/2026-06_oss-sonos-controller-research.md`.

Dieser Ordner ist self-contained und wird später der **Repo-Root** (git init → GitHub → Claude Code).

## Konventionen — VOR jeder Änderung lesen

Agent-Regeln (Non-negotiables + Pflicht-Lektüre) → **`CLAUDE.md`** in diesem Ordner (die spätere Repo-Root-Regel-Datei). Detail-Referenzen: `DESIGN.md` (Grundgesetze, Screens, Flows) + `ARCHITECTURE.md` (Backend-Adapter).

## Design-Spec

Gesamtdesign (Prinzipien, vier Screens, Flows, Gruppen/Szenen-Modell, Touch-Regeln, Seitenblättern, Edge Cases) → `DESIGN.md`. Referenz vor dem finalen Ausdetaillieren je Screen.

Backend-Architektur & HA-Readiness (Adapter-Interface, damit SoCo→HA-Wechsel + Hue-Erweiterung später ohne Rewrite gehen) → `ARCHITECTURE.md`.

## Phase 1: soco-cli-Schnelltest auf Mele

Reines lokales UPnP-Tooling, isoliert im venv. **Read-only Test** — ändert nichts an den Speakern. Mele-Footprint: `~/lab/sonos-controller/` (venv) + `~/.soco-cli/` (Speaker-Cache, beim ersten Discover) — beide entfernt das Uninstall-Skript.

Vom MacBook aus (Skripte werden über SSH auf Mele ausgeführt, nichts wird dauerhaft auf Mele kopiert außer dem venv):

```
cd ~/Workspaces/__claude/projects/lab/2026-06_sonos-controller

ssh -t mele 'dpkg -s python3-venv >/dev/null 2>&1 || sudo apt-get install -y python3-venv'

ssh mele 'bash -s' < scripts/mele-install.sh
ssh mele 'bash -s' < scripts/mele-test.sh
```

Die erste Zeile (mit `-t`, einmalig) stellt nur sicher, dass das `venv`-Modul da ist — fragt ggf. dein Mele-sudo-Passwort. Danach laufen Install und Test ohne sudo.

### Erwartung im Test
- **Discovery** (`sonos-discover`): findet idealerweise alle 5 Speaker. Wenn nicht → Multicast über WLAN/Repeater zickt (nicht schlimm, siehe nächster Punkt).
- **Direkt-IP** (`sonos 192.168.0.157 state/track/volume`): muss klappen — Unicast an die feste IP, unabhängig von Multicast. Das ist der verlässliche Pfad.

### Restlos aufräumen
```
ssh mele 'bash -s' < scripts/mele-uninstall.sh
```
Entfernt `~/lab/sonos-controller` komplett. (Das apt-Paket `python3-venv` bleibt — harmlos.)

## Phase 2: Lokaler Controller (Backend + Touch-UI) — Test am MacBook

Schlankes Backend (`app.py`, Flask + SoCo) + Touch-UI (`web/index.html`) auf **einem** Port (kein CORS). Nutzt die festen Sonos-IPs als Seed → keine Multicast-Discovery nötig. Läuft identisch am MacBook (Dev/Test, hängt im selben LAN wie die Speaker) und später auf Mele.

**Am MacBook starten:**
```
cd ~/Workspaces/__claude/projects/lab/2026-06_sonos-controller
bash scripts/run-local-macbook.sh
```
Legt ein lokales `.venv` an (gitignored), installiert Flask+SoCo, startet auf `http://localhost:5005` und öffnet den Browser. Strg+C beendet.

**Gebaut & am MacBook getestet:**
- **Now Playing** (Hub): Cover/Titel je Gruppe, Play/Pause/Skip, Gruppen-Lautstärke (proportional) + Einzel-Lautstärken je Box (− / Tipp-Leiste / +) als Flat-Popover, Gruppen-Umschalter, Zustände (läuft/pausiert/nichts läuft/nicht erreichbar).
- **Quellen** (Spoke): Sonos-Favoriten als Kacheln, Tipp → spielt auf der aktiven Gruppe → zurück zum Hub. Tab-Router; Räume/Szenen folgen.
- UI pollt alle 5 s.

**Verifiziert (Sandbox, soco 0.31.1):** bootet, Routen + SoCo-Methodennamen stimmen. Live gegen echte Speaker = dein Test. Wackelkandidat: Favoriten-Playback (DIDL-Metadaten) — `play_source` nutzt `play_uri(fav.get_uri(), meta=resMD)` (das Paar, das die S1-App beim Antippen sendet). Falls ein Favorit nicht startet, melden → dann justiere ich (Container/Radio-Sonderfall, ggf. `force_radio`).

**Aufräumen MacBook:** `rm -rf .venv` (kein System-Eingriff, alles im Projektordner).

## Code & Scripts

| Datei | Zweck |
|-------|-------|
| `app.py` | HTTP/UI-Schicht (Flask) — spricht nur das `Backend`-Interface |
| `backend.py` | Adapter-Interface + `SocoBackend` (stabile Raum-Slugs) |
| `ha_backend.py` | Platzhalter für späteren `HaBackend` (HA-Umstieg) |
| `web/index.html` | Touch-UI „Now Playing" (Hochkontrast, große Tippziele, Tipp-Lautstärke) |
| `scripts/run-local-macbook.sh` | Lokal am MacBook starten (venv + Browser) |
| `scripts/mele-install.sh` | soco-cli in venv unter `~/lab/sonos-controller/` installieren |
| `scripts/mele-test.sh` | Read-only-Funktionstest: Discovery + Direkt-IP-Status |
| `scripts/mele-uninstall.sh` | Footprint restlos entfernen |
