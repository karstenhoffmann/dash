"""Backend-Port + Domänenmodell (ADR-0002).

Die UI spricht NUR dieses Interface — nie SoCo/HA direkt. Das Domänenmodell ist
bewusst HA-förmig (Player/Light), damit `SocoBackend` → `HaBackend` ohne Rewrite
tauschbar ist. Stabile IDs = Raum-Slugs (`wohn`, `bad`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

# Normalisierte States (Adapter mappt SoCo/HA darauf).
PLAYER_STATES = ("playing", "paused", "idle", "off", "unknown")


@dataclass
class Now:
    """Aktuell laufender Titel."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    art_url: str | None = None


@dataclass
class Source:
    """Quelle (Sonos-Favorit oder eigene Schnellquelle)."""

    id: str
    name: str
    art_url: str | None = None
    kind: str = "favorite"  # favorite | quicksource


@dataclass
class Player:
    """Ein Raum/Speaker. `id` = Raum-Slug, `volume` 0–100."""

    id: str
    name: str
    state: str = "unknown"
    volume: int = 0
    mute: bool = False
    now: Now = field(default_factory=Now)
    group_members: list[str] = field(default_factory=list)  # Raum-Slugs


@dataclass
class Group:
    """Live-Gruppe (flüchtige Sonos-Realität). `coordinator` = Raum-Slug."""

    id: str
    name: str
    coordinator: str
    members: list[str] = field(default_factory=list)  # Raum-Slugs


@dataclass
class StateSnapshot:
    """Ein Snapshot des gesamten steuerbaren Zustands.

    Als Strom gedacht (ADR-0002 §5): heute Poll dahinter, später Push (SSE/WS).
    `capabilities` meldet, was der Adapter kann → UI blendet Nicht-Unterstütztes aus.
    """

    players: list[Player] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    capabilities: dict[str, bool] = field(default_factory=dict)


@runtime_checkable
class Backend(Protocol):
    """Der Port. Zwei Implementierungen: SocoBackend (jetzt), HaBackend (später)."""

    name: str

    def get_state(self) -> StateSnapshot: ...

    def play(self, room: str) -> None: ...

    def pause(self, room: str) -> None: ...

    def next(self, room: str) -> None: ...

    def previous(self, room: str) -> None: ...

    def set_volume(self, room: str, level: int) -> None:  # 0–100, rastet auf 5 %
        ...

    def set_mute(self, room: str, on: bool) -> None: ...

    def group(self, room: str, into_room: str) -> None: ...

    def ungroup(self, room: str) -> None: ...

    def list_sources(self, room: str) -> list[Source]: ...

    def play_source(self, room: str, source_id: str) -> None: ...

    # Später (Hue, der „Licht-Hebel"):
    # def set_light(self, light_id, on=None, brightness=None) -> None: ...
