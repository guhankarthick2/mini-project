"""
Transfer-learning classifier for Plastic-Pulse Ocean Tracker.

Frozen ImageNet backbone (MobileNetV2 or ResNet50) as a feature extractor +
custom binary head: Marine Life (0) vs Plastic Debris (1).
"""

from __future__ import annotations

import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import Model, layers
from tensorflow.keras.applications import MobileNetV2, ResNet50
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.utils import plot_model

CLASS_NAMES = ("marine_life", "plastic_debris")
IMG_SIZE = (224, 224)


def build_feature_extractor(backbone: str, input_shape: tuple[int, int, int]):
    backbone = backbone.lower()
    if backbone == "mobilenetv2":
        base = MobileNetV2(
            include_top=False,
            weights="imagenet",
            input_shape=input_shape,
        )
        preprocess = mobilenet_preprocess
    elif backbone == "resnet50":
        base = ResNet50(
            include_top=False,
            weights="imagenet",
            input_shape=input_shape,
        )
        preprocess = resnet_preprocess
    else:
        raise ValueError(f"Unsupported backbone '{backbone}'. Use mobilenetv2 or resnet50.")

    base.trainable = False
    for layer in base.layers:
        layer.trainable = False
    return base, preprocess


def build_classifier(
    backbone: str = "mobilenetv2",
    img_size: tuple[int, int] = IMG_SIZE,
    dropout: float = 0.3,
    dense_units: int = 128,
) -> Model:
    """Frozen pretrained CNN + custom sigmoid head for binary classification."""
    input_shape = (img_size[0], img_size[1], 3)
    base, preprocess = build_feature_extractor(backbone, input_shape)

    inputs = layers.Input(shape=input_shape, name="image")
    x = layers.Lambda(preprocess, name=f"{backbone}_preprocess")(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D(name="gap_features")(x)
    x = layers.Dropout(dropout, name="dropout_1")(x)
    x = layers.Dense(dense_units, activation="relu", name="dense_features")(x)
    x = layers.Dropout(dropout, name="dropout_2")(x)
    outputs = layers.Dense(1, activation="sigmoid", name="plastic_probability")(x)

    return Model(inputs=inputs, outputs=outputs, name=f"PlasticPulse_{backbone}_classifier")


def compile_model(model: Model, learning_rate: float = 1e-3) -> Model:
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
        ],
    )
    return model


def inspect_model(model: Model, outputs_dir: Path) -> dict:
    outputs_dir.mkdir(parents=True, exist_ok=True)

    summary_lines: list[str] = []
    model.summary(print_fn=summary_lines.append)
    summary_text = "\n".join(summary_lines)
    print(summary_text)

    summary_path = outputs_dir / f"{model.name}_summary.txt"
    summary_path.write_text(summary_text, encoding="utf-8")

    trainable = int(sum(tf.keras.backend.count_params(w) for w in model.trainable_weights))
    non_trainable = int(sum(tf.keras.backend.count_params(w) for w in model.non_trainable_weights))
    total = trainable + non_trainable

    arch = {
        "model_name": model.name,
        "task": "binary_classification",
        "classes": list(CLASS_NAMES),
        "label_mapping": {"0": "marine_life", "1": "plastic_debris"},
        "feature_extractor": "frozen ImageNet-pretrained backbone",
        "custom_head": [
            "GlobalAveragePooling2D",
            "Dropout",
            "Dense(relu)",
            "Dropout",
            "Dense(1, sigmoid)",
        ],
        "optimizer": "Adam",
        "loss": "binary_crossentropy",
        "metrics": ["accuracy", "precision", "recall", "auc"],
        "input_shape": list(model.input_shape[1:]),
        "params": {
            "total": total,
            "trainable": trainable,
            "non_trainable": non_trainable,
        },
        "layers": [
            {
                "name": layer.name,
                "type": layer.__class__.__name__,
                "trainable": bool(layer.trainable),
            }
            for layer in model.layers
        ],
    }

    json_path = outputs_dir / f"{model.name}_architecture.json"
    json_path.write_text(json.dumps(arch, indent=2), encoding="utf-8")

    plot_path = outputs_dir / f"{model.name}_plot.png"
    try:
        plot_model(
            model,
            to_file=str(plot_path),
            show_shapes=True,
            show_layer_names=True,
            expand_nested=False,
            dpi=120,
        )
        arch["plot"] = str(plot_path)
        print(f"Architecture plot saved: {plot_path}")
    except Exception as exc:  # noqa: BLE001
        arch["plot"] = None
        arch["plot_error"] = str(exc)
        print(f"Architecture plot skipped ({exc})")

    print("\nParameter summary")
    print(f"  Total         : {total:,}")
    print(f"  Trainable     : {trainable:,}  (custom head)")
    print(f"  Non-trainable : {non_trainable:,}  (frozen feature extractor)")
    print(f"  Summary file  : {summary_path}")
    print(f"  JSON file     : {json_path}")
    return arch
