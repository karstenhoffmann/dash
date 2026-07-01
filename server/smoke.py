"""Boot-/Routen-Smoke (CI, ADR-0008). Hardware-frei: keine echten Speaker nötig.

Lauf:  python -m server.smoke   →  Exit 0 = ok, sonst Fehler.
"""

from __future__ import annotations

import sys

from .backend import Backend, SocoBackend
from .backend.soco_backend import CAPABILITIES
from .config import DEFAULT_ROOMS
from .main import app


def main() -> int:
    paths = {getattr(r, "path", None) for r in app.routes}
    required = {
        "/api/health",
        "/api/state",
        "/api/rooms/{room}/play",
        "/api/rooms/{room}/group-volume",
        "/api/rooms/{room}/sources",
        "/login",
    }
    missing = required - paths
    if missing:
        print(f"FEHLT: Routen {sorted(missing)} nicht registriert", file=sys.stderr)
        return 1

    # Hardware-frei: leere Geräte-Injektion → kein Netzwerk.
    be = SocoBackend(rooms=DEFAULT_ROOMS, devices={})
    if not isinstance(be, Backend):
        print("FEHLT: SocoBackend erfüllt das Backend-Protocol nicht", file=sys.stderr)
        return 1

    snap = be.get_state()
    if snap.groups != [] or snap.capabilities != CAPABILITIES:
        print("FEHLT: leerer Snapshot unerwartet", file=sys.stderr)
        return 1

    print("smoke ok: Routen registriert, SocoBackend erfüllt Backend-Port, Snapshot valide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
