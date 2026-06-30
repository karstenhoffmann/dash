#!/usr/bin/env python3
"""
Backend-Adapter — die UI/HTTP-Schicht spricht NUR dieses Interface (siehe ARCHITECTURE.md).
SoCo jetzt, HaBackend spaeter. Stabile IDs = Raum-Slugs, damit Szenen/Config einen
Backend-Wechsel ueberleben.
"""
from __future__ import annotations
import os
import time
from typing import Protocol

# Stabile IDs (Raum-Slugs) -> feste DHCP-IPs. Backend-agnostisch.
ROOMS = {
    "wohn": "192.168.0.157",
    "spielzimmer": "192.168.0.127",
    "bad": "192.168.0.204",
    "kueche": "192.168.0.91",
    "schlaf": "192.168.0.236",
}
DISPLAY = {
    "wohn": "Wohn", "spielzimmer": "Spielzimmer", "bad": "Bad",
    "kueche": "Küche", "schlaf": "Schlaf",
}

# Radio kann nicht echt pausieren (Sonos stoppt es). „Pause" bei Radio = stummschalten
# (Stream laeuft weiter → Play = sofort, lueckenlos). Nach so vielen Sekunden dauerhaft
# gemutet wird wirklich pausiert (kein Dauer-Streaming ins Leere).
SOFT_PAUSE_SECS = 3600


class Backend(Protocol):
    def get_state(self) -> dict: ...
    def play(self, room: str) -> None: ...
    def pause(self, room: str) -> None: ...
    def next(self, room: str) -> None: ...
    def previous(self, room: str) -> None: ...
    def set_room_volume(self, room: str, level: int) -> None: ...
    def set_room_mute(self, room: str, on: bool) -> None: ...
    def set_group_volume(self, room: str, level: int) -> None: ...
    def set_group_volume_rel(self, room: str, delta: int) -> None: ...
    def set_group_mute(self, room: str, on: bool) -> None: ...
    def group(self, room: str, into_room: str) -> None: ...
    def ungroup(self, room: str) -> None: ...
    def list_sources(self, room: str) -> list: ...        # Quellen (Sonos-Favoriten): [{id,name,artUrl}]
    def play_source(self, room: str, source_id: str) -> None: ...  # Favorit auf der Gruppe starten
    # spaeter: set_light, ...


def _clamp(v) -> int:
    return max(0, min(100, int(v)))


