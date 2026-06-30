# Rebuild-Brief — Projekt „dash" (Wohnungsinterface; Sonos S1 jetzt, Hue/u.a. später)

**Stand:** 2026-06-30 · **Zweck:** Handoff für den **From-scratch-Neuaufbau in Claude Code**. **Projektname:** `dash` (Kurz für Dashboard) · **Zielordner:** `~/dev/dash`. Adressat: Claude Code (+ Karsten). **Reife:** Entschieden, wo nicht anders markiert.

> Der bisherige Code (`app.py`, `backend.py`, `web/`) ist **Prototyp = Spezifikation**, nicht Keim. Er hat Anforderungen, Interaktionen und Design-Absicht abgesichert. Neuaufbau auf sauberer Foundation, **kein Recyceln/Faul-Fixen** von Code.

---

## 0. TL;DR

Neu bauen auf **Tokens → Layout-Primitive → Skin (S/W) zuletzt**, mit **mechanisch erzwungener Disziplin** (Lint/CI + Verfassung in Repo-`CLAUDE.md`). Meta-Ziel: **Features mit Claude Cowork trivial erweiterbar — neue Screens = Komposition aus Primitiven + Komponenten-Katalog, kein Pixel-/Layout-Gefrickel.**

---

## 1. Mitnehmen (Spec) vs. neu schreiben (Code)

**Mitnehmen (Wert, reist mit):**
- `DESIGN.md` (Grundgesetze, vier Screens, Flows, Edge Cases), `ARCHITECTURE.md` (Backend-Adapter / HA-Readiness).
- Entscheidungen → `memory/projects/2026-06_sonos-controller.md` (SSoT).
- Recherche → `referenzen/frontend/2026-06_ui-foundation-vergleich.md` (Foundation), `referenzen/sonos/2026-06_oss-sonos-controller-research.md` (OSS).
- Interaktionsmodell + Screen-Ideen (aus Prototyp/Screenshots), feste Geräte/IPs (`guides/netzwerk-stolperfallen.md`).
- Backend-Adapter-**Konzept** (Interface `Backend`, Raum-Slugs, `SocoBackend`/`HaBackend`).

**Neu schreiben:**
- Gesamtes Front-End (HTML/CSS/JS) — **kein** handgerolltes `clamp()`/`--chrome/--ph/--te`.
- Backend-Code sauber neu (Adapter-Pattern beibehalten, Code nicht copy-pasten).

**Prototyp** → `reference/` (read-only) oder Git-History.

---

## 2. Anforderungen (destilliert)

- **Use-case jetzt:** Sonos S1 — Now Playing, Quellen/Favoriten, Räume & Gruppen, Szenen. **Später:** Hue, dann Kalender/Todos/Wetter/Status.
- **Hosting:** Mele (Docker). **LAN-only, kein Login.** Zugriff: bekannte Geräte per **reservierter IP-Whitelist**, sonst **einmalig Passwort** (Remember-Cookie). *(MAC ist für den Webserver nicht sichtbar → IP-Whitelist ist die korrekte Umsetzung der Absicht.)*
- **Faces:** Handy, Tablet, Browser; später evtl. **browserfähiges** E-Ink-Touch-Gerät (E-Ink-Touch-**Steuerung** sonst geparkt).
- **Design (Grundgesetze, aus DESIGN.md):** minimalistisch **flach S/W**, große Tippziele (≥64px), **kein Scrollen → Blättern**, **kein Abdunkeln** (Popover statt Modal), fluid responsive **Portrait UND Landscape**, e-ink-tauglich (diskrete Updates, kein Auto-Poll im Endausbau).
- **Backend-Entkopplung:** UI spricht **nur** das `Backend`-Interface (SoCo jetzt → HA später), eigene Konzepte (Szenen/Namen) backend-agnostisch über Raum-Slugs.
- **META-ZIEL (load-bearing):** mit Claude Cowork **mega-einfach** weiterentwickelbar — **ohne** an Layout-/Design-Specifics zu frickeln. Neue Funktion = vorhandene Primitive/Komponenten komponieren.

---

## 3. Empfohlener Stack (Vorschlag + Begründung)

