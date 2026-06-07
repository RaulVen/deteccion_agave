import argparse
import csv
from collections import defaultdict, deque
from pathlib import Path

import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Track objects with YOLO and count line crossings."
    )
    parser.add_argument("--model", required=True, help="Path to YOLO weights.")
    parser.add_argument("--source", required=True, help="Input video path.")
    parser.add_argument("--output", required=True, help="Output annotated video path.")
    parser.add_argument("--csv", default=None, help="Optional crossings CSV output.")
    parser.add_argument("--tracker", default="botsort.yaml", help="Tracker YAML path/name.")
    parser.add_argument("--line-ratio", type=float, default=0.25, help="Horizontal line Y ratio.")
    parser.add_argument(
        "--direction",
        choices=("down", "up", "both"),
        default="both",
        help="Count objects crossing down, up, or both directions.",
    )
    parser.add_argument("--conf", type=float, default=0.30, help="Detection confidence.")
    parser.add_argument("--iou", type=float, default=0.40, help="NMS IoU threshold.")
    parser.add_argument("--imgsz", type=int, default=640, help="YOLO image size.")
    parser.add_argument("--device", default="0", help="Inference device.")
    parser.add_argument(
        "--trail-length", type=int, default=24, help="Center trail length per track."
    )
    parser.add_argument(
        "--duplicate-window",
        type=int,
        default=90,
        help="Frames to suppress nearby repeated crossings from changed IDs.",
    )
    parser.add_argument(
        "--duplicate-x-ratio",
        type=float,
        default=0.05,
        help="Same-crossing X tolerance as frame-width ratio.",
    )
    parser.add_argument(
        "--show-conf",
        action="store_true",
        help="Draw confidence next to track IDs.",
    )
    parser.add_argument(
        "--unique-id-only",
        action="store_true",
        help="Count each track ID once per direction, without nearby duplicate suppression.",
    )
    return parser.parse_args()


def crossed(prev_y, y, line_y, direction):
    if direction in ("down", "both") and prev_y < line_y <= y:
        return "down"
    if direction in ("up", "both") and prev_y > line_y >= y:
        return "up"
    return None


def is_recent_duplicate(recent_crossings, frame_idx, x, direction, x_tol, window):
    for item in recent_crossings:
        if frame_idx - item["frame"] > window:
            continue
        if item["direction"] != direction:
            continue
        if abs(x - item["x"]) <= x_tol:
            return True
    return False


