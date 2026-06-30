"""Backend-Adapter-Paket. Factory wählt die Implementierung per Config (ADR-0002)."""

from __future__ import annotations

from .base import Backend, Group, Now, Player, Source, StateSnapshot
from .ha_backend import HaBackend
from .soco_backend import SocoBackend

__all__ = [
    "Backend",
    "Group",
    "HaBackend",
    "Now",
    "Player",
    "Source",
    "SocoBackend",
    "StateSnapshot",
    "make_backend",
]


def make_backend(kind: str, *, soco_seed_ips=None, ha_url=None, ha_token=None) -> Backend:
    """Erzeugt das konfigurierte Backend. Wechsel SoCo↔HA = eine Config-Zeile."""
    kind = (kind or "soco").lower()
    if kind == "soco":
        return SocoBackend(seed_ips=soco_seed_ips)
    if kind == "ha":
        if not (ha_url and ha_token):
            raise ValueError("HaBackend braucht DASH_HA_URL und DASH_HA_TOKEN")
        return HaBackend(url=ha_url, token=ha_token)
    raise ValueError(f"Unbekanntes Backend: {kind!r} (erwartet: soco | ha)")
