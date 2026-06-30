"""Boot-/Routen-Smoke (CI, ADR-0008). Importiert die App und prüft Kernrouten + Backend.

Lauf:  python -m server.smoke   →  Exit 0 = ok, sonst Fehler.
"""

from __future__ import annotations

import sys

from .backend import Backend, make_backend
from .main import app


def main() -> int:
    paths = {getattr(r, "path", None) for r in app.routes}
    required = {"/api/health", "/api/state", "/login"}
    missing = required - paths
    if missing:
        print(f"FEHLT: Routen {sorted(missing)} nicht registriert", file=sys.stderr)
        return 1

    be = make_backend("soco")
    if not isinstance(be, Backend):
        print("FEHLT: SocoBackend erfüllt das Backend-Protocol nicht", file=sys.stderr)
        return 1

    snap = be.get_state()
    if snap.capabilities.get("transport") is not True:
        print("FEHLT: Capabilities-Snapshot unerwartet", file=sys.stderr)
        return 1

    print("smoke ok: Routen registriert, SocoBackend erfüllt Backend-Port, Snapshot valide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
