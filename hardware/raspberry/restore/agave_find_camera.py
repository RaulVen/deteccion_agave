#!/usr/bin/env python3
import argparse
import concurrent.futures
import ipaddress
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


def parse_args():
    parser = argparse.ArgumentParser(description="Find a Dahua RTSP camera on the local LAN.")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--subnet", default="192.168.1.0/24")
    parser.add_argument("--preferred", action="append", default=[])
    parser.add_argument("--timeout", type=float, default=6.0)
    return parser.parse_args()


def port_open(ip, port, timeout=0.35):
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def probe_rtsp(ip, user, password, timeout):
    if not port_open(ip, 554):
        return None
    safe_user = quote(user, safe="")
    safe_password = quote(password, safe="")
    url = f"rtsp://{safe_user}:{safe_password}@{ip}:554/cam/realmonitor?channel=1&subtype=1"
    cmd = [
        "timeout",
        str(int(timeout) + 2),
        "ffprobe",
        "-v",
        "error",
        "-rtsp_transport",
        "tcp",
        "-analyzeduration", "1000000",
        "-probesize", "128000",
        "-show_entries",
        "stream=codec_name,width,height,avg_frame_rate",
        "-of",
        "default=nw=1",
        url,
    ]
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+3)
    except subprocess.TimeoutExpired:
        return None
    if completed.returncode == 0 and "codec_name=" in completed.stdout:
        return url
    return None


def scan_candidates(subnet):
    hosts = [str(ip) for ip in ipaddress.ip_network(subnet).hosts()]

    def check(ip):
        ports = []
        for port in (37777, 554, 80):
            if port_open(ip, port):
                ports.append(port)
        return ip, ports

    with concurrent.futures.ThreadPoolExecutor(max_workers=96) as pool:
        rows = list(pool.map(check, hosts))

    strong = [ip for ip, ports in rows if 37777 in ports and 554 in ports]
    rtsp = [ip for ip, ports in rows if ip not in strong and 554 in ports]
    return strong + rtsp


def main():
    args = parse_args()
    preferred = []
    for item in args.preferred:
        preferred.extend(part.strip() for part in item.split(",") if part.strip())

    cache = Path.home() / 'deteccion_agave/rpi_live_tests/last_camera_ip.txt'
    if cache.exists():
        preferred.insert(0, cache.read_text().strip())
    seen = set()
    candidates = []
    groups = [lambda: preferred]
    for subnet in args.subnet.split(','):
        groups.append(lambda subnet=subnet: scan_candidates(subnet.strip()))
    for group in groups:
        for ip in group():
            if ip in seen:
                continue
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                continue
            seen.add(ip); candidates.append(ip)
            url = probe_rtsp(ip, args.user, args.password, args.timeout)
            if url:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(ip+'\n')
                print(url)
                return 0

    print("No RTSP camera found with the configured credentials.", file=sys.stderr)
    print("Tried: " + ", ".join(candidates), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
