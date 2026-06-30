# Kickoff-Prompt für Claude Code — Projekt „dash"

> **So benutzen:**
> 1. Projektordner an den Zielort kopieren: `cp -R ~/Workspaces/__claude/projects/lab/2026-06_sonos-controller ~/dev/dash`
> 2. Claude Code dort öffnen: `cd ~/dev/dash && claude`
> 3. Den Block unten (zwischen den Linien) **komplett als erste Nachricht** einfügen.
>
> Claude Code bereitet zuerst Git vor, **recherchiert/prüft dann den Stack — und baut noch nichts.** Ergebnis: ein kopierbares Findings-Dokument, das Karsten zurück in Claude Cowork legt, bevor gebaut wird.

---

Du bist Claude Code und übernimmst den **From-scratch-Neuaufbau** dieses Projekts. Es heißt **`dash`** (Kurzform für Dashboard / Wohnungsinterface): jetzt Sonos S1, später Hue, Kalender, Todos, Wetter, Status. **Baue in diesem Schritt noch nichts** — erst Git vorbereiten, dann Recherche/Prüfung.

## Teil 1 — Repo & Git vorbereiten (via `git`, GitHub-Repo legt Karsten manuell an)

1. **Prototyp wegräumen:** Lege `reference/` an und verschiebe den bestehenden Prototyp dorthin (read-only Spezifikation, **nicht** recyceln): `app.py`, `backend.py`, `ha_backend.py`, `web/`, `scripts/`, `requirements.txt`, `scenes.json` (falls vorhanden). **Behalte im Root:** `CLAUDE.md`, `README.md`, `DESIGN.md`, `ARCHITECTURE.md`, `REBUILD-BRIEF.md`, `KICKOFF-CLAUDE-CODE.md`, `.gitignore`.
2. **`.gitignore` prüfen/ergänzen:** muss `.venv/`, `__pycache__/`, `*.pyc`, `.DS_Store`, `scenes.json`, später `node_modules/`, `dist/` abdecken.
3. **Git initialisieren:** `git init`, alles stagen, erster Commit: `chore: Prototyp + Rebuild-Brief als Baseline`. Branch `main` (`git branch -M main`).
4. **GitHub-Push (mit Handshake):** **Stoppe** und bitte Karsten, ein **leeres, privates** GitHub-Repo namens **`dash`** anzulegen (github.com/new — **ohne** README, **ohne** .gitignore, **ohne** Lizenz). Sobald er bestätigt und Username/URL nennt: `git remote add origin <URL>` → `git push -u origin main`. Erst danach weiter.

## Teil 2 — Recherche & Stack-Prüfung (immer noch nicht bauen)

**Lies zuerst (Pflicht):** `REBUILD-BRIEF.md` (Ziele, Anforderungen, vorgeschlagener Stack mit Begründung), `DESIGN.md`, `ARCHITECTURE.md`, `reference/` (Prototyp als Spec), sowie die im Brief referenzierten Dossiers, soweit vorhanden.

**Dann recherchiere tief und prüfe kritisch**, ob der im Brief vorgeschlagene Stack für **diesen** Anwendungsfall und **diese** Ziele wirklich der beste ist. Gewichte besonders:
1. **Mega-einfache Weiterentwicklung mit einem KI-Assistenten (Claude Cowork)** — neue Screens/Features als reine Komposition aus Primitiven + Komponenten-Katalog, **ohne** an Layout-/Responsive-/Design-Specifics zu frickeln. Welcher Stack ist dafür am robustesten und am wenigsten fehleranfällig für KI-generierte Änderungen?
2. **Einfachheit, Wartbarkeit, Zukunftssicherheit** (wenig Abhängigkeiten, kein Framework-Churn, langlebige Web-Standards).
3. **Leichtgewicht / e-ink- und schwache-CPU-Tauglichkeit** (flach, kleine DOM, kein schwerer Runtime).
4. **Strikte Trennung Layout ↔ Skin** (Tokens + Primitive + Skin zuletzt) und **mechanisch erzwingbare Disziplin** (Lint/CI, die Magic-Numbers/per-View-CSS verbietet).
5. **Backend-Adapter** (SoCo jetzt → Home Assistant via WS/REST später), Hosting auf einem kleinen Homeserver (Docker), LAN-only-Zugriff (IP-Whitelist + Passwort, kein Login).

**Konkret zu vergleichen / zu entscheiden:**
- Komponenten-/JS-Schicht: **vanilla** vs **Lit/Web Components** vs **Preact + htm** vs **Svelte** (Gewicht, Build-Bedarf, KI-Erweiterbarkeit, Langlebigkeit). Begründete Wahl.
- Design-System-Bausteine: **Every Layout-Primitive + CUBE-CSS + Utopia-Scales + Tokens** — adoptieren, ersetzen oder ergänzen? Open Props ja/nein?
- Build/Lint: **Vite + stylelint + prettier + CI** — passend, oder simpler/anders?
- Backend: **FastAPI** vs **Flask** vs **Node/TS** für den Adapter (async/HA-WebSocket-Zukunft bedenken).
- Stelle ausdrücklich dar, **wo du dem Vorschlag aus dem Brief widersprichst** und warum.

**Arbeitsweise:** echte Web-Quellen, Behauptungen adversarial prüfen, konkrete Zahlen (Bundle-Größen etc.) mit Quelle, Unsicheres flaggen.

**Liefere am Ende EIN einziges, in sich geschlossenes Markdown-Dokument** (für einfaches Kopieren), mit:
- **Empfehlung** (klarer Stack-Entscheid je Schicht) + je 1–2 Sätze Begründung.
- **Vergleichstabelle** der Alternativen je Schicht.
- **Abweichungen** vom Brief-Vorschlag (falls vorhanden) + Begründung.
- **Offene Entscheidungen / Rückfragen an Karsten.**
- **Quellenliste** (URLs).

Gib dieses Dokument als Markdown im Chat aus (zum Kopieren) **und** speichere es als `docs/STACK-FINDINGS.md` (committe es). **Baue erst nach Karstens Freigabe.**
