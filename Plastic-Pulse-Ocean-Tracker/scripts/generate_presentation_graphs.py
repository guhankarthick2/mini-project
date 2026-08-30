"""
Generate presentation-ready accuracy / metrics graphs for Week 3.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEEK3 = PROJECT_ROOT / "outputs" / "week3"
OUT = WEEK3 / "presentation"
RESULTS_JSON = WEEK3 / "week3_training_results.json"
TRAINING_CSV = WEEK3 / "training_log.csv"
EXPERIMENT_JSON = WEEK3 / "experiments" / "experiment_summary.json"

# Presentation-friendly style
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#334155",
    "axes.labelcolor": "#0f172a",
    "text.color": "#0f172a",
    "xtick.color": "#334155",
    "ytick.color": "#334155",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
    "figure.dpi": 140,
})

COLORS = {
    "train": "#2563eb",
    "val": "#f59e0b",
    "test": "#059669",
    "marine": "#0284c7",
    "plastic": "#dc2626",
    "grid": "#e2e8f0",
}


def load_training_log() -> dict[str, list[float]]:
    rows: dict[str, list[float]] = {}
    with TRAINING_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k, v in row.items():
                rows.setdefault(k, []).append(float(v))
    return rows


def save(fig: plt.Figure, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_accuracy_epochs(log: dict[str, list[float]]) -> Path:
    epochs = np.arange(1, len(log["accuracy"]) + 1)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(epochs, log["accuracy"], color=COLORS["train"], marker="o", lw=2.2, ms=7, label="Train accuracy")
    ax.plot(epochs, log["val_accuracy"], color=COLORS["val"], marker="s", lw=2.2, ms=7, label="Validation accuracy")
    lo = min(min(log["accuracy"]), min(log["val_accuracy"]))
    ax.set_ylim(max(0.97, lo - 0.01), 1.001)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.set_title("Training & Validation Accuracy Over Epochs", fontweight="bold", pad=12)
    ax.set_xticks(epochs)
    ax.grid(True, alpha=0.35, color=COLORS["grid"])
    ax.legend(loc="lower right", framealpha=0.95)
    for x, y in zip(epochs, log["val_accuracy"]):
        if y == max(log["val_accuracy"]):
            ax.annotate(f"best val\n{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 12),
                        ha="center", fontsize=9, color=COLORS["val"], fontweight="bold")
    return save(fig, "graph_accuracy_epochs.png")


def plot_loss_epochs(log: dict[str, list[float]]) -> Path:
    epochs = np.arange(1, len(log["loss"]) + 1)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(epochs, log["loss"], color=COLORS["train"], marker="o", lw=2.2, ms=7, label="Train loss")
    ax.plot(epochs, log["val_loss"], color=COLORS["val"], marker="s", lw=2.2, ms=7, label="Validation loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Binary cross-entropy loss")
    ax.set_title("Training & Validation Loss Over Epochs", fontweight="bold", pad=12)
    ax.set_xticks(epochs)
    ax.grid(True, alpha=0.35, color=COLORS["grid"])
    ax.legend(loc="upper right", framealpha=0.95)
    return save(fig, "graph_loss_epochs.png")


def plot_accuracy_loss_combined(log: dict[str, list[float]]) -> Path:
    epochs = np.arange(1, len(log["accuracy"]) + 1)
    lo = min(min(log["accuracy"]), min(log["val_accuracy"]))
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(epochs, log["accuracy"], color=COLORS["train"], marker="o", lw=2, label="Train")
    axes[0].plot(epochs, log["val_accuracy"], color=COLORS["val"], marker="s", lw=2, label="Val")
    axes[0].set_ylim(max(0.97, lo - 0.01), 1.001)
    axes[0].set_title("Accuracy", fontweight="bold")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Accuracy")
    axes[0].grid(True, alpha=0.35)
    axes[0].legend()
    axes[1].plot(epochs, log["loss"], color=COLORS["train"], marker="o", lw=2, label="Train")
    axes[1].plot(epochs, log["val_loss"], color=COLORS["val"], marker="s", lw=2, label="Val")
    axes[1].set_title("Loss", fontweight="bold")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Loss")
    axes[1].grid(True, alpha=0.35)
    axes[1].legend()
    fig.suptitle("Plastic-Pulse Week 3 — Model Learning Curves", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return save(fig, "graph_accuracy_loss_combined.png")


def plot_test_metrics_bar(results: dict) -> Path:
    m = results["test_metrics"]
    labels = ["Accuracy", "Precision", "Recall", "F1", "AUC"]
    values = [m["accuracy"], m["precision"], m["recall"], m["f1"], m["auc"]]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.bar(labels, values, color=[COLORS["test"], "#0d9488", "#14b8a6", "#2dd4bf", "#5eead4"], edgecolor="#0f766e", linewidth=1.2)
    ax.set_ylim(0.97, 1.005)
    ax.set_ylabel("Score")
    ax.set_title("Held-Out Test Set — Overall Metrics", fontweight="bold", pad=12)
    ax.grid(True, axis="y", alpha=0.35)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0008,
                f"{val:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.text(0.02, 0.02, f"n = {m['n_samples']:,} images (unseen test split)",
            transform=ax.transAxes, fontsize=9, color="#64748b")
    return save(fig, "graph_test_metrics.png")


def plot_per_class_metrics(results: dict) -> Path:
    cm = np.array(results["test_metrics"]["confusion_matrix"]["matrix"])
    # rows=true marine, plastic; cols=pred marine, plastic
    marine_prec = cm[0, 0] / cm[:, 0].sum()
    marine_rec = cm[0, 0] / cm[0, :].sum()
    plastic_prec = cm[1, 1] / cm[:, 1].sum()
    plastic_rec = cm[1, 1] / cm[1, :].sum()

    metrics = ["Precision", "Recall"]
    marine_vals = [marine_prec, marine_rec]
    plastic_vals = [plastic_prec, plastic_rec]
    x = np.arange(len(metrics))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.bar(x - width / 2, marine_vals, width, label="marine_life", color=COLORS["marine"], edgecolor="#0369a1")
    ax.bar(x + width / 2, plastic_vals, width, label="plastic_debris", color=COLORS["plastic"], edgecolor="#b91c1c")
    ax.set_ylim(0.97, 1.005)
    ax.set_xticks(x, metrics)
    ax.set_ylabel("Score")
    ax.set_title("Per-Class Precision & Recall (Test Set)", fontweight="bold", pad=12)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.35)
    for i, (mv, pv) in enumerate(zip(marine_vals, plastic_vals)):
        ax.text(i - width / 2, mv + 0.0008, f"{mv:.3f}", ha="center", fontsize=9, fontweight="bold")
        ax.text(i + width / 2, pv + 0.0008, f"{pv:.3f}", ha="center", fontsize=9, fontweight="bold")
    return save(fig, "graph_per_class_metrics.png")


def plot_confusion_enhanced(results: dict) -> Path:
    cm = np.array(results["test_metrics"]["confusion_matrix"]["matrix"])
    labels = results["test_metrics"]["confusion_matrix"]["labels"]
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], labels, rotation=15, ha="right")
    ax.set_yticks([0, 1], labels)
    ax.set_xlabel("Predicted label", fontweight="bold")
    ax.set_ylabel("True label", fontweight="bold")
    ax.set_title("Test Confusion Matrix", fontweight="bold", pad=12)
    total = cm.sum()
    for i in range(2):
        for j in range(2):
            count = int(cm[i, j])
            pct = 100 * count / total
            color = "white" if count > cm.max() * 0.5 else "#0f172a"
            ax.text(j, i, f"{count}\n({pct:.1f}%)", ha="center", va="center",
                    color=color, fontsize=12, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046)
    return save(fig, "graph_confusion_matrix.png")


def plot_experiment_comparison(summary: dict) -> Path:
    # Fair comparison: full-aug experiments only
    fair = [e for e in summary["experiments"] if e.get("aug_mode") == "all"]
    fair = sorted(fair, key=lambda e: e["test_accuracy"], reverse=True)
    names = [e["name"] for e in fair]
    accs = [e["test_accuracy"] for e in fair]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = [COLORS["test"] if n == "dropout_0.5" else "#94a3b8" for n in names]
    bars = ax.barh(names[::-1], accs[::-1], color=colors[::-1], edgecolor="#475569")
    ax.set_xlim(0.991, 0.996)
    ax.set_xlabel("Test accuracy")
    ax.set_title("Hyperparameter Experiments — Test Accuracy (full augmentation)", fontweight="bold", pad=12)
    ax.grid(True, axis="x", alpha=0.35)
    for bar, val in zip(bars, accs[::-1]):
        ax.text(val + 0.00015, bar.get_y() + bar.get_height() / 2, f"{val:.4f}",
                va="center", fontsize=9, fontweight="bold")
    return save(fig, "graph_experiment_accuracy.png")


def plot_summary_dashboard(results: dict, log: dict[str, list[float]]) -> Path:
    m = results["test_metrics"]
    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.28)

    ax1 = fig.add_subplot(gs[0, 0])
    epochs = np.arange(1, len(log["accuracy"]) + 1)
    ax1.plot(epochs, log["accuracy"], color=COLORS["train"], marker="o", label="Train")
    ax1.plot(epochs, log["val_accuracy"], color=COLORS["val"], marker="s", label="Val")
    lo = min(min(log["accuracy"]), min(log["val_accuracy"]))
    ax1.set_ylim(max(0.97, lo - 0.01), 1.001)
    ax1.set_title("Accuracy curves", fontweight="bold")
    ax1.set_xlabel("Epoch")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2 = fig.add_subplot(gs[0, 1])
    labels = ["Acc", "Prec", "Rec", "F1", "AUC"]
    vals = [m["accuracy"], m["precision"], m["recall"], m["f1"], m["auc"]]
    ax2.bar(labels, vals, color=COLORS["test"], alpha=0.85, edgecolor="#047857")
    ax2.set_ylim(0.97, 1.005)
    ax2.set_title("Test metrics", fontweight="bold")
    ax2.grid(True, axis="y", alpha=0.3)

    ax3 = fig.add_subplot(gs[1, 0])
    cm = np.array(m["confusion_matrix"]["matrix"])
    im = ax3.imshow(cm, cmap="Blues")
    cls = m["confusion_matrix"]["labels"]
    ax3.set_xticks([0, 1], cls, rotation=12, ha="right")
    ax3.set_yticks([0, 1], cls)
    ax3.set_title("Confusion matrix", fontweight="bold")
    for i in range(2):
        for j in range(2):
            ax3.text(j, i, int(cm[i, j]), ha="center", va="center", color="white", fontweight="bold")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")
    fit = results["fit_diagnosis"]
    text = (
        f"Plastic-Pulse Ocean Tracker\n"
        f"Frozen MobileNetV2 + Dense head\n\n"
        f"Test accuracy:  {m['accuracy']:.2%}\n"
        f"Test AUC:       {m['auc']:.4f}\n"
        f"Train−val gap:  {fit['train_val_acc_gap']:+.4f}\n"
        f"Fit diagnosis:  {fit['status']}\n"
        f"Errors:         {int(cm.sum() - np.trace(cm))} / {int(cm.sum())}\n"
        f"Best val epoch: {fit['best_epoch']}"
    )
    ax4.text(0.05, 0.95, text, va="top", fontsize=12, family="monospace",
             bbox=dict(boxstyle="round", facecolor="#f0fdf4", edgecolor="#86efac"))

    fig.suptitle("Plastic-Pulse — Algorithm Performance Summary", fontsize=15, fontweight="bold", y=1.01)
    path = OUT / "graph_summary_dashboard.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main() -> None:
    log = load_training_log()
    results = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    summary = json.loads(EXPERIMENT_JSON.read_text(encoding="utf-8"))

    paths = [
        plot_accuracy_epochs(log),
        plot_loss_epochs(log),
        plot_accuracy_loss_combined(log),
        plot_test_metrics_bar(results),
        plot_per_class_metrics(results),
        plot_confusion_enhanced(results),
        plot_experiment_comparison(summary),
        plot_summary_dashboard(results, log),
    ]
    print("Presentation graphs saved:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()
