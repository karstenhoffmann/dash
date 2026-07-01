"""Backend-Port + Domänenmodell (ADR-0002).

Die UI spricht NUR dieses Interface — nie SoCo/HA direkt. Modell ist gruppen-zentriert
(Now Playing = aktive Gruppe, DESIGN §4) und bleibt HA-mappbar: HaBackend baut Groups
aus HA-`media_player`-Entities + `group_members`. Stabile IDs = Raum-Slugs (`wohn`, `bad`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

# Normalisierte Transport-States (Adapter mappt SoCo/HA darauf).
PLAYER_STATES = ("playing", "paused", "idle", "off", "unknown")


@dataclass
class Now:
    """Aktuell laufender Titel der Gruppe."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    art_url: str | None = None
    source: str | None = None  # Favoriten-Name, falls laufende URI matcht (für Szenen-Capture)


@dataclass
class Member:
    """Ein Raum/Speaker innerhalb einer Gruppe. `id` = Raum-Slug, `volume` 0–100."""

    id: str
    name: str
    volume: int = 0
    mute: bool = False
    online: bool = True


@dataclass
class Group:
    """Live-Gruppe (flüchtige Sonos-Realität). `coordinator` = Raum-Slug.

    `volume`/`mute` = Gruppen-Ebene (proportional). Mitglieder tragen Einzel-Volumes.
    """

    id: str
    name: str
    coordinator: str
    state: str = "unknown"
    volume: int = 0
    mute: bool = False
    now: Now = field(default_factory=Now)
    members: list[Member] = field(default_factory=list)


@dataclass
class Source:
    """Quelle (Sonos-Favorit oder eigene Schnellquelle)."""

    id: str
    name: str
    art_url: str | None = None
    kind: str = "favorite"  # favorite | quicksource


@dataclass
class StateSnapshot:
    """Snapshot des steuerbaren Zustands.

    Als Strom gedacht (ADR-0002 §5): heute Poll dahinter, später Push (SSE/WS).
    `capabilities` meldet, was der Adapter kann → UI blendet Nicht-Unterstütztes aus.
    """

    groups: list[Group] = field(default_factory=list)
    capabilities: dict[str, bool] = field(default_factory=dict)
    ok: bool = True


@runtime_checkable
class Backend(Protocol):
    """Der Port. Zwei Implementierungen: SocoBackend (jetzt), HaBackend (später)."""

    name: str

    def get_state(self) -> StateSnapshot: ...

    # Transport (auf dem Gruppen-Koordinator)
    def play(self, room: str) -> None: ...
    def pause(self, room: str) -> None: ...
    def next(self, room: str) -> None: ...
    def previous(self, room: str) -> None: ...

    # Lautstärke — Gruppe (proportional) und einzelner Raum (exakt)
    def set_group_volume(self, room: str, level: int) -> None: ...  # 0–100
    def set_group_volume_rel(self, room: str, delta: int) -> None: ...
    def set_group_mute(self, room: str, on: bool) -> None: ...
    def set_room_volume(self, room: str, level: int) -> None: ...
    def set_room_mute(self, room: str, on: bool) -> None: ...

    # Gruppierung
    def group(self, room: str, into_room: str) -> None: ...
    def ungroup(self, room: str) -> None: ...

    # Quellen (Sonos-Favoriten kontoweit; `room` = Ziel-Gruppe / HA-Parity)
    def list_sources(self, room: str) -> list[Source]: ...
    def play_source(self, room: str, source_id: str) -> None: ...

    # Später (Hue, „Licht-Hebel"):
    # def set_light(self, light_id, on=None, brightness=None) -> None: ...
