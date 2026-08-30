"""
Week 3 — Train, monitor, plot, and evaluate Plastic-Pulse classifier.

- Stratified stem-level split so all 6 augmentations of one source image
  stay in the same split (no train/test leakage).
- Frozen MobileNetV2 feature extractor (Week 2 architecture).
- Features are cached once, then the custom head is trained (equivalent to
  end-to-end fit with a frozen backbone; much faster on CPU).
- Plots train/val accuracy & loss; evaluates on held-out test set;
  reports overfitting / underfitting diagnosis.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from tensorflow.keras import Model, layers

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.classifier import CLASS_NAMES, IMG_SIZE, build_classifier, compile_model

AUGMENTED_DIR = PROJECT_ROOT / "data" / "augmented"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "week3"
MODELS_DIR = PROJECT_ROOT / "models" / "saved"
CACHE_DIR = PROJECT_ROOT / "data" / "feature_cache"


def stem_key(path: Path) -> str:
    """marine_life_00000__hflip.jpg -> marine_life_00000"""
    return path.stem.rsplit("__", 1)[0]


def collect_groups(data_dir: Path) -> dict[str, dict]:
    """Group files by class + source stem so augmentations stay together."""
    groups: dict[str, dict] = {}
    for label, class_name in enumerate(CLASS_NAMES):
        class_dir = data_dir / class_name
        if not class_dir.is_dir():
            raise FileNotFoundError(f"Missing class folder: {class_dir}")
        by_stem: dict[str, list[Path]] = defaultdict(list)
        for path in sorted(class_dir.glob("*.jpg")):
            by_stem[stem_key(path)].append(path)
        for stem, paths in by_stem.items():
            gid = f"{class_name}/{stem}"
            groups[gid] = {
                "class_name": class_name,
                "label": label,
                "stem": stem,
                "paths": paths,
            }
    return groups


def stratified_group_split(
    groups: dict[str, dict],
    train_ratio: float,
    val_ratio: float,
    seed: int,
) -> dict[str, list[str]]:
    rng = random.Random(seed)
    by_label: dict[int, list[str]] = defaultdict(list)
    for gid, meta in groups.items():
        by_label[meta["label"]].append(gid)

    splits = {"train": [], "val": [], "test": []}
    for label, gids in sorted(by_label.items()):
        rng.shuffle(gids)
        n = len(gids)
        n_train = int(round(n * train_ratio))
        n_val = int(round(n * val_ratio))
        # Keep at least 1 in val/test when class has enough groups
        if n >= 10:
            n_train = min(max(n_train, 1), n - 2)
            n_val = min(max(n_val, 1), n - n_train - 1)
        n_test = n - n_train - n_val
        splits["train"].extend(gids[:n_train])
        splits["val"].extend(gids[n_train : n_train + n_val])
        splits["test"].extend(gids[n_train + n_val :])
        print(
            f"  class {CLASS_NAMES[label]}: "
            f"{n} stems -> train={n_train} val={n_val} test={n_test}"
        )
    return splits


def paths_for_split(groups: dict[str, dict], gids: list[str]) -> tuple[list[str], list[int]]:
    files: list[str] = []
    labels: list[int] = []
    for gid in gids:
        meta = groups[gid]
        for path in meta["paths"]:
            files.append(str(path))
            labels.append(meta["label"])
    return files, labels


def load_rgb(path: tf.Tensor) -> tf.Tensor:
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, IMG_SIZE)
    return tf.cast(image, tf.float32)


def make_image_dataset(
    files: list[str],
    labels: list[int],
    batch_size: int,
    shuffle: bool,
    seed: int,
) -> tf.data.Dataset:
    ds = tf.data.Dataset.from_tensor_slices((files, np.array(labels, dtype=np.float32)))
    if shuffle:
        ds = ds.shuffle(buffer_size=min(len(files), 4096), seed=seed, reshuffle_each_iteration=True)

    def _map(path, label):
        return load_rgb(path), label

    return (
        ds.map(_map, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )


def build_feature_model(backbone: str = "mobilenetv2") -> Model:
    """Frozen backbone + GAP — outputs 1280-D feature vectors."""
    full = build_classifier(backbone=backbone)
    # image -> ... -> gap_features
    return Model(inputs=full.input, outputs=full.get_layer("gap_features").output, name="feature_extractor")


def build_head_model(dropout: float = 0.3, dense_units: int = 128, feature_dim: int = 1280) -> Model:
    inputs = layers.Input(shape=(feature_dim,), name="features")
    x = layers.Dropout(dropout, name="dropout_1")(inputs)
    x = layers.Dense(dense_units, activation="relu", name="dense_features")(x)
    x = layers.Dropout(dropout, name="dropout_2")(x)
    outputs = layers.Dense(1, activation="sigmoid", name="plastic_probability")(x)
    return Model(inputs=inputs, outputs=outputs, name="PlasticPulse_head")


def cache_features(
    feature_model: Model,
    files: list[str],
    labels: list[int],
    cache_path: Path,
    batch_size: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    if cache_path.exists():
        data = np.load(cache_path)
        print(f"  loaded cache {cache_path.name}: {data['X'].shape}")
        return data["X"], data["y"]

    print(f"  extracting features -> {cache_path.name} ({len(files)} images)...")
    ds = make_image_dataset(files, labels, batch_size=batch_size, shuffle=False, seed=seed)
    feats = feature_model.predict(ds, verbose=1)
    y = np.array(labels, dtype=np.float32)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_path, X=feats.astype(np.float32), y=y)
    print(f"  saved {cache_path} ({feats.shape})")
    return feats.astype(np.float32), y


def plot_history(history: dict, out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    epochs = range(1, len(history["loss"]) + 1)
    paths: dict[str, str] = {}

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(epochs, history["accuracy"], marker="o", label="Train accuracy")
    ax.plot(epochs, history["val_accuracy"], marker="o", label="Val accuracy")
    ax.set_title("Training & Validation Accuracy")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    lo = min(min(history["accuracy"]), min(history["val_accuracy"]))
    if lo >= 0.9:
        ax.set_ylim(max(0.9, lo - 0.02), 1.002)
    else:
        ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    acc_path = out_dir / "accuracy_curve.png"
    fig.savefig(acc_path, dpi=140)
    plt.close(fig)
    paths["accuracy"] = str(acc_path)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(epochs, history["loss"], marker="o", label="Train loss")
    ax.plot(epochs, history["val_loss"], marker="o", label="Val loss")
    ax.set_title("Training & Validation Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Binary cross-entropy")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    loss_path = out_dir / "loss_curve.png"
    fig.savefig(loss_path, dpi=140)
    plt.close(fig)
    paths["loss"] = str(loss_path)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(epochs, history["accuracy"], marker="o", label="Train")
    axes[0].plot(epochs, history["val_accuracy"], marker="o", label="Val")
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Epoch")
    lo = min(min(history["accuracy"]), min(history["val_accuracy"]))
    if lo >= 0.9:
        axes[0].set_ylim(max(0.9, lo - 0.02), 1.002)
    else:
        axes[0].set_ylim(0, 1.05)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[1].plot(epochs, history["loss"], marker="o", label="Train")
    axes[1].plot(epochs, history["val_loss"], marker="o", label="Val")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Epoch")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    fig.suptitle("Plastic-Pulse Week 3 — Training Curves", fontsize=12)
    fig.tight_layout()
    both = out_dir / "train_val_curves.png"
    fig.savefig(both, dpi=140)
    plt.close(fig)
    paths["combined"] = str(both)
    return paths


def plot_confusion(cm: np.ndarray, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], list(CLASS_NAMES), rotation=20, ha="right")
    ax.set_yticks([0, 1], list(CLASS_NAMES))
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Test Confusion Matrix")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="black", fontsize=14)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def diagnose_fit(history: dict, test_metrics: dict) -> dict:
    """Heuristic overfitting / underfitting check from curves + test metrics."""
    train_acc = float(history["accuracy"][-1])
    val_acc = float(history["val_accuracy"][-1])
    train_loss = float(history["loss"][-1])
    val_loss = float(history["val_loss"][-1])
    best_val_acc = float(max(history["val_accuracy"]))
    best_epoch = int(np.argmax(history["val_accuracy"])) + 1
    gap = train_acc - val_acc
    test_acc = float(test_metrics["accuracy"])

    if train_acc < 0.70 and val_acc < 0.70:
        status = "underfitting"
        rationale = (
            f"Both train ({train_acc:.3f}) and val ({val_acc:.3f}) accuracy stay low — "
            "the head is not capturing the task well enough yet."
        )
    elif gap > 0.08 and val_loss > train_loss * 1.25:
        status = "overfitting"
        rationale = (
            f"Train accuracy ({train_acc:.3f}) is clearly above val ({val_acc:.3f}); "
            f"val loss ({val_loss:.3f}) exceeds train loss ({train_loss:.3f})."
        )
    elif abs(train_acc - val_acc) <= 0.05 and test_acc >= 0.85 and val_acc >= 0.85:
        status = "good_fit"
        rationale = (
            f"Train/val gap is small ({gap:+.3f}), val accuracy {val_acc:.3f}, "
            f"test accuracy {test_acc:.3f} — generalization looks healthy."
        )
    elif gap > 0.05:
        status = "mild_overfitting"
        rationale = (
            f"Moderate train/val gap ({gap:+.3f}). Still usable, but watch for further divergence."
        )
    else:
        status = "acceptable_fit"
        rationale = (
            f"Train {train_acc:.3f} / val {val_acc:.3f} / test {test_acc:.3f}. "
            "No strong under- or overfitting signal."
        )

    return {
        "status": status,
        "rationale": rationale,
        "train_accuracy_final": train_acc,
        "val_accuracy_final": val_acc,
        "train_loss_final": train_loss,
        "val_loss_final": val_loss,
        "best_val_accuracy": best_val_acc,
        "best_epoch": best_epoch,
        "train_val_acc_gap": gap,
        "test_accuracy": test_acc,
    }


def assemble_full_model(backbone: str, head: Model) -> Model:
    """Wire frozen backbone + trained head into one inference model."""
    base = build_classifier(backbone=backbone)
    # Copy head weights into the matching layers of the full classifier
    for name in ("dropout_1", "dense_features", "dropout_2", "plastic_probability"):
        base.get_layer(name).set_weights(head.get_layer(name).get_weights())
    return compile_model(base)


def main() -> None:
    parser = argparse.ArgumentParser(description="Week 3: train + evaluate Plastic-Pulse classifier")
    parser.add_argument("--backbone", default="mobilenetv2", choices=["mobilenetv2", "resnet50"])
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--dropout", type=float, default=0.5)
    parser.add_argument("--dense-units", type=int, default=128)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit-stems", type=int, default=0, help="Debug: max stems per class (0=all)")
    parser.add_argument("--refresh-cache", action="store_true")
    args = parser.parse_args()

    tf.keras.utils.set_random_seed(args.seed)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("Plastic-Pulse Ocean Tracker — Week 3 Train / Evaluate")
    print(f"TensorFlow : {tf.__version__}")
    print(f"Data       : {AUGMENTED_DIR}")
    print(f"Backbone   : {args.backbone} (frozen); train custom head only\n")

    groups = collect_groups(AUGMENTED_DIR)
    if args.limit_stems > 0:
        trimmed: dict[str, dict] = {}
        counts = {0: 0, 1: 0}
        for gid, meta in sorted(groups.items()):
            label = meta["label"]
            if counts[label] >= args.limit_stems:
                continue
            trimmed[gid] = meta
            counts[label] += 1
        groups = trimmed
        print(f"Limited to {args.limit_stems} stems/class -> {len(groups)} groups")

    print("Stem-level stratified split (augmentations stay together):")
    splits = stratified_group_split(groups, args.train_ratio, args.val_ratio, args.seed)

    split_files: dict[str, tuple[list[str], list[int]]] = {}
    for name, gids in splits.items():
        files, labels = paths_for_split(groups, gids)
        split_files[name] = (files, labels)
        print(f"  {name:5s}: {len(gids):4d} stems, {len(files):5d} images")

    feature_model = build_feature_model(args.backbone)
    feature_model.trainable = False

    cache_tag = f"{args.backbone}_s{args.seed}"
    if args.limit_stems:
        cache_tag += f"_lim{args.limit_stems}"
    if args.refresh_cache:
        for p in CACHE_DIR.glob(f"{cache_tag}_*.npz"):
            p.unlink()

    features = {}
    for name in ("train", "val", "test"):
        files, labels = split_files[name]
        cache_path = CACHE_DIR / f"{cache_tag}_{name}.npz"
        features[name] = cache_features(
            feature_model, files, labels, cache_path, args.batch_size, args.seed
        )

    X_train, y_train = features["train"]
    X_val, y_val = features["val"]
    X_test, y_test = features["test"]
    feature_dim = int(X_train.shape[1])

    head = build_head_model(dropout=args.dropout, dense_units=args.dense_units, feature_dim=feature_dim)
    head.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
        ],
    )
    head.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=4,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
        tf.keras.callbacks.CSVLogger(str(OUTPUTS_DIR / "training_log.csv")),
    ]

    print("\nTraining custom head on cached features...")
    history_obj = head.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
        verbose=1,
    )
    history = {k: [float(v) for v in vals] for k, vals in history_obj.history.items()}

    plot_paths = plot_history(history, OUTPUTS_DIR)
    print("\nSaved plots:")
    for k, p in plot_paths.items():
        print(f"  {k}: {p}")

    print("\nEvaluating on unseen test set...")
    test_probs = head.predict(X_test, batch_size=args.batch_size, verbose=0).reshape(-1)
    test_preds = (test_probs >= 0.5).astype(int)
    y_true = y_test.astype(int)

    cm = confusion_matrix(y_true, test_preds)
    plot_confusion(cm, OUTPUTS_DIR / "confusion_matrix.png")

    test_metrics = {
        "accuracy": float(accuracy_score(y_true, test_preds)),
        "precision": float(precision_score(y_true, test_preds, zero_division=0)),
        "recall": float(recall_score(y_true, test_preds, zero_division=0)),
        "f1": float(f1_score(y_true, test_preds, zero_division=0)),
        "auc": float(roc_auc_score(y_true, test_probs)) if len(np.unique(y_true)) > 1 else None,
        "loss": float(
            tf.keras.losses.binary_crossentropy(
                y_test.astype(np.float32), test_probs.astype(np.float32)
            ).numpy().mean()
        ),
        "n_samples": int(len(y_true)),
        "confusion_matrix": {
            "labels": list(CLASS_NAMES),
            "matrix": cm.tolist(),
        },
        "classification_report": classification_report(
            y_true,
            test_preds,
            target_names=list(CLASS_NAMES),
            digits=4,
            zero_division=0,
        ),
        "confidence": {
            "mean_prob_plastic": float(test_probs.mean()),
            "mean_confidence_correct": float(
                np.nanmean(
                    np.where(
                        test_preds == y_true,
                        np.maximum(test_probs, 1.0 - test_probs),
                        np.nan,
                    )
                )
            ),
        },
    }
    print(test_metrics["classification_report"])
    print(
        f"Test accuracy={test_metrics['accuracy']:.4f}  "
        f"precision={test_metrics['precision']:.4f}  "
        f"recall={test_metrics['recall']:.4f}  "
        f"AUC={test_metrics['auc']}"
    )

    fit_diag = diagnose_fit(history, test_metrics)
    print(f"\nFit diagnosis: {fit_diag['status']}")
    print(f"  {fit_diag['rationale']}")

    # Save full end-to-end model with trained head weights
    full_model = assemble_full_model(args.backbone, head)
    model_path = MODELS_DIR / f"PlasticPulse_{args.backbone}_trained.keras"
    full_model.save(model_path)
    head_path = MODELS_DIR / f"PlasticPulse_{args.backbone}_head.keras"
    head.save(head_path)
    print(f"\nSaved trained model: {model_path}")
    print(f"Saved head-only model: {head_path}")

    split_summary = {
        name: {
            "stems": len(splits[name]),
            "images": len(split_files[name][0]),
            "class_balance": {
                CLASS_NAMES[0]: int(sum(1 for y in split_files[name][1] if y == 0)),
                CLASS_NAMES[1]: int(sum(1 for y in split_files[name][1] if y == 1)),
            },
        }
        for name in ("train", "val", "test")
    }

    results = {
        "project": "Plastic-Pulse Ocean Tracker",
        "week": 3,
        "backbone": args.backbone,
        "training_mode": "frozen_backbone_cached_features_then_head",
        "seed": args.seed,
        "epochs_requested": args.epochs,
        "epochs_ran": len(history["loss"]),
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "dropout": args.dropout,
        "dense_units": args.dense_units,
        "splits": split_summary,
        "history": history,
        "plots": plot_paths,
        "test_metrics": test_metrics,
        "fit_diagnosis": fit_diag,
        "artifacts": {
            "trained_model": str(model_path),
            "head_model": str(head_path),
            "confusion_matrix_plot": str(OUTPUTS_DIR / "confusion_matrix.png"),
            "training_log_csv": str(OUTPUTS_DIR / "training_log.csv"),
        },
    }
    results_path = OUTPUTS_DIR / "week3_training_results.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    report = f"""# Week 3 — Training & Evaluation Report

