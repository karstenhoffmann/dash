#!/bin/bash
# Zweck:    soco-cli-Test-Footprint restlos von Mele entfernen
# Aufrufer: manuell, via: ssh mele 'bash -s' < scripts/mele-uninstall.sh
# Stand:    2026-06-29
# Erstellt: 2026-06-29
set -euo pipefail

removed=0

DIR="$HOME/lab/sonos-controller"
if [ -d "$DIR" ]; then rm -rf "$DIR"; echo "entfernt: $DIR"; removed=1; fi

CACHE="$HOME/.soco-cli"
if [ -d "$CACHE" ]; then rm -rf "$CACHE"; echo "entfernt: $CACHE (soco-cli Speaker-Cache)"; removed=1; fi

if [ "$removed" -eq 1 ]; then
  echo "OK: Mele ist wieder sauber. (apt-Paket python3-venv bleibt — System-Paket, harmlos.)"
else
  echo "Nichts zu tun: kein Footprint gefunden."
fi
