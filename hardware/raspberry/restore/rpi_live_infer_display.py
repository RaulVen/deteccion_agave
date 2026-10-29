import argparse
import json
import os
import threading
import multiprocessing as mp
import queue
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import cv2
import numpy as np


@dataclass
class SharedState:
    frame = None
    boxes: list = field(default_factory=list)
    names: dict = field(default_factory=dict)
    infer_count: int = 0
    infer_id: int = 0
    infer_seconds: float = 0.0
    error: str = ""
    stop: bool = False
    captured: int = 0
    frame_at: float = 0.0
    model_ready: bool = False


def parse_args():
    parser = argparse.ArgumentParser(description="Show RTSP video with YOLO detections on the Pi monitor.")
    parser.add_argument("--source", default=os.environ.get("AGAVE_CAMERA_RTSP"), help="RTSP URL or video source.")
    parser.add_argument("--model", required=True, help="YOLO model path.")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.40)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--window", default="Agave inference")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--screen-width", type=int, default=int(os.environ.get("AGAVE_SCREEN_WIDTH", "1024")))
    parser.add_argument("--screen-height", type=int, default=int(os.environ.get("AGAVE_SCREEN_HEIGHT", "600")))
    parser.add_argument("--line-ratio", type=float, default=None)
    parser.add_argument("--line-state-file", default=os.environ.get("AGAVE_LINE_STATE_FILE"))
    parser.add_argument("--events-file", default=os.environ.get("AGAVE_EVENTS_FILE"))
    parser.add_argument("--track-max-distance", type=float, default=float(os.environ.get("AGAVE_TRACK_MAX_DISTANCE", "110")))
    parser.add_argument("--track-ttl", type=int, default=int(os.environ.get("AGAVE_TRACK_TTL", "8")))
    args = parser.parse_args()
    if not args.source:
        parser.error("--source or AGAVE_CAMERA_RTSP is required")
    return args


def clamp(value, low=0.05, high=0.95):
    return max(low, min(high, value))


def read_line_ratio(args):
    if args.line_state_file:
        try:
            return clamp(float(Path(args.line_state_file).read_text().strip()))
        except Exception:
            pass
    return clamp(args.line_ratio if args.line_ratio is not None else 0.50)


def write_line_ratio(path, value):
    if not path:
        return
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{value:.4f}\n")
    except Exception:
        pass


def default_events_file():
    return Path("rpi_live_tests") / f"detections_{datetime.now().strftime('%Y%m%d')}.jsonl"


def source_host(source):
    try:
        return urlparse(source).hostname or str(source)
    except Exception:
        return str(source)


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def box_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def append_jsonl(path, payload):
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n")
    except Exception:
        pass


