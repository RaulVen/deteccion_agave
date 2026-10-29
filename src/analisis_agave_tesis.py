from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "yolo26"
BEST_RUN = ROOT / "runs" / "detect" / "agave_experiments" / "yolo26s_sgd_cos_slow_120e"
BENCHMARK = ROOT / "benchmark" / "agave_benchmark.csv"
TRACKING_CSV = ROOT / "video_predictions" / "3_segment_01m30s_02m00s_tracking_line50_down_unique.csv"
TRACKING_FRAME = ROOT / "docs" / "results" / "final_tracking_video_frame.jpg"
EVIDENCE = ROOT / "docs" / "evidencia"
FIGS_ES = EVIDENCE / "figuras"
FIGS_EN = EVIDENCE / "figuras_en"
STATS_JSON = EVIDENCE / "estadisticas_agave_tesis.json"
REPORT_MD = EVIDENCE / "analisis_agave_tesis.md"


TEXT = {
    "es": {
        "overlay_title": "Overlay de verificacion de etiquetas YOLO",
        "dataset_title": "Distribucion del dataset local usado en entrenamiento",
        "bbox_title": "Geometria de cajas anotadas",
        "benchmark_title": "Benchmark de corridas YOLO en test",
        "pr_title": "Precision vs recall por experimento",
        "curves_title": "Curvas del mejor entrenamiento",
        "sanity_title": "Sanity checks de etiquetas e imagenes",
        "tracking_title": "Tracking y conteo operacional en video",
        "versioning_title": "Deriva entre Roboflow vivo y export local",
        "images": "Imagenes",
        "boxes": "Cajas",
        "split": "Particion",
        "boxes_per_image": "Cajas por imagen",
        "width": "Ancho normalizado",
        "height": "Alto normalizado",
        "aspect": "Relacion ancho/alto",
        "area": "Area normalizada",
        "precision": "Precision",
        "recall": "Recall",
        "map50": "mAP50",
        "map5095": "mAP50-95",
        "epoch": "Epoca",
        "loss": "Perdida",
        "metric": "Metrica",
        "cum_count": "Conteo acumulado",
        "time_s": "Tiempo (s)",
        "count": "Conteo",
        "value": "Valor",
    },
    "en": {
        "overlay_title": "YOLO label verification overlay",
        "dataset_title": "Local training dataset distribution",
        "bbox_title": "Annotated bounding-box geometry",
        "benchmark_title": "YOLO test benchmark across runs",
        "pr_title": "Precision vs. recall by experiment",
        "curves_title": "Best-run training curves",
        "sanity_title": "Image and label sanity checks",
        "tracking_title": "Operational video tracking and counting",
        "versioning_title": "Roboflow-live vs. local-export drift",
        "images": "Images",
        "boxes": "Boxes",
        "split": "Split",
        "boxes_per_image": "Boxes per image",
        "width": "Normalized width",
        "height": "Normalized height",
        "aspect": "Width/height ratio",
        "area": "Normalized area",
        "precision": "Precision",
        "recall": "Recall",
        "map50": "mAP50",
        "map5095": "mAP50-95",
        "epoch": "Epoch",
        "loss": "Loss",
        "metric": "Metric",
        "cum_count": "Cumulative count",
        "time_s": "Time (s)",
        "count": "Count",
        "value": "Value",
    },
}


PALETTE = {
    "green": "#2E7D32",
    "blue": "#2B6CB0",
    "gold": "#C49A00",
    "coral": "#D95F43",
    "purple": "#6A4C93",
    "gray": "#59656F",
    "light": "#F3F6F4",
}


@dataclass
class BoxRecord:
    split: str
    image: str
    image_width: int
    image_height: int
    cls: int
    x: float
    y: float
    w: float
    h: float

    @property
    def area(self) -> float:
        return self.w * self.h

    @property
    def aspect(self) -> float:
        return self.w / self.h if self.h else math.nan

    @property
    def xyxy(self) -> tuple[float, float, float, float]:
        return (
            self.x - self.w / 2,
            self.y - self.h / 2,
            self.x + self.w / 2,
            self.y + self.h / 2,
        )


