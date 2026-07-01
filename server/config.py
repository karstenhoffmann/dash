"""Konfiguration aus Umgebungsvariablen (extern, ADR-0002 §7). Keine Secrets im Repo."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# Bekannte Anlage: Raum-Slug → feste DHCP-IP (Seed, kein Multicast nötig).
# Override per ENV DASH_SOCO_ROOMS="wohn=192.168.0.157,bad=192.168.0.204,…".
DEFAULT_ROOMS = {
    "wohn": "192.168.0.157",
    "spielzimmer": "192.168.0.127",
    "bad": "192.168.0.204",
    "kueche": "192.168.0.91",
    "schlaf": "192.168.0.236",
}
# Anzeige-Labels (Slug → UI-Name). Override per ENV DASH_SOCO_DISPLAY.
DEFAULT_DISPLAY = {
    "wohn": "Wohn",
    "spielzimmer": "Spielzimmer",
    "bad": "Bad",
    "kueche": "Küche",
    "schlaf": "Schlaf",
}


def _csv(name: str) -> list[str]:
    raw = os.environ.get(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _pairs(name: str) -> dict[str, str]:
    """Parst 'a=1,b=2' → {'a':'1','b':'2'} (leer → {})."""
    out: dict[str, str] = {}
    for item in _csv(name):
        if "=" in item:
            k, v = item.split("=", 1)
            out[k.strip()] = v.strip()
    return out


@dataclass
class Settings:
    backend: str = "soco"  # soco | ha
    soco_rooms: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_ROOMS))
    soco_display: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_DISPLAY))
    ha_url: str | None = None
    ha_token: str | None = None

    # LAN-Zugriff (ADR-0004): IP-Whitelist + optionales Passwort. Kein Login.
    ip_whitelist: list[str] | None = None
    password: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            backend=os.environ.get("DASH_BACKEND", "soco"),
            soco_rooms=_pairs("DASH_SOCO_ROOMS") or dict(DEFAULT_ROOMS),
            soco_display=_pairs("DASH_SOCO_DISPLAY") or dict(DEFAULT_DISPLAY),
            ha_url=os.environ.get("DASH_HA_URL") or None,
            ha_token=os.environ.get("DASH_HA_TOKEN") or None,
            ip_whitelist=_csv("DASH_IP_WHITELIST"),
            password=os.environ.get("DASH_PASSWORD") or None,
        )

    @property
    def auth_enforced(self) -> bool:
        """Auth greift nur, wenn Whitelist ODER Passwort gesetzt ist (sonst LAN-offen)."""
        return bool(self.ip_whitelist) or bool(self.password)
