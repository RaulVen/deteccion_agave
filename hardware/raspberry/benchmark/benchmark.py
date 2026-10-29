"""CPU inference benchmark: real images, no camera or display. Run on the Pi."""
import argparse
import hashlib
import json
import os
import resource
import statistics
import subprocess
import threading
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--threads', type=int, default=4)
parser.add_argument('--count', type=int, default=30)
parser.add_argument('--output', default='results.json')
args = parser.parse_args()
os.environ['OMP_NUM_THREADS'] = str(args.threads)
os.environ['OPENBLAS_NUM_THREADS'] = str(args.threads)
os.environ['MPLBACKEND'] = 'Agg'
os.environ['YOLO_AUTOINSTALL'] = 'false'
import psutil

started = time.perf_counter()
process = psutil.Process()
samples = []
stop = threading.Event()
def monitor():
    while not stop.is_set():
        mem = psutil.virtual_memory()
        samples.append({'elapsed': time.perf_counter() - started,
                        'rss_mib': process.memory_info().rss / 2**20,
                        'available_mib': mem.available / 2**20,
                        'swap_used_mib': psutil.swap_memory().used / 2**20,
                        'temp_c': int(Path('/sys/class/thermal/thermal_zone0/temp').read_text()) / 1000})
        stop.wait(.2)
thread = threading.Thread(target=monitor, daemon=True)
thread.start()
import cv2
import torch
import ultralytics
from ultralytics import YOLO
torch.set_num_threads(args.threads)
torch.set_num_interop_threads(1)
cv2.setNumThreads(1)
root = Path(__file__).resolve().parent
weights = root / 'best.pt'
sha = hashlib.sha256(weights.read_bytes()).hexdigest().upper()
assert sha == 'A847C3E25D4AF7B6AC8B78033F5A268034D67B621DFBCB61456BA33E454F2C0A'
load_start = time.perf_counter()
model = YOLO(str(weights))
load_seconds = time.perf_counter() - load_start
images = sorted((root / 'images').glob('*.jpg'))
assert images
print(json.dumps({'stage': 'loaded', 'load_seconds': load_seconds, 'images': len(images),
                  'threads': args.threads, 'names': model.names}), flush=True)
records = []
for index in range(args.count + 3):
    image = cv2.imread(str(images[index % len(images)]))
    assert image is not None
    # Match the documented 640-pixel-wide camera substream without cropping.
    image = cv2.resize(image, (640, round(image.shape[0] * 640 / image.shape[1])))
    t = time.perf_counter()
    result = model.predict(image, imgsz=320, device='cpu', conf=.20, iou=.40,
                           verbose=False, save=False)[0]
    elapsed = time.perf_counter() - t
    record = {'index': index, 'warmup': index < 3, 'seconds': elapsed,
              'boxes': len(result.boxes), 'speed_ms': result.speed, 'input_shape': list(image.shape)}
    records.append(record)
    print(json.dumps(record), flush=True)
stop.set(); thread.join()
times = [r['seconds'] for r in records if not r['warmup']]
output = {'model_sha256': sha, 'versions': {'torch': torch.__version__, 'ultralytics': ultralytics.__version__,
          'opencv': cv2.__version__}, 'threads': args.threads, 'imgsz': 320, 'load_seconds': load_seconds,
          'total_process_seconds': time.perf_counter() - started,
          'actual_torch_threads': torch.get_num_threads(),
          'input_shapes': [r['input_shape'] for r in records[:len(images)]],
          'mean_seconds': statistics.mean(times), 'median_seconds': statistics.median(times),
          'min_seconds': min(times), 'max_seconds': max(times), 'fps': len(times) / sum(times),
          'peak_rss_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
          'min_available_mib': min(s['available_mib'] for s in samples),
          'max_swap_used_mib': max(s['swap_used_mib'] for s in samples),
          'max_temp_c': max(s['temp_c'] for s in samples),
          'throttled_after': subprocess.check_output(['vcgencmd', 'get_throttled'], text=True).strip(),
          'records': records, 'samples': samples}
(root / args.output).write_text(json.dumps(output, indent=2))
print(json.dumps({k:v for k,v in output.items() if k not in ['records','samples']}, indent=2), flush=True)
