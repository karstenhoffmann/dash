#!/usr/bin/env python3
"""
HaBackend — Platzhalter. Spaeter: REST/WebSocket-Service-Calls gegen Home Assistant
(siehe ARCHITECTURE.md). Implementiert dasselbe Backend-Interface wie SocoBackend,
sodass der Umstieg ein reiner Adapter-Tausch ist (UI + Szenen + Config bleiben).

Aktivierung spaeter: SONOS_BACKEND=ha  +  HA_URL  +  HA_TOKEN.
Service-Mapping (Skizze):
    play/pause/next/previous -> media_player.media_*
    set_*_volume             -> media_player.volume_set (level/100)
    set_*_mute               -> media_player.volume_mute
    group/ungroup            -> media_player.join / media_player.unjoin
    list/play_source         -> media_player.select_source (Sonos-Favoriten)
    set_light                -> light.turn_on / turn_off  (Hue, „geschenkt")
"""


class HaBackend:
    def __init__(self) -> None:
        raise NotImplementedError(
            "HaBackend kommt spaeter — siehe ARCHITECTURE.md. "
            "Vorerst SONOS_BACKEND=soco verwenden."
        )
