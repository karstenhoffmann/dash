"""Unit-Tests für SocoBackend-Mapping — mit Fake-Geräten, ohne echte Speaker.

Deckt die Logik ab, die sonst nur live prüfbar wäre: State-Normalisierung,
Gruppen-Zusammenbau, Radio-Soft-Pause, Favoriten-Fallback, Quellen.
"""

from __future__ import annotations

import pytest

from server.backend.soco_backend import (
    SocoBackend,
    clamp_volume,
    normalize_state,
    uri_key,
)

ROOMS = {"wohn": "10.0.0.1", "bad": "10.0.0.2", "kueche": "10.0.0.3"}
DISPLAY = {"wohn": "Wohn", "bad": "Bad", "kueche": "Küche"}


class FakeFav:
    def __init__(self, title, uri, art="", meta="META"):
        self.title = title
        self._uri = uri
        self.album_art_uri = art
        self.resource_meta_data = meta

    def get_uri(self):
        return self._uri


class FakeML:
    def __init__(self, favs):
        self._favs = favs

    def get_sonos_favorites(self):
        return self._favs


class FakeGroup:
    def __init__(self, coordinator, volume=0, mute=False):
        self.coordinator = coordinator
        self.volume = volume
        self.mute = mute
        self.rel = []

    def set_relative_volume(self, d):
        self.rel.append(d)


class FakeDevice:
    def __init__(
        self,
        name,
        ip,
        *,
        volume=0,
        mute=False,
        track=None,
        transport="PLAYING",
        radio=False,
        favs=None,
    ):
        self.player_name = name
        self.ip_address = ip
        self.volume = volume
        self.mute = mute
        self._track = track or {}
        self._transport = transport
        self.is_playing_radio = radio
        self.calls = []
        self.group = FakeGroup(self)  # solo per Default; Tests setzen coordinator um
        self.music_library = FakeML(favs or [])

    def get_current_track_info(self):
        return dict(self._track)

    def get_current_transport_info(self):
        return {"current_transport_state": self._transport}

    def play(self):
        self.calls.append("play")

    def pause(self):
        self.calls.append("pause")

    def stop(self):
        self.calls.append("stop")

    def next(self):
        self.calls.append("next")

    def previous(self):
        self.calls.append("previous")

    def join(self, coord):
        self.calls.append(("join", coord.player_name))

    def unjoin(self):
        self.calls.append("unjoin")

    def play_uri(self, uri, meta=""):
        self.calls.append(("play_uri", uri, meta))


def backend(devices):
    return SocoBackend(rooms=ROOMS, display=DISPLAY, devices=devices)


# ---- reine Helfer ----
def test_clamp_volume():
    assert clamp_volume(-5) == 0
    assert clamp_volume(150) == 100
    assert clamp_volume(42) == 42


def test_uri_key_strips_query():
    assert uri_key("x-sonosapi-stream:s123?sid=1&flags=32") == "x-sonosapi-stream:s123"
    assert uri_key(None) == ""


def test_normalize_state():
    assert normalize_state("PLAYING", "uri") == "playing"
    assert normalize_state("PAUSED_PLAYBACK", "uri") == "paused"
    assert normalize_state("STOPPED", "some:uri") == "paused"  # geladen → pausiert
    assert normalize_state("STOPPED", "") == "idle"  # nichts geladen


# ---- get_state: Gruppen-Zusammenbau ----
def test_get_state_groups_members_under_coordinator():
    wohn = FakeDevice("Wohn", "10.0.0.1", volume=12, track={"title": "Song", "artist": "A"})
    wohn.group = FakeGroup(wohn, volume=20, mute=False)
    bad = FakeDevice("Bad", "10.0.0.2", volume=30)
    bad.group = FakeGroup(wohn, volume=20)  # Bad folgt Wohn als Koordinator

    snap = backend({"wohn": wohn, "bad": bad}).get_state()

    assert len(snap.groups) == 1
    g = snap.groups[0]
    assert g.coordinator == "wohn"
    assert g.volume == 20  # Gruppen-Lautstärke vom Koordinator
    assert g.state == "playing"
    assert g.now.title == "Song"
    assert [m.id for m in g.members] == ["bad", "wohn"]  # nach Name sortiert
    assert g.name == "Bad + Wohn"
    assert {m.id: m.volume for m in g.members} == {"wohn": 12, "bad": 30}


