#!/usr/bin/env python3
"""
Sonos-Controller — HTTP/UI-Schicht. Spricht NUR das Backend-Interface (backend.py),
nie SoCo direkt → SoCo↔HA-Wechsel ist ein Adapter-Tausch (siehe ARCHITECTURE.md).

Phase 2: 'Now Playing' echt. Start:  PORT=5005 python app.py
"""
import json
import os
import traceback
from uuid import uuid4
from flask import Flask, jsonify, request, send_from_directory
from backend import get_backend

app = Flask(__name__, static_folder="web", static_url_path="")
backend = get_backend()

# Szenen = UNSERE Schicht (Sonos kennt keine benannten Szenen). Backend-agnostisch: nur Raum-Slugs.
SCENES_FILE = os.path.join(os.path.dirname(__file__), "scenes.json")


def _load_scenes():
    try:
        with open(SCENES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_scenes(scenes):
    with open(SCENES_FILE, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)


def _apply_scene(scene):
    rooms = scene.get("rooms") or []
    if not rooms:
        return
    anchor = rooms[0]
    for r in rooms:            # erst alle Szenen-Räume solo → saubere Konstellation
        backend.ungroup(r)
    for r in rooms[1:]:        # dann zur Anker-Gruppe
        backend.group(r, anchor)
    for slug, lvl in (scene.get("volumes") or {}).items():
        try:
            backend.set_room_volume(slug, int(lvl))
        except Exception:
            traceback.print_exc()
    if scene.get("source"):
        try:
            backend.play_source(anchor, scene["source"])
        except Exception:
            traceback.print_exc()


@app.route("/")
def index():
    return send_from_directory("web", "index.html")


@app.route("/api/state")
def api_state():
    try:
        return jsonify(backend.get_state())
    except Exception as e:
        return jsonify({"ok": False, "groups": [], "error": str(e)})


def _ok(fn, *a):
    try:
        fn(*a)
        return jsonify({"ok": True})
    except Exception as e:
        traceback.print_exc()   # voller Traceback ins Terminal (Dev-Debugging)
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/<room>/play", methods=["POST"])
def r_play(room): return _ok(backend.play, room)


@app.route("/api/<room>/pause", methods=["POST"])
def r_pause(room): return _ok(backend.pause, room)


@app.route("/api/<room>/next", methods=["POST"])
def r_next(room): return _ok(backend.next, room)


@app.route("/api/<room>/previous", methods=["POST"])
def r_prev(room): return _ok(backend.previous, room)


@app.route("/api/<room>/groupvolume/<int:level>", methods=["POST"])
def r_gvol(room, level): return _ok(backend.set_group_volume, room, level)


@app.route("/api/<room>/groupnudge/<int(signed=True):delta>", methods=["POST"])
def r_gnudge(room, delta): return _ok(backend.set_group_volume_rel, room, delta)


@app.route("/api/<room>/groupmute/<int:on>", methods=["POST"])
def r_gmute(room, on): return _ok(backend.set_group_mute, room, bool(on))


@app.route("/api/<room>/volume/<int:level>", methods=["POST"])
def r_vol(room, level): return _ok(backend.set_room_volume, room, level)


@app.route("/api/<room>/mute/<int:on>", methods=["POST"])
def r_mute(room, on): return _ok(backend.set_room_mute, room, bool(on))


@app.route("/api/<room>/group/<into_room>", methods=["POST"])
def r_group(room, into_room): return _ok(backend.group, room, into_room)


@app.route("/api/<room>/ungroup", methods=["POST"])
def r_ungroup(room): return _ok(backend.ungroup, room)


@app.route("/api/<room>/sources")
def r_sources(room):
    try:
        return jsonify({"ok": True, "sources": backend.list_sources(room)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "sources": [], "error": str(e)})


@app.route("/api/<room>/playsource", methods=["POST"])
def r_playsource(room):
    data = request.get_json(silent=True) or {}
    return _ok(backend.play_source, room, data.get("id", ""))


@app.route("/api/scenes")
def r_scenes():
    return jsonify({"ok": True, "scenes": _load_scenes()})


@app.route("/api/<room>/savescene", methods=["POST"])
def r_savescene(room):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    try:
        st = backend.get_state()
        grp = next((g for g in st.get("groups", [])
                    if g["id"] == room or any(m["id"] == room for m in g["members"])), None)
        if not grp:
            return jsonify({"ok": False, "error": "Gruppe nicht gefunden"})
        scene = {
            "id": "sc_" + uuid4().hex[:8],
            "name": name or grp["name"],
            "rooms": [m["id"] for m in grp["members"]],
            "volumes": {m["id"]: m["volume"] for m in grp["members"]},
            "source": grp.get("now", {}).get("source", ""),
        }
        scenes = _load_scenes()
        scenes.append(scene)
        _save_scenes(scenes)
        return jsonify({"ok": True, "scene": scene})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/scenes/<sid>/apply", methods=["POST"])
def r_scene_apply(sid):
    scene = next((s for s in _load_scenes() if s.get("id") == sid), None)
    if not scene:
        return jsonify({"ok": False, "error": "Szene nicht gefunden"})
    return _ok(_apply_scene, scene)


@app.route("/api/scenes/<sid>/delete", methods=["POST"])
def r_scene_delete(sid):
    _save_scenes([s for s in _load_scenes() if s.get("id") != sid])
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5005"))
    # SONOS_DEV=1 -> Auto-Reload bei Code-Aenderungen (Dev am MacBook), damit
    # Backend-Aenderungen ohne manuellen Neustart greifen.
    dev = os.environ.get("SONOS_DEV") == "1"
    app.run(host="0.0.0.0", port=port, use_reloader=dev)
