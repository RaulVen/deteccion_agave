import argparse
import getpass
import html
import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import paramiko


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.image = b""
        self.metrics = {"status": "starting"}
        self.updated = 0.0

    def update(self, image=None, metrics=None):
        with self.lock:
            if image:
                self.image = image
            if metrics:
                self.metrics = metrics
            self.updated = time.time()

    def snapshot(self):
        with self.lock:
            return self.image, dict(self.metrics), self.updated


def connect(args):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=args.host,
        username=args.user,
        password=args.password,
        timeout=12,
        banner_timeout=12,
        auth_timeout=12,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def ssh_text(client, cmd, timeout=10):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    rc = stdout.channel.recv_exit_status()
    return rc, out, err


def parse_metrics(text):
    data = {"status": "ok"}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def collector(args, state):
    metrics_cmd = r"""
temp="$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0)"
echo "temp_c=$(awk "BEGIN {printf \"%.1f\", $temp/1000}")"
echo "throttled=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2 || echo n/a)"
echo "arm_mhz=$(vcgencmd measure_clock arm 2>/dev/null | awk -F= "{printf \"%.0f\", \$2/1000000}" || echo n/a)"
echo "core_volts=$(vcgencmd measure_volts core 2>/dev/null | cut -d= -f2 || echo n/a)"
echo "loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
free -m | awk '/Mem:/ {printf "mem_used_mb=%s\nmem_total_mb=%s\n", $3, $2}'
df -h / | awk 'NR==2 {printf "root_used=%s\nroot_avail=%s\nroot_use_pct=%s\n", $3, $4, $5}'
df -h /boot/firmware 2>/dev/null | awk 'NR==2 {printf "boot_used=%s\nboot_avail=%s\nboot_use_pct=%s\n", $3, $4, $5}'
ps -u bioiot -o pid=,pcpu=,pmem=,etime=,comm=,args= | grep -E '[r]pi_live_infer_display|[a]gave-display' | head -n 4 | sed 's/^/proc=/'
tail -n 3 /home/bioiot/deteccion_agave/rpi_live_tests/live_display.log 2>/dev/null | sed 's/^/log=/'
ls -lh /home/bioiot/deteccion_agave/rpi_live_tests/*.jsonl 2>/dev/null | sed 's/^/jsonl=/'
"""
    image_cmd = (
        "export XDG_RUNTIME_DIR=/run/user/1000; "
        "export WAYLAND_DISPLAY=wayland-0; "
        "export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; "
        "grim - 2>/dev/null"
    )
    while True:
        client = None
        try:
            client = connect(args)
            while True:
                rc, out, err = ssh_text(client, metrics_cmd, timeout=10)
                metrics = parse_metrics(out)
                metrics["ssh_rc"] = str(rc)
                metrics["time"] = time.strftime("%H:%M:%S")
                stdin, stdout, stderr = client.exec_command(image_cmd, timeout=10)
                image = stdout.read()
                img_rc = stdout.channel.recv_exit_status()
                if img_rc != 0 or not image.startswith(b"\x89PNG"):
                    image = None
                    metrics["capture"] = f"failed rc={img_rc}"
                state.update(image=image, metrics=metrics)
                time.sleep(args.interval)
        except Exception as exc:
            state.update(metrics={"status": f"ssh error: {exc!r}", "time": time.strftime("%H:%M:%S")})
            time.sleep(2)
        finally:
            if client:
                client.close()


def color_for_temp(value):
    try:
        temp = float(value)
    except Exception:
        return "#aaa"
    if temp >= 80:
        return "#ff4d4d"
    if temp >= 70:
        return "#ffb84d"
    return "#72e06a"


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def do_GET(self):
            image, metrics, updated = state.snapshot()
            if self.path.startswith("/latest.png"):
                if not image:
                    self.send_response(503)
                    self.end_headers()
                    self.wfile.write(b"no image yet")
                    return
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(image)))
                self.end_headers()
                self.wfile.write(image)
                return
            if self.path.startswith("/metrics.json"):
                body = json.dumps(metrics).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return

            temp_color = color_for_temp(metrics.get("temp_c", ""))
            rows = []
            for key in ["time", "status", "temp_c", "throttled", "arm_mhz", "core_volts", "loadavg", "mem_used_mb", "mem_total_mb", "root_used", "root_avail", "root_use_pct", "boot_used", "boot_avail", "boot_use_pct"]:
                rows.append(f"<tr><th>{html.escape(key)}</th><td>{html.escape(str(metrics.get(key, '')))}</td></tr>")
            procs = "\n".join(v for k, v in metrics.items() if k == "proc")
            body = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>RPi Health Monitor</title>
<style>
body{{margin:0;background:#101214;color:#e8e8e8;font-family:Arial,sans-serif;display:grid;grid-template-columns:360px 1fr;height:100vh}}
aside{{padding:16px;background:#191d20;overflow:auto;border-right:1px solid #30363a}}
h1{{font-size:18px;margin:0 0 14px}} table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{text-align:left;border-bottom:1px solid #30363a;padding:7px}} th{{color:#9aa4aa;font-weight:500}}
.temp{{font-size:48px;color:{temp_color};font-weight:700;margin:10px 0 18px}}
main{{display:grid;place-items:center;background:#0b0b0b}} img{{max-width:100%;max-height:100%;object-fit:contain}}
pre{{white-space:pre-wrap;background:#111;padding:10px;border:1px solid #333;border-radius:6px}}
</style></head>
<body><aside><h1>Raspberry Pi</h1><div class="temp">{html.escape(str(metrics.get('temp_c','?')))} °C</div>
<table>{''.join(rows)}</table><h1>Procesos</h1><pre>{html.escape(procs)}</pre></aside>
<main><img id="screen" src="/latest.png?t={time.time()}"></main>
<script>
setInterval(()=>{{location.reload()}}, 2000);
</script></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.1.239")
    parser.add_argument("--user", default="bioiot")
    parser.add_argument("--password", default=os.environ.get("RPI_PASSWORD"))
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    if not args.password:
        args.password = getpass.getpass("RPi SSH password: ")
    state = State()
    threading.Thread(target=collector, args=(args, state), daemon=True).start()
    print(f"Health monitor: http://127.0.0.1:{args.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(state)).serve_forever()


if __name__ == "__main__":
    main()
