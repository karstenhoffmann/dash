"""SocoBackend — Sonos S1 lokal via SoCo (UPnP/SOAP). Implementiert den Backend-Port.

Seed über feste IPs (kein Multicast, Dossier `docs/2026-06_oss-sonos-controller-research.md`).
SoCo ist SYNCHRON → in FastAPI über plain `def`-Endpoints im Threadpool (ADR-0008).

Der Geräte-Zugriff ist injizierbar (`devices=`), damit die Mapping-Logik ohne echte
Speaker testbar ist (siehe tests/). Radio-Sonderfall (Soft-Pause = muten) wie im
Prototyp, DESIGN §8.
"""

from __future__ import annotations

import time

from .base import Group, Member, Now, Source, StateSnapshot

# Radio kann nicht echt pausieren → „Pause" = muten (Stream läuft, Play lückenlos).
# Nach so vielen Sekunden gemutet wird wirklich pausiert (kein Dauer-Streaming ins Leere).
SOFT_PAUSE_SECS = 3600
FAV_CACHE_SECS = 60

CAPABILITIES = {
    "transport": True,
    "group_volume": True,
    "room_volume": True,
    "grouping": True,
    "sources": True,
    "lights": False,  # SoCo kann kein Licht → erst HaBackend (Hue)
}

_TRANSPORT = {"PLAYING": "playing", "PAUSED_PLAYBACK": "paused", "TRANSITIONING": "playing"}


def clamp_volume(v) -> int:
    return max(0, min(100, int(v)))


def uri_key(uri: str | None) -> str:
    """Stream-URI ohne Query → stabiler Schlüssel (Favorit & laufender Stream teilen ihn)."""
    return (uri or "").split("?")[0]


def normalize_state(transport_state: str, uri: str) -> str:
    """SoCo-Transport-String → normalisierter State. STOPPED mit Inhalt = paused (Radio)."""
    state = _TRANSPORT.get(transport_state, "")
    if state:
        return state
    return "paused" if uri else "idle"


