# UI-Foundation für das Wohnungsinterface — Recherche & Gegenüberstellung

**Stand:** 2026-06-30 · **Reife:** Recherche-Ergebnis (Quellen geprüft) · **Kontext:** Sonos-Controller → erweiterbares Wohnungsinterface (Sonos S1, Hue, Kalender, Todos, Wetter), mehrere Panels (E-Ink-Wand, Tablet/TFT, Handy), Stil = minimalistisch flach S/W, Ziel = wenig Pflege.

## Frage

Welcher **Layout-/Front-End-Unterbau** liefert „fluides responsives Layout out of the box" (Schluss mit per-View-Gefrickel), trennt **Layout von Skin** (S/W zuletzt), bleibt **wartungsarm** und ist **e-ink-tauglich**?

---

## TL;DR — Empfehlung

1. **Unterbau für das interaktive Front-End: Layout-Primitive + Design-Tokens + fluide Scales in reinem CSS** — *Every Layout* (Cover/Center/Stack/Cluster/Grid/Frame) + *CUBE-CSS*-Schichtung + *Utopia*-generierte fluide Typo-/Space-Scales + kleines S/W-Token-Set. Leichtgewichtig, kein Framework/Build, Skin zuletzt, e-ink-freundliche Ästhetik. **Genau das löst das „jeden View einzeln fixen"-Problem.**
2. **Keine React-Komponenten-Lib als Fundament** (React+Build+Bundle, „soft modern"-Look gegen unseren S/W-Stil, e-ink-feindlich). Falls je nötig: **shadcn/ui** (Code gehört dir, am ehesten neutral) — aber nur wenn viele komplexe Komponenten gebraucht werden. Tailwind höchstens als optionale „Delivery"-Schicht.
3. **Home Assistant als Backend, nicht als UI.** Custom-Front-End über HA-WebSocket/REST ist ein **offiziell unterstütztes Muster**. Lovelace als UI hat eine Design-Decke; der Polish-Weg (Mushroom + card-mod) ist **fragil** (bricht bei HA-Updates).
4. **Gating-Entscheidung (von Karsten):** Ist die Wand ein **Touch-TFT** oder **echtes E-Ink**? Das ändert die Architektur (s.u.) grundlegend.

---

## Die wichtigste Erkenntnis: E-Ink ≠ interaktive Web-App

Die E-Ink-Recherche dreht die Frage teilweise um. **Echtes E-Ink läuft keine interaktive SPA gut** — und der durchgängige Konsens erfolgreicher Projekte ist: **nicht** die Live-App aufs Gerät, sondern **serverseitig zu einem Bild rendern** und dem Gerät das fertige Bild schicken (TRMNL-Muster), oder geänderte Kacheln streamen.

Gründe (Physik):
- **Langsamer Refresh:** Voll-Refresh ~600–900 ms (kleine Panels), Inkplate 6 = 1,26 s; **Farb-E-Ink 15–19 s** (M5Paper Color). Quellen: [orientdisplay](https://orientdisplay.com/why-does-e-ink-refresh-slowly/), [Soldered Inkplate 6](https://soldered.com/products/inkplate-6-6-e-paper-board), [CNX M5Paper Color](https://www.cnx-software.com/2026/05/15/m5stack-papercolor-esp32-s3-devkit-features-4-inch-e-ink-spectra-6-color-display/).
- **Ghosting** durch Teil-Refresh → periodischer Voll-„Flash" nötig. [Pervasive Displays](https://www.pervasivedisplays.com/how-e-paper-works/fast-update-refresh/).
- **Schwache CPUs** (ESP32 ~240 MHz / alte E-Reader) → häufiges React-DOM-Re-Rendering doppelt falsch.
- **Design-Regeln** (E-Ink-Browser-Entwickler): „weniger Repaints, kleinere Repaint-Fläche", **Animationen entfernen**, **nicht scrollen sondern blättern**, und **Abdunkel-/Overlay-Effekte sind explizit schädlich** (lösen Vollbild-Flash aus). [EinkBro](https://medium.com/einkbro/web-browser-for-android-e-ink-devices-c78b680edf98).

→ **Validiert unsere bisherigen Design-Entscheidungen** (kein Abdunkeln, Blättern statt Scrollen, flacher Hochkontrast). Unser Instinkt war richtig — nur die Umsetzung war handgefrickelt statt systematisch.

**Konsequenz:** Es gibt zwei verschiedene Rendering-Ziele:
- **Interaktive Faces (Handy, Tablet, Touch-TFT):** echte Web-App. Hier glänzt der leichte Primitive-Ansatz.
- **Echte E-Ink-Wand:** besser **separater, serverseitig gerenderter „Glance"-View** (statisches Bild, alle paar Minuten), Steuerung läuft auf Handy/Tablet. Nicht unsere interaktive SPA aufs E-Ink zwingen.

---

## Gegenüberstellung der vier Ansätze

| Kriterium | (1) Primitive + Tokens (Vanilla) | (2) Tailwind | (3) React-Komp.-Libs | (4) HA-Lovelace |
|---|---|---|---|---|
| „Layout out of the box" | **Ja** (Cover/Grid/Switcher reflowen intrinsisch, ohne Media-Queries) | Nein (du komponierst alles selbst) | Komponenten ja, Layout teils | Karten-Raster, begrenzt |
| Layout↔Skin getrennt | **Ja, by design** (CUBE Composition verbietet Skin) | Teils (Tokens ja, Markup vermischt) | Lib-Look eingebacken | Theme = nur CSS-Variablen |
| S/W-Minimal erreichen | **Trivial** (Skin = dünne Token-Schicht) | Machbar | shadcn/Radix ok; Mantine/Chakra „soft"; **MUI am schwersten** | Nur via Custom Cards + card-mod |
| Gewicht | **Winzig**, kein JS-Framework, kein Build | ~6–10 kB CSS nach Purge, **Build nötig** | **React ~45 kB + Lib** (MUI/Chakra/Mantine je ~143 kB gz Vollimport), Build nötig | HA-Frontend (schwer) |
| E-Ink-Tauglichkeit | **Am besten** (klein, flach, statisch) | ok (CSS), aber Build | **Schlecht** (DOM-Re-Render, soft-Look) | Schlecht (schwer); E-Ink via ESPHome separat |
| Wartung | Kein Upgrade-Treadmill (Plain CSS) | Mäßig (Build-Toolchain) | **Breaking Majors** (Chakra v3 Rewrite, Mantine v7 Emotion-Drop, MUI v7) | **card-mod bricht** bei HA-Updates (2025.1, 2026.3) |
| „Wie vom Profi" | Über Disziplin (Scales/Tokens) erreichbar | Über Disziplin | Schnell hübsch, aber Lib-Look | „Dashboard"-Anmutung |

---

## Detail-Befunde (mit Quellen)

### (1) Layout-Primitive + Tokens — bester Fit
- **Every Layout** = ~12 Primitive (Stack, Box, Center, Cluster, Sidebar, Switcher, **Cover**, **Grid**, **Frame**, Reel, Imposter, Icon), responsiv **ohne Media-Queries** (Flexbox/Grid/`clamp`/`min`/`max`). [every-layout.dev/layouts](https://every-layout.dev/layouts/)
  - **Cover** = `min-block-size: 100vh` (→ besser `100dvh`), Header oben / zentrierte Mitte / Footer unten → **genau unsere App-Shell + „füllt Viewport, kein Scroll"**. [Cover](https://every-layout.dev/layouts/cover/)
  - **Grid** = `repeat(auto-fit, minmax(min(<ideal>,100%), 1fr))` → Spalten reflowen nach Breite, **null Media-Queries** → ersetzt unsere `--cols`-Logik. [Grid](https://every-layout.dev/layouts/grid/)
  - **Frame** = `aspect-ratio` + `object-fit:cover` → unser quadratisches Cover.
- **CUBE CSS** (Andy Bell): Composition-Schicht **darf kein Skin** (keine Farbe/Schatten/Pixel-Perfektion) → Layout/Skin-Trennung ist eingebaut. [cube.fyi/composition](https://cube.fyi/composition)
- **Open Props** = fertige CSS-Custom-Property-Tokens (Spacing, Sizes, Typo…), JIT-Plugin shippt nur Genutztes. [GitHub](https://github.com/argyleink/open-props)
- **Utopia** = generiert **fluide Typo-/Space-Scales mit `clamp()`** zwischen Min-/Max-Viewport → **systematisiert genau die per-View-`clamp()`-Mathematik, die wir von Hand gerechnet haben** ("guards against infinite magic-number sizes"). [Smashing/Utopia](https://www.smashingmagazine.com/2021/04/designing-developing-fluid-type-space-scales/), [utopia.fyi](https://utopia.fyi/type/calculator/)
- Browser-Support modern, aber sicher: `aspect-ratio` Baseline seit 2021; `dvh/svh/lvh` Baseline „Widely Available" Juni 2025 (~95 %). [caniuse dvh](https://caniuse.com/viewport-unit-variants)

### (2) Tailwind — Delivery-Schicht, kein Layout-System
- Utility-first, responsive via Prefix (`md:`); **Build nötig** für Produktion (CDN nur Prototyp); Bundle „selten >10 kB" nach Purge (Netflix 6,5 kB). [Tailwind optimizing](https://v3.tailwindcss.com/docs/optimizing-for-production)
- Gibt **gute Default-Tokens**, aber **„kein Layout out of the box"** — du komponierst jeden Layout selbst. Hauptkritik: Markup-Verbosität. [Hovhannisyan](https://www.aleksandrhovhannisyan.com/blog/why-i-dont-like-tailwind-css/)
- Kann mit Utopia kombiniert werden (Plugin existiert). Andy Bell nutzt Tailwind als „U" in CUBE.

### (3) React-Komponenten-Libs — schwerer, Look-Kampf
- Baseline **React+ReactDOM ≈ 45 kB gz**. Voll-Importe: **MUI ≈143 / Chakra ≈143 / Mantine ≈142 kB gz** (Tree-shaking reduziert real); **Radix Themes ≈63 kB**; **einzelnes Radix-Primitive ≈10 kB**. [Bundlephobia react-dom](https://bundlephobia.com/package/react-dom)
- **shadcn/ui** = **kein npm-Paket**, kopiert Radix+Tailwind-Code in dein Repo (du besitzt ihn), Default fast neutral → am ehesten zu S/W; **aber React+Build+Tailwind Pflicht**. [shadcn install](https://ui.shadcn.com/docs/installation)
- **MUI** = Material, injiziert CSS mit höchster Spezifität → **am schwersten zu „ent-materialisieren"**. Mantine/Chakra „soft modern" (rund+Schatten), zentral abrüstbar aber gegen Default. [MUI overrides](https://v3.mui.com/customization/overrides/)
- **Wartung:** Chakra v3 = Fast-Rewrite (viele Breaking Changes); Mantine v7 = Emotion→CSS-Modules-Umbau; MUI v7 = Paket-Layout/Grid-Umbenennung. Codemods vorhanden. [Chakra v3](https://www.chakra-ui.com/docs/get-started/migration)

### (4) HA-Lovelace + Sonos-S1-Fakten
- Lovelace-Theming = **nur CSS-Variablen**; tiefer = Custom Cards (**Mushroom**, **Bubble**, **button-card**) + **card-mod** (CSS-Injektion ins Shadow-DOM). [HA frontend](https://www.home-assistant.io/integrations/frontend/)
- **card-mod bricht** bei HA-Frontend-Updates (dokumentiert 2025.1, 2026.3 — hängt an undokumentiertem internen DOM). [card-mod #595](https://github.com/thomasloven/lovelace-card-mod/issues/595)
- **Custom Front-End über HA WS/REST + Long-Lived-Token (10 J.) = unterstütztes First-Class-Muster** (Companion-Apps, `ha-component-kit`, `ha-fusion`). [HA auth](https://developers.home-assistant.io/docs/auth_api/), [ha-component-kit](https://github.com/shannonhochkins/ha-component-kit)
- **Sonos S1: unterstützt, lokale Steuerung (Local Push, UPnP/SOAP im LAN).** Kern (Play/Pause/Volume/Gruppieren *innerhalb S1*) solide. Caveats: **S1↔S2 nicht gruppierbar**, **Announce/TTS ggf. nicht voll**, Battery braucht Push-Events. [HA Sonos](https://www.home-assistant.io/integrations/sonos/), [Music Assistant Sonos](https://www.music-assistant.io/player-support/sonos/) → **Für unseren Basics-Use-Case (Play/Pause/Volume/Quelle/Gruppen) auf solider Basis.**

---

## „Wie vom Profi gemacht" ist nicht nur Tooling

*Refactoring UI* (Wathan/Schoger): Profi-Anmutung kommt aus **vorab definierter Disziplin** — **nicht-lineare Spacing-Scale** (keine zwei Werte näher als ~25 %), **modulare Typo-Scale** ab 16 px-Basis, **Hierarchie über Gewicht/Farbe statt nur Größe**, **Graustufen zuerst**, **Nähe/Gruppierung** (mehr Abstand um Gruppen als innerhalb). [Refactoring UI summary](https://iamaatoh.com/essays/refactoring-ui.html) → Unser Schmerz kam daher, dass wir das **nicht vorab definiert**, sondern per View nachgezogen haben.

---

## Empfohlener Pfad

1. **Gating-Entscheidung treffen:** Wand-Panel = **Touch-TFT** (interaktive App läuft direkt) **oder echtes E-Ink** (dann separater server-gerenderter Glance-View, Steuerung auf Handy/Tablet).
2. **Front-End neu fundieren (einmalig):** Tokens definieren (Spacing-/Typo-Scale via Utopia/`clamp`, Sizes, S/W-Skin-Tokens) → ~6 Primitive (Cover, Center, Stack, Cluster, Grid, Frame) → bestehende Screens als **Kompositionen** neu bauen → Skin zuletzt. Ersetzt das handgerollte CSS (`--ph/--pd/--chrome/--te`).
3. **Backend-Adapter behalten**, auf HA zeigen (`HaBackend`), sobald **Hue** dazukommt (der „Licht-Hebel").
4. **Bei echtem E-Ink:** separater TRMNL-artiger Glance-View (Server rendert Bild) für die Wand; interaktive Steuerung bleibt App.

## Quellen (Auswahl)
Every Layout / CUBE / Open Props / Utopia (s. Detail-Links oben) · E-Ink: orientdisplay, Pervasive Displays, EinkBro, TRMNL/Kindle-Walkthrough ([intothevoid](https://intothevoid.github.io/posts/repurpose-an-old-kindle-and-use-it-as-an-e-ink-dashboard-2026-05-20.html)), HA Remote-WebView · React-Libs: Bundlephobia, shadcn/Radix/Mantine/Chakra/MUI Docs · HA: home-assistant.io, developers.home-assistant.io, card-mod GitHub, Music Assistant.
