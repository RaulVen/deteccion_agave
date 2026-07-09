# LLM handoff: Raspberry Pi camera inference

This handoff captures the current research state so another LLM/session can continue without rediscovering the setup.

## Current objective

Run image/video inference for agave detection from a Dahua IP camera through a Raspberry Pi 4. The current focus is research reproducibility, not production hardening.

## Verified infrastructure

- Raspberry Pi 4 Model B Rev 1.5, 64-bit Debian 13, 8 GB class RAM.
- Dahua-like IP camera reachable on the LAN.
- RTSP substream works from the Pi.
- Ultralytics can run on the Pi when using Debian's `python3-torch`.
- Generic `yolo11n.pt` smoke tests work on frames and 10 second clips.

## Important paths on the Pi

```text
Repo: /home/bioiot/deteccion_agave
Working venv: /home/bioiot/deteccion_agave/.venv-rpi-apt
Avoid venv: /home/bioiot/deteccion_agave/.venv-rpi
Camera test frames: /home/bioiot/camera-test
Video smoke tests: /home/bioiot/deteccion_agave/rpi_video_tests
Ultralytics smoke outputs: /home/bioiot/deteccion_agave/runs/detect/rpi_video_tests
Optional HLS viewer: /home/bioiot/camera-view
```

## Secrets policy

Credentials were used during the live setup, but should not be committed. Use `.env` copied from `.env.example` and keep it untracked.

## Known good RTSP form

```text
rtsp://USER:PASSWORD@CAMERA_IP:554/cam/realmonitor?channel=1&subtype=1
```

Use the substream first: H.264, 640x360, 15 FPS.

## Current blocker

The repo does not include trained weights. The agave model expected by the README is:

```text
runs/detect/agave_experiments/yolo26s_sgd_cos_slow_120e/weights/best.pt
```

Put the real `best.pt` there before agave-specific inference.

## Working environment recipe

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3-torch python3-torchvision python3-opencv python3-pip python3-venv ffmpeg

cd ~/deteccion_agave
python3 -m venv --system-site-packages .venv-rpi-apt
source .venv-rpi-apt/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install --no-deps ultralytics ultralytics-thop
```

Do not use the project `Pipfile` on the Pi for inference; it is for CUDA laptop training.

## Last measured smoke test

Using the Dahua substream and `yolo11n.pt`:

```text
Clip length: 10.07 s
Resolution: 640x360
Frames: 151
Boxes: 51
Elapsed inference time: 74.87 s
Effective speed: 2.02 FPS
```

Conclusion: the flow is correct, but raw PyTorch CPU is slow. Try the real agave model first, then consider ONNX/NCNN/TFLite export.

## Recommended next commands

```bash
cd ~/deteccion_agave
source .venv-rpi-apt/bin/activate
set -a
. ./.env
set +a

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
