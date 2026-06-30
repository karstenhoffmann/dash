"""SocoBackend — Sonos S1 lokal via SoCo (UPnP/SOAP). SKELETT.

Implementiert den `Backend`-Port (ADR-0002). Die echte SoCo-Verdrahtung folgt als
eigener Schritt (Discovery via feste Seed-IPs statt Multicast, siehe Dossier
`docs/2026-06_oss-sonos-controller-research.md`). SoCo ist SYNCHRON → in FastAPI
über plain `def`-Endpoints im Threadpool aufrufen (ADR-0008 / STACK-FINDINGS §2.4).
"""

from __future__ import annotations

from .base import Source, StateSnapshot

CAPABILITIES = {
    "transport": True,
    "volume": True,
    "grouping": True,
    "sources": True,
    "lights": False,  # SoCo kann kein Licht → erst HaBackend (Hue)
}


class SocoBackend:
    name = "soco"

    def __init__(self, seed_ips: list[str] | None = None) -> None:
        self.seed_ips = seed_ips or []
        # TODO(soco): SoCo-Geräte über seed_ips initialisieren (kein Multicast).

    def get_state(self) -> StateSnapshot:
        # SKELETT: leerer, aber valider Snapshot, damit die App bootet.
        # TODO(soco): echte Player/Gruppen aus SoCo lesen und auf Raum-Slugs mappen.
        return StateSnapshot(players=[], groups=[], capabilities=dict(CAPABILITIES))

    def play(self, room: str) -> None:
        raise NotImplementedError("SocoBackend.play — folgt")

    def pause(self, room: str) -> None:
        raise NotImplementedError("SocoBackend.pause — folgt")

    def next(self, room: str) -> None:
        raise NotImplementedError("SocoBackend.next — folgt")

    def previous(self, room: str) -> None:
        raise NotImplementedError("SocoBackend.previous — folgt")

    def set_volume(self, room: str, level: int) -> None:
        raise NotImplementedError("SocoBackend.set_volume — folgt")

    def set_mute(self, room: str, on: bool) -> None:
        raise NotImplementedError("SocoBackend.set_mute — folgt")

    def group(self, room: str, into_room: str) -> None:
        raise NotImplementedError("SocoBackend.group — folgt")

    def ungroup(self, room: str) -> None:
        raise NotImplementedError("SocoBackend.ungroup — folgt")

    def list_sources(self, room: str) -> list[Source]:
        raise NotImplementedError("SocoBackend.list_sources — folgt")

    def play_source(self, room: str, source_id: str) -> None:
        raise NotImplementedError("SocoBackend.play_source — folgt")