def draw_label(frame, text, x, y, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.7
    thickness = 2
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    x = max(0, min(x, frame.shape[1] - tw - 4))
    y = max(th + baseline + 4, y)
    cv2.rectangle(frame, (x, y - th - baseline - 4), (x + tw + 4, y + 4), color, -1)
    cv2.putText(frame, text, (x + 2, y - baseline), font, scale, (255, 255, 255), thickness)


def main():
    args = parse_args()
    source = Path(args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    csv_path = Path(args.csv) if args.csv else output.with_suffix(".csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir el video: {source}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    line_y = int(round(height * args.line_ratio))
    duplicate_x_tol = width * args.duplicate_x_ratio

    writer = cv2.VideoWriter(
        str(output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"No se pudo crear el video de salida: {output}")

    model = YOLO(args.model)
    trails = defaultdict(lambda: deque(maxlen=args.trail_length))
    last_centers = {}
    counted_track_keys = set()
    recent_crossings = deque(maxlen=500)
    counts = {"down": 0, "up": 0}
    csv_rows = []

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1

        results = model.track(
            frame,
            persist=True,
            tracker=args.tracker,
            conf=args.conf,
            iou=args.iou,
            imgsz=args.imgsz,
            device=args.device,
            verbose=False,
        )
        result = results[0]
        boxes = result.boxes

        cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 255), 4)
        cv2.putText(
            frame,
            f"Linea {args.line_ratio:.2f} ({args.direction})",
            (24, max(36, line_y - 14)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            3,
        )

        if boxes is not None and boxes.id is not None:
            xyxy = boxes.xyxy.cpu().numpy()
            ids = boxes.id.cpu().numpy().astype(int)
            confs = boxes.conf.cpu().numpy() if boxes.conf is not None else [0] * len(ids)

            for box, track_id, conf in zip(xyxy, ids, confs):
                x1, y1, x2, y2 = box
                cx = float((x1 + x2) / 2)
                cy = float((y1 + y2) / 2)
                track_key = (int(track_id), args.direction)

                prev = last_centers.get(track_id)
                last_centers[track_id] = (cx, cy)
                trails[track_id].append((int(cx), int(cy)))

                color = (45, 180, 45)
                crossing_direction = None
                duplicate = False
                if prev is not None:
                    crossing_direction = crossed(prev[1], cy, line_y, args.direction)
                    if crossing_direction and (track_id, crossing_direction) not in counted_track_keys:
                        duplicate = False
                        if not args.unique_id_only:
                            duplicate = is_recent_duplicate(
                                recent_crossings,
                                frame_idx,
                                cx,
                                crossing_direction,
                                duplicate_x_tol,
                                args.duplicate_window,
                            )
                        counted_track_keys.add((track_id, crossing_direction))
                        if not duplicate:
                            counts[crossing_direction] += 1
                            recent_crossings.append(
                                {
                                    "frame": frame_idx,
                                    "x": cx,
                                    "direction": crossing_direction,
                                    "track_id": track_id,
                                }
                            )
                            csv_rows.append(
                                {
                                    "frame": frame_idx,
                                    "time_s": frame_idx / fps,
                                    "track_id": track_id,
                                    "direction": crossing_direction,
                                    "x": round(cx, 2),
                                    "y": round(cy, 2),
                                    "duplicate_suppressed": False,
                                }
                            )
                            color = (0, 0, 255)
                        else:
                            csv_rows.append(
                                {
                                    "frame": frame_idx,
                                    "time_s": frame_idx / fps,
                                    "track_id": track_id,
                                    "direction": crossing_direction,
                                    "x": round(cx, 2),
                                    "y": round(cy, 2),
                                    "duplicate_suppressed": True,
                                }
                            )
                            color = (0, 165, 255)

                cv2.rectangle(
                    frame,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    color,
                    3,
                )
                label = f"ID {track_id}"
                if args.show_conf:
                    label += f" {conf:.2f}"
                draw_label(frame, label, int(x1), int(y1) - 8, color)

                pts = list(trails[track_id])
                for p1, p2 in zip(pts, pts[1:]):
                    cv2.line(frame, p1, p2, (255, 200, 0), 2)
                cv2.circle(frame, (int(cx), int(cy)), 5, color, -1)

        panel = f"DOWN: {counts['down']}  UP: {counts['up']}  TOTAL: {counts['down'] + counts['up']}"
        cv2.rectangle(frame, (16, 16), (760, 72), (0, 0, 0), -1)
        cv2.putText(
            frame,
            panel,
            (28, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (255, 255, 255),
            3,
        )

        writer.write(frame)
        if total_frames and frame_idx % 50 == 0:
            print(f"Procesados {frame_idx}/{total_frames} frames", flush=True)

    cap.release()
    writer.release()

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "frame",
            "time_s",
            "track_id",
            "direction",
            "x",
            "y",
            "duplicate_suppressed",
        ]
        writer_csv = csv.DictWriter(f, fieldnames=fieldnames)
        writer_csv.writeheader()
        writer_csv.writerows(csv_rows)

    print(f"video={output}")
    print(f"csv={csv_path}")
    print(f"down={counts['down']}")
    print(f"up={counts['up']}")
    print(f"total={counts['down'] + counts['up']}")
    print(
        "duplicates_suppressed="
        + str(sum(1 for row in csv_rows if row["duplicate_suppressed"]))
    )


if __name__ == "__main__":
    main()