class LineCounter:
    def __init__(self, max_distance, ttl):
        self.max_distance = max_distance
        self.ttl = ttl
        self.next_id = 1
        self.tracks = {}
        self.count = 0

    def update(self, boxes, names, line_ratio, frame_shape, infer_id, args):
        h, w = frame_shape[:2]
        line_y = h * line_ratio
        detections = []
        for box, class_id, score in boxes:
            cx, cy = box_center(box)
            detections.append(
                {
                    "box": [float(v) for v in box],
                    "class_id": int(class_id),
                    "class_name": str(names.get(class_id, class_id)),
                    "confidence": float(score),
                    "center": (cx, cy),
                    "side": -1 if cy < line_y else 1,
                }
            )

        assigned = set()
        events = []
        for det in detections:
            cx, cy = det["center"]
            best_id = None
            best_dist = self.max_distance
            for track_id, track in self.tracks.items():
                if track_id in assigned:
                    continue
                tx, ty = track["center"]
                dist = ((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5
                if dist < best_dist:
                    best_dist = dist
                    best_id = track_id

            if best_id is None:
                best_id = self.next_id
                self.next_id += 1
                self.tracks[best_id] = {
                    "center": det["center"],
                    "side": det["side"],
                    "last_seen": infer_id,
                    "counted": False,
                }

            track = self.tracks[best_id]
            old_side = track["side"]
            crossed = old_side != det["side"] and not track["counted"]
            track.update(center=det["center"], side=det["side"], last_seen=infer_id)
            assigned.add(best_id)

            if crossed:
                track["counted"] = True
                self.count += 1
                event = {
                    "timestamp": now_iso(),
                    "event": "line_crossing",
                    "count": self.count,
                    "track_id": best_id,
                    "class_id": det["class_id"],
                    "class_name": det["class_name"],
                    "confidence": round(det["confidence"], 4),
                    "bbox_xyxy": [round(v, 2) for v in det["box"]],
                    "center_xy": [round(cx, 2), round(cy, 2)],
                    "line_ratio": round(float(line_ratio), 4),
                    "line_y": round(float(line_y), 2),
                    "infer_id": int(infer_id),
                    "source_host": source_host(args.source),
                }
                events.append(event)

        stale = [track_id for track_id, track in self.tracks.items() if infer_id - track["last_seen"] > self.ttl]
        for track_id in stale:
            del self.tracks[track_id]
        return events


def inference_worker(args, frames, results, stop):
    """Separate process: NCNN must not hold the viewer's Python interpreter."""
    try:
        ncnn_mode = Path(args.model).is_dir()
        if ncnn_mode:
            from agave_ncnn import AgaveNCNN
            model = AgaveNCNN(args.model, threads=2)
        else:
            from ultralytics import YOLO
            import torch
            torch.set_num_threads(2)
            model = YOLO(args.model, task="detect")
        infer_id = 0
        while not stop.is_set():
            try:
                frame = frames.get(timeout=0.2)
            except queue.Empty:
                continue
            t0 = time.monotonic()
            if ncnn_mode:
                parsed = model.predict(frame, conf=args.conf, iou=args.iou)
                names = model.names
            else:
                result = model.predict(frame, imgsz=args.imgsz, device=args.device,
                                       conf=args.conf, iou=args.iou, verbose=False)[0]
                parsed = [(box[:4], int(box[5]), float(box[4]))
                          for box in result.boxes.data.cpu().tolist()]
                names = result.names
            infer_id += 1
            payload = (parsed, names, infer_id, time.monotonic()-t0, "")
            try:
                results.put(payload, timeout=0.2)
            except queue.Full:
                pass
    except Exception as exc:
        print(f"Inference error: {type(exc).__name__}: {exc}", flush=True)
        try:
            results.put(([], {}, 0, 0, "Error al cargar/ejecutar modelo local"), timeout=1)
        except queue.Full:
            pass


def capture_worker(args, state, lock):
    """Continuously drain RTSP; display and inference only take the latest frame."""
    while not state.stop:
        cap = cv2.VideoCapture(args.source, cv2.CAP_FFMPEG, [
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,
            cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000,
        ])
        while not state.stop and cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            with lock:
                state.frame = frame
                state.frame_at = time.monotonic()
                state.captured += 1
        cap.release()
        if not state.stop:
            time.sleep(1)


def draw_overlay(frame, boxes, names, infer_count, infer_seconds, error, args, line_ratio, total_count=0):
    h, w = frame.shape[:2]
    for box, class_id, score in boxes:
        x1, y1, x2, y2 = [int(v) for v in box]
        label = f"{names.get(class_id, class_id)} {score:.2f}"
        color = (35, 220, 70)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        y = max(th + baseline + 4, y1)
        cv2.rectangle(frame, (x1, y - th - baseline - 4), (min(w - 1, x1 + tw + 6), y + 4), color, -1)
        cv2.putText(frame, label, (x1 + 3, y - baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    line_y = int(round(h * line_ratio))
    cv2.line(frame, (0, line_y), (w, line_y), (0, 0, 255), 3)
    cv2.circle(frame, (w - 24, line_y), 10, (0, 0, 255), -1)

    panel = f"agaves={total_count} boxes={len(boxes)} infer={infer_seconds:.2f}s line={line_ratio:.2f}"
    if error:
        panel = "ERROR " + error[:120]
    cv2.rectangle(frame, (8, 8), (min(w - 8, 760), 42), (0, 0, 0), -1)
    cv2.putText(frame, panel, (18, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    bx1, by1, bx2, by2 = w - 58, 10, w - 10, 58
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (25, 25, 25), -1)
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 0, 255), 2)
    cv2.line(frame, (bx1 + 12, by1 + 12), (bx2 - 12, by2 - 12), (0, 0, 255), 4)
    cv2.line(frame, (bx2 - 12, by1 + 12), (bx1 + 12, by2 - 12), (0, 0, 255), 4)
    return frame


def fit_to_screen(frame, screen_w, screen_h):
    h, w = frame.shape[:2]
    scale = min(screen_w / w, screen_h / h)
    out_w = max(1, int(round(w * scale)))
    out_h = max(1, int(round(h * scale)))
    resized = cv2.resize(frame, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
    if out_w == screen_w and out_h == screen_h:
        return resized, {"left": 0, "top": 0, "width": out_w, "height": out_h}
    canvas = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
    left = (screen_w - out_w) // 2
    top = (screen_h - out_h) // 2
    canvas[top : top + out_h, left : left + out_w] = resized
    return canvas, {"left": left, "top": top, "width": out_w, "height": out_h}


def main():
    args = parse_args()
    cv2.setNumThreads(1)
    state = SharedState()
    signal.signal(signal.SIGTERM, lambda *_: setattr(state, "stop", True))
    lock = threading.Lock()
    capture = threading.Thread(target=capture_worker, args=(args, state, lock), daemon=True)
    capture.start()
    context = mp.get_context("spawn")
    frames = context.Queue(maxsize=1)
    results = context.Queue(maxsize=2)
    inference_stop = context.Event()
    worker = context.Process(target=inference_worker, args=(args, frames, results, inference_stop), daemon=True)
    worker.start()
    submitted_at = 0.0
    events_file = args.events_file or str(default_events_file())
    counter = LineCounter(args.track_max_distance, args.track_ttl)
    last_infer_id = -1

    ui = {
        "line_ratio": read_line_ratio(args),
        "dragging": False,
        "display": {"left": 0, "top": 0, "width": args.screen_width, "height": args.screen_height},
        "close_button": None,
        "exit_requested": False,
    }

    def set_line_from_mouse(y):
        display = ui["display"]
        if display["height"] <= 0:
            return
        ui["line_ratio"] = clamp((y - display["top"]) / display["height"])
        write_line_ratio(args.line_state_file, ui["line_ratio"])
        # Calibration movement must not produce false crossing events.
        counter.tracks.clear()

    def close_button_hit(x, y):
        button = ui.get("close_button")
        if not button:
            return False
        x1, y1, x2, y2 = button
        return x1 <= x <= x2 and y1 <= y <= y2

    def on_mouse(event, x, y, flags, userdata):
        if event == cv2.EVENT_LBUTTONDOWN:
            if close_button_hit(x, y):
                ui["exit_requested"] = True
                return
            ui["dragging"] = True
            set_line_from_mouse(y)
        elif event == cv2.EVENT_MOUSEMOVE and ui["dragging"]:
            set_line_from_mouse(y)
        elif event == cv2.EVENT_LBUTTONUP:
            if ui["dragging"]:
                set_line_from_mouse(y)
            ui["dragging"] = False
        elif event == cv2.EVENT_RBUTTONDOWN:
            ui["line_ratio"] = 0.50
            write_line_ratio(args.line_state_file, ui["line_ratio"])
            counter.tracks.clear()
        elif event == cv2.EVENT_MOUSEWHEEL:
            step = -0.01 if flags > 0 else 0.01
            ui["line_ratio"] = clamp(ui["line_ratio"] + step)
            write_line_ratio(args.line_state_file, ui["line_ratio"])
            counter.tracks.clear()

    from agave_screen import AgaveScreen
    screen = AgaveScreen(args.window, args.screen_width, args.screen_height, args.fullscreen)

    last_read = time.time()
    stats_at = time.monotonic()
    displayed = 0
    last_captured = 0
    last_inferred = 0
    try:
        while not state.stop:
            try:
                while True:
                    boxes, names, infer_id, infer_seconds, error = results.get_nowait()
                    with lock:
                        state.boxes=boxes; state.names=names; state.infer_id=infer_id
                        state.infer_seconds=infer_seconds; state.error=error
                        state.model_ready=not bool(error)
            except queue.Empty:
                pass
            with lock:
                frame = None if state.frame is None else state.frame.copy()
                boxes = list(state.boxes)
                names = dict(state.names)
                infer_count = state.infer_count
                infer_id = state.infer_id
                infer_seconds = state.infer_seconds
                error = state.error
                frame_at = state.frame_at
                captured = state.captured
                model_ready = state.model_ready

            if frame is not None and frame_at != submitted_at:
                try:
                    frames.get_nowait()
                except queue.Empty:
                    pass
                try:
                    frames.put_nowait(frame)
                    submitted_at=frame_at
                except queue.Full:
                    pass
            if frame is None:
                frame = np.zeros((360, 640, 3), dtype=np.uint8)
                error = "Conectando camara local..."
            elif time.monotonic() - frame_at > 3:
                error = "Sin video reciente; reconectando..."
            elif not model_ready:
                error = "Cargando modelo local..."

            if infer_id != last_infer_id:
                for event in counter.update(boxes, names, ui["line_ratio"], frame.shape, infer_id, args):
                    append_jsonl(events_file, event)
                last_infer_id = infer_id

            shown = draw_overlay(
                frame,
                boxes,
                names,
                infer_count,
                infer_seconds,
                error,
                args,
                ui["line_ratio"],
                counter.count,
            )
            display = screen.show(shown)
            ui["display"] = display
            src_h, src_w = frame.shape[:2]
            scale_x = display["width"] / src_w if src_w else 1.0
            scale_y = display["height"] / src_h if src_h else 1.0
            ui["close_button"] = (
                int(display["left"] + (src_w - 58) * scale_x),
                int(display["top"] + 10 * scale_y),
                int(display["left"] + (src_w - 10) * scale_x),
                int(display["top"] + 58 * scale_y),
            )
            displayed += 1
            key = screen.poll(on_mouse)
            if ui.get("exit_requested"):
                break
            if key in (ord("q"), 27):
                break
            if key in (ord("w"), 82):
                ui["line_ratio"] = clamp(ui["line_ratio"] - 0.02)
                write_line_ratio(args.line_state_file, ui["line_ratio"])
            elif key in (ord("s"), 84):
                ui["line_ratio"] = clamp(ui["line_ratio"] + 0.02)
                write_line_ratio(args.line_state_file, ui["line_ratio"])
            elif key == ord("r"):
                ui["line_ratio"] = 0.50
                write_line_ratio(args.line_state_file, ui["line_ratio"])

            now = time.time()
            delay = max(0.0, (1.0 / 15.0) - (now - last_read))
            if delay:
                time.sleep(delay)
            last_read = time.time()
            elapsed = time.monotonic() - stats_at
            if elapsed >= 10:
                stats = {"timestamp": now_iso(), "event": "performance", "video_fps": round((captured-last_captured)/elapsed,2),
                         "display_fps": round(displayed/elapsed,2),
                         "detection_fps": round((infer_id-last_inferred)/elapsed,2),
                         "infer_seconds": round(infer_seconds,3),
                         "frame_age_seconds": round(time.monotonic()-frame_at,3) if frame_at else None}
                print(json.dumps(stats), flush=True)
                Path("rpi_live_tests/performance.json").write_text(json.dumps(stats))
                stats_at=time.monotonic(); displayed=0; last_captured=captured; last_inferred=infer_id
    finally:
        with lock:
            state.stop = True
        inference_stop.set()
        worker.join(timeout=2.0)
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=2.0)
        frames.cancel_join_thread()
        results.cancel_join_thread()
        frames.close(); results.close()
        screen.close()


if __name__ == "__main__":
    main()