def test_get_state_offline_device_skipped_as_coordinator():
    wohn = FakeDevice("Wohn", "10.0.0.1")

    class Dead(FakeDevice):
        @property
        def group(self):  # Zugriff wirft → offline
            raise OSError("unreachable")

        @group.setter
        def group(self, v):
            pass

    dead = Dead("Küche", "10.0.0.3")
    snap = backend({"wohn": wohn, "kueche": dead}).get_state()
    # Nur die erreichbare Gruppe; das tote Gerät taucht nicht als eigene Gruppe auf.
    assert len(snap.groups) == 1
    assert snap.groups[0].coordinator == "wohn"


def test_get_state_favorite_fallback_for_radio():
    # Radio: kein Track-Titel/-Bild → Fallback aus Favoriten über URI-Key.
    uri = "x-sonosapi-stream:s25111?sid=254"
    fav = FakeFav("FM4", "x-sonosapi-stream:s25111?sid=254", art="/getaa?u=fm4")
    wohn = FakeDevice("Wohn", "10.0.0.1", track={"uri": uri}, transport="PLAYING", favs=[fav])
    wohn.group = FakeGroup(wohn, volume=10)

    g = backend({"wohn": wohn}).get_state().groups[0]
    assert g.now.title == "FM4"
    assert g.now.source == "FM4"
    assert g.now.art_url == "http://10.0.0.1:1400/getaa?u=fm4"  # absolutiert


# ---- Steuerung ----
def test_pause_radio_soft_mutes_then_play_unmutes():
    wohn = FakeDevice("Wohn", "10.0.0.1", radio=True)
    wohn.group = FakeGroup(wohn)
    be = backend({"wohn": wohn})

    be.pause("wohn")
    assert wohn.group.mute is True
    assert "pause" not in wohn.calls  # Radio wird nicht gestoppt
    assert "wohn" in be._soft

    be.play("wohn")
    assert wohn.group.mute is False
    assert "wohn" not in be._soft
    assert "play" not in wohn.calls  # Entmuten, kein echtes play()


def test_pause_ondemand_real_pause():
    wohn = FakeDevice("Wohn", "10.0.0.1", radio=False)
    wohn.group = FakeGroup(wohn)
    be = backend({"wohn": wohn})
    be.pause("wohn")
    assert wohn.calls == ["pause"]


def test_group_and_ungroup():
    wohn = FakeDevice("Wohn", "10.0.0.1")
    wohn.group = FakeGroup(wohn)
    bad = FakeDevice("Bad", "10.0.0.2")
    bad.group = FakeGroup(bad)
    be = backend({"wohn": wohn, "bad": bad})

    be.group("bad", "wohn")
    assert ("join", "Wohn") in bad.calls
    be.ungroup("bad")
    assert "unjoin" in bad.calls


def test_volume_group_and_room():
    wohn = FakeDevice("Wohn", "10.0.0.1")
    g = FakeGroup(wohn, volume=0)
    wohn.group = g
    be = backend({"wohn": wohn})

    be.set_group_volume("wohn", 150)  # clamp
    assert g.volume == 100
    be.set_group_volume_rel("wohn", -5)
    assert g.rel == [-5]
    be.set_room_volume("wohn", 33)
    assert wohn.volume == 33
    be.set_room_mute("wohn", True)
    assert wohn.mute is True


# ---- Quellen ----
def test_list_sources_and_play_source():
    fav = FakeFav("FM4", "x-sonosapi-stream:s1?sid=2", art="/aa", meta="THEMETA")
    wohn = FakeDevice("Wohn", "10.0.0.1", favs=[fav])
    wohn.group = FakeGroup(wohn)
    be = backend({"wohn": wohn})

    sources = be.list_sources("wohn")
    assert sources[0].name == "FM4"
    assert sources[0].art_url == "http://10.0.0.1:1400/aa"

    be.play_source("wohn", "FM4")
    assert ("play_uri", "x-sonosapi-stream:s1?sid=2", "THEMETA") in wohn.calls

    with pytest.raises(ValueError):
        be.play_source("wohn", "Unbekannt")