def normalize_rf_name(name: str) -> str:
    return re.sub(r"_jpg\.rf\.[^.]+\.jpg$", ".jpg", name)


def pct(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    arr = sorted(values)
    if len(arr) == 1:
        return arr[0]
    pos = (len(arr) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return arr[int(pos)]
    return arr[lo] * (hi - pos) + arr[hi] * (pos - lo)


def distribution(values: list[float]) -> dict[str, float | int | None]:
    vals = [float(v) for v in values if v is not None and not math.isnan(float(v))]
    if not vals:
        return {"n": 0}
    mu = mean(vals)
    sd = pstdev(vals) if len(vals) > 1 else 0.0
    return {
        "n": len(vals),
        "mean": mu,
        "std": sd,
        "cv": (sd / mu) if mu else None,
        "min": min(vals),
        "p05": pct(vals, 0.05),
        "p10": pct(vals, 0.10),
        "p25": pct(vals, 0.25),
        "p50": pct(vals, 0.50),
        "p75": pct(vals, 0.75),
        "p90": pct(vals, 0.90),
        "p95": pct(vals, 0.95),
        "max": max(vals),
    }


def read_boxes() -> tuple[list[BoxRecord], dict[str, dict]]:
    boxes: list[BoxRecord] = []
    image_meta: dict[str, dict] = {}
    for split in ("train", "val", "test"):
        image_dir = DATASET / "images" / split
        label_dir = DATASET / "labels" / split
        for image_path in sorted(image_dir.glob("*.jpg")):
            with Image.open(image_path) as im:
                width, height = im.size
            normalized = normalize_rf_name(image_path.name)
            label_path = label_dir / image_path.with_suffix(".txt").name
            image_meta[image_path.name] = {
                "normalized_name": normalized,
                "split": split,
                "width": width,
                "height": height,
                "label_path": str(label_path.relative_to(ROOT)),
                "image_path": str(image_path.relative_to(ROOT)),
            }
            if not label_path.exists():
                continue
            for line in label_path.read_text(encoding="utf-8").splitlines():
                parts = line.strip().split()
                if not parts:
                    continue
                if len(parts) != 5:
                    raise ValueError(f"Invalid YOLO row in {label_path}: {line}")
                cls, x, y, w, h = parts
                boxes.append(
                    BoxRecord(
                        split=split,
                        image=image_path.name,
                        image_width=width,
                        image_height=height,
                        cls=int(cls),
                        x=float(x),
                        y=float(y),
                        w=float(w),
                        h=float(h),
                    )
                )
    return boxes, image_meta


def bbox_iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter
    return inter / denom if denom else 0.0


def duplicate_iou_checks(boxes: list[BoxRecord]) -> dict:
    by_image: dict[str, list[BoxRecord]] = defaultdict(list)
    for box in boxes:
        by_image[box.image].append(box)
    pairs_gt_09 = 0
    pairs_gt_08 = 0
    max_iou_by_image = {}
    top_pairs = []
    for image, image_boxes in by_image.items():
        max_iou = 0.0
        for i in range(len(image_boxes)):
            for j in range(i + 1, len(image_boxes)):
                iou = bbox_iou(image_boxes[i].xyxy, image_boxes[j].xyxy)
                max_iou = max(max_iou, iou)
                if iou > 0.9:
                    pairs_gt_09 += 1
                if iou > 0.8:
                    pairs_gt_08 += 1
                if iou > 0.75:
                    top_pairs.append({"image": image, "box_i": i, "box_j": j, "iou": iou})
        max_iou_by_image[image] = max_iou
    top_pairs = sorted(top_pairs, key=lambda x: x["iou"], reverse=True)[:20]
    return {
        "images_checked": len(by_image),
        "pairs_iou_gt_0_90": pairs_gt_09,
        "pairs_iou_gt_0_80": pairs_gt_08,
        "max_iou_distribution": distribution(list(max_iou_by_image.values())),
        "top_suspicious_pairs": top_pairs,
    }


def read_benchmark() -> list[dict]:
    rows = []
    with BENCHMARK.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = dict(row)
            for key in [
                "rank",
                "epochs_run",
                "best_epoch",
                "test_precision",
                "test_recall",
                "test_mAP50",
                "test_mAP50_95",
                "val_precision",
                "val_recall",
                "val_mAP50",
                "val_mAP50_95",
            ]:
                if key in clean:
                    clean[key] = float(clean[key])
                    if key in {"rank", "epochs_run", "best_epoch"}:
                        clean[key] = int(clean[key])
            rows.append(clean)
    return rows


def read_training_results() -> list[dict]:
    path = BEST_RUN / "results.csv"
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip(): float(v) for k, v in row.items() if v != ""})
    return rows


