"""Konfiguration aus Umgebungsvariablen (extern, ADR-0002 §7). Keine Secrets im Repo."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _csv(name: str) -> list[str]:
    raw = os.environ.get(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class Settings:
    backend: str = "soco"  # soco | ha
    soco_seed_ips: list[str] | None = None  # feste Speaker-IPs (kein Multicast)
    ha_url: str | None = None
    ha_token: str | None = None

    # LAN-Zugriff (ADR-0004): IP-Whitelist + optionales Passwort. Kein Login.
    ip_whitelist: list[str] | None = None
    password: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            backend=os.environ.get("DASH_BACKEND", "soco"),
            soco_seed_ips=_csv("DASH_SOCO_SEED_IPS"),
            ha_url=os.environ.get("DASH_HA_URL") or None,
            ha_token=os.environ.get("DASH_HA_TOKEN") or None,
            ip_whitelist=_csv("DASH_IP_WHITELIST"),
            password=os.environ.get("DASH_PASSWORD") or None,
        )

    @property
    def auth_enforced(self) -> bool:
        """Auth greift nur, wenn Whitelist ODER Passwort gesetzt ist (sonst LAN-offen)."""
        return bool(self.ip_whitelist) or bool(self.password)
