"""Run the authorized two-model, exactly-150-epoch campaign sequentially.

--check performs preflight without training. Only --run starts training.
No automatic resume, overwrite, early stopping, or timed training is permitted.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import sys
import time
import traceback
import zipfile

import train_benchmark as common


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = "agave_maleza_150ep_2026-10-21"
CONFIG_DIR = ROOT / "configs/training" / CAMPAIGN
RUNS = ROOT / "runs/detect" / CAMPAIGN
REPORTS = ROOT / "benchmark" / CAMPAIGN
STATUS = REPORTS / "status.json"
ORDER = ("yolo26s_sgd_640_150e", "yolo26n_campo_640_150e")
EPOCHS = 150
LOCKS = (REPORTS / ".runner.lock", common.BENCHMARK / ".runner.lock")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    os.replace(temp, path)


def configurations() -> dict[str, dict]:
    values = {}
    required = {"epochs": EPOCHS, "patience": 0, "time": None, "flipud": 0.0,
                "save_period": 10, "save": True, "plots": True, "val": True,
                "batch": 8, "seed": 26, "imgsz": 640, "resume": False,
                "exist_ok": False}
    for name in ORDER:
        cfg = common.read_yaml(CONFIG_DIR / f"{name}.yaml")
        if cfg.get("name") != name or "save_dir" in cfg:
            raise ValueError(f"Unsafe name or inherited save_dir: {name}")
        for key, expected in required.items():
            if cfg.get(key) != expected:
                raise ValueError(f"{name}: {key} must be {expected!r}")
        for key in ("model", "data", "project"):
            cfg[key] = str(common.repo_path(cfg[key]))
        if Path(cfg["project"]) != RUNS.resolve() or Path(cfg["data"]) != common.DATA.resolve():
            raise ValueError(f"Unexpected campaign output or data: {name}")
        common.inside(Path(cfg["model"]), ROOT / "models/pretrained")
        expected_model = "yolo26s.pt" if name == ORDER[0] else "yolo26n.pt"
        if Path(cfg["model"]) != (ROOT / "models/pretrained" / expected_model).resolve():
            raise ValueError(f"Expected the approved pretrained base, not a historical best.pt: {name}")
        common.inside(RUNS / name, RUNS)
        values[name] = cfg
    return values


def check(configs: dict[str, dict]) -> dict:
    for name, cfg in configs.items():
        if not Path(cfg["model"]).is_file():
            raise FileNotFoundError(cfg["model"])
        if (RUNS / name).exists():
            raise FileExistsError(f"Existing run preserved; no resume/overwrite: {RUNS / name}")
    if STATUS.exists() or (REPORTS / "agave_benchmark.csv").exists():
        raise FileExistsError(f"Campaign already has execution records: {REPORTS}")
    for lock in LOCKS:
        if lock.exists():
            raise FileExistsError(f"Another runner or an unresolved previous run holds: {lock}")
    dataset = common.dataset_check()
    # A process-local profile keeps AMP's model lookup away from user-global settings.
    profile = REPORTS / "runtime_settings"
    profile.mkdir(parents=True, exist_ok=True)
    os.environ["YOLO_CONFIG_DIR"] = str(profile)
    environment = common.environment_check()
    from ultralytics.utils import SETTINGS
    SETTINGS.update({"weights_dir": str(ROOT / "models/pretrained"),
                     "runs_dir": str(ROOT / "runs"), "datasets_dir": str(ROOT / "datasets")})
    from ultralytics.utils.torch_utils import EarlyStopping
    stopper = EarlyStopping(patience=0)
    if not math.isinf(stopper.patience) or stopper(150, 1.0) or stopper(1000, 0.0):
        raise RuntimeError("Installed Ultralytics does not disable early stopping with patience=0")
    result = {"campaign": CAMPAIGN, "order": list(ORDER), "epochs_each": EPOCHS,
              "early_stopping": "disabled: patience=0 maps to infinity", "time_limit": None,
              "dataset": dataset, "environment": environment,
              "runtime_settings": str(profile), "amp_weights_dir": SETTINGS["weights_dir"],
              "evaluation_protocol": common.EVALUATION, "configs": configs}
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
    print("Preflight passed. No training or evaluation has been started by this check.", flush=True)
    return result


@contextlib.contextmanager
def exclusive_runner():
    acquired = []
    try:
        for path in LOCKS:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as stream:
                json.dump({"pid": os.getpid(), "campaign": CAMPAIGN, "started_utc": now()}, stream)
            acquired.append(path)
        yield
    finally:
        for path in reversed(acquired):
            path.unlink(missing_ok=True)


@contextlib.contextmanager
def prevent_automatic_sleep():
    if os.name != "nt":
        yield
        return
    import ctypes
    set_state = ctypes.windll.kernel32.SetThreadExecutionState
    set_state.argtypes = [ctypes.c_uint]
    set_state.restype = ctypes.c_uint
    previous = set_state(0x80000000 | 0x00000001)  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    if previous == 0:
        raise OSError("Windows could not temporarily prevent automatic sleep")
    try:
        yield
    finally:
        set_state(previous)


@contextlib.contextmanager
def capture_log(name: str):
    from ultralytics.utils import LOGGER
    path = REPORTS / "logs" / f"{name}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation is intentional; a partial log is preserved for diagnosis.
    with path.open("x", encoding="utf-8"):
        pass
    handler = logging.FileHandler(path, encoding="utf-8")
    LOGGER.addHandler(handler)
    try:
        with path.open("a", encoding="utf-8") as stream:
            with contextlib.redirect_stdout(common.Tee(sys.stdout, stream)), contextlib.redirect_stderr(common.Tee(sys.stderr, stream)):
                yield
    finally:
        LOGGER.removeHandler(handler)
        handler.close()


def validate_training(output: Path) -> dict:
    with (output / "results.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [{key.strip(): value for key, value in row.items()} for row in csv.DictReader(stream)]
    epochs = [float(row["epoch"]) for row in rows]
    if epochs != list(range(1, EPOCHS + 1)):
        raise RuntimeError(f"Training is incomplete: expected epochs 1..150; found {len(rows)} rows ending {epochs[-1:]}")
    for row in rows:
        for key, value in row.items():
            if not math.isfinite(float(value)):
                raise RuntimeError(f"Non-finite metric in results.csv: epoch={row['epoch']} {key}={value}")
    hashes = {}
    for name in ("best.pt", "last.pt"):
        path = output / "weights" / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing trained checkpoint: {path}")
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise RuntimeError(f"Corrupt checkpoint member: {path}: {bad}")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    args = common.read_yaml(output / "args.yaml")
    for key, expected in {"epochs": 150, "patience": 0, "time": None, "flipud": 0.0}.items():
        if args.get(key) != expected:
            raise RuntimeError(f"Saved training argument drift: {key}={args.get(key)!r}")
    best = max(rows, key=lambda row: float(row["metrics/mAP50-95(B)"]))
    return {"epochs_verified": EPOCHS, "best_epoch": int(float(best["epoch"])),
            "batch_in_saved_args": args.get("batch"),
            "checkpoint_sha256": hashes, "results_csv_sha256": hashlib.sha256((output / "results.csv").read_bytes()).hexdigest()}


def append_benchmark(row: dict) -> None:
    path = REPORTS / "agave_benchmark.csv"
    rows = []
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    if any(previous["run"] == row["run"] for previous in rows):
        raise RuntimeError(f"Duplicate benchmark result: {row['run']}")
    rows.append(row)
    rows.sort(key=lambda item: -float(item["test_mAP50_95"]))
    temp = path.with_suffix(".csv.tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=common.FIELDS)
        writer.writeheader()
        for index, item in enumerate(rows, 1):
            writer.writerow({**item, "rank": index})
    os.replace(temp, path)


def train_one(name: str, cfg: dict, state: dict) -> None:
    from ultralytics import YOLO
    output = RUNS / name
    if output.exists():
        raise FileExistsError(f"Refusing to reuse output: {output}")
    entry = state["runs"][name]
    entry.update(status="training", started_utc=now(), epochs_completed=0, output=str(output))
    state.update(current_run=name, updated_utc=now())
    atomic_json(STATUS, state)
    started = time.monotonic()
    history = REPORTS / "epochs" / f"{name}.jsonl"
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("x", encoding="utf-8"):
        pass
    atomic_json(REPORTS / "metadata" / f"{name}_planned.json", {"config": cfg, "started_utc": now(),
                "config_sha256": hashlib.sha256((CONFIG_DIR / f"{name}.yaml").read_bytes()).hexdigest()})
    with capture_log(name):
        print(f"START {name}: exactly 150 epochs; early stopping disabled", flush=True)
        print(json.dumps(cfg, indent=2), flush=True)
        model = YOLO(cfg["model"])

        def guard(trainer):
            if Path(trainer.save_dir).resolve() != output.resolve():
                raise RuntimeError(f"Unexpected output directory: {trainer.save_dir}")
            expected_args = {"epochs": 150, "patience": 0, "time": None, "flipud": 0.0,
                             "seed": 26, "hsv_h": cfg["hsv_h"], "hsv_s": cfg["hsv_s"], "hsv_v": cfg["hsv_v"]}
            for key, expected in expected_args.items():
                if getattr(trainer.args, key) != expected:
                    raise RuntimeError(f"Runtime argument changed: {key}")
            if not (0 < trainer.batch_size <= 8):
                raise RuntimeError(f"Unexpected effective batch: {trainer.batch_size}")
            if entry.get("effective_batch") != trainer.batch_size:
                entry.setdefault("batch_history", []).append({"epoch": getattr(trainer, "epoch", -1) + 1,
                    "timestamp_utc": now(), "effective_batch": trainer.batch_size})
                entry.update(configured_batch=8, effective_batch=trainer.batch_size)
                print(f"EFFECTIVE_BATCH configured=8 effective={trainer.batch_size}", flush=True)

        def verify_stopper(trainer):
            guard(trainer)
            if not math.isinf(trainer.stopper.patience):
                raise RuntimeError("Early stopping is still enabled")
            entry["resolved_optimizer"] = {
                "declared": cfg["optimizer"], "class": type(trainer.optimizer).__name__,
                "warmup_bias_lr": trainer.args.warmup_bias_lr,
                "groups": [{key: group[key] for key in ("lr", "initial_lr", "momentum", "betas", "weight_decay") if key in group}
                           for group in trainer.optimizer.param_groups],
            }
            print("RESOLVED_OPTIMIZER", json.dumps(entry["resolved_optimizer"]), flush=True)
            atomic_json(STATUS, state)

        def epoch_done(trainer):
            epoch = trainer.epoch + 1
            # Ultralytics emits another fit event while evaluating best.pt after training.
            if epoch > EPOCHS or epoch <= entry["epochs_completed"]:
                return
            guard(trainer)
            if epoch != entry["epochs_completed"] + 1:
                raise RuntimeError(f"Non-consecutive epoch callback: {epoch}")
            metrics = {key: float(value) for key, value in trainer.metrics.items()}
            progress = {"epoch": epoch, "epochs_required": EPOCHS, "timestamp_utc": now(),
                        "elapsed_seconds": round(time.monotonic() - started, 2), "metrics": metrics,
                        "best_fitness": float(trainer.best_fitness), "batch": trainer.batch_size,
                        "accumulate": trainer.accumulate,
                        "optimizer": {"class": type(trainer.optimizer).__name__,
                            "groups": [{key: group[key] for key in ("lr", "momentum", "betas", "weight_decay") if key in group}
                                       for group in trainer.optimizer.param_groups]}}
            with history.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(progress, allow_nan=False) + "\n")
            entry.update(epochs_completed=epoch, effective_batch=trainer.batch_size,
                         effective_optimizer=progress["optimizer"], latest=progress)
            state["updated_utc"] = now()
            atomic_json(STATUS, state)
            print(f"CAMPAIGN_PROGRESS {name} {epoch}/150", flush=True)

        model.add_callback("on_pretrain_routine_start", guard)
        model.add_callback("on_pretrain_routine_end", verify_stopper)
        model.add_callback("on_train_epoch_start", guard)
        model.add_callback("on_fit_epoch_end", epoch_done)
        try:
            model.train(**{key: value for key, value in cfg.items() if key != "model"})
            verification = validate_training(output)
        except BaseException:
            entry.update(status="training_failed", error=traceback.format_exc(), failed_utc=now())
            state.update(status="failed", updated_utc=now())
            atomic_json(STATUS, state)
            traceback.print_exc()
            raise
        entry.update(status="trained_150_epochs", epochs_completed=150, training_verified=verification,
                     training_completed_utc=now())
        atomic_json(STATUS, state)
        weights = output / "weights/best.pt"
        try:
            entry["status"] = "evaluating"
            atomic_json(STATUS, state)
            metrics = common.evaluate(weights, output / "evaluation")
            row = {"run": name, "model": Path(cfg["model"]).name, "epochs_run": 150,
                   "best_epoch": verification["best_epoch"], "weights": str(weights), **metrics}
            append_benchmark(row)
            entry.update(status="completed", evaluation=metrics, completed_utc=now())
        except Exception:
            # A trained model remains valid; continue to the second authorized training.
            entry.update(status="trained_150_epochs_evaluation_failed", evaluation_error=traceback.format_exc(),
                         evaluation_failed_utc=now())
            traceback.print_exc()
            print(f"Evaluation failed for {name}; its 150 epochs and checkpoints are verified. Continuing queue.", flush=True)
        atomic_json(REPORTS / "metadata" / f"{name}.json", {"config": cfg, **entry})
        state["updated_utc"] = now()
        atomic_json(STATUS, state)


def run(configs: dict[str, dict], checked: dict) -> int:
    with exclusive_runner(), prevent_automatic_sleep():
        # Recheck after acquiring locks so competing starts cannot reuse outputs.
        if STATUS.exists() or any((RUNS / name).exists() for name in ORDER):
            raise FileExistsError("Campaign state/output appeared after preflight; nothing will be overwritten")
        state = {"campaign": CAMPAIGN, "pid": os.getpid(), "status": "running", "started_utc": now(),
                 "updated_utc": now(), "order": list(ORDER), "preflight": checked,
                 "runs": {name: {"status": "pending", "epochs_required": EPOCHS, "epochs_completed": 0} for name in ORDER}}
        atomic_json(STATUS, state)
        try:
            for name in ORDER:
                train_one(name, configs[name], state)
        except BaseException:
            state.update(status="failed", error=traceback.format_exc(), updated_utc=now())
            atomic_json(STATUS, state)
            raise
        all_evaluated = all(entry["status"] == "completed" for entry in state["runs"].values())
        state.update(status="completed" if all_evaluated else "training_completed_evaluation_errors",
                     completed_utc=now(), updated_utc=now(), current_run=None)
        atomic_json(STATUS, state)
        print(json.dumps({"status": state["status"], "status_file": str(STATUS)}, indent=2), flush=True)
        return 0 if all_evaluated else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="Check data, environment and disabled early stopping; no training")
    action.add_argument("--run", action="store_true", help="Train SGD small then nano field, 150 epochs each")
    args = parser.parse_args()
    configs = configurations()
    checked = check(configs)
    return run(configs, checked) if args.run else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ImportError, ValueError, RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
