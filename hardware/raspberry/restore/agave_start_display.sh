#!/usr/bin/env bash
set -euo pipefail

REPO="/home/bioiot/deteccion_agave"
CONFIG="/home/bioiot/.config/agave-display.env"
LOG_DIR="$REPO/rpi_live_tests"
LOG="$LOG_DIR/live_display.log"
PID_FILE="$LOG_DIR/live_display.pid"
MODEL="$REPO/runs/detect/agave_experiments/yolo26s_sgd_cos_slow_120e/weights/best.pt"
PY="$REPO/.venv-rpi-apt/bin/python"

mkdir -p "$LOG_DIR"
touch "$LOG"
exec 9>"$LOG_DIR/start.lock"
flock -n 9 || exit 0
printf "Preparando detector local de agaves...\n"

log() {
  printf '%s %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"
}

if [ ! -f "$CONFIG" ]; then
  log "Missing config: $CONFIG"
  exit 1
fi

# shellcheck disable=SC1090
source "$CONFIG"
MODEL="${AGAVE_MODEL_PATH:-$MODEL}"

if [ ! -x "$PY" ]; then
  log "Missing Python environment: $PY"
  exit 1
fi
if [ ! -f "$MODEL" ] && [ ! -d "$MODEL" ]; then
  log "Missing model: $MODEL"
  exit 1
fi

if [ -f "$PID_FILE" ]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$OLD_PID" ]; then
    "$REPO/scripts/agave_stop_display.sh"
  fi
fi

cd "$REPO"
if ! sudo -n /usr/local/sbin/agave-field-network; then
  log "No se pudo preparar Ethernet. Revisa el cable y la alimentacion de la camara."
  if [ -t 0 ]; then read -r -p "Presiona Enter para cerrar..."; fi
  exit 1
fi
if grep -q '"mode": "field"' /run/agave-field-network.json; then
  CAMERA_SUBNET='192.168.1.0/24,192.168.0.0/24,10.1.1.0/24'
fi
log "Finding camera..."
CAMERA_URL=""
for attempt in 1 2 3 4 5 6; do
  if CAMERA_URL="$($PY scripts/agave_find_camera.py \
    --user "$CAMERA_USER" \
    --password "$CAMERA_PASSWORD" \
    --subnet "${CAMERA_SUBNET:-192.168.1.0/24}" \
    --preferred "${CAMERA_PREFERRED_IPS:-192.168.1.73,192.168.1.108,192.168.1.250,192.168.1.249,192.168.1.248}" \
    --timeout "${CAMERA_PROBE_TIMEOUT:-2.0}" \
    2>> "$LOG")"; then
    break
  fi
  log "Camera scan attempt $attempt failed; retrying..."
  sleep 3
done

if [ -z "$CAMERA_URL" ]; then
  log "No se encontro la camara local. Revisa cable, alimentacion e IP de la red. Internet no es necesario."
  if [ -t 0 ]; then read -r -p "Presiona Enter para cerrar..."; fi
  exit 1
fi
CAMERA_HOST="$(printf '%s\n' "$CAMERA_URL" | sed -E 's#^rtsp://([^:]+):[^@]+@([^/:]+).*#\2#')"
log "Camera found at $CAMERA_HOST. Starting display."

export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
export QT_QPA_PLATFORM=wayland
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export OMP_NUM_THREADS=3
export OPENBLAS_NUM_THREADS=1
export YOLO_AUTOINSTALL=false
export YOLO_OFFLINE=true
export YOLO_VERBOSE=false
export OPENCV_FFMPEG_CAPTURE_OPTIONS="rtsp_transport;tcp|fflags;nobuffer|flags;low_delay"
export AGAVE_CAMERA_RTSP="$CAMERA_URL"
export AGAVE_SCREEN_WIDTH="${AGAVE_SCREEN_WIDTH:-1024}"
export AGAVE_SCREEN_HEIGHT="${AGAVE_SCREEN_HEIGHT:-600}"
export AGAVE_LINE_STATE_FILE="${AGAVE_LINE_STATE_FILE:-$LOG_DIR/line_ratio.txt}"
export AGAVE_EVENTS_FILE="${AGAVE_EVENTS_FILE:-$LOG_DIR/detections_$(date '+%Y%m%d').jsonl}"

# Match the attached Wayland monitor, with the saved size as a fallback.
if SCREEN_SIZE="$($PY -c 'import json,subprocess; outputs=json.loads(subprocess.check_output(["wlr-randr","--json"])); output=next(o for o in outputs if o.get("enabled")); mode=next(m for m in output["modes"] if m.get("current")); scale=output.get("scale",1); print(round(mode["width"]/scale),round(mode["height"]/scale))' 2>/dev/null)"; then
  read -r AGAVE_SCREEN_WIDTH AGAVE_SCREEN_HEIGHT <<< "$SCREEN_SIZE"
fi

nohup setsid bash -c '
while true; do
  "$1" scripts/rpi_live_infer_display.py \
    --model "$2" \
    --conf "$3" \
    --iou "$4" \
    --imgsz "$5" \
    --device "$6" \
    --fullscreen \
    --screen-width "$7" \
    --screen-height "$8" \
    --line-ratio "$9" \
    --line-state-file "${10}" \
    --events-file "${11}" \
    >> "${12}" 2>&1
  rc=$?
  if [ "$rc" -eq 0 ]; then
    exit 0
  fi
  printf "%s Viewer exited with rc=%s; restarting in 2s\n" "$(date "+%F %T")" "$rc" >> "${12}"
  sleep 2
done
' agave-display "$PY" "$MODEL" "${AGAVE_CONF:-0.20}" "${AGAVE_IOU:-0.40}" "${AGAVE_IMGSZ:-320}" "${AGAVE_DEVICE:-cpu}" "$AGAVE_SCREEN_WIDTH" "$AGAVE_SCREEN_HEIGHT" "${AGAVE_LINE_RATIO:-0.50}" "$AGAVE_LINE_STATE_FILE" "$AGAVE_EVENTS_FILE" "$LOG" >> "$LOG" 2>&1 < /dev/null 9>&- &

echo $! > "$PID_FILE"
log "Started PID $(cat "$PID_FILE")"
