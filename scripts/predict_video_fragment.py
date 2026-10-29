"""Run a trained detector on an exact frame interval, including DAV sources.

Decode sequentially: seeking in DAV containers is not reliable. Outputs are
qualitative predictions with optional tracking and line-crossing events, not
labels, verified unique plant counts, or accuracy metrics.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import cv2
import numpy as np


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def header(frame, text):
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), (22, 27, 31), -1)
    cv2.putText(frame, text, (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.72,
                (255, 255, 255), 2, cv2.LINE_AA)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("source", "model", "ffmpeg", "output"):
        parser.add_argument(f"--{key}", type=Path, required=True)
    parser.add_argument("--start", type=float, default=60)
    parser.add_argument("--duration", type=float, default=60)
    parser.add_argument("--conf", type=float, default=0.30)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="0")
    parser.add_argument("--tracker", type=Path, help="Enable persistent tracking with this YAML.")
    parser.add_argument("--line-ratio", type=float, default=0.5)
    parser.add_argument("--direction", choices=("down", "up", "both"), default="down")
    parser.add_argument("--output-width", type=int, default=1920)
    parser.add_argument("--crf", type=int, default=20)
    parser.add_argument("--maxrate", help="Optional H.264 bitrate cap, e.g. 6M.")
    args = parser.parse_args()
    if args.start < 0 or args.duration <= 0 or not 0 < args.conf < 1:
        parser.error("Invalid interval or confidence threshold")
    if not 0 < args.line_ratio < 1 or args.output_width < 640 or args.output_width % 2:
        parser.error("Invalid line position or even output width")
    for p in (args.source, args.model, args.ffmpeg, *((args.tracker,) if args.tracker else ())):
        if not p.is_file():
            raise FileNotFoundError(p)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    basename = "conteo_agaves" if args.tracker else "prediccion_agave"
    movie = out / f"{basename}.mp4"
    partial = out / f"{basename}.partial.mp4"
    for name in (movie, partial, out / "predicciones.jsonl", out / "inferencia.json", out / "cruces.csv"):
        if name.exists():
            raise FileExistsError(f"Refusing to overwrite {name}")
    (out / "runtime_settings").mkdir(exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(out / "runtime_settings"))
    from ultralytics import YOLO, __version__ as ultralytics_version
    import torch

    cap = cv2.VideoCapture(str(args.source), cv2.CAP_FFMPEG,
                           [cv2.CAP_PROP_N_THREADS, 2])
    if not cap.isOpened():
        raise RuntimeError("Cannot decode the input video")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width, height = (int(cap.get(prop)) for prop in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT))
    if not fps > 0:
        raise RuntimeError("Video frame rate is unknown")
    start_frame = round(args.start * fps)
    count = round(args.duration * fps)
    ow = min(args.output_width, width)
    oh = round(height * ow / width / 2) * 2
    meta = {
        "status": "running", "started_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(args.source.resolve()), "source_sha256": sha256(args.source),
        "source_fps": fps, "source_size": [width, height],
        "start_frame_zero_based": start_frame, "end_frame_exclusive": start_frame + count,
        "start_seconds": start_frame / fps, "duration_seconds": count / fps,
        "model": str(args.model.resolve()), "model_sha256": sha256(args.model),
        "parameters": {"imgsz": args.imgsz, "conf": args.conf, "iou": 0.7,
                       "rect": False, "half": False, "max_det": 300, "device": args.device},
        "ultralytics": ultralytics_version, "torch": torch.__version__,
        "output_size": [ow, oh], "output_fps": fps,
        "interpretation": "Qualitative per-frame predictions; no tracking, unique counts, or ground-truth scoring.",
        "frames_written": 0,
    }
    save_json(out / "inferencia.json", meta)
    model = YOLO(str(args.model))
    meta["classes"] = model.names
    meta["model_end2end"] = bool(getattr(model.model, "end2end", False))
    counter = None
    trails = defaultdict(lambda: deque(maxlen=24))
    flash_until = {}
    if args.tracker:
        from line_crossing_counter import LineCrossingCounter
        counter = LineCrossingCounter(height * args.line_ratio, args.direction)
        meta["tracking"] = {
            "tracker_yaml": str(args.tracker.resolve()), "tracker_sha256": sha256(args.tracker),
            "persist": True, "line_ratio": args.line_ratio, "line_y_source": counter.line_y,
            "anchor": "bounding_box_center", "direction": args.direction,
            "unique_id_once_per_direction": True,
            "start_state": "Tracker and counter start empty at the clip's first frame.",
            "note": "IDs are tracker identities, not a verified census of unique plants."
        }
        meta["interpretation"] = "Automatic line-crossing events by persistent track ID; no manual ground-truth count."
    for i in range(start_frame):
        if not cap.grab():
            raise RuntimeError(f"Input ended before requested start at frame {i}")

    command = [str(args.ffmpeg), "-hide_banner", "-loglevel", "warning", "-n",
               "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ow}x{oh}",
               "-r", str(fps), "-i", "pipe:0", "-an", "-c:v", "libx264",
               "-preset", "fast", "-crf", str(args.crf), "-threads", "4"]
    if args.maxrate:
        command += ["-maxrate", args.maxrate, "-bufsize", args.maxrate]
    command += ["-pix_fmt", "yuv420p", "-movflags", "+faststart", str(partial)]
    counts, comparisons = [], []
    sample_indices = sorted({0, count // 5, count * 2 // 5, count * 3 // 5, count * 4 // 5, count - 1})
    tick = time.perf_counter()
    proc = None
    try:
        with (out / "ffmpeg.log").open("w", encoding="utf-8") as log, \
                (out / "predicciones.jsonl").open("x", encoding="utf-8") as predictions:
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            for local in range(count):
                ok, frame = cap.read()
                if not ok:
                    raise RuntimeError(f"Input ended at frame {start_frame + local}")
                if args.tracker:
                    result = model.track(frame, persist=True, tracker=str(args.tracker.resolve()),
                                         verbose=False, save=False, **meta["parameters"])[0]
                else:
                    result = model.predict(frame, verbose=False, save=False, **meta["parameters"])[0]
                boxes = result.boxes
                data = np.column_stack((boxes.xyxy.cpu().numpy(), boxes.conf.cpu().numpy(),
                                        boxes.cls.cpu().numpy()))
                ids = boxes.id.cpu().numpy().astype(int).tolist() if boxes.id is not None else [None] * len(data)
                counts.append(len(data))
                new_events = []
                if counter:
                    for row, track_id in zip(data, ids):
                        if track_id is None:
                            continue
                        cx, cy = (row[0]+row[2])/2, (row[1]+row[3])/2
                        event = counter.update(track_id, start_frame + local, float(cx), float(cy))
                        trails[track_id].append((round(cx*ow/width), round(cy*oh/height)))
                        if event:
                            event.update(event_number=counter.total,
                                         source_time_seconds=(start_frame+local)/fps,
                                         clip_time_seconds=local/fps,
                                         crossing_source_time_seconds=event["crossing_frame_interpolated"]/fps,
                                         confidence=float(row[4]))
                            new_events.append(event)
                            flash_until[track_id] = local + round(fps)
                predictions.write(json.dumps({"frame": start_frame + local,
                    "time_seconds": (start_frame + local) / fps,
                    "clip_time_seconds": local/fps,
                    "detections_xyxy_conf_class": data.tolist(), "track_ids": ids,
                    "crossing_total": counter.total if counter else None,
                    "new_crossings": new_events}, allow_nan=False) + "\n")
                rendered = cv2.resize(frame, (ow, oh), interpolation=cv2.INTER_AREA)
                labels = []
                for (x1, y1, x2, y2, confidence, cls), track_id in zip(data, ids):
                    x1, x2 = (round(v * ow / width) for v in (x1, x2))
                    y1, y2 = (round(v * oh / height) for v in (y1, y2))
                    color = (65, 230, 80)
                    if counter and track_id is not None:
                        color = (30, 165, 255) if flash_until.get(track_id, -1) >= local else color
                        pts = list(trails[track_id])
                        for p1, p2 in zip(pts, pts[1:]):
                            cv2.line(rendered, p1, p2, (255, 200, 0), 2, cv2.LINE_AA)
                        cv2.circle(rendered, ((x1+x2)//2, (y1+y2)//2), 4, color, -1)
                    cv2.rectangle(rendered, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
                    label = f"{model.names[int(cls)]} " + (f"ID {track_id} " if track_id is not None else "") + f"{confidence:.2f}"
                    labels.append((label, x1, y1, color))
                for label, x1, y1, color in labels:
                    (tw, th), base = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, .55, 1)
                    lx, ly = max(0, min(x1, ow - tw - 8)), max(th + 6, y1 - 4)
                    cv2.rectangle(rendered, (lx, ly-th-5), (lx+tw+6, ly+base), color, -1)
                    cv2.putText(rendered, label, (lx+3, ly), cv2.FONT_HERSHEY_SIMPLEX,
                                .55, (10, 30, 10), 1, cv2.LINE_AA)
                t = (start_frame + local) / fps
                if counter:
                    ly = round(args.line_ratio * oh)
                    cv2.line(rendered, (0, ly), (ow-1, ly), (0, 255, 255), 3, cv2.LINE_AA)
                    cv2.rectangle(rendered, (12, ly-32), (280, ly-7), (22,27,31), -1)
                    cv2.putText(rendered, f"LINEA DE CONTEO {args.line_ratio:.0%}", (20,ly-13),
                                cv2.FONT_HERSHEY_SIMPLEX, .57, (0,255,255), 1, cv2.LINE_AA)
                    cv2.rectangle(rendered, (0,0), (ow,88), (22,27,31), -1)
                    direction_label = {"down":"hacia abajo", "up":"hacia arriba", "both":"ambos sentidos"}[args.direction]
                    cv2.putText(rendered, f"AGAVES CONTADOS: {counter.total}  |  Cruce {direction_label}",
                                (16,34), cv2.FONT_HERSHEY_SIMPLEX, .9, (255,255,255), 2, cv2.LINE_AA)
                    cv2.putText(rendered, f"YOLO26s + SGD | {args.imgsz}px | conf {args.conf:.2f} | "
                                f"Video {int(t)//60:02d}:{t%60:05.2f} | Clip {local/fps:.1f}s",
                                (16,67), cv2.FONT_HERSHEY_SIMPLEX, .60, (220,220,220), 1, cv2.LINE_AA)
                else:
                    header(rendered, f"YOLO26s + SGD | {args.imgsz}px | conf >= {args.conf:.2f} | "
                           f"{int(t)//60:02d}:{t%60:05.2f} | detecciones: {len(data)}")
                proc.stdin.write(rendered.tobytes())
                for event in new_events:
                    cv2.imwrite(str(out / f"cruce_{event['event_number']:03d}_id{event['track_id']:03d}.jpg"), rendered)
                if local in sample_indices:
                    cv2.imwrite(str(out / f"prediccion_frame_{start_frame+local:05d}.jpg"), rendered)
                    original = cv2.resize(frame, (ow, oh), interpolation=cv2.INTER_AREA)
                    header(original, f"Original | {int(t)//60:02d}:{t%60:05.2f}")
                    comparison = np.hstack((cv2.resize(original, (960, 540)),
                                            cv2.resize(rendered, (960, 540))))
                    cv2.imwrite(str(out / f"comparacion_frame_{start_frame+local:05d}.jpg"), comparison)
                    comparisons.append(cv2.resize(comparison, (1280, 360)))
                if (local + 1) % 150 == 0:
                    meta["frames_written"] = local + 1
                    if counter:
                        meta["crossing_counts"] = dict(counter.counts)
                    save_json(out / "inferencia.json", meta)
                    print(f"Processed {local+1}/{count} frames" +
                          (f" | crossings={counter.total}" if counter else ""), flush=True)
            proc.stdin.close()
            if proc.wait(timeout=120) != 0:
                raise RuntimeError("MP4 encoding failed; see ffmpeg.log")
        cap.release()
        partial.rename(movie)
        cv2.imwrite(str(out / "comparacion_original_prediccion.jpg"), np.vstack(comparisons))
        if counter:
            meta["crossing_counts"] = dict(counter.counts)
            meta["crossing_total"] = counter.total
            save_json(out / "cruces.json", counter.events)
            fields = ["event_number", "track_id", "direction", "frame", "previous_frame",
                      "source_time_seconds", "clip_time_seconds", "crossing_source_time_seconds",
                      "previous_x", "previous_y", "x", "y", "line_y", "crossing_x",
                      "crossing_frame_interpolated", "gap_frames", "confidence"]
            with (out / "cruces.csv").open("x", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(counter.events)
        meta.update(status="completed", frames_written=count, video=str(movie),
                    completed_utc=datetime.now(timezone.utc).isoformat(),
                    processing_wall_seconds=time.perf_counter() - tick,
                    detection_count_per_frame={"min": min(counts), "max": max(counts),
                                               "median": float(np.median(counts)),
                                               "zero_detection_frames": counts.count(0)})
        save_json(out / "inferencia.json", meta)
        print(json.dumps(meta, ensure_ascii=False), flush=True)
    except Exception as exc:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        meta.update(status="failed", error=str(exc), frames_written=len(counts))
        save_json(out / "inferencia.json", meta)
        raise
    finally:
        cap.release()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
