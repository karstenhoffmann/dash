#!/bin/bash
# Zweck:    Sonos-Controller lokal am MacBook starten (venv + Browser, gegen echte Speaker)
# Aufrufer: manuell am MacBook: bash scripts/run-local-macbook.sh
# Stand:    2026-06-29
# Erstellt: 2026-06-29
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"

python3 -m venv .venv 2>/dev/null || true
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

PORT="${PORT:-5005}"
PIDS="$(lsof -ti tcp:"$PORT" 2>/dev/null || true)"
[ -n "$PIDS" ] && kill $PIDS 2>/dev/null && sleep 1 || true

echo "Sonos-Controller laeuft auf http://localhost:$PORT  (Strg+C zum Beenden)"
( sleep 1.5; open "http://localhost:$PORT" 2>/dev/null || true ) &
PORT="$PORT" SONOS_DEV=1 .venv/bin/python app.py