def read_tracking() -> list[dict]:
    if not TRACKING_CSV.exists():
        return []
    rows = []
    with TRACKING_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = dict(row)
            clean["frame"] = int(float(clean["frame"]))
            clean["time_s"] = float(clean["time_s"])
            clean["track_id"] = int(float(clean["track_id"]))
            clean["x"] = float(clean["x"])
            clean["y"] = float(clean["y"])
            rows.append(clean)
    return rows


def load_json(path: Path) -> dict | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def build_stats() -> dict:
    boxes, image_meta = read_boxes()
    benchmark = read_benchmark()
    training = read_training_results()
    tracking = read_tracking()
    roboflow_live = load_json(EVIDENCE / "roboflow_live_verification.json")
    roboflow_diff = load_json(EVIDENCE / "roboflow_local_label_count_diff.json")
    roboflow_version = load_json(EVIDENCE / "roboflow_live_version_dataset_summary.json")

    boxes_by_split = Counter(box.split for box in boxes)
    images_by_split = Counter(meta["split"] for meta in image_meta.values())
    boxes_per_image = Counter(box.image for box in boxes)
    image_sizes = Counter((meta["width"], meta["height"]) for meta in image_meta.values())

    labels_in_bounds = all(
        0.0 <= b.x <= 1.0
        and 0.0 <= b.y <= 1.0
        and 0.0 < b.w <= 1.0
        and 0.0 < b.h <= 1.0
        and b.xyxy[0] >= 0.0
        and b.xyxy[1] >= 0.0
        and b.xyxy[2] <= 1.0
        and b.xyxy[3] <= 1.0
        for b in boxes
    )
    duplicate_checks = duplicate_iou_checks(boxes)

    metric_keys = ["test_precision", "test_recall", "test_mAP50", "test_mAP50_95"]
    best = sorted(benchmark, key=lambda r: r["rank"])[0]
    best_by_training_curve = max(training, key=lambda r: r.get("metrics/mAP50-95(B)", -1))

    stats = {
        "metadata": {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "repo": str(ROOT),
            "dataset_path": str(DATASET.relative_to(ROOT)),
            "best_run_path": str(BEST_RUN.relative_to(ROOT)),
            "benchmark_path": str(BENCHMARK.relative_to(ROOT)),
            "tracking_csv_path": str(TRACKING_CSV.relative_to(ROOT)),
            "scope_note": "This paper reports the local 404-image export and benchmark used for training, not the later Roboflow generated version with 699 images.",
        },
        "dataset": {
            "splits": {
                split: {
                    "images": int(images_by_split[split]),
                    "boxes": int(boxes_by_split[split]),
                    "boxes_per_image": distribution(
                        [boxes_per_image[name] for name, meta in image_meta.items() if meta["split"] == split]
                    ),
                }
                for split in ["train", "val", "test"]
            },
            "total_images": len(image_meta),
            "total_boxes": len(boxes),
            "classes": {"0": "agave"},
            "class_counts": {str(k): int(v) for k, v in Counter(box.cls for box in boxes).items()},
            "image_sizes": {f"{w}x{h}": int(c) for (w, h), c in image_sizes.items()},
            "image_aspect_ratio": distribution([meta["width"] / meta["height"] for meta in image_meta.values()]),
            "bbox_width": distribution([box.w for box in boxes]),
            "bbox_height": distribution([box.h for box in boxes]),
            "bbox_area": distribution([box.area for box in boxes]),
            "bbox_aspect_ratio": distribution([box.aspect for box in boxes]),
            "boxes_per_image": distribution(list(boxes_per_image.values())),
        },
        "benchmark": {
            "runs": benchmark,
            "best_model": best,
            "metric_distributions": {key: distribution([float(row[key]) for row in benchmark]) for key in metric_keys},
        },
        "training_curve": {
            "epochs_recorded": len(training),
            "best_epoch_by_val_map50_95": int(best_by_training_curve["epoch"]),
            "best_val_map50_95": best_by_training_curve.get("metrics/mAP50-95(B)"),
            "best_val_map50": best_by_training_curve.get("metrics/mAP50(B)"),
            "final_epoch": int(training[-1]["epoch"]) if training else None,
        },
        "tracking": {
            "events": len(tracking),
            "unique_track_ids": len({row["track_id"] for row in tracking}),
            "final_count": len(tracking),
            "direction_counts": dict(Counter(row["direction"] for row in tracking)),
            "time_s_distribution": distribution([row["time_s"] for row in tracking]),
            "first_event_s": min([row["time_s"] for row in tracking]) if tracking else None,
            "last_event_s": max([row["time_s"] for row in tracking]) if tracking else None,
        },
        "sanity_checks": {
            "expected_single_class_agave": set(box.cls for box in boxes) == {0},
            "labels_in_bounds": labels_in_bounds,
            "all_images_2880x1620": set(image_sizes.keys()) == {(2880, 1620)},
            "local_export_has_no_640x640_files": all(size != (640, 640) for size in image_sizes.keys()),
            "duplicate_iou": duplicate_checks,
            "roboflow_live_project": roboflow_live,
            "roboflow_local_diff": roboflow_diff,
            "roboflow_version_dataset": roboflow_version,
        },
    }
    return stats


