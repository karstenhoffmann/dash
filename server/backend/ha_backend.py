"""HaBackend — Home Assistant via REST + WebSocket. PLATZHALTER (ADR-0002).

Kommt mit Hue („Licht-Hebel"): HA steuert Sonos *und* Hue über dieselbe API. Dann
abonniert dieser Adapter den HA-WebSocket (echtes Push) und mappt HA-Entities auf
unser Domänenmodell (entity_id ↔ Raum-Slug, volume_level 0–1 ↔ 0–100). HA ist
async-first → hier darf/ soll async genutzt werden (STACK-FINDINGS §2.4).
"""

from __future__ import annotations

from .base import Source, StateSnapshot


class HaBackend:
    name = "ha"

    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token
        # TODO(ha): HTTP-Client + WS-Subscription (Authorization: Bearer <token>).

    def get_state(self) -> StateSnapshot:
        raise NotImplementedError("HaBackend — kommt mit Hue")

    def play(self, room: str) -> None:
        raise NotImplementedError

    def pause(self, room: str) -> None:
        raise NotImplementedError

    def next(self, room: str) -> None:
        raise NotImplementedError

    def previous(self, room: str) -> None:
        raise NotImplementedError

    def set_volume(self, room: str, level: int) -> None:
        raise NotImplementedError

    def set_mute(self, room: str, on: bool) -> None:
        raise NotImplementedError

    def group(self, room: str, into_room: str) -> None:
        raise NotImplementedError

    def ungroup(self, room: str) -> None:
        raise NotImplementedError

    def list_sources(self, room: str) -> list[Source]:
        raise NotImplementedError

    def play_source(self, room: str, source_id: str) -> None:
        raise NotImplementedError
