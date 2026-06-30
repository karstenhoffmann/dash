# dash

Lokales Wohnungsinterface. **Jetzt:** Sonos S1. **Später:** Hue, Kalender, Todos, Wetter, Status.
Minimalistisch flach S/W, große Tippziele, Blättern statt Scrollen, e-ink-tauglich. **LAN-only, kein Login.** Hosting: Mele (Docker).

## Vor jeder Änderung lesen
- [`CLAUDE.md`](CLAUDE.md) — **Verfassung** (gelockter Stack, Non-negotiables, Definition of Done)
- [`docs/DESIGN.md`](docs/DESIGN.md) — Grundgesetze, Screens, Flows, Edge Cases
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Backend-Adapter / HA-Readiness
- [`docs/STACK-FINDINGS.md`](docs/STACK-FINDINGS.md) — Stack-Entscheid je Schicht (recherchiert)
- [`docs/adr/`](docs/adr/) — verbindliche Entscheidungen (Abweichung nur per neuem ADR)

## Stack (kurz)
Frontend **Preact + htm** (Light DOM, no-build, vendored ESM) · Layout **Every-Layout-Primitive** als globale CSS-Klassen · **CUBE**-Methodik · **Utopia**-`clamp()`-Scales · **geschlossene Tokens** · Skin (S/W) zuletzt · Guardrails **stylelint + prettier + CI** · Backend **FastAPI** + Adapter (`SocoBackend` → `HaBackend`).

## Struktur
```
web/        Frontend (no-build, von FastAPI ausgeliefert)
  tokens/     scale.css (Utopia) · sizes.css · skin-bw.css   ← einzige Magic-Number-Quelle
  primitives/ cover, center, stack, cluster, grid, frame      ← globale Klassen
  vendor/     lokal vendored Preact + htm (committed, offline)
  base.css · index.html · app.js
server/     FastAPI (main.py) + backend/ (base.py Port, soco_backend.py, ha_backend.py) + auth.py
scripts/    gen-scales.mjs (Utopia-Token-Generator)
docs/       DESIGN, ARCHITECTURE, STACK-FINDINGS, Dossiers, adr/
reference/  Prototyp = read-only Spezifikation (nicht recyceln)
```

## Lokal starten (MacBook, im selben LAN wie die Speaker)
```sh
# Frontend-Guardrails (Node)
npm install
npm run check                       # stylelint + prettier

# Backend (Python)
python3 -m venv .venv && . .venv/bin/activate
pip install -r server/requirements.txt
python -m uvicorn server.main:app --reload --port 8099
```
Dann <http://localhost:8099>. `python -m server.smoke` prüft Routen + Backend-Port (wie CI).

### Konfiguration (ENV, optional)
| Var | Default | Zweck |
|---|---|---|
| `DASH_BACKEND` | `soco` | `soco` \| `ha` |
| `DASH_SOCO_SEED_IPS` | — | feste Speaker-IPs (kein Multicast), Komma-getrennt |
| `DASH_HA_URL` / `DASH_HA_TOKEN` | — | für `HaBackend` (später) |
| `DASH_IP_WHITELIST` | — | bekannte Geräte-IPs (LAN-Zugriff ohne Passwort) |
| `DASH_PASSWORD` | — | einmaliges Passwort (Remember-Cookie). Ohne Whitelist+Passwort: LAN offen |

## Status
**Foundation steht** (Tokens · Primitive · Skin · Preact-Shell · FastAPI-Adapter-Skelett, alles verifiziert). **Als Nächstes:** Screens als Kompositionen — Now Playing, Räume & Gruppen, Quellen, Szenen (siehe `docs/DESIGN.md`) + echte SoCo-Verdrahtung im `SocoBackend`.
