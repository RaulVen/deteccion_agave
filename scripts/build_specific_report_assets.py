from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "detect" / "agave_experiments" / "yolo26s_sgd_cos_slow_120e"
OUT = ROOT / "docs" / "results"
OUT.mkdir(parents=True, exist_ok=True)


def read_results() -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with (RUN / "results.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            clean = {k.strip(): float(v) for k, v in raw.items() if k is not None and v != ""}
            rows.append(clean)
    return rows


def plot_operational_accuracy(rows: list[dict[str, float]]) -> None:
    epochs = [int(r["epoch"]) for r in rows]
    precision = np.array([r["metrics/precision(B)"] for r in rows])
    recall = np.array([r["metrics/recall(B)"] for r in rows])
    map50 = np.array([r["metrics/mAP50(B)"] for r in rows])
    acc = np.where((precision + recall) > 0, 2 * precision * recall / (precision + recall), 0)

    best_idx = int(np.nanargmax(map50))
    best_epoch = epochs[best_idx]

    plt.figure(figsize=(10.5, 6.2))
    plt.plot(epochs, acc, color="#1f77b4", linewidth=2.4, label="ACC operacional (F1)")
    plt.plot(epochs, precision, color="#2ca02c", linewidth=1.8, alpha=0.85, label="Precision")
    plt.plot(epochs, recall, color="#ff7f0e", linewidth=1.8, alpha=0.85, label="Recall")
    plt.plot(epochs, map50, color="#9467bd", linewidth=1.8, alpha=0.85, label="mAP50")
    plt.axvline(best_epoch, color="#333333", linestyle="--", linewidth=1.2, label=f"Mejor epoca mAP50: {best_epoch}")
    plt.title("Evolucion de ACC operacional, precision, recall y mAP50", fontsize=14, weight="bold")
    plt.xlabel("Epoca")
    plt.ylabel("Valor")
    plt.ylim(0, 1.0)
    plt.grid(True, linestyle=":", alpha=0.45)
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    plt.savefig(OUT / "best_yolo26s_operational_accuracy.png", dpi=180)
    plt.close()


def plot_readable_confusion_from_metrics(rows: list[dict[str, float]]) -> None:
    # El entrenamiento no guarda una matriz 2x2 cruda exportable en CSV.
    # Para el reporte se redibuja una matriz explicativa estimada a partir de precision/recall
    # de la mejor epoca. Esto evita el problema visual del fondo blanco contra background.
    best = max(rows, key=lambda r: r["metrics/mAP50(B)"])
    precision = best["metrics/precision(B)"]
    recall = best["metrics/recall(B)"]
    support = 100
    tp = recall * support
    fn = support - tp
    fp = tp * (1 / precision - 1) if precision > 0 else support
    matrix = np.array([[tp, fn], [fp, 0.0]])

    labels = ["Agave real", "Background"]
    pred_labels = ["Predicho agave", "Sin deteccion/background"]

    plt.figure(figsize=(8.2, 6.6))
    im = plt.imshow(matrix, cmap="Blues")
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.title("Matriz de confusion explicativa con contraste alto", fontsize=14, weight="bold")
    plt.xticks(range(2), pred_labels, rotation=20, ha="right")
    plt.yticks(range(2), labels)

    max_val = matrix.max() if matrix.max() else 1
    cell_text = [
        ["TP\nAgaves detectados", "FN\nAgaves no detectados"],
        ["FP\nFalsas detecciones", "TN\nNo aplica en deteccion"],
    ]
    for i in range(2):
        for j in range(2):
            color = "white" if matrix[i, j] > max_val * 0.45 else "black"
            value = f"{matrix[i, j]:.1f}" if not (i == 1 and j == 1) else "N/A"
            plt.text(
                j,
                i,
                f"{cell_text[i][j]}\n{value}",
                ha="center",
                va="center",
                color=color,
                fontsize=11,
                weight="bold",
            )
    plt.xlabel("Prediccion del modelo")
    plt.ylabel("Referencia")
    plt.tight_layout()
    plt.savefig(OUT / "best_yolo26s_confusion_matrix_readable.png", dpi=180)
    plt.close()


def main() -> None:
    rows = read_results()
    plot_operational_accuracy(rows)
    plot_readable_confusion_from_metrics(rows)
    best = max(rows, key=lambda r: r["metrics/mAP50(B)"])
    precision = best["metrics/precision(B)"]
    recall = best["metrics/recall(B)"]
    f1 = 2 * precision * recall / (precision + recall)
    print(f"best_epoch={int(best['epoch'])} precision={precision:.4f} recall={recall:.4f} f1={f1:.4f} mAP50={best['metrics/mAP50(B)']:.4f}")


if __name__ == "__main__":
    main()
