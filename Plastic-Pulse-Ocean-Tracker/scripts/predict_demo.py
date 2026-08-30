"""
Week 4 — Live inference demo for recording / presentation.

Loads the trained Plastic-Pulse model and classifies sample images with
confidence scores. Optionally saves a labeled grid PNG for slides/video.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from models.classifier import CLASS_NAMES, IMG_SIZE
from train_model import assemble_full_model

AUGMENTED_DIR = PROJECT_ROOT / "data" / "augmented"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "saved" / "PlasticPulse_mobilenetv2_trained.keras"
DEFAULT_HEAD = PROJECT_ROOT / "models" / "saved" / "PlasticPulse_mobilenetv2_head.keras"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "week4"


def default_samples() -> list[Path]:
    """A few clear marine vs plastic examples for demo recording."""
    picks = [
        AUGMENTED_DIR / "marine_life" / "marine_life_00500__orig.jpg",
        AUGMENTED_DIR / "marine_life" / "marine_life_01200__hflip.jpg",
        AUGMENTED_DIR / "marine_life" / "marine_life_02000__rot15.jpg",
        AUGMENTED_DIR / "plastic_debris" / "plastic_debris_00500__orig.jpg",
        AUGMENTED_DIR / "plastic_debris" / "plastic_debris_01200__vflip.jpg",
        AUGMENTED_DIR / "plastic_debris" / "plastic_debris_02000__rot_neg15.jpg",
    ]
    found = [p for p in picks if p.is_file()]
    if len(found) >= 4:
        return found
    # Fallback: first orig per class + a few more
    fallback: list[Path] = []
    for cls in CLASS_NAMES:
        folder = AUGMENTED_DIR / cls
        orig = sorted(folder.glob("*__orig.jpg"))
        if orig:
            fallback.append(orig[min(500, len(orig) - 1)])
        others = [p for p in sorted(folder.glob("*.jpg")) if p not in fallback][:2]
        fallback.extend(others)
    return fallback[:6]


def load_inference_model(model_path: Path, head_path: Path = DEFAULT_HEAD) -> tf.keras.Model:
    """Load the trained network. Keras Lambda preprocess often fails to deserialize
    from the full .keras file, so rebuild from the saved head when needed."""
    try:
        return tf.keras.models.load_model(model_path)
    except Exception as exc:
        print(f"Could not load {model_path.name} ({type(exc).__name__}).")
        print(f"Rebuilding from head weights: {head_path}")
        if not head_path.is_file():
            raise FileNotFoundError(
                f"Head model missing: {head_path}\n"
                "Run: python scripts/train_model.py --epochs 20 --batch-size 64 --dropout 0.5"
            ) from exc
        head = tf.keras.models.load_model(head_path)
        return assemble_full_model("mobilenetv2", head)


def load_image_tensor(path: Path) -> np.ndarray:
    arr = np.array(Image.open(path).convert("RGB"), dtype=np.float32)
    arr = tf.image.resize(arr, IMG_SIZE).numpy()
    return arr


def predict_one(model: tf.keras.Model, path: Path) -> dict:
    batch = load_image_tensor(path)[None, ...]
    prob_plastic = float(model.predict(batch, verbose=0)[0, 0])
    label_idx = 1 if prob_plastic >= 0.5 else 0
    label = CLASS_NAMES[label_idx]
    confidence = prob_plastic if label_idx == 1 else 1.0 - prob_plastic
    true_cls = path.parent.name
    correct = true_cls == label
    return {
        "path": path,
        "label": label,
        "prob_plastic": prob_plastic,
        "confidence": confidence,
        "true_class": true_cls,
        "correct": correct,
    }


def print_results(results: list[dict]) -> None:
    print("\nPlastic-Pulse Ocean Tracker — live predictions")
    print("Labels: 0 = marine_life · 1 = plastic_debris\n")
    for r in results:
        mark = "OK" if r["correct"] else "MISS"
        print(f"[{mark}] {r['path'].name}")
        print(f"     true folder : {r['true_class']}")
        print(f"     prediction  : {r['label']}")
        print(f"     confidence  : {r['confidence']:.1%}")
        print(f"     plastic prob: {r['prob_plastic']:.3f}\n")
    acc = sum(r["correct"] for r in results) / len(results)
    print(f"Demo batch accuracy: {acc:.0%} ({sum(r['correct'] for r in results)}/{len(results)})\n")


def save_grid(results: list[dict], out_path: Path) -> None:
    n = len(results)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes = np.atleast_1d(axes).reshape(rows, cols)

    for ax, r in zip(axes.flat, results):
        img = Image.open(r["path"])
        ax.imshow(img)
        ax.axis("off")
        color = "#34d399" if r["correct"] else "#f87171"
        title = (
            f"{r['label'].replace('_', ' ')}\n"
            f"{r['confidence']:.1%} confident"
        )
        ax.set_title(title, fontsize=10, color=color, fontweight="bold")

    for ax in axes.flat[len(results) :]:
        ax.axis("off")

    fig.suptitle("Plastic-Pulse — Marine Life vs Plastic Debris", fontsize=13, fontweight="bold")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved demo grid: {out_path}")


def show_grid(results: list[dict]) -> None:
    n = len(results)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes = np.atleast_1d(axes).reshape(rows, cols)

    for ax, r in zip(axes.flat, results):
        ax.imshow(Image.open(r["path"]))
        ax.axis("off")
        color = "#047857" if r["correct"] else "#b91c1c"
        ax.set_title(
            f"{r['label'].replace('_', ' ')}\n{r['confidence']:.1%}",
            fontsize=11,
            color=color,
            fontweight="bold",
        )

    for ax in axes.flat[len(results) :]:
        ax.axis("off")

    fig.suptitle("Plastic-Pulse live demo", fontsize=14, fontweight="bold")
    fig.tight_layout()
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Live inference demo for Plastic-Pulse")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--images", nargs="*", type=Path, help="Optional image paths")
    parser.add_argument("--show", action="store_true", help="Open matplotlib window (best for recording)")
    parser.add_argument("--save", type=Path, default=OUTPUTS_DIR / "demo_predictions.png")
    parser.add_argument("--no-save", action="store_true")
    args = parser.parse_args()

    if not args.model.is_file():
        raise FileNotFoundError(
            f"Trained model not found: {args.model}\n"
            "Run: python scripts/train_model.py --epochs 20 --batch-size 64 --dropout 0.5"
        )

    paths = args.images if args.images else default_samples()
    paths = [p for p in paths if p.is_file()]
    if not paths:
        raise FileNotFoundError(f"No demo images found under {AUGMENTED_DIR}")

    print(f"Loading model: {args.model}")
    model = load_inference_model(args.model)
    print(f"Classifying {len(paths)} image(s)...")

    results = [predict_one(model, p) for p in paths]
    print_results(results)

    if not args.no_save:
        save_grid(results, args.save)
    if args.show:
        show_grid(results)


if __name__ == "__main__":
    main()
