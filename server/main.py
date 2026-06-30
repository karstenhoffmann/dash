"""dash — FastAPI-App: liefert das Frontend (web/) + JSON-API gegen den Backend-Port.

Ein Port, UI + API zusammen (kein CORS). Blockierende SoCo-Aufrufe laufen über
plain `def`-Endpoints im Threadpool (FastAPI-Empfehlung, ADR-0008). Auth = LAN
(ADR-0004).
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .auth import LanAuthMiddleware, register_login
from .backend import make_backend
from .config import Settings

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

settings = Settings.from_env()
backend = make_backend(
    settings.backend,
    soco_seed_ips=settings.soco_seed_ips,
    ha_url=settings.ha_url,
    ha_token=settings.ha_token,
)

app = FastAPI(title="dash", version="0.0.0")
app.add_middleware(LanAuthMiddleware, settings=settings)
register_login(app, settings)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "backend": backend.name, "auth": settings.auth_enforced}


@app.get("/api/state")
def get_state() -> dict:
    # plain def → Threadpool: blockierendes SoCo blockiert den Event-Loop nicht.
    return asdict(backend.get_state())


@app.post("/api/rooms/{room}/play")
def play(room: str) -> dict:
    try:
        backend.play(room)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    return {"ok": True}


# web/ als letztes mounten (greift als Catch-all NACH den /api-Routen).
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
