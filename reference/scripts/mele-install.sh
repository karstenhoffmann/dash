#!/bin/bash
# Zweck:    soco-cli (lokale Sonos-Steuerung) in isoliertem venv auf Mele installieren
# Aufrufer: manuell, via: ssh mele 'bash -s' < scripts/mele-install.sh
# Stand:    2026-06-29
# Erstellt: 2026-06-29
set -euo pipefail

DIR="$HOME/lab/sonos-controller"
mkdir -p "$DIR"

if ! python3 -m venv "$DIR/venv" 2>/tmp/sonos_venv_err; then
  echo "FEHLER: venv-Erstellung fehlgeschlagen. Einmalig noetig (mit TTY):"
  echo "  ssh -t mele 'sudo apt-get install -y python3-venv'"
  echo "Danach dieses Skript erneut laufen lassen. Details:"
  cat /tmp/sonos_venv_err
  exit 1
fi

"$DIR/venv/bin/pip" install --upgrade pip --quiet
"$DIR/venv/bin/pip" install soco-cli --quiet

cat > "$DIR/README.txt" <<EOF
Sonos-Controller — Test-Footprint (soco-cli im venv)
Reines lokales UPnP-Tooling fuer Sonos S1. Aendert nichts an den Speakern.
Workspace-Quelle/Doku: projects/lab/2026-06_sonos-controller/ (MacBook __claude)
Restlos entfernen: rm -rf ~/lab/sonos-controller
Stand: 2026-06-29
EOF

echo "OK: soco-cli installiert in $DIR/venv"
"$DIR/venv/bin/sonos" --version 2>/dev/null || true
