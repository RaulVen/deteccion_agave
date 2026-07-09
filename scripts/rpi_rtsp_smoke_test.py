import argparse
import shutil
import subprocess
import time
from pathlib import Path

from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Capture a short RTSP clip and run an Ultralytics smoke test."
    )
    parser.add_argument("--source", required=True, help="RTSP URL or video source.")
    parser.add_argument("--model", default="yolo11n.pt", help="YOLO model path/name.")
    parser.add_argument("--seconds", type=float, default=10.0, help="Clip duration.")
    parser.add_argument("--imgsz", type=int, default=320, help="Inference image size.")
    parser.add_argument("--device", default="cpu", help="Ultralytics device.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--iou", type=float, default=0.40, help="IoU threshold.")
    parser.add_argument(
        "--output-dir",
        default="rpi_video_tests",
        help="Directory for raw clip and annotated output.",
    )
    parser.add_argument("--name", default="rtsp_smoke", help="Ultralytics run name.")
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep audio in the raw clip. Default drops audio.",
    )
    return parser.parse_args()


def require_tool(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"Required command not found: {name}")


def run(cmd):
    subprocess.run(cmd, check=True)


def capture_clip(source, raw_clip, seconds, keep_audio):
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-rtsp_transport",
        "tcp",
        "-i",
        source,
        "-t",
        str(seconds),
    ]
    if not keep_audio:
        cmd.append("-an")
    cmd.extend(["-c:v", "copy", str(raw_clip)])
    run(cmd)


def probe_clip(raw_clip):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_name,width,height,avg_frame_rate",
        "-of",
        "default=nw=1",
        str(raw_clip),
    ]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def main():
    args = parse_args()
    require_tool("ffmpeg")
    require_tool("ffprobe")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_clip = output_dir / f"{args.name}_raw.mp4"

    print("capture=started", flush=True)
    capture_clip(args.source, raw_clip, args.seconds, args.keep_audio)
    print(f"raw_clip={raw_clip}", flush=True)
    print(f"raw_clip_bytes={raw_clip.stat().st_size}", flush=True)
    print("probe_start", flush=True)
    print(probe_clip(raw_clip), flush=True)

    model = YOLO(args.model)
    start = time.time()
    results = model.predict(
        str(raw_clip),
        imgsz=args.imgsz,
        device=args.device,
        conf=args.conf,
        iou=args.iou,
        save=True,
        project=str(output_dir),
        name=args.name,
        exist_ok=True,
        verbose=False,
    )
    elapsed = time.time() - start
    frame_count = len(results)
    box_count = sum(len(r.boxes) if r.boxes is not None else 0 for r in results)
    results_dir = results[0].save_dir if results else output_dir / args.name

    print(f"results_dir={results_dir}", flush=True)
    print(f"frames={frame_count}", flush=True)
    print(f"boxes={box_count}", flush=True)
    print(f"elapsed_s={elapsed:.2f}", flush=True)
    if elapsed:
        print(f"fps_inference={frame_count / elapsed:.2f}", flush=True)


if __name__ == "__main__":
    main()