> **Claude Code soll diesen Vorschlag tief gegenprüfen** (siehe `KICKOFF-CLAUDE-CODE.md`). Hier die Begründung als Ausgangspunkt.

### 3.1 Design-/CSS-Schicht — das Herzstück (löst das Gefrickel)
- **Design-Tokens** (CSS Custom Properties): nicht-lineare **Spacing-Scale**, modulare **Typo-Scale**, Sizes/Radii, **S/W-Skin-Tokens**. Quelle der Wahrheit, eine Datei.
- **Fluide Scales via Utopia** (`clamp()`-Interpolation Min↔Max-Viewport) → **systematisiert genau die per-View-clamp-Mathematik, die wir von Hand gerechnet haben.**
- **Layout-Primitive** (Every Layout): **Cover** (App-Shell, „füllt Viewport, kein Scroll"), **Center**, **Stack**, **Cluster**, **Grid** (auto-fit, Spalten ohne Media-Queries), **Frame** (quadratisches Cover). Bei Bedarf Switcher/Sidebar.
- **CUBE-CSS-Methodik:** Composition-Schicht trägt **kein** Skin; Skin = dünne Token-Schicht **zuletzt**.
- **Komponenten-Katalog** (vorgestylt, aus Primitiven+Tokens): `button`, `iconbtn`, `tile/card`, `segbar` (Tipp-Lautstärke), `overlay` (Popover-Varianten), `pager`, `tabbar`, `appbar`.

**Warum:** Genau das löst das per-View-Gefrickel (Layout intrinsisch/ohne Media-Queries); **Skin-last** macht S/W trivial; flach+winzig = e-ink-freundlich; **Erweiterung = Komposition** (Meta-Ziel). Belege → Dossier.

### 3.2 Komponenten-/JS-Schicht — leicht (Claude Code soll vergleichen)
- **Vorschlag:** **Lit / Web Components** (standards-basiert, ~6 KB, kein Framework-Churn → zukunftssicher, wartungsarm) **oder** **Preact + htm** (~4 KB, React-Ergonomie, ohne Build möglich).
- **Bewusst NICHT** React-Komponenten-Lib (Mantine/MUI/Chakra): Gewicht (~45 KB React + ~140 KB Lib), „soft modern"-Look gegen S/W, e-ink-feindlich (siehe Dossier).
- **Claude Code soll vergleichen:** *vanilla* vs *Lit* vs *Preact+htm* vs *Svelte* — Kriterien: „leicht für Claude generierbar/erweiterbar", „e-ink-/CPU-leicht", „wartbar/zukunftssicher", „minimaler Build".

### 3.3 Build/Tooling — die Guardrails (erzwingen Disziplin)
- **Vite** (dev/build/minify, minimale Config). **stylelint** mit Regeln, die **rohe px-Werte / Nicht-Token-`clamp()` in Komponenten verbieten**. **prettier**. **CI-Check** (Lint + Build + Smoke).
- *Das* ist der Mechanismus gegen „später schummeln sich Lokal-Fixes rein" — nicht der gute Wille.

### 3.4 Backend
- **Python + FastAPI** (typisiert, **async** → passt zur HA-**WebSocket**-Zukunft) mit **Backend-Adapter** (`SocoBackend` → `HaBackend`). *(Flask ginge auch; FastAPI ist für async/HA zukunftssicherer — Claude Code soll FastAPI vs Flask vs node-ts kurz gegenchecken.)*
- **Docker** auf Mele; **Caddy** Reverse-Proxy (TLS/Host, schon im Setup); **Middleware:** IP-Whitelist + Passwort/Cookie.

---

## 4. Verfassung (gehört in Repo-Root-`CLAUDE.md`)

Non-negotiables, mechanisch geprüft wo möglich:
1. **Tokens zuerst. Nur Primitive fürs Layout. Skin zuletzt.**
2. **KEINE Magic-Numbers / `clamp()` außerhalb der Scale-Tokens. Kein Inline-Style. Kein per-View-CSS.** (stylelint erzwingt.)
3. **UI spricht nur das `Backend`-Interface** — nie SoCo/HA direkt.
4. **Neue Screens = Komposition** aus Primitiven + Komponenten-Katalog. Neue Werte **nur als Token**.
5. **Verifizieren vor „fertig":** Lint grün, Build ok, Boot/Routen geprüft.
6. **Bei jeder Abweichung:** explizite Exception dokumentieren (ADR/Kommentar), nie still hinbiegen.

---

## 5. Ordnerstruktur (Vorschlag)

```
/ (repo root)
  CLAUDE.md              # Verfassung (Abschnitt 4) + Pflicht-Lektüre
  README.md
  docs/
    DESIGN.md  ARCHITECTURE.md
    adr/ 0001-eigenes-frontend.md 0002-backend-adapter-ha.md ...
  web/
    tokens/      # scale.css (Utopia), sizes.css, skin-bw.css
    primitives/  # cover, center, stack, cluster, grid, frame
    components/  # button, iconbtn, tile, segbar, overlay, pager, tabbar, appbar
    screens/     # now-playing, quellen, raeume, szenen
    app.(ts|js)  # Router + State + Backend-Client
  server/
    main.py            # FastAPI
    backend/ base.py soco_backend.py ha_backend.py
    auth.py            # IP-Whitelist + Passwort/Cookie
  reference/           # Prototyp, read-only
  stylelint.config.* prettier.* vite.config.* Dockerfile
```

---

## 6. Screens (Spec → Detail in DESIGN.md)

- **Now Playing (Hub):** Gruppenname + ▾-Umschalter, Cover (Frame), Transport, Gruppen-Lautstärke (Tipp-Segbar + ±), Einzel-Lautstärken als Flat-Popover. Komposition: `Cover`-Shell → `Stack`(Cover, Title, Transport-`Cluster`, Volume).
- **Quellen:** Favoriten als `Grid` aus `tile`-Komponenten, `pager`, Tipp = abspielen.
- **Räume & Gruppen:** Block je Gruppe (Name, Chips, now), expliziter **„Gruppieren"-Button** → staged Picker (✓/○ + „Alle Räume" + Übernehmen).
- **Szenen:** `tile`-Raster, Tipp = anwenden; „Verwalten" (speichern aus aktueller Gruppe inkl. Räume/Volumes/Quelle, löschen); Persistenz `scenes.json`.
- Verhalten: kein Abdunkeln (Popover), Blättern statt Scrollen, fluid Portrait+Landscape, große Tippziele.

