#!/usr/bin/env bash
set -euo pipefail

REPO="/home/bioiot/deteccion_agave"
PID_FILE="$REPO/rpi_live_tests/live_display.pid"
LOG="$REPO/rpi_live_tests/live_display.log"

mkdir -p "$REPO/rpi_live_tests"
if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$PID" ]; then
    if [ -r "/proc/$PID/cmdline" ] && tr '\0' ' ' < "/proc/$PID/cmdline" | grep -q 'agave-display'; then
      PGID="$(ps -o pgid= -p "$PID" | tr -d ' ')"
      if [ "$PGID" = "$PID" ]; then
        kill -- "-$PID" 2>/dev/null || true
      fi
    fi
    pkill -P "$PID" 2>/dev/null || true
    kill "$PID" 2>/dev/null || true
    printf '%s Stopped PID %s\n' "$(date '+%F %T')" "$PID" >> "$LOG"
  fi
fi

rm -f "$PID_FILE"
