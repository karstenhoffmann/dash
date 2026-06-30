"""LAN-Zugriffsschutz (ADR-0004): IP-Whitelist + einmaliges Passwort (Remember-Cookie).

Kein Benutzer-Login. Reihenfolge je Request:
  1. Auth nicht erzwungen (weder Whitelist noch Passwort gesetzt) → durchlassen (LAN-Dev).
  2. Client-IP in Whitelist → durchlassen.
  3. Gültiges Remember-Cookie → durchlassen.
  4. Sonst: /api/* → 401; HTML → schlanke Passwort-Seite.

Hinweis: hinter Caddy steht die echte Client-IP in `X-Forwarded-For` (Proxy als
vertrauenswürdig konfigurieren). MAC ist für den Webserver nicht sichtbar → IP ist
die korrekte Umsetzung der Absicht.
"""

from __future__ import annotations

import hashlib
import hmac

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

from .config import Settings

COOKIE_NAME = "dash_auth"
PUBLIC_PATHS = {"/api/health", "/login"}


def _token(password: str) -> str:
    """Stabiles Cookie-Token aus dem Passwort (kein Klartext im Cookie)."""
    return hashlib.sha256(("dash:" + password).encode()).hexdigest()


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else ""


class LanAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next):
        s = self.settings
        if not s.auth_enforced or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        if s.ip_whitelist and _client_ip(request) in s.ip_whitelist:
            return await call_next(request)

        if s.password and hmac.compare_digest(
            request.cookies.get(COOKIE_NAME, ""), _token(s.password)
        ):
            return await call_next(request)

        if request.url.path.startswith("/api/"):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        return HTMLResponse(_LOGIN_PAGE, status_code=401)


def register_login(app, settings: Settings) -> None:
    """POST /login: Passwort prüfen, Remember-Cookie setzen."""

    @app.post("/login")
    async def login(request: Request):  # noqa: ANN202 (FastAPI-Route)
        form = await request.form()
        password = str(form.get("password", ""))
        if settings.password and hmac.compare_digest(password, settings.password):
            resp = RedirectResponse("/", status_code=303)
            resp.set_cookie(
                COOKIE_NAME,
                _token(settings.password),
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="lax",
            )
            return resp
        return HTMLResponse(_LOGIN_PAGE, status_code=401)


_LOGIN_PAGE = """<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>dash — Zugang</title></head>
<body style="font-family:system-ui;display:grid;place-items:center;min-height:100dvh">
<form method="post" action="/login" style="display:flex;gap:.5rem">
<input type="password" name="password" placeholder="Passwort" autofocus
 style="padding:.75rem;font-size:1rem">
<button style="padding:.75rem 1rem;font-size:1rem">OK</button>
</form></body></html>
"""