---

## 7. ADRs (Kurzliste, in `docs/adr/` ausformulieren)

1. **Eigenes Front-End** statt HA-Lovelace (Design-Decke, card-mod fragil).
2. **Backend-Adapter** SoCo→HA; **HA als Integrations-Schicht ab Hue**, eigenes Front-End bleibt.
3. **UI-Foundation = Tokens + Primitive + CUBE**, Skin zuletzt.
4. **LAN-only, IP-Whitelist + Passwort, kein Login.**
5. **E-Ink-Touch-Steuerung geparkt** (später evtl. reines Info-Display, subscription-frei).

---

## 8. Definition of Done (pro Änderung)

- Komponiert aus Primitiven/Komponenten · nutzt nur Tokens · **keine neuen Magic-Numbers** · stylelint+prettier grün · Build ok · Boot/Routen geprüft · ggf. ADR/Exception dokumentiert.

---

## 9. Migration in Claude Code

1. Ordner kopieren: `cp -R ~/Workspaces/__claude/projects/lab/2026-06_sonos-controller ~/dev/dash`.
2. Claude Code dort öffnen (`cd ~/dev/dash && claude`) und den Block aus `KICKOFF-CLAUDE-CODE.md` als erste Nachricht einfügen.
3. Claude Code erledigt dann selbst: Prototyp → `reference/`, `git init` + Baseline-Commit, und auf **Aufforderung** GitHub-Push in das von Karsten manuell angelegte **leere, private** Repo `dash`.
4. **Reihenfolge:** erst Git-Prep, **dann** Stack gegenprüfen (`docs/STACK-FINDINGS.md` + Findings zurück an Karsten/Cowork), **dann** nach Freigabe Foundation bauen, **dann** Screen für Screen migrieren.
5. Cowork-Seite (separat): Trigger-Zeile zum Projekt aus der Workspace-Root-`CLAUDE.md` entfernen (Repo ist eigenständig).
