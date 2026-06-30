# Sonos-Controller — Design-Spec

**Stand:** 2026-06-29 · **Reife:** Entwurf/Skizze (Wireframes abgestimmt, Screens noch nicht final) · **Projekt-SSoT:** `memory/projects/2026-06_sonos-controller.md`

Roter Faden für den Bau. Jeder Screen wird gegen diese Prinzipien gebaut und geprüft.

## 1. Zweck & Haltung

- Eigene, **lokale** Steuerung der 5× Gen-1/S1-Sonos. Nur die **Basics** — bewusst *kein* „Empfohlen für dich"-Content-Bloat der Sonos-Apps.
- **Additiv & koexistent:** iPhone (Karsten), Android (Freundin) und offizielle Sonos-S1-App laufen weiter. Mehrere Controller, gemeinsamer Zustand → kein Konflikt (Zustand lebt in den Speakern).
- **Zugang ohne Tamtam:** wer im Heim-WLAN ist, steuert per URL — kein Login, kein App-Store. Optional per Geräte-MAC freigegeben.

## 2. Architektur — „ein Gehirn, viele Gesichter"

- **Gehirn (Backend):** SoCo auf Mele (`~/lab/sonos-controller/`), Seed über feste IPs (keine Multicast-Abhängigkeit). Ein Port: UI + JSON-API zusammen (kein CORS).
- **Gesichter (Clients) gegen dieselbe API:** Web-UI auf TFT (jetzt) + Handys; E-Ink-Touch-Panel an der Wand (später, z.B. M5Paper-Firmware).
- **Backbone-Option:** Wenn Hue + Wand-E-Ink + Mehrnutzer real werden → Home Assistant als Hub (Hue, OpenDisplay-E-Ink, Zugriff „fertig"), mit bewusst minimalistischem Dashboard. Bis dahin reicht die eigene App.

## 3. Design-Grundgesetze

| Gesetz | Bedeutung |
|--------|-----------|
| **E-Ink-nativ** | Tap-getrieben statt Timer-getrieben. Teilrefresh beim Tippen, Vollrefresh beim Wecken. |
| **Grobe Touch-Zonen** | Mindestziel **≥ 64 px** (Wandbedienung, unpräzise), wichtige Aktionen 72–96 px, großzügige Abstände, ganze Zeilen/Kacheln tippbar. Nie „pfriemelig". |
| **Seitenblättern statt Scrollen** | E-Ink hasst Scrollen, liebt Seiten-Flips. Gilt überall (auch TFT/Handy). |
| **Ein Muster für alle Gesichter** | Gleiche Bedienlogik überall. E-Ink-spezifisch nur: S/W-Hochkontrast-Skin, Refresh-Choreografie, Sleep/Wake. |
| **Basics, ruhig, glanceable** | Keine Content-Bühne. |
| **Icons = Lucide-SVG** | Nur saubere Lucide-SVG-Icons, einheitlich. **Nie Emoji.** |
| **Voll responsiv** | Dedizierte, durchdachte Layouts für **Portrait UND Landscape** — nie auf ein Format festgezurrt. |
| **Primitive statt Sonderlocken** | Screens komponieren geteilte Komponenten (`btn`, `segbar`, `overlay`, …). Verhalten/Präsentation an *einer* Stelle (z.B. `OVERLAY_VARIANT` = sheet-top/-bottom/modal); bewusste Abweichung nur als explizite Variante (`{variant}`)/Fork, nie als Einzelfall hingebogen. |

## 4. Screens

Hub-and-Spoke: **Now Playing** ist der Hub; Räume, Quellen, Szenen sind Speichen; Sleep umschließt.

| Screen | Zweck | Kern-Elemente |
|--------|-------|---------------|
| **Now Playing** (Hub) | aktive Gruppe steuern | Gruppenname + ▾-Umschalter, Now-Playing (Cover/Titel), Transport, Gruppen-Lautstärke, Nav zu Räume/Quellen/Szenen |
| **Räume & Gruppen** | live gruppieren, Lautstärke je Raum | Übersicht aller Gruppen + Solo-Boxen; Block antippen → bearbeiten (Räume ✓/○); Kurzname |
| **Quellen** | Quelle wählen + eigene Liste pflegen | Tabs „Favoriten / Schnellquellen", Pager; „Bearbeiten" (eigene Liste sortieren/+/−) |
| **Szenen** | 1-Tipp-Stimmungen + globale Befehle | Kacheln (Raster, Pager) |
| **Sleep** | Ruhe | Cover + Uhr, hält ohne Strom; Tippen weckt (erst Vollrefresh) |

## 5. Gruppen & Szenen — „ein Ding, unterschiedlich voll"

Zwei Ebenen:
- **Live-Gruppe** = echte Sonos-Realität (flüchtig). Mehrere Gruppen + Solo-Boxen = Normalfall. Sonos benennt nur über Räume.
- **Gespeicherte Konstellation/Szene** = unsere Schicht (Config auf Mele; **Sonos speichert keine Gruppennamen**).

Eine **Szene** = bis zu 4 Zutaten: **Räume** (immer) · **Name** (optional) · **Lautstärke(n)** (optional) · **Quelle + Aktion** (optional).
- Nur Räume + Name → „gespeicherte Gruppe" (formt + beschriftet).
- + Lautstärke/Quelle → „volle Szene" (formt + stellt + startet).
- Ohne Räume, nur Aktion → „globaler Befehl" (Pause alle, Auflösen, Play alle).

**Ein Editor** für alle. **Label-Regel:** Live-Gruppe entspricht *exakt* einer gespeicherten Konstellation → Kurzname oben; Teil-Match → Raumliste.

**Anzeige-Orte:** Szenen als Kacheln im Szenen-Screen (optisch eigenständig); Kurznamen im ▾-Umschalter + Übersicht. Gleiche Daten, kontextgerecht.

## 6. Bedien-Bausteine

- **Lautstärke:** Anzeige in 5%-Segmenten, **Eingabe = ganze Leiste antippen** (rastet auf 5%) + große − / + + Mute. Pro Raum: Zeile = Tippzone → öffnet große Einzel-Lautstärke (kein Zielen auf 8-px-Balken).
- **Pager:** ◀ + große nummerierte Kreise + „…" + ▶. ≤ 5 Seiten alle zeigen, sonst „1 … aktuell … letzte". Feste Anzahl je Seite (stabiles Layout). Adaptiv: TFT mehr, E-Ink weniger.
- **Gruppieren:** auswählen (✓/○) statt ziehen.
- **Umblättern:** Pager-Tasten, Wischen, Tippzonen links/rechts; am Panel später physische Tasten.

## 7. E-Ink-Refresh-Modell

Tippen → optimistisch sofort umzeichnen (nur der Bereich), Befehl im Hintergrund. Wecken → Vollrefresh (Geister weg) + frische Daten. Wach → sanftes Mitziehen nur geänderter Bereiche. Ruhe → Sleep-Screen, 0 Strom. Kein Auto-Poll im Schlaf.

## 8. Edge Cases

| Fall | Verhalten |
|------|-----------|
| Nichts läuft (UPnP 701) | „Nichts läuft" + Vorschlag Quelle/Szene, kein toter Play-Knopf |
| Box offline | ausgegraut, nicht gruppierbar |
| Parallel-Steuerung (Freundin/App) | beim Wecken/wach sauber nachziehen |
| Mehrere Gruppen | ▾-Umschalter wählt, welche gesteuert wird |
| Gruppen- vs Einzel-Lautstärke | Gruppe = Master (proportional), je Box = exakt |
| Pause bei Radio | Radio kann nicht echt pausieren → „Pause" = muten (Stream läuft, Play lückenlos); nach 60 Min wirklich pausiert. On-Demand = echtes Pause (positionsgenau). |
| Favorit startet nicht | Hinweis + Fallback über `soco-cli` |
| Backend/Netz weg | „Nicht erreichbar — erneut versuchen" |
| Box nur in *einer* Gruppe | beim Hinzufügen verlässt sie die alte (Sonos-Regel) |
| Teil-Match Konstellation | kein Kurzname → Raumliste |

## 9. Favoriten-Nuance

Sonos-Favoriten: nur **anzeigen + abspielen** (gehören dem Sonos-Konto; auch HA kann sie nicht umbauen). Eigene **„Schnellquellen"-Liste**: voll editierbar (sortieren/+/−), in unserer Config.

## 10. Zukunft (Skizze)

Hue (lokale Bridge-API) als zweites Steuerungs-Thema im selben Bild; Mehrnutzer-Zugriff LAN-gegated. Ggf. Auslöser für HA-Backbone (siehe §2).

---

## Status der Screens

| Screen | Wireframe | Final ausdetailliert |
|--------|-----------|----------------------|
| Now Playing | ✓ | echt gebaut (v2 gegen Adapter), Test am MacBook |
| Räume & Gruppen | ✓ | gebaut: Übersicht (Gruppen-Blöcke + Chips) + Editor (Räume ✓/○, live join/ungroup); offen: Lautstärke je Raum inline |
| Quellen | ✓ | Favoriten gebaut (Adapter, Test am MacBook); offen: Pager + Schnellquellen |
| Szenen | ✓ | v1 gebaut: Kacheln (Tap=anwenden) + Verwalten (speichern aus aktueller Gruppe inkl. Räume/Volumes/Quelle, löschen); Persistenz `scenes.json`. Offen: Editor (Räume/Volumes/Quelle gezielt ändern), Pager |
| Sleep | ✓ | — |
