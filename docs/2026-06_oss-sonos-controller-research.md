# OSS Sonos-Controller für S1/Gen-1 — Recherche & Empfehlung

**Stand:** 2026-06-29 · **Zweck:** Entscheidungsgrundlage für eigenen Sonos-Controller (fertige Lösung vs. Eigenbau) für Karstens 5× Gen-1/S1-Speaker.

## Kontext & Kriterien

- **Hardware:** 2× Play:1, 1× Play:3, 2× Play:5 (alle Gen-1, **S1-only**), jetzt auf SonosNet, feste IPs.
- **Muss:** lokale Steuerung (UPnP/SOAP Port 1400, SSDP-Discovery), **keine Cloud-API** (die ist S2-/Cloud-zentriert und für S1 kein Fit), self-host auf bescheidener Linux-Box (Mele 4 GB / Synology), **koexistent** mit offiziellen iOS/Android-S1-Apps.
- **Bonus:** e-ink/Touch-Frontend, Event-getriebene Status-Updates, Gruppierung, Favoriten/Presets, Now-Playing mit Cover.

## Kernbefund

„Alt" ≠ „tot". Deine S1-Geräte sprechen das **lokale UPnP-Protokoll**, das sich seit Jahren nicht ändert — deshalb sind viele Libraries alt, funktionieren aber. Die *neue* offizielle Sonos-**Cloud**-API ist der falsche Weg (cloud-abhängig, S2-fokussiert, widerspricht „lokal & resilient"). Entscheidend ist daher **Wartungsstand der Library bei gleichem Protokoll** — nicht „neu vs. alt".

## Vergleich

| Lösung | Typ | Stack | Wartung (2026) | S1 | UX | e-ink-Eignung |
|--------|-----|-------|----------------|----|----|---------------|
| **Home Assistant + custom-sonos-card** (punxaphil) | Fertig (UI+Server) | HA (Python) + Lovelace-Card (TS/Lit) | **Aktiv** (Card v10, 2025-Updates) | ✅ | **Sehr gut** (Gruppen, Queue, Favoriten, Suche, Media-Browser, Sleep) | gut (HA-Dashboard im Browser; e-ink-Dashboards existieren) |
| **soco-cli (HTTP-API-Modus)** | Backend (kein UI) | Python (SoCo) | **Aktiv** (v0.4.x) | ✅ | n/a (API) | indirekt (eigene UI davor) |
| **SoCo** | Library | Python 3.8+ | **Aktiv** (Team, 0.30.x / 0.32-dev) | ✅ | n/a | Basis für Eigenbau |
| **@svrooij/sonos (node-sonos-ts)** + sonos2mqtt | Library + MQTT-Bridge | TypeScript | **Halbaktiv** (NPM 2.5.0 ~4 J alt, Repo-Aktivität moderat) | ✅ | n/a | Basis (event-getrieben) |
| **jishi/node-sonos-http-api** (+web-controller) | Backend (+altes UI) | Node (alt, max Node 18) | **Stagnierend** (Issues 2024, Node-20-Probleme) | ✅ | mäßig/alt | indirekt |
| **sonos-web** (sonos-web/sonos-web) | Fertig (Web-UI) | Node + Vue, baut auf altem `node-sonos` | **Verrottet** (fibers→Node<16, veraltete/vulnerable Deps) | ✅ (wenn lauffähig) | hübsch, aber schwer lauffähig | indirekt |
| **SonosESP** (OpenSurface) | Embedded-Controller | ESP32-P4 + **LCD**-Touch | aktiv, jung | ✅ | dediziertes Gerät | ❌ (LCD, **kein** e-ink) — aber Code-Vorlage |

## Details je Kandidat

**Home Assistant + custom-sonos-card (punxaphil).** Der stärkste „fertige" Weg mit durchdachter UX. Die HA-Sonos-Integration ist eines der am aktivsten gepflegten Projekte überhaupt und unterstützt **S1 und S2** (S1 mit Einschränkungen nur bei Akku-/TTS-Features — für deine netzbetriebenen Speaker irrelevant). Die Community-Card von punxaphil (aktuell v10, 2025 erweitert um Media-Browser & Music-Assistant-Queue) liefert Gruppierung, Queue, Favoriten, **Suche**, Sleep-Timer, relative Gruppen-Lautstärke. Smarte Idee obendrauf: **Music Assistant** (self-hosted Musik-Server, vereint Streaming-Dienste + lokale Bibliothek, steuert Sonos) — sehr aktiv entwickelt; **S1-Support vorab verifizieren**. Preis: du betreibst HA (schwergewichtiger, aber läuft als Docker auf Mele/Synology).

**SoCo (Python) + soco-cli.** Die lebendigste lokale Sonos-Library, ausdrücklich S1+S2, Team-gepflegt. `soco-cli` ist eine mächtige CLI, lässt sich **als High-Level-API importieren** und kann **als simpler HTTP-API-Server laufen** — d.h. es ersetzt jishi als wartbares Backend. Ideale Basis für einen Eigenbau auf Mini/Mele.

**@svrooij/sonos (node-sonos-ts) + sonos2mqtt.** Moderner TypeScript-Stack, gruppen-bewusst (`SonosManager`), event-getrieben über MQTT (`sonos2mqtt`) — attraktiv, wenn die UI live auf fremde Änderungen reagieren soll. Release-Kadenz langsamer (NPM 2.5.0 ~4 J), aber protokoll-stabil und nutzbar.

**jishi/node-sonos-http-api.** Funktioniert noch (S1/S2 via UPnP), riesiger Funktionsumfang (Presets, TTS, Favoriten, SSE-Events). Aber **stagniert**: offene Issues 2024, läuft zuverlässig nur bis Node 18. Gut für 10-Minuten-Proof-of-Concept, nicht als Dauerbasis.

**sonos-web.** Schöne dedizierte Web-UI, aber technisch verrottet (Abhängigkeit `fibers` zwingt Node < 16, viele veraltete/vulnerable Deps, baut auf altem `node-sonos`). Heute mühsam lauffähig zu bekommen — nicht empfohlen.

**Embedded/e-ink.** Kein schlüsselfertiges **e-ink**-Sonos-Projekt gefunden. `SonosESP` ist ein **LCD**-Touch-Controller (ESP32-P4) — sehr gute Code-/Logik-Vorlage, aber kein e-ink. Für e-ink baut man selbst: **M5Paper** (Lib `m5stack/M5EPD`, kapazitiver Touch) oder **Inkplate** (Arduino-Lib), die ein Backend (soco-cli-HTTP/HA) aufrufen. Für Kindle: Browser-Kiosk auf ein HA-Dashboard oder eine eigene Mini-Web-UI.

## Empfehlung

**(a) Schnell & „fertig" zum Ausprobieren:**
- Wenn HA ok ist → **Home Assistant + custom-sonos-card** ist die ausgereifteste, am besten gepflegte Komplettlösung mit der besten UX und den meisten smarten Ideen (Suche, Media-Browser, Gruppen). Läuft als Docker auf Mele/Synology.
- Wenn leichtgewichtig ohne HA gewünscht → **soco-cli im HTTP-API-Modus** als gepflegtes Backend + eine schlanke eigene Web-UI. (jishi nur als Wegwerf-PoC, wegen Node-18-Deckel.)

**(b) Beste Basis für einen dauerhaften eigenen S1-App-Ersatz:**
- **SoCo (Python)** — am besten gepflegt, S1-erprobt, `soco-cli` als bequeme Abstraktion/HTTP-Server. Darauf eine kleine FastAPI/Flask + Touch-Web-UI; läuft auf Mini/Mele. Das ist auch konzeptionell dieselbe Grundlage, aus der das HA-Ökosystem schöpft.
- Alternative bei TS-Präferenz / Event-Fokus: **node-sonos-ts + sonos2mqtt** (MQTT-Events → reaktive UI).

**Realismus-Hinweis (gilt für alle):** Discovery via SSDP-Multicast kann über Meles WLAN-Repeater-Anbindung zicken. Workaround: Backend per **bekannter Speaker-IP seeden** (unsere festen IPs!) statt Broadcast-Discovery; alternativ Backend auf der **verkabelten Synology** hosten.

## Quellen

- Home Assistant Sonos-Integration: https://www.home-assistant.io/integrations/sonos/
- custom-sonos-card (punxaphil): https://github.com/punxaphil/custom-sonos-card
- SoCo (Python): https://github.com/SoCo/SoCo · Doku: http://docs.python-soco.com/
- soco-cli (CLI + HTTP-Server): https://pypi.org/project/soco-cli/
- node-sonos-ts (@svrooij/sonos): https://github.com/svrooij/node-sonos-ts · sonos2mqtt: https://sonos2mqtt.svrooij.io/
- jishi/node-sonos-http-api: https://github.com/jishi/node-sonos-http-api
- sonos-web: https://github.com/sonos-web/sonos-web (veraltete Deps, Node<16)
- SonosESP (LCD-Referenz): https://opensurface.github.io/SonosESP/
- M5Paper-Lib: https://github.com/m5stack/M5EPD · Inkplate: https://github.com/SolderedElectronics/Inkplate-Arduino-library
- Music Assistant: https://www.music-assistant.io/
