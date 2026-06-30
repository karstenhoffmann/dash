#!/bin/bash
# Zweck:    soco-cli Funktionstest (READ-ONLY) — Discovery + Direkt-IP-Status der Sonos
# Aufrufer: manuell, via: ssh mele 'bash -s' < scripts/mele-test.sh
# Stand:    2026-06-29
# Erstellt: 2026-06-29
set -uo pipefail

BIN="$HOME/lab/sonos-controller/venv/bin"

if [ ! -x "$BIN/sonos" ]; then
  echo "FEHLER: soco-cli nicht gefunden. Erst mele-install.sh laufen lassen."
  exit 1
fi

echo "=== 1) Discovery via SSDP-Multicast ==="
"$BIN/sonos-discover" || echo "(Discovery fehlgeschlagen — evtl. Multicast ueber WLAN/Repeater. Direkt-IP unten ist der verlaessliche Pfad.)"
echo

echo "=== 2) Direkt-IP (Unicast): Zustand Wohnzimmer-Play:5 (192.168.0.157) ==="
"$BIN/sonos" 192.168.0.157 state
echo

echo "=== 3) Direkt-IP: aktueller Track + Lautstaerke ==="
"$BIN/sonos" 192.168.0.157 track
"$BIN/sonos" 192.168.0.157 volume
echo
echo "Fertig. (Read-only — nichts an den Speakern veraendert.)"
