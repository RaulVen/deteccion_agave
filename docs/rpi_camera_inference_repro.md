# Raspberry Pi camera inference reproducibility notes

These notes document the July 2026 research setup used to validate the end-to-end path:

```text
Dahua IP camera -> RTSP -> Raspberry Pi 4 -> Ultralytics inference -> annotated video
```

The goal is reproducibility across a few research machines. This is not a production deployment guide.

## Lab hardware observed

Raspberry Pi:

```text
Model: Raspberry Pi 4 Model B Rev 1.5
OS: Debian GNU/Linux 13 (trixie)
Architecture: aarch64 / 64-bit
CPU: Cortex-A72, 4 cores
RAM: 7.6 GiB
Python: 3.13.5
```

Camera:

```text
Vendor/family: Dahua-like IP camera
Observed IP: 192.168.1.248
Observed MAC: c4:aa:c4:ff:31:79
Open ports: 80, 554, 37777
```

Do not commit real camera passwords. Copy `.env.example` to `.env` on each machine and fill local values there.

## Camera streams

The camera accepted the Dahua RTSP path:

```text
rtsp://USER:PASSWORD@CAMERA_IP:554/cam/realmonitor?channel=1&subtype=0
rtsp://USER:PASSWORD@CAMERA_IP:554/cam/realmonitor?channel=1&subtype=1
```

Observed stream metadata:

```text
subtype=0: HEVC, 2880x1620, 15 FPS
subtype=1: H.264, 640x360, 15 FPS
```

Use `subtype=1` first on Raspberry Pi. It is the practical research baseline for CPU inference.

Validate the stream:

```bash
ffprobe -v error -rtsp_transport tcp \
  -show_entries stream=codec_type,codec_name,width,height,avg_frame_rate \
  -of default=nw=1 \
  "$AGAVE_CAMERA_RTSP"
```

Capture one frame:

```bash
mkdir -p ~/camera-test
ffmpeg -y -hide_banner -loglevel error -rtsp_transport tcp \
  -i "$AGAVE_CAMERA_RTSP" \
  -frames:v 1 -q:v 2 \
  ~/camera-test/dahua_subtype1_frame.jpg
```

## Raspberry Pi Python environment

The repo `Pipfile` targets the CUDA laptop training environment. On Raspberry Pi, avoid installing the CUDA PyTorch wheels from the `Pipfile`.

The working research environment used Debian's ARM packages for PyTorch/OpenCV, then installed Ultralytics without pulling a replacement PyTorch wheel:

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3-torch \
  python3-torchvision \
  python3-opencv \
  python3-pip \
  python3-venv \
  ffmpeg

cd ~/deteccion_agave
python3 -m venv --system-site-packages .venv-rpi-apt
source .venv-rpi-apt/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install --no-deps ultralytics ultralytics-thop
```

Expected imports:

```bash
python - <<'PY'
import torch, torchvision, cv2, ultralytics
print("torch", torch.__version__, "cuda", torch.cuda.is_available())
print("torchvision", torchvision.__version__)
print("cv2", cv2.__version__)
print("ultralytics", ultralytics.__version__)
PY
```

Observed working versions:

```text
torch 2.6.0+debian
torchvision 0.21.0
opencv 4.10.0
ultralytics 8.4.90
CUDA false
```

An earlier pip-only environment installed a PyTorch wheel that crashed on this Pi with `Illegal instruction`. If that happens, remove that environment and use the Debian-package path above.

## Model weights

The trained weights are intentionally not versioned. The README currently documents the best expected model path:

```text
runs/detect/agave_experiments/yolo26s_sgd_cos_slow_120e/weights/best.pt
```

Place the local `best.pt` there before running agave-specific inference. Until that file exists, use `yolo11n.pt` only as a pipeline smoke test; it is a generic COCO model and does not validate agave quality.

## Ten-second smoke test

After creating `.env`, run:

```bash
cd ~/deteccion_agave
source .venv-rpi-apt/bin/activate
set -a
. ./.env
set +a

python scripts/rpi_rtsp_smoke_test.py \
  --source "$AGAVE_CAMERA_RTSP" \
  --model yolo11n.pt \
  --seconds 10 \
  --imgsz 320 \
  --device cpu \
  --output-dir rpi_video_tests \
  --name dahua_10s_yolo11n
```

For the agave model, use:

```bash
python scripts/rpi_rtsp_smoke_test.py \
  --source "$AGAVE_CAMERA_RTSP" \
  --model "$AGAVE_MODEL_PATH" \
  --seconds 10 \
  --imgsz 320 \
  --device cpu \
  --conf 0.30 \
  --output-dir rpi_video_tests \
  --name agave_10s_best
```

## Observed smoke-test result

With `yolo11n.pt`, `imgsz=320`, CPU inference, and the 640x360 substream:

```text
Captured duration: 10.07 s
Frames processed: 151
Boxes: 51
Inference elapsed: 74.87 s
Effective inference speed: 2.02 FPS
```

This confirms the flow works, but PyTorch CPU is not real time on Raspberry Pi 4. For longer runs, always prefer streaming/generator style processing or process short clips.

## Optional local web viewer

For operator viewing on a laptop, the Pi can republish the camera as HLS:

```bash
mkdir -p ~/camera-view
cd ~/camera-view

ffmpeg -hide_banner -loglevel warning -rtsp_transport tcp \
  -i "$AGAVE_CAMERA_RTSP" \
  -an -c:v copy \
  -f hls -hls_time 1 -hls_list_size 5 \
  -hls_flags delete_segments+omit_endlist \
  stream.m3u8
```

In another shell:

```bash
cd ~/camera-view
python3 -m http.server 8090 --bind 0.0.0.0
```

Then open from a laptop on the same LAN:

```text
http://RPI_IP:8090/stream.m3u8
```

VLC handles this URL directly. A simple `index.html` wrapper can be added locally for browser HLS playback.

## Research next steps

- Copy the trained `best.pt` to the documented weights path.
- Benchmark `imgsz=320`, `416`, and `640` against the substream.
- Compare raw PyTorch CPU against ONNX, NCNN, or TFLite exports.
- If running continuously, use `stream=True` or a custom loop to avoid accumulating `Results` in RAM.
- Keep generated videos, weights, datasets, and `.env` out of git.