def setup_plot() -> None:
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 160,
            "savefig.dpi": 220,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def yolo_boxes_for_image(image_name: str) -> list[BoxRecord]:
    boxes, _ = read_boxes()
    return [box for box in boxes if box.image == image_name]


def sample_images_for_overlay(image_meta: dict[str, dict]) -> list[str]:
    counts = Counter()
    for box in read_boxes()[0]:
        counts[box.image] += 1
    selected = []
    for split in ["train", "val", "test"]:
        candidates = [name for name, meta in image_meta.items() if meta["split"] == split]
        candidates.sort(key=lambda n: counts[n], reverse=True)
        selected.extend(candidates[:1])
    remaining = [name for name in image_meta if name not in selected]
    remaining.sort(key=lambda n: counts[n], reverse=True)
    selected.extend(remaining[: 4 - len(selected)])
    return selected[:4]


def draw_overlay_figure(image_meta: dict[str, dict], outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    selected = sample_images_for_overlay(image_meta)
    tiles = []
    font = ImageFont.load_default()
    for image_name in selected:
        meta = image_meta[image_name]
        image_path = ROOT / meta["image_path"]
        im = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(im)
        for box in yolo_boxes_for_image(image_name):
            x1 = (box.x - box.w / 2) * im.width
            y1 = (box.y - box.h / 2) * im.height
            x2 = (box.x + box.w / 2) * im.width
            y2 = (box.y + box.h / 2) * im.height
            draw.rectangle([x1, y1, x2, y2], outline=(20, 190, 80), width=max(3, im.width // 500))
        caption = f"{meta['split']} | {normalize_rf_name(image_name)}"
        tile_w = 780
        tile_h = int(tile_w * im.height / im.width)
        im = im.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (tile_w, tile_h + 30), "white")
        canvas.paste(im, (0, 0))
        ImageDraw.Draw(canvas).text((8, tile_h + 8), caption[:115], fill=(30, 30, 30), font=font)
        tiles.append(canvas)
    grid = Image.new("RGB", (tiles[0].width * 2 + 16, tiles[0].height * 2 + 52), "white")
    title_draw = ImageDraw.Draw(grid)
    title_draw.text((8, 8), labels["overlay_title"], fill=(20, 20, 20), font=font)
    for idx, tile in enumerate(tiles):
        x = (idx % 2) * (tiles[0].width + 16)
        y = 36 + (idx // 2) * (tiles[0].height + 16)
        grid.paste(tile, (x, y))
    outdir.mkdir(parents=True, exist_ok=True)
    grid.save(outdir / "fig01_overlay_verificacion_agave.png")


def draw_dataset_distribution(stats: dict, outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    setup_plot()
    splits = ["train", "val", "test"]
    images = [stats["dataset"]["splits"][s]["images"] for s in splits]
    boxes = [stats["dataset"]["splits"][s]["boxes"] for s in splits]
    boxes_per_image = [stats["dataset"]["splits"][s]["boxes_per_image"]["mean"] for s in splits]
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.2))
    x = np.arange(len(splits))
    width = 0.36
    axes[0].bar(x - width / 2, images, width=width, label=labels["images"], color=PALETTE["blue"])
    axes[0].bar(x + width / 2, boxes, width=width, label=labels["boxes"], color=PALETTE["green"])
    axes[0].set_xticks(x, splits)
    axes[0].set_title(labels["dataset_title"])
    axes[0].legend()
    axes[0].set_ylabel(labels["count"])
    axes[1].bar(splits, boxes_per_image, color=[PALETTE["gold"], PALETTE["coral"], PALETTE["purple"]])
    axes[1].set_title(labels["boxes_per_image"])
    axes[1].set_ylabel(labels["boxes_per_image"])
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
    savefig(outdir / "fig02_distribucion_dataset.png")


def draw_bbox_geometry(boxes: list[BoxRecord], outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    setup_plot()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.6))
    axes = axes.ravel()
    axes[0].hist([b.w for b in boxes], bins=35, color=PALETTE["blue"], alpha=0.9)
    axes[0].set_title(labels["width"])
    axes[1].hist([b.h for b in boxes], bins=35, color=PALETTE["green"], alpha=0.9)
    axes[1].set_title(labels["height"])
    axes[2].hist([min(b.aspect, 5.0) for b in boxes], bins=35, color=PALETTE["gold"], alpha=0.9)
    axes[2].set_title(labels["aspect"])
    axes[3].hist([b.area for b in boxes], bins=35, color=PALETTE["coral"], alpha=0.9)
    axes[3].set_title(labels["area"])
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
        ax.set_ylabel(labels["count"])
    fig.suptitle(labels["bbox_title"], y=1.02, fontsize=12)
    savefig(outdir / "fig03_geometria_bboxes.png")


def short_run_name(run: str) -> str:
    return (
        run.replace("yolo26", "")
        .replace("_120e", "")
        .replace("_60e", "")
        .replace("_45e", "")
        .replace("_30e", "")
        .replace("_", "\n")
    )


def draw_benchmark(stats: dict, outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    setup_plot()
    rows = sorted(stats["benchmark"]["runs"], key=lambda r: r["rank"])
    names = [short_run_name(r["run"]) for r in rows]
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(9.0, 4.2))
    ax.bar(x - 0.18, [r["test_mAP50"] for r in rows], width=0.35, label=labels["map50"], color=PALETTE["green"])
    ax.bar(x + 0.18, [r["test_mAP50_95"] for r in rows], width=0.35, label=labels["map5095"], color=PALETTE["blue"])
    ax.scatter([0], [rows[0]["test_mAP50"]], color=PALETTE["coral"], s=45, zorder=3)
    ax.set_xticks(x, names, rotation=0)
    ax.set_ylim(0, max(r["test_mAP50"] for r in rows) * 1.25)
    ax.set_title(labels["benchmark_title"])
    ax.set_ylabel(labels["metric"])
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    savefig(outdir / "fig04_benchmark_modelos.png")


def draw_precision_recall(stats: dict, outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    setup_plot()
    rows = sorted(stats["benchmark"]["runs"], key=lambda r: r["rank"])
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    map5095 = np.array([r["test_mAP50_95"] for r in rows])
    sizes = 120 + 900 * (map5095 - map5095.min()) / max(0.001, (map5095.max() - map5095.min()))
    sc = ax.scatter(
        [r["test_recall"] for r in rows],
        [r["test_precision"] for r in rows],
        s=sizes,
        c=[r["test_mAP50"] for r in rows],
        cmap="viridis",
        alpha=0.85,
        edgecolors="white",
        linewidths=0.8,
    )
    for r in rows[:4]:
        ax.annotate(str(r["rank"]), (r["test_recall"], r["test_precision"]), xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel(labels["recall"])
    ax.set_ylabel(labels["precision"])
    ax.set_title(labels["pr_title"])
    ax.grid(alpha=0.25)
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label(labels["map50"])
    savefig(outdir / "fig05_precision_recall_experimentos.png")


def draw_training_curves(outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    rows = read_training_results()
    setup_plot()
    epochs = [r["epoch"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.6))
    axes[0].plot(epochs, [r["metrics/precision(B)"] for r in rows], label=labels["precision"], color=PALETTE["blue"])
    axes[0].plot(epochs, [r["metrics/recall(B)"] for r in rows], label=labels["recall"], color=PALETTE["green"])
    axes[0].plot(epochs, [r["metrics/mAP50(B)"] for r in rows], label=labels["map50"], color=PALETTE["gold"])
    axes[0].plot(epochs, [r["metrics/mAP50-95(B)"] for r in rows], label=labels["map5095"], color=PALETTE["coral"])
    axes[0].set_xlabel(labels["epoch"])
    axes[0].set_ylabel(labels["metric"])
    axes[0].legend(ncol=2)
    axes[0].grid(alpha=0.25)
    axes[1].plot(epochs, [r["train/box_loss"] for r in rows], label="train box", color=PALETTE["blue"])
    axes[1].plot(epochs, [r["val/box_loss"] for r in rows], label="val box", color=PALETTE["coral"])
    axes[1].plot(epochs, [r["train/cls_loss"] for r in rows], label="train cls", color=PALETTE["green"])
    axes[1].plot(epochs, [r["val/cls_loss"] for r in rows], label="val cls", color=PALETTE["gold"])
    axes[1].set_xlabel(labels["epoch"])
    axes[1].set_ylabel(labels["loss"])
    axes[1].legend(ncol=2)
    axes[1].grid(alpha=0.25)
    fig.suptitle(labels["curves_title"], y=1.03, fontsize=12)
    savefig(outdir / "fig06_curvas_entrenamiento_mejor_modelo.png")


def draw_sanity(stats: dict, outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    setup_plot()
    sanity = stats["sanity_checks"]
    checks = [
        ("single class", int(sanity["expected_single_class_agave"])),
        ("labels in bounds", int(sanity["labels_in_bounds"])),
        ("2880x1620 files", int(sanity["all_images_2880x1620"])),
        ("no local 640 files", int(sanity["local_export_has_no_640x640_files"])),
        ("IoU>0.90 pairs", sanity["duplicate_iou"]["pairs_iou_gt_0_90"]),
        ("IoU>0.80 pairs", sanity["duplicate_iou"]["pairs_iou_gt_0_80"]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6))
    axes[0].barh([c[0] for c in checks], [c[1] for c in checks], color=[PALETTE["green"]] * 4 + [PALETTE["gold"], PALETTE["coral"]])
    axes[0].set_title(labels["sanity_title"])
    axes[0].set_xlabel(labels["value"])
    dist = sanity["duplicate_iou"]["max_iou_distribution"]
    box_stats = [
        dist.get("p50", 0),
        dist.get("p75", 0),
        dist.get("p90", 0),
        dist.get("p95", 0),
        dist.get("max", 0),
    ]
    axes[1].plot(["p50", "p75", "p90", "p95", "max"], box_stats, marker="o", color=PALETTE["blue"])
    axes[1].set_ylim(0, max(1.0, max(box_stats) * 1.1))
    axes[1].set_ylabel("Max IoU")
    axes[1].set_title("Duplicate-box screen")
    axes[1].grid(alpha=0.25)
    savefig(outdir / "fig07_sanity_checks.png")


def draw_tracking(outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    tracking = read_tracking()
    setup_plot()
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0), gridspec_kw={"width_ratios": [1.2, 1]})
    if TRACKING_FRAME.exists():
        frame = mpimg.imread(TRACKING_FRAME)
        axes[0].imshow(frame)
        axes[0].axis("off")
    axes[0].set_title(labels["tracking_title"])
    if tracking:
        times = [row["time_s"] for row in tracking]
        cum = list(range(1, len(tracking) + 1))
        axes[1].step(times, cum, where="post", color=PALETTE["green"], linewidth=2)
        axes[1].scatter(times[-1:], cum[-1:], color=PALETTE["coral"], s=55, zorder=3)
        axes[1].annotate(str(cum[-1]), (times[-1], cum[-1]), xytext=(-18, 8), textcoords="offset points")
    axes[1].set_xlabel(labels["time_s"])
    axes[1].set_ylabel(labels["cum_count"])
    axes[1].grid(alpha=0.25)
    savefig(outdir / "fig08_tracking_conteo.png")


def draw_versioning(stats: dict, outdir: Path, lang: str) -> None:
    labels = TEXT[lang]
    setup_plot()
    live = stats["sanity_checks"].get("roboflow_live_project") or {}
    diff = stats["sanity_checks"].get("roboflow_local_diff") or {}
    version = stats["sanity_checks"].get("roboflow_version_dataset") or {}
    project = live.get("project_summary") or {}
    search = live.get("search_summary") or {}
    version_1 = (version.get("version_1") or {}).get("version") or {}
    names = ["project\nsummary", "live\nsearch", "local\nexport"]
    values = [
        (project.get("classes") or {}).get("agave", 0),
        (search.get("classes_returned") or {}).get("agave", 0),
        diff.get("local_boxes", stats["dataset"]["total_boxes"]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.4))
    axes[0].bar(names, values, color=[PALETTE["gold"], PALETTE["blue"], PALETTE["green"]])
    axes[0].set_ylabel(labels["boxes"])
    axes[0].set_title(labels["versioning_title"])
    for i, v in enumerate(values):
        axes[0].text(i, v + max(values) * 0.01, str(v), ha="center", va="bottom", fontsize=8)
    image_values = [
        project.get("images", 0),
        version_1.get("images", 0),
        stats["dataset"]["total_images"],
    ]
    axes[1].bar(["project\nimages", "version 1\nimages", "local\nimages"], image_values, color=[PALETTE["blue"], PALETTE["coral"], PALETTE["green"]])
    axes[1].set_ylabel(labels["images"])
    for i, v in enumerate(image_values):
        axes[1].text(i, v + max(image_values) * 0.01, str(v), ha="center", va="bottom", fontsize=8)
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
    savefig(outdir / "fig09_versionado_roboflow_local.png")


def write_report(stats: dict) -> None:
    best = stats["benchmark"]["best_model"]
    ds = stats["dataset"]
    sanity = stats["sanity_checks"]
    live = (sanity.get("roboflow_live_project") or {}).get("project_summary") or {}
    search = (sanity.get("roboflow_live_project") or {}).get("search_summary") or {}
    diff = sanity.get("roboflow_local_diff") or {}
    version = ((sanity.get("roboflow_version_dataset") or {}).get("version_1") or {}).get("version") or {}
    duplicate = sanity["duplicate_iou"]
    lines = [
        "# Analisis reproducible - deteccion de agave joven",
        "",
        "## Fuente viva y alcance",
        "",
        "- Proyecto Roboflow vivo verificado: `raul-stlme/agave-vty65` (nombre `agave`).",
        f"- Roboflow proyecto: {live.get('images', 'NA')} imagenes, splits {live.get('splits', {})}, clases {live.get('classes', {})}.",
        f"- Busqueda viva imagen-por-imagen: {search.get('returned_records', 'NA')} imagenes y {search.get('annotation_count_returned', 'NA')} anotaciones.",
        f"- Export local usado para entrenamiento: {ds['total_images']} imagenes y {ds['total_boxes']} cajas YOLO.",
        "- Advertencia: `datasets/yolo26/data.yaml` conserva el slug `raul-stlme/raul-stlme`, pero Roboflow devuelve `raul-stlme/agave-vty65` como ID real del proyecto.",
        f"- Advertencia: la version viva `1` reporta {version.get('images', 'NA')} imagenes generadas; el benchmark local no usa esa version aumentada.",
        f"- Deriva localizada: {len(diff.get('count_differences', []))} imagen con conteo distinto entre Roboflow vivo y export local.",
        "",
        "## Dataset local",
        "",
    ]
    for split in ["train", "val", "test"]:
        s = ds["splits"][split]
        lines.append(
            f"- `{split}`: {s['images']} imagenes, {s['boxes']} cajas, media {s['boxes_per_image']['mean']:.2f} cajas/imagen."
        )
    lines += [
        f"- Todas las imagenes locales tienen dimension {', '.join(ds['image_sizes'].keys())}.",
        f"- Ancho de caja medio: {ds['bbox_width']['mean']:.4f}; alto medio: {ds['bbox_height']['mean']:.4f}; area media: {ds['bbox_area']['mean']:.4f}.",
        "",
        "## Mejor modelo",
        "",
        f"- Corrida: `{best['run']}` con base `{best['model']}`.",
        f"- Test: precision={best['test_precision']:.3f}, recall={best['test_recall']:.3f}, mAP50={best['test_mAP50']:.3f}, mAP50-95={best['test_mAP50_95']:.3f}.",
        f"- Epocas corridas: {best['epochs_run']}; mejor epoca segun benchmark: {best['best_epoch']}.",
        "",
        "## Tracking",
        "",
        f"- Segmento con tracking: {stats['tracking']['events']} cruces/eventos y {stats['tracking']['unique_track_ids']} IDs unicos.",
        f"- Conteo final reportado: {stats['tracking']['final_count']} agaves en direccion `{list(stats['tracking']['direction_counts'].keys())[0] if stats['tracking']['direction_counts'] else 'NA'}`.",
        "",
        "## Sanity checks",
        "",
        f"- Clase unica `agave`: {sanity['expected_single_class_agave']}.",
        f"- Cajas dentro de limites normalizados: {sanity['labels_in_bounds']}.",
        f"- Pares potencialmente duplicados IoU>0.90: {duplicate['pairs_iou_gt_0_90']}; IoU>0.80: {duplicate['pairs_iou_gt_0_80']}.",
        "- GSD/calibracion fisica: no se infiere. El analisis reporta desempeno de deteccion y conteo en pixeles/frames, no dimensiones metricas de planta.",
        "",
        "## Figuras",
        "",
        "- `fig01_overlay_verificacion_agave.png`: overlay de etiquetas locales.",
        "- `fig02_distribucion_dataset.png`: imagenes, cajas y cajas/imagen por particion.",
        "- `fig03_geometria_bboxes.png`: distribuciones de ancho, alto, aspecto y area.",
        "- `fig04_benchmark_modelos.png`: comparacion de mAP por corrida.",
        "- `fig05_precision_recall_experimentos.png`: trade-off precision/recall.",
        "- `fig06_curvas_entrenamiento_mejor_modelo.png`: curvas del mejor entrenamiento.",
        "- `fig07_sanity_checks.png`: validaciones de etiquetas e IoU duplicado.",
        "- `fig08_tracking_conteo.png`: frame final y conteo acumulado.",
        "- `fig09_versionado_roboflow_local.png`: deriva Roboflow/export local.",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def generate_figures(stats: dict, lang: str = "es") -> None:
    outdir = FIGS_ES if lang == "es" else FIGS_EN
    outdir.mkdir(parents=True, exist_ok=True)
    boxes, image_meta = read_boxes()
    draw_overlay_figure(image_meta, outdir, lang)
    draw_dataset_distribution(stats, outdir, lang)
    draw_bbox_geometry(boxes, outdir, lang)
    draw_benchmark(stats, outdir, lang)
    draw_precision_recall(stats, outdir, lang)
    draw_training_curves(outdir, lang)
    draw_sanity(stats, outdir, lang)
    draw_tracking(outdir, lang)
    draw_versioning(stats, outdir, lang)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["es", "en"], default="es")
    parser.add_argument("--figures-only", action="store_true")
    args = parser.parse_args()

    EVIDENCE.mkdir(exist_ok=True)
    stats = build_stats()
    if not args.figures_only or not STATS_JSON.exists():
        STATS_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.lang == "es":
            write_report(stats)
    generate_figures(stats, args.lang)
    print(f"Wrote {STATS_JSON.relative_to(ROOT)}")
    print(f"Wrote figures in {(FIGS_ES if args.lang == 'es' else FIGS_EN).relative_to(ROOT)}")
    if args.lang == "es":
        print(f"Wrote {REPORT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
