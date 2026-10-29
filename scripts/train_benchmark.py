"""Prepare, train and evaluate the October dataset without replacing historical runs.

No action trains implicitly: --list and --check are read-only; --run/--all/--remaining train.
--baseline reevaluates historical checkpoints on the new splits without training.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.metadata
import json
import logging
import os
from pathlib import Path
import sys
import tomllib
from datetime import datetime, timezone

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs/training/agave_maleza_2026-10-21"
DATA = ROOT / "datasets/prepared/agave_maleza_2026-10-21/data.yaml"
RUNS = ROOT / "runs/detect/agave_maleza_2026-10-21"
BENCHMARK = ROOT / "benchmark/agave_maleza_2026-10-21"
HISTORICAL_CSV = ROOT / "benchmark/agave_benchmark.csv"
FIELDS = ["rank", "run", "model", "epochs_run", "best_epoch", "test_precision",
          "test_recall", "test_mAP50", "test_mAP50_95", "val_precision",
          "val_recall", "val_mAP50", "val_mAP50_95", "weights"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
EVALUATION = {"imgsz": 640, "batch": 8, "device": "0", "workers": 4,
              "conf": 0.001, "iou": 0.7, "max_det": 300, "half": False,
              "augment": False, "rect": True, "plots": True, "save_json": False,
              "save_txt": False, "verbose": True, "seed": 26, "deterministic": True}


def read_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return value


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def inside(path: Path, parent: Path) -> Path:
    path = path.resolve()
    path.relative_to(parent.resolve())
    return path


def configs() -> dict[str, dict]:
    values = {}
    for path in sorted(CONFIGS.glob("*.yaml"), key=lambda p: (p.stem != "agave_quick_test", p.name)):
        cfg = read_yaml(path)
        if cfg.get("name") != path.stem:
            raise ValueError(f"Config name must match filename: {path}")
        cfg["model"] = str(repo_path(cfg["model"]))
        cfg["data"] = str(repo_path(cfg["data"]))
        cfg["project"] = str(repo_path(cfg["project"]))
        if Path(cfg["data"]) != DATA.resolve() or Path(cfg["project"]) != RUNS.resolve():
            raise ValueError(f"Unexpected dataset or output project: {path}")
        if cfg.get("exist_ok") is not False or cfg.get("resume") is not False or "save_dir" in cfg:
            raise ValueError(f"Config must forbid overwrite/resume and omit save_dir: {path}")
        inside(Path(cfg["model"]), ROOT / "models/pretrained")
        inside(RUNS / path.stem, RUNS)
        values[path.stem] = cfg
    if len(values) != 11:
        raise ValueError(f"Expected 11 experiment configs, found {len(values)} in {CONFIGS}")
    return values


def dataset_check() -> dict:
    cfg = read_yaml(DATA)
    base = Path(cfg.get("path", DATA.parent))
    if not base.is_absolute():
        raise ValueError("Dataset YAML 'path' must be absolute to avoid Ultralytics datasets_dir ambiguity")
    names = cfg.get("names")
    if isinstance(names, dict):
        if sorted(names) != list(range(len(names))):
            raise ValueError("Class IDs must be consecutive integers starting at 0")
        names = [names[i] for i in range(len(names))]
    if not isinstance(names, list) or not names or len(set(names)) != len(names):
        raise ValueError("Dataset must define distinct class names")
    if cfg.get("nc", len(names)) != len(names):
        raise ValueError("nc and names disagree")
    summary = {"yaml": str(DATA), "yaml_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
               "classes": names, "splits": {}}
    seen_paths: set[Path] = set()
    for split in ("train", "val", "test"):
        if not isinstance(cfg.get(split), str):
            raise ValueError(f"Expected a directory for dataset split {split}")
        directory = (base / cfg[split]).resolve()
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing {split} image directory: {directory}")
        images = sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
        if not images:
            raise ValueError(f"Empty {split}: {directory}")
        boxes = negatives = 0
        for image in images:
            if image.resolve() in seen_paths:
                raise ValueError(f"Same image path occurs in more than one split: {image}")
            seen_paths.add(image.resolve())
            parts = list(image.parts)
            positions = [i for i, part in enumerate(parts) if part == "images"]
            if not positions:
                raise ValueError(f"Image path needs an images directory for YOLO labels: {image}")
            parts[positions[-1]] = "labels"
            label = Path(*parts).with_suffix(".txt")
            if not label.is_file():
                raise FileNotFoundError(f"Missing label (use empty txt for a verified negative): {label}")
            lines = [line for line in label.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
            negatives += not lines
            for line in lines:
                fields = line.split()
                if len(fields) != 5:
                    raise ValueError(f"Expected detection class/x/y/w/h: {label}")
                cls, x, y, w, h = map(float, fields)
                if not (cls.is_integer() and 0 <= cls < len(names) and 0 <= x <= 1 and 0 <= y <= 1
                        and 0 < w <= 1 and 0 < h <= 1):
                    raise ValueError(f"Invalid normalized detection label: {label}: {line}")
                boxes += 1
        summary["splits"][split] = {"images": len(images), "boxes": boxes, "negatives": negatives}
    return summary


def environment_check() -> dict:
    lock = json.loads((ROOT / "Pipfile.lock").read_text(encoding="utf-8"))["default"]
    versions = {}
    for package in ("ultralytics", "torch", "torchvision", "numpy", "opencv-python", "matplotlib"):
        expected = lock[package]["version"].removeprefix("==")
        installed = importlib.metadata.version(package)
        if installed != expected:
            raise RuntimeError(f"{package}: installed {installed}; locked {expected}. Use the repository .venv.")
        versions[package] = installed
    python_expected = tomllib.loads((ROOT / "Pipfile").read_text(encoding="utf-8"))["requires"]["python_full_version"]
    if sys.version.split()[0] != python_expected:
        raise RuntimeError(f"Expected Python {python_expected}, got {sys.version.split()[0]}")
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU unavailable; historical protocol requires device=0")
    # Matching package metadata alone does not prove that native DLLs can load.
    # This includes the actual YOLO import used by training and validation.
    phase = "Ultralytics YOLO"
    try:
        from ultralytics import YOLO
        phase = "NumPy"
        import numpy
        phase = "OpenCV (cv2)"
        import cv2
        phase = "Matplotlib and its native ft2font extension"
        import matplotlib
        from matplotlib import ft2font
    except (ImportError, OSError) as exc:
        raise RuntimeError(f"Environment preflight failed importing {phase}: {exc}") from exc
    versions.update(python=sys.version.split()[0], executable=sys.executable,
                    gpu=torch.cuda.get_device_name(0), cuda=torch.version.cuda,
                    native_imports="numpy, cv2, matplotlib.ft2font and ultralytics.YOLO imported successfully")
    return versions


def historical_rows() -> dict[str, dict]:
    with HISTORICAL_CSV.open(encoding="utf-8-sig", newline="") as stream:
        return {row["run"]: row for row in csv.DictReader(stream)}


def remaining_configs(available: dict[str, dict]) -> dict[str, dict]:
    path = BENCHMARK / "agave_benchmark.csv"
    rows = {}
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = {row["run"]: row for row in csv.DictReader(stream)}
    data_hash = hashlib.sha256(DATA.read_bytes()).hexdigest()
    remaining = {}
    for name, cfg in available.items():
        output = RUNS / name
        meta_path = BENCHMARK / "metadata" / f"{name}.json"
        if not output.exists() and not meta_path.exists() and name not in rows:
            remaining[name] = cfg
            continue
        complete = output.is_dir() and meta_path.is_file() and name in rows
        complete = complete and (output / "weights/best.pt").is_file()
        complete = complete and all((output / "evaluation" / split).is_dir() for split in ("val", "test"))
        if complete:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            complete = (meta.get("completed_utc") and meta.get("run") == name
                        and meta.get("config_sha256") == hashlib.sha256((CONFIGS / f"{name}.yaml").read_bytes()).hexdigest()
                        and meta.get("dataset", {}).get("yaml_sha256") == data_hash
                        and Path(rows[name]["weights"]).resolve() == (output / "weights/best.pt").resolve())
        if not complete:
            raise RuntimeError(f"Incomplete or inconsistent existing run {name}. Preserved for review: {output}")
        print(f"Skipping completed run: {name}")
    return remaining


def preflight(selected: dict[str, dict], baseline: bool = False) -> dict:
    data = dataset_check()
    historical = historical_rows() if baseline else {}
    for name, cfg in selected.items():
        weights = Path(historical[name]["weights"]) if baseline else Path(cfg["model"])
        if not weights.is_file():
            raise FileNotFoundError(f"Missing weights: {weights}")
        outputs = ([RUNS / "baseline" / name / split for split in ("val", "test")]
                   if baseline else [RUNS / name])
        for output in outputs:
            inside(output, RUNS)
            if output.exists():
                raise FileExistsError(f"Refusing to reuse an existing output: {output}")
    env = environment_check()
    result = {"dataset": data, "environment": env, "runs": list(selected),
              "evaluation": EVALUATION, "baseline": baseline}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("Checks passed. No training or evaluation was performed by this check.")
    return result


class Tee:
    def __init__(self, first, second):
        self.first, self.second = first, second

    def write(self, value):
        self.first.write(value)
        self.second.write(value)
        self.second.flush()
        return len(value)

    def flush(self):
        self.first.flush()
        self.second.flush()

    def isatty(self):
        return False


@contextlib.contextmanager
def run_log(name: str):
    from ultralytics.utils import LOGGER
    directory = BENCHMARK / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    path = directory / f"{name}_{stamp}.log"
    handler = logging.FileHandler(path, encoding="utf-8")
    LOGGER.addHandler(handler)
    try:
        with path.open("a", encoding="utf-8") as stream:
            with contextlib.redirect_stdout(Tee(sys.stdout, stream)), contextlib.redirect_stderr(Tee(sys.stderr, stream)):
                yield
    finally:
        LOGGER.removeHandler(handler)
        handler.close()


def evaluate(weights: Path, project: Path) -> dict:
    from ultralytics import YOLO
    for split in ("val", "test"):
        if (project / split).exists():
            raise FileExistsError(f"Refusing to reuse evaluation output: {project / split}")
    metrics = {}
    for split in ("val", "test"):
        args = {**EVALUATION, "data": str(DATA), "split": split,
                "project": str(project), "name": split, "exist_ok": False}
        print("Evaluation arguments:", json.dumps(args, indent=2))
        model = YOLO(str(weights))
        expected_names = read_yaml(DATA)["names"]
        if isinstance(expected_names, list):
            expected_names = dict(enumerate(expected_names))
        if model.names != expected_names:
            raise ValueError(f"Checkpoint classes {model.names} differ from dataset classes {expected_names}")
        def guard_output(validator):
            if Path(validator.save_dir).resolve() != (project / split).resolve():
                raise RuntimeError(f"Unexpected evaluation output: {validator.save_dir}")
        model.add_callback("on_val_start", guard_output)
        result = model.val(**args)
        metrics.update({f"{split}_precision": float(result.box.mp),
                        f"{split}_recall": float(result.box.mr),
                        f"{split}_mAP50": float(result.box.map50),
                        f"{split}_mAP50_95": float(result.box.map)})
    return metrics


def save_benchmark(row: dict, baseline: bool) -> None:
    BENCHMARK.mkdir(parents=True, exist_ok=True)
    path = BENCHMARK / ("historical_models_on_new_dataset.csv" if baseline else "agave_benchmark.csv")
    rows = []
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    if any(old["run"] == row["run"] for old in rows):
        raise RuntimeError(f"Benchmark already contains {row['run']}: {path}")
    rows.append(row)
    rows.sort(key=lambda item: (-float(item["test_mAP50_95"]), -float(item["test_mAP50"]), item["run"]))
    temp = path.with_suffix(".csv.tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for index, item in enumerate(rows, 1):
            item["rank"] = index
            writer.writerow(item)
    os.replace(temp, path)


def execute(name: str, cfg: dict, checked: dict, baseline: bool) -> None:
    from ultralytics import YOLO
    output = RUNS / ("baseline" if baseline else "") / name
    if output.exists():
        raise FileExistsError(f"Refusing to reuse output: {output}")
    tag = f"baseline_{name}" if baseline else name
    with run_log(tag):
        print(f"Action: {'historical model evaluation' if baseline else 'training + validation + test'}; run={name}")
        print("Resolved training config:", json.dumps(cfg, indent=2))
        metadata = {**checked, "run": name, "training_config": cfg,
                    "started_utc": datetime.now(timezone.utc).isoformat(),
                    "config_sha256": hashlib.sha256((CONFIGS / f"{name}.yaml").read_bytes()).hexdigest()}
        if baseline:
            old = historical_rows()[name]
            weights = Path(old["weights"])
            row = {k: old[k] for k in ("run", "model", "epochs_run", "best_epoch")}
            eval_project = output
        else:
            args = {key: value for key, value in cfg.items() if key != "model"}
            model = YOLO(cfg["model"])
            def guard_training_output(trainer):
                if Path(trainer.save_dir).resolve() != output.resolve():
                    raise RuntimeError(f"Unexpected training output before training: {trainer.save_dir}")
            model.add_callback("on_pretrain_routine_start", guard_training_output)
            model.train(**args)
            if Path(model.trainer.save_dir).resolve() != output.resolve():
                raise RuntimeError(f"Unexpected training output: {model.trainer.save_dir}")
            weights = output / "weights/best.pt"
            if not weights.is_file():
                raise FileNotFoundError(f"Training did not produce a best checkpoint: {weights}")
            with (output / "results.csv").open(encoding="utf-8-sig", newline="") as stream:
                results = [{k.strip(): v for k, v in item.items()} for item in csv.DictReader(stream)]
            best = max(results, key=lambda item: float(item["metrics/mAP50-95(B)"]))
            row = {"run": name, "model": Path(cfg["model"]).name,
                   "epochs_run": len(results), "best_epoch": int(float(best["epoch"]))}
            eval_project = output / "evaluation"
        row.update(evaluate(weights, eval_project))
        row["weights"] = str(weights.resolve())
        metadata.update(completed_utc=datetime.now(timezone.utc).isoformat(), metrics=row,
                        weights_sha256=hashlib.sha256(weights.read_bytes()).hexdigest())
        meta_dir = BENCHMARK / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        meta_path = meta_dir / f"{tag}.json"
        with meta_path.open("x", encoding="utf-8") as stream:
            json.dump(metadata, stream, indent=2, ensure_ascii=False)
        save_benchmark(row, baseline)
        print(json.dumps(row, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--list", action="store_true", help="List the 11 configurations; no GPU required")
    action.add_argument("--check", action="store_true", help="Read-only dataset/weights/environment/GPU preflight")
    action.add_argument("--run", metavar="NAME", help="Train one named experiment, then evaluate val/test")
    action.add_argument("--all", action="store_true", help="Explicitly train all 11 experiments sequentially")
    action.add_argument("--remaining", action="store_true", help="Train pending experiments; skip only verified complete runs")
    action.add_argument("--baseline", metavar="NAME_OR_ALL", help="Evaluate historical best.pt on new val/test; no training")
    args = parser.parse_args()
    available = configs()
    if args.list or not any((args.check, args.run, args.all, args.remaining, args.baseline)):
        for name, cfg in available.items():
            print(f"{name:38s} model={Path(cfg['model']).name:10s} epochs={cfg['epochs']:3} "
                  f"patience={cfg['patience']:3} batch={cfg['batch']} seed={cfg['seed']} optimizer={cfg['optimizer']}")
        return
    requested = args.run or (args.baseline if args.baseline != "all" else None)
    if requested and requested not in available:
        parser.error(f"Unknown run {requested!r}; use --list")
    selected = {requested: available[requested]} if requested else available
    if args.remaining:
        selected = remaining_configs(available)
        if not selected:
            print("All 11 experiments are complete. Nothing to train.")
            return
    checked = preflight(selected, baseline=bool(args.baseline))
    if args.check:
        return
    BENCHMARK.mkdir(parents=True, exist_ok=True)
    lock = BENCHMARK / ".runner.lock"
    # This serializes writers and also prevents simultaneous training on the GPU.
    with lock.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "started_utc": datetime.now(timezone.utc).isoformat()}, stream)
    try:
        for name, cfg in selected.items():
            execute(name, cfg, checked, baseline=bool(args.baseline))
    finally:
        lock.unlink()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ImportError, ValueError, RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