class SocoBackend:
    name = "soco"

    def __init__(self, rooms: dict[str, str], display=None, devices=None) -> None:
        self.rooms = dict(rooms)
        self.display = dict(display or {})
        self._ip2slug = {ip: slug for slug, ip in self.rooms.items()}
        self._devices = devices  # optional Injektion (Tests); sonst lazy via SoCo
        self._fav_cache: dict | None = None
        self._fav_cache_ts = 0.0
        self._soft: dict[str, float] = {}  # coordinator-slug → Mute-Zeitstempel

    # ---- Geräte-Zugriff ------------------------------------------------------
    def _all(self) -> dict:
        if self._devices is None:
            import soco  # lazy: kein Hardware-Import in Tests

            self._devices = {slug: soco.SoCo(ip) for slug, ip in self.rooms.items()}
        return self._devices

    def _device(self, room: str):
        dev = self._all().get(room)
        if dev is None:
            raise KeyError(f"Unbekannter Raum: {room!r}")
        return dev

    def _coordinator(self, room: str):
        return self._device(room).group.coordinator

    def _slug_of(self, device) -> str:
        return self._ip2slug.get(getattr(device, "ip_address", ""), device.player_name)

    def _label(self, slug: str, device=None) -> str:
        return self.display.get(slug) or (getattr(device, "player_name", "") if device else "") or slug

    def _any(self):
        return next(iter(self._all().values()))

    # ---- State ---------------------------------------------------------------
    def get_state(self) -> StateSnapshot:
        groups: dict[str, Group] = {}
        for slug, dev in self._all().items():
            try:
                coord = dev.group.coordinator
                gid = self._slug_of(coord)
            except Exception:
                continue  # Gerät offline → nicht gruppierbar (DESIGN §8)

            if gid not in groups:
                groups[gid] = self._build_group(gid, coord)

            try:
                groups[gid].members.append(
                    Member(
                        id=slug,
                        name=self._label(slug, dev),
                        volume=int(dev.volume),
                        mute=bool(dev.mute),
                        online=True,
                    )
                )
            except Exception:
                groups[gid].members.append(
                    Member(id=slug, name=self._label(slug), online=False)
                )

        out = []
        for g in groups.values():
            g.members.sort(key=lambda m: m.name)
            g.name = " + ".join(m.name for m in g.members)
            out.append(g)
        out.sort(key=lambda g: g.name)
        return StateSnapshot(groups=out, capabilities=dict(CAPABILITIES), ok=True)

    def _build_group(self, gid: str, coord) -> Group:
        ti = _safe(coord.get_current_track_info, {})
        ts = _safe(lambda: coord.get_current_transport_info().get("current_transport_state", ""), "")
        uri = ti.get("uri", "")
        state = normalize_state(ts, uri)
        art = ti.get("album_art", "") or self._fav_art_for(uri)
        title = ti.get("title", "") or self._fav_name_for(uri)
        gvol = _safe(lambda: int(coord.group.volume), 0)
        gmute = _safe(lambda: bool(coord.group.mute), False)

        # Soft-Pause (Radio gemutet statt gestoppt): als pausiert präsentieren.
        if gid in self._soft:
            if not gmute:
                self._soft.pop(gid, None)  # extern entmutet → aufgehoben
            elif time.time() - self._soft[gid] > SOFT_PAUSE_SECS:
                self._real_pause(coord)  # lange gemutet → jetzt wirklich pausieren
                self._soft.pop(gid, None)
                state, gmute = "paused", False
            else:
                state, gmute = "paused", False

        return Group(
            id=gid,
            name=gid,
            coordinator=gid,
            state=state,
            volume=gvol,
            mute=gmute,
            now=Now(
                title=title or None,
                artist=ti.get("artist") or None,
                album=ti.get("album") or None,
                art_url=art or None,
                source=self._fav_name_for(uri) or None,
            ),
            members=[],
        )

    # ---- Transport -----------------------------------------------------------
    def play(self, room: str) -> None:
        coord = self._coordinator(room)
        slug = self._slug_of(coord)
        if slug in self._soft:
            coord.group.mute = False  # Soft-Pause aufheben = entmuten (lückenlos)
            self._soft.pop(slug, None)
        else:
            coord.play()

    def pause(self, room: str) -> None:
        coord = self._coordinator(room)
        if _safe(lambda: coord.is_playing_radio, False):
            coord.group.mute = True  # Radio: muten statt stoppen → Play lückenlos
            self._soft[self._slug_of(coord)] = time.time()
        else:
            coord.pause()  # On-Demand: echtes, positionsgenaues Pause

    def next(self, room: str) -> None:
        self._coordinator(room).next()

    def previous(self, room: str) -> None:
        self._coordinator(room).previous()

    @staticmethod
    def _real_pause(coord) -> None:
        try:
            coord.pause()
        except Exception:
            _safe(coord.stop, None)  # Radio kann nicht pausieren → stoppen
        _safe(lambda: setattr(coord.group, "mute", False), None)

    # ---- Lautstärke ----------------------------------------------------------
    def set_group_volume(self, room: str, level: int) -> None:
        # Sonos skaliert Mitglieder proportional → individuelle Balance bleibt.
        self._coordinator(room).group.volume = clamp_volume(level)

    def set_group_volume_rel(self, room: str, delta: int) -> None:
        self._coordinator(room).group.set_relative_volume(int(delta))

    def set_group_mute(self, room: str, on: bool) -> None:
        self._coordinator(room).group.mute = bool(on)

    def set_room_volume(self, room: str, level: int) -> None:
        self._device(room).volume = clamp_volume(level)

    def set_room_mute(self, room: str, on: bool) -> None:
        self._device(room).mute = bool(on)

    # ---- Gruppierung ---------------------------------------------------------
    def group(self, room: str, into_room: str) -> None:
        self._device(room).join(self._coordinator(into_room))

    def ungroup(self, room: str) -> None:
        self._device(room).unjoin()

    # ---- Quellen (Sonos-Favoriten, kontoweit) --------------------------------
    def _favorites(self):
        return self._any().music_library.get_sonos_favorites()

    @staticmethod
    def _abs_art(dev, art: str) -> str:
        if not art:
            return ""
        if art.startswith("http"):
            return art
        return f"http://{dev.ip_address}:1400{art}" if art.startswith("/") else art

    def _fav_map(self) -> dict:
        now = time.time()
        if self._fav_cache is None or now - self._fav_cache_ts > FAV_CACHE_SECS:
            m: dict[str, dict] = {}
            try:
                dev = self._any()
                for f in self._favorites():
                    key = uri_key(_safe(f.get_uri, ""))
                    if not key:
                        continue
                    m[key] = {
                        "art": self._abs_art(dev, getattr(f, "album_art_uri", "") or ""),
                        "name": getattr(f, "title", "") or "",
                    }
            except Exception:
                m = self._fav_cache or {}
            self._fav_cache = m
            self._fav_cache_ts = now
        return self._fav_cache

    def _fav_art_for(self, uri: str) -> str:
        e = self._fav_map().get(uri_key(uri)) if uri else None
        return e["art"] if e else ""

    def _fav_name_for(self, uri: str) -> str:
        e = self._fav_map().get(uri_key(uri)) if uri else None
        return e["name"] if e else ""

    def list_sources(self, room: str) -> list[Source]:
        dev = self._all().get(room) or self._any()
        return [
            Source(
                id=f.title,
                name=f.title,
                art_url=self._abs_art(dev, getattr(f, "album_art_uri", "") or "") or None,
            )
            for f in self._favorites()
        ]

    def play_source(self, room: str, source_id: str) -> None:
        fav = next((f for f in self._favorites() if f.title == source_id), None)
        if fav is None:
            raise ValueError(f"Favorit nicht gefunden: {source_id}")
        # uri + resMD = exakt das Paar, das die Sonos-App beim Antippen sendet.
        self._coordinator(room).play_uri(fav.get_uri(), meta=getattr(fav, "resource_meta_data", ""))


def _safe(fn, default):
    """Ruft fn() auf; bei Exception → default. Hält get_state robust gegen Einzelfehler."""
    try:
        return fn()
    except Exception:
        return default