**Plastic-Pulse Ocean Tracker** · backbone `{args.backbone}` (frozen) + custom Dense head

## Dataset split (stem-level, no augmentation leakage)

| Split | Stems | Images | marine_life | plastic_debris |
|-------|------:|-------:|------------:|---------------:|
| Train | {split_summary['train']['stems']} | {split_summary['train']['images']} | {split_summary['train']['class_balance']['marine_life']} | {split_summary['train']['class_balance']['plastic_debris']} |
| Val   | {split_summary['val']['stems']} | {split_summary['val']['images']} | {split_summary['val']['class_balance']['marine_life']} | {split_summary['val']['class_balance']['plastic_debris']} |
| Test  | {split_summary['test']['stems']} | {split_summary['test']['images']} | {split_summary['test']['class_balance']['marine_life']} | {split_summary['test']['class_balance']['plastic_debris']} |

## Training

- Epochs ran: **{len(history['loss'])}** (requested {args.epochs}; early stopping on `val_loss`)
- Final train accuracy / loss: **{history['accuracy'][-1]:.4f}** / **{history['loss'][-1]:.4f}**
- Final val accuracy / loss: **{history['val_accuracy'][-1]:.4f}** / **{history['val_loss'][-1]:.4f}**
- Best val accuracy: **{fit_diag['best_val_accuracy']:.4f}** (epoch {fit_diag['best_epoch']})

Plots: `accuracy_curve.png`, `loss_curve.png`, `train_val_curves.png`

## Test set (unseen)

| Metric | Value |
|--------|------:|
| Accuracy | {test_metrics['accuracy']:.4f} |
| Precision | {test_metrics['precision']:.4f} |
| Recall | {test_metrics['recall']:.4f} |
| F1 | {test_metrics['f1']:.4f} |
| AUC | {test_metrics['auc']} |
| Loss | {test_metrics['loss']:.4f} |

Confusion matrix:

```
{cm.tolist()}
```

## Overfitting / underfitting

**Status: `{fit_diag['status']}`**

{fit_diag['rationale']}

Train−val accuracy gap: **{fit_diag['train_val_acc_gap']:+.4f}**

## Artifacts

- Trained model: `{model_path.name}`
- Results JSON: `week3_training_results.json`
- CSV log: `training_log.csv`
"""
    (OUTPUTS_DIR / "WEEK3_REPORT.md").write_text(report, encoding="utf-8")
    print(f"\nResults JSON : {results_path}")
    print(f"Report       : {OUTPUTS_DIR / 'WEEK3_REPORT.md'}")
    print("Week 3 complete.")


if __name__ == "__main__":
    main()
