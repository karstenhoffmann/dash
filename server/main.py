"""dash — FastAPI-App: liefert das Frontend (web/) + JSON-API gegen den Backend-Port.

Ein Port, UI + API zusammen (kein CORS). Blockierende SoCo-Aufrufe laufen über plain
`def`-Endpoints im Threadpool (FastAPI-Empfehlung, ADR-0008). Auth = LAN (ADR-0004).
Die UI spricht NUR diese API → nur das Backend-Interface (nie SoCo/HA direkt).
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .auth import LanAuthMiddleware, register_login
from .backend import make_backend
from .config import Settings

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

settings = Settings.from_env()
backend = make_backend(
    settings.backend,
    soco_rooms=settings.soco_rooms,
    soco_display=settings.soco_display,
    ha_url=settings.ha_url,
    ha_token=settings.ha_token,
)

app = FastAPI(title="dash", version="0.0.0")
app.add_middleware(LanAuthMiddleware, settings=settings)
register_login(app, settings)


@app.middleware("http")
async def revalidate(request, call_next):
    # LAN-only, kleine Dateien: immer revalidieren (ETag) → nie stale Assets.
    resp = await call_next(request)
    resp.headers.setdefault("Cache-Control", "no-cache")
    return resp


def _call(fn, *args):
    """Backend-Aufruf → HTTP-Fehler übersetzen. Blockierendes SoCo läuft im Threadpool."""
    try:
        return fn(*args)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc) or "nicht implementiert") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class Level(BaseModel):
    level: int


class Delta(BaseModel):
    delta: int


class Toggle(BaseModel):
    on: bool


class Into(BaseModel):
    into: str


class SourceId(BaseModel):
    source_id: str


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "backend": backend.name, "auth": settings.auth_enforced}


@app.get("/api/state")
def get_state() -> dict:
    return asdict(_call(backend.get_state))


# ---- Transport (auf der Gruppe des Raums) ----
@app.post("/api/rooms/{room}/play")
def play(room: str) -> dict:
    _call(backend.play, room)
    return {"ok": True}


@app.post("/api/rooms/{room}/pause")
def pause(room: str) -> dict:
    _call(backend.pause, room)
    return {"ok": True}


@app.post("/api/rooms/{room}/next")
def next_track(room: str) -> dict:
    _call(backend.next, room)
    return {"ok": True}


@app.post("/api/rooms/{room}/previous")
def previous_track(room: str) -> dict:
    _call(backend.previous, room)
    return {"ok": True}


# ---- Lautstärke ----
@app.post("/api/rooms/{room}/group-volume")
def group_volume(room: str, body: Level) -> dict:
    _call(backend.set_group_volume, room, body.level)
    return {"ok": True}


@app.post("/api/rooms/{room}/group-volume/rel")
def group_volume_rel(room: str, body: Delta) -> dict:
    _call(backend.set_group_volume_rel, room, body.delta)
    return {"ok": True}


@app.post("/api/rooms/{room}/group-mute")
def group_mute(room: str, body: Toggle) -> dict:
    _call(backend.set_group_mute, room, body.on)
    return {"ok": True}


@app.post("/api/rooms/{room}/volume")
def room_volume(room: str, body: Level) -> dict:
    _call(backend.set_room_volume, room, body.level)
    return {"ok": True}


@app.post("/api/rooms/{room}/mute")
def room_mute(room: str, body: Toggle) -> dict:
    _call(backend.set_room_mute, room, body.on)
    return {"ok": True}


# ---- Gruppierung ----
@app.post("/api/rooms/{room}/group")
def group_into(room: str, body: Into) -> dict:
    _call(backend.group, room, body.into)
    return {"ok": True}


@app.post("/api/rooms/{room}/ungroup")
def ungroup(room: str) -> dict:
    _call(backend.ungroup, room)
    return {"ok": True}


# ---- Quellen ----
@app.get("/api/rooms/{room}/sources")
def sources(room: str) -> list[dict]:
    return [asdict(s) for s in _call(backend.list_sources, room)]


@app.post("/api/rooms/{room}/play-source")
def play_source(room: str, body: SourceId) -> dict:
    _call(backend.play_source, room, body.source_id)
    return {"ok": True}


# web/ als letztes mounten (greift als Catch-all NACH den /api-Routen).
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
