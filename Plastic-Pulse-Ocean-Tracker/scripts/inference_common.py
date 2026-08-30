"""Shared model loading and prediction helpers for Plastic-Pulse inference."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from models.classifier import CLASS_NAMES, IMG_SIZE
from train_model import assemble_full_model, collect_groups, paths_for_split, stratified_group_split

DEFAULT_MODEL = PROJECT_ROOT / "models" / "saved" / "PlasticPulse_mobilenetv2_trained.keras"
DEFAULT_HEAD = PROJECT_ROOT / "models" / "saved" / "PlasticPulse_mobilenetv2_head.keras"
AUGMENTED_DIR = PROJECT_ROOT / "data" / "augmented"

LABEL_DISPLAY = {
    "marine_life": "Marine Life",
    "plastic_debris": "Plastic Debris",
}


def load_inference_model(
    model_path: Path = DEFAULT_MODEL,
    head_path: Path = DEFAULT_HEAD,
) -> tf.keras.Model:
    try:
        return tf.keras.models.load_model(model_path)
    except Exception as exc:
        if not head_path.is_file():
            raise FileNotFoundError(
                f"Head model missing: {head_path}\n"
                "Run: python scripts/train_model.py --epochs 30 --batch-size 64 --dropout 0.2"
            ) from exc
        head = tf.keras.models.load_model(head_path)
        return assemble_full_model("mobilenetv2", head)


def preprocess_rgb_uint8(rgb: np.ndarray) -> np.ndarray:
    """Resize to model input; keep uint8 RGB (preprocess runs inside the model)."""
    if rgb.dtype != np.uint8:
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    pil = Image.fromarray(rgb)
    pil = pil.resize(IMG_SIZE, Image.Resampling.BILINEAR)
    return np.array(pil, dtype=np.uint8)


def predict_rgb(model: tf.keras.Model, rgb_uint8: np.ndarray) -> dict:
    batch = preprocess_rgb_uint8(rgb_uint8)[None, ...]
    prob_plastic = float(model.predict(batch, verbose=0)[0, 0])
    label_idx = 1 if prob_plastic >= 0.5 else 0
    label = CLASS_NAMES[label_idx]
    confidence = prob_plastic if label_idx == 1 else 1.0 - prob_plastic
    return {
        "label": label,
        "label_display": LABEL_DISPLAY[label],
        "prob_plastic": prob_plastic,
        "confidence": confidence,
        "label_idx": label_idx,
    }


def test_split_orig_samples(seed: int = 42, per_class: int = 4) -> list[Path]:
    """Original (__orig) images from the held-out test split only."""
    groups = collect_groups(AUGMENTED_DIR)
    splits = stratified_group_split(groups, 0.70, 0.15, seed)
    files, _labels = paths_for_split(groups, splits["test"])
    orig_paths = [Path(p) for p in files if p.endswith("__orig.jpg")]
    by_class: dict[str, list[Path]] = {c: [] for c in CLASS_NAMES}
    for path in orig_paths:
        by_class[path.parent.name].append(path)
    picked: list[Path] = []
    for cls in CLASS_NAMES:
        picked.extend(sorted(by_class[cls])[:per_class])
    return picked