class SocoBackend:
    """Fuellt das Interface via SoCo (lokales UPnP). Seed ueber feste IPs."""

    def __init__(self) -> None:
        import soco
        self._dev = {slug: soco.SoCo(ip) for slug, ip in ROOMS.items()}
        self._ip2slug = {ip: slug for slug, ip in ROOMS.items()}
        self._fav_cache = None      # {normalisierte-URI: absolutes Logo} — Cover-Fallback bei Radio
        self._fav_cache_ts = 0.0    # Zeitstempel; alle 60s neu (nicht bei jedem 5s-Poll)
        self._soft = {}             # coord-slug → Mute-Zeitstempel (Soft-Pause bei Radio)

    def _room(self, room: str):
        return self._dev[room]

    def _coord(self, room: str):
        return self._dev[room].group.coordinator

    def _slug(self, device) -> str:
        return self._ip2slug.get(device.ip_address, device.player_name)

    def get_state(self) -> dict:
        groups = {}
        for slug, dev in self._dev.items():
            try:
                coord = dev.group.coordinator
                gid = self._slug(coord)
            except Exception:
                continue
            if gid not in groups:
                try:
                    ti = coord.get_current_track_info()
                except Exception:
                    ti = {}
                try:
                    ts = coord.get_current_transport_info().get("current_transport_state", "")
                except Exception:
                    ts = ""
                uri = ti.get("uri", "")
                # STOPPED mit geladenem Inhalt (z.B. Radio nach „Pause") = pausiert, nicht „nichts"
                state = {"PLAYING": "playing", "PAUSED_PLAYBACK": "paused",
                         "TRANSITIONING": "playing"}.get(ts, "")
                if not state:
                    state = "paused" if uri else "idle"
                # Track-Bild/Titel, sonst Senderlogo/-name aus dem Favoriten (Radio liefert oft beides nicht)
                art = ti.get("album_art", "") or self._fav_art_for(uri)
                title = ti.get("title", "") or self._fav_name_for(uri)
                try:
                    gvol = int(coord.group.volume)   # echte, proportionale Gruppen-Lautstaerke
                except Exception:
                    gvol = 0
                try:
                    gmute = bool(coord.group.mute)
                except Exception:
                    gmute = False
                # Soft-Pause (Radio gemutet statt gestoppt): als pausiert zeigen.
                if gid in self._soft:
                    if not gmute:
                        self._soft.pop(gid, None)               # extern entmutet → Soft-Pause aufgehoben
                    elif time.time() - self._soft[gid] > SOFT_PAUSE_SECS:
                        self._real_pause(coord)                 # 60 Min gemutet → jetzt wirklich pausieren
                        self._soft.pop(gid, None)
                        state, gmute = "paused", False
                    else:
                        state, gmute = "paused", False          # gemutet, läuft → als Pause präsentieren
                groups[gid] = {
                    "id": gid,
                    "state": state,
                    "volume": gvol,
                    "mute": gmute,
                    "now": {
                        "title": title,
                        "artist": ti.get("artist", ""),
                        "album": ti.get("album", ""),
                        "artUrl": art,
                        "source": self._fav_name_for(uri),   # Favoriten-Name, falls laufende URI matcht (für Szenen-Capture)
                    },
                    "members": [],
                }
            try:
                groups[gid]["members"].append({
                    "id": slug, "name": DISPLAY.get(slug, slug),
                    "volume": int(dev.volume), "mute": bool(dev.mute),
                })
            except Exception:
                pass
        out = []
        for g in groups.values():
            g["members"].sort(key=lambda m: m["name"])
            g["name"] = " + ".join(m["name"] for m in g["members"])
            out.append(g)
        out.sort(key=lambda g: g["name"])
        return {"ok": True, "groups": out}

    @staticmethod
    def _real_pause(coord):
        try:
            coord.pause()
        except Exception:
            try:
                coord.stop()        # Radio kann nicht pausieren → stoppen
            except Exception:
                pass
        try:
            coord.group.mute = False
        except Exception:
            pass

    def play(self, room):
        coord = self._coord(room)
        slug = self._slug(coord)
        if slug in self._soft:
            coord.group.mute = False        # Soft-Pause aufheben = entmuten (sofort, lückenlos)
            self._soft.pop(slug, None)
        else:
            coord.play()

    def pause(self, room):
        coord = self._coord(room)
        try:
            radio = coord.is_playing_radio
        except Exception:
            radio = False
        if radio:
            coord.group.mute = True         # Radio: muten statt stoppen → Play bleibt lückenlos
            self._soft[self._slug(coord)] = time.time()
        else:
            coord.pause()                   # On-Demand: echtes Pause (positionsgenau)

    def next(self, room): self._coord(room).next()
    def previous(self, room): self._coord(room).previous()

    def set_room_volume(self, room, level): self._room(room).volume = _clamp(level)
    def set_room_mute(self, room, on): self._room(room).mute = bool(on)

    def set_group_volume(self, room, level):
        # Sonos skaliert die Mitglieder proportional -> individuelle Balance bleibt erhalten
        self._coord(room).group.volume = _clamp(level)

    def set_group_volume_rel(self, room, delta):
        self._coord(room).group.set_relative_volume(int(delta))

    def set_group_mute(self, room, on):
        self._coord(room).group.mute = bool(on)

    def group(self, room, into_room):
        self._room(room).join(self._coord(into_room))

    def ungroup(self, room):
        self._room(room).unjoin()

    # ---- Quellen (Sonos-Favoriten) ----
    # Favoriten sind kontoweit (nicht raumspezifisch); room nur fuer HA-Parity
    # (dort = source_list/select_source je Entity). Lazy: nur beim Oeffnen des
    # Quellen-Tabs abgefragt, nicht im 5s-Poll.
    def _any(self):
        return next(iter(self._dev.values()))

    @staticmethod
    def _abs_art(dev, art):
        if not art:
            return ""
        if art.startswith("http"):
            return art
        return f"http://{dev.ip_address}:1400{art}" if art.startswith("/") else art

    def _favorites(self):
        return self._any().music_library.get_sonos_favorites()

    @staticmethod
    def _uri_key(uri):
        # Stream-URI ohne Query (?sid=…&flags=…) → stabiler Schluessel; Favorit und
        # laufender Stream teilen den Teil davor (z.B. x-sonosapi-stream:s12345).
        return (uri or "").split("?")[0]

    def _fav_map(self):
        # URI→{art,name} aller Favoriten; 60s gecacht, damit get_state (5s-Poll) nicht jedes Mal
        # die Favoriten per UPnP zieht. Greift fuer JEDEN laufenden Sender (auch S1-App-gestartet).
        now = time.time()
        if self._fav_cache is None or now - self._fav_cache_ts > 60:
            m = {}
            try:
                dev = self._any()
                for f in self._favorites():
                    try:
                        key = self._uri_key(f.get_uri())
                    except Exception:
                        key = ""
                    if not key:
                        continue
                    m[key] = {
                        "art": self._abs_art(dev, getattr(f, "album_art_uri", "") or ""),
                        "name": getattr(f, "title", "") or "",
                    }
            except Exception:
                m = self._fav_cache or {}   # bei Fehler alten Cache behalten
            self._fav_cache = m
            self._fav_cache_ts = now
        return self._fav_cache

    def _fav_art_for(self, uri):
        e = self._fav_map().get(self._uri_key(uri)) if uri else None
        return e["art"] if e else ""

    def _fav_name_for(self, uri):
        e = self._fav_map().get(self._uri_key(uri)) if uri else None
        return e["name"] if e else ""

    def list_sources(self, room):
        dev = self._dev.get(room) or self._any()
        out = []
        for f in self._favorites():
            out.append({
                "id": f.title,
                "name": f.title,
                "artUrl": self._abs_art(dev, getattr(f, "album_art_uri", "") or ""),
            })
        return out

    def play_source(self, room, source_id):
        fav = next((f for f in self._favorites() if f.title == source_id), None)
        if fav is None:
            raise ValueError(f"Favorit nicht gefunden: {source_id}")
        # uri + resMD = exakt das Paar, das die Sonos-App beim Antippen sendet
        self._coord(room).play_uri(fav.get_uri(), meta=getattr(fav, "resource_meta_data", ""))


def get_backend() -> Backend:
    kind = os.environ.get("SONOS_BACKEND", "soco").lower()
    if kind == "ha":
        from ha_backend import HaBackend
        return HaBackend()
    return SocoBackend()
