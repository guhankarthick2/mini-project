"""
Week 2 — Build, compile, and inspect the transfer-learning classifier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.classifier import IMG_SIZE, build_classifier, compile_model, inspect_model

OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "week2"
MODELS_DIR = PROJECT_ROOT / "models" / "saved"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Plastic-Pulse transfer learning classifier")
    parser.add_argument("--backbone", choices=["mobilenetv2", "resnet50"], default="mobilenetv2")
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--dense-units", type=int, default=128)
    parser.add_argument("--save", action="store_true", help="Save compiled untrained model")
    args = parser.parse_args()

    print("Plastic-Pulse Ocean Tracker - Week 2 Model Build")
    print(f"TensorFlow     : {tf.__version__}")
    print(f"Backbone       : {args.backbone} (ImageNet, frozen feature extractor)")
    print(f"Head           : GAP -> Dense({args.dense_units}) -> sigmoid binary")
    print("Classes        : marine_life (0) vs plastic_debris (1)\n")

    model = build_classifier(
        backbone=args.backbone,
        dropout=args.dropout,
        dense_units=args.dense_units,
    )
    compile_model(model, learning_rate=args.learning_rate)
    arch = inspect_model(model, OUTPUTS_DIR)

    if args.save:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        out = MODELS_DIR / f"{model.name}.keras"
        model.save(out)
        print(f"Saved compiled model: {out}")

    probe = tf.random.uniform((2, *IMG_SIZE, 3), minval=0, maxval=255)
    preds = model(probe, training=False)
    print(f"\nSanity check batch predictions shape: {tuple(preds.shape)}  (expect (2, 1))")
    print(f"Sample probabilities: {[round(float(x), 4) for x in preds.numpy().reshape(-1)]}")

    meta_path = OUTPUTS_DIR / "week2_model_build.json"
    meta_path.write_text(
        json.dumps({"status": "compiled_and_inspected", "backbone": args.backbone, "architecture": arch}, indent=2),
        encoding="utf-8",
    )
    print(f"\nWeek 2 model deliverable written to: {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
