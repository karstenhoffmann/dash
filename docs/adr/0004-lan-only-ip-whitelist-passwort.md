# ADR-0004: LAN-only, IP-Whitelist + Passwort, kein Login

**Status:** Accepted · **Datum:** 2026-07-01

## Kontext
Wer im Heim-WLAN ist, soll per URL steuern — ohne Login, ohne App-Store. Mehrere Geräte (Handy, Tablet, Browser). Hosting auf Mele hinter Caddy.

## Entscheidung
**LAN-only.** Zugriff für bekannte Geräte per **reservierter IP-Whitelist**; sonst **einmalig Passwort** mit Remember-Cookie. Kein Benutzer-Login. Umsetzung als Middleware (`server/auth.py`) hinter Caddy-Reverse-Proxy.

## Konsequenzen
- Niedrige Reibung im Alltag, koexistent mit offiziellen Sonos-Apps.
- Kein Internet-Exposure; keine Account-Verwaltung.

## Alternativen
- **MAC-Whitelist:** verworfen — MAC ist für den Webserver nicht sichtbar; IP-Whitelist setzt die Absicht korrekt um.
- **Echtes Login:** verworfen — Overkill für LAN-only Heimgebrauch.
