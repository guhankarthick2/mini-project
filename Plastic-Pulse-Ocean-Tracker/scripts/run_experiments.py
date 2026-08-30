"""
Week 3 experiments — learning rate, batch size, dropout, epochs, augmentation.

Reuses the same stem-level split as train_model.py. Head training on cached
MobileNetV2 features is fast; orig-only augmentation runs extract a separate cache.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.train_model import (  # noqa: E402
    AUGMENTED_DIR,
    CACHE_DIR,
    build_feature_model,
    build_head_model,
    cache_features,
    collect_groups,
    paths_for_split,
    stratified_group_split,
)

EXPERIMENTS_DIR = PROJECT_ROOT / "outputs" / "week3" / "experiments"
SEED = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
BACKBONE = "mobilenetv2"
DENSE_UNITS = 128


def filter_paths(
    files: list[str],
    labels: list[int],
    mode: str,
) -> tuple[list[str], list[int]]:
    """mode: all | orig | flips | light (orig+hflip+vflip)"""
    if mode == "all":
        return files, labels
    keep = []
    if mode == "orig":
        keep = {"orig"}
    elif mode == "flips":
        keep = {"orig", "hflip", "vflip"}
    elif mode == "light":
        keep = {"orig", "hflip", "vflip", "rot15"}
    else:
        raise ValueError(f"Unknown aug mode: {mode}")

    out_f, out_y = [], []
    for path, y in zip(files, labels):
        variant = Path(path).stem.rsplit("__", 1)[-1]
        if variant in keep:
            out_f.append(path)
            out_y.append(y)
    return out_f, out_y


def load_or_build_features(
    splits_files: dict[str, tuple[list[str], list[int]]],
    aug_mode: str,
    batch_size: int,
    feature_model: tf.keras.Model,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    tag = f"{BACKBONE}_s{SEED}"
    if aug_mode != "all":
        tag += f"_aug{aug_mode}"

    features = {}
    for name in ("train", "val", "test"):
        files, labels = splits_files[name]
        files, labels = filter_paths(files, labels, aug_mode)
        cache_path = CACHE_DIR / f"{tag}_{name}.npz"
        features[name] = cache_features(
            feature_model, files, labels, cache_path, batch_size=max(batch_size, 64), seed=SEED
        )
        print(f"  {aug_mode:5s} {name}: {len(files)} images -> {features[name][0].shape}")
    return features


def run_one(
    name: str,
    features: dict[str, tuple[np.ndarray, np.ndarray]],
    *,
    learning_rate: float,
    batch_size: int,
    epochs: int,
    dropout: float,
    patience: int,
) -> dict:
    tf.keras.utils.set_random_seed(SEED)
    X_train, y_train = features["train"]
    X_val, y_val = features["val"]
    X_test, y_test = features["test"]

    head = build_head_model(dropout=dropout, dense_units=DENSE_UNITS, feature_dim=int(X_train.shape[1]))
    head.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
        ],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=patience,
            restore_best_weights=True,
            verbose=0,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=max(1, patience // 2),
            min_lr=1e-6,
            verbose=0,
        ),
    ]

    t0 = time.perf_counter()
    hist = head.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=0,
    )
    train_sec = time.perf_counter() - t0
    history = {k: [float(v) for v in vals] for k, vals in hist.history.items()}

    probs = head.predict(X_test, batch_size=batch_size, verbose=0).reshape(-1)
    preds = (probs >= 0.5).astype(int)
    y_true = y_test.astype(int)

    best_epoch = int(np.argmin(history["val_loss"])) + 1
    train_acc = float(history["accuracy"][best_epoch - 1])
    val_acc = float(history["val_accuracy"][best_epoch - 1])
    train_loss = float(history["loss"][best_epoch - 1])
    val_loss = float(history["val_loss"][best_epoch - 1])
    gap = train_acc - val_acc

    test_acc = float(accuracy_score(y_true, preds))
    result = {
        "name": name,
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "epochs_requested": epochs,
        "epochs_ran": len(history["loss"]),
        "best_epoch": best_epoch,
        "dropout": dropout,
        "patience": patience,
        "train_seconds": round(train_sec, 2),
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "n_test": int(len(y_test)),
        "train_accuracy_best": train_acc,
        "val_accuracy_best": val_acc,
        "train_loss_best": train_loss,
        "val_loss_best": val_loss,
        "train_val_acc_gap": gap,
        "test_accuracy": test_acc,
        "test_precision": float(precision_score(y_true, preds, zero_division=0)),
        "test_recall": float(recall_score(y_true, preds, zero_division=0)),
        "test_f1": float(f1_score(y_true, preds, zero_division=0)),
        "test_auc": float(roc_auc_score(y_true, probs)),
        "history": history,
    }
    print(
        f"[{name}] test_acc={test_acc:.4f} val_acc={val_acc:.4f} "
        f"gap={gap:+.4f} epochs={result['epochs_ran']} ({train_sec:.1f}s)"
    )
    return result


def plot_comparison(rows: list[dict], out_dir: Path) -> None:
    names = [r["name"] for r in rows]
    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x - width / 2, [r["val_accuracy_best"] for r in rows], width, label="Val acc (best epoch)")
    ax.bar(x + width / 2, [r["test_accuracy"] for r in rows], width, label="Test acc")
    ax.set_xticks(x, names, rotation=30, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0.97, 1.002)
    ax.set_title("Experiment comparison — validation vs test accuracy")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "comparison_accuracy.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x - width / 2, [r["val_loss_best"] for r in rows], width, label="Val loss (best)")
    ax.bar(x + width / 2, [r["train_val_acc_gap"] for r in rows], width, label="Train−val acc gap")
    ax.set_xticks(x, names, rotation=30, ha="right")
    ax.set_title("Experiment comparison — val loss & train/val gap")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "comparison_loss_gap.png", dpi=140)
    plt.close(fig)

    # Overlay loss curves for LR family
    fig, ax = plt.subplots(figsize=(9, 5))
    for r in rows:
        if r["name"].startswith("lr_") or r["name"] == "baseline":
            ax.plot(range(1, len(r["history"]["val_loss"]) + 1), r["history"]["val_loss"], marker="o", label=r["name"])
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Val loss")
    ax.set_title("Validation loss by learning-rate experiment")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "comparison_lr_val_loss.png", dpi=140)
    plt.close(fig)


def pick_winner(rows: list[dict]) -> dict:
    """Primary: test accuracy; tie-break: lower |train-val gap|, then lower val loss."""
    return sorted(
        rows,
        key=lambda r: (
            -r["test_accuracy"],
            abs(r["train_val_acc_gap"]),
            r["val_loss_best"],
        ),
    )[0]


def write_report(rows: list[dict], winner: dict, out_dir: Path) -> Path:
    lines = [
        "# Week 3 — Hyperparameter & Augmentation Experiments",
        "",
        "Plastic-Pulse Ocean Tracker · frozen MobileNetV2 features + trainable Dense head",
        "",
        "Same stem-level 70/15/15 split (seed 42) for every run. EarlyStopping restores best `val_loss` weights.",
        "",
        "## Results table",
        "",
        "| Experiment | LR | Batch | Dropout | Aug | Epochs ran | Val acc | Test acc | Test F1 | Train−val gap | Val loss |",
        "|------------|---:|------:|--------:|-----|----------:|--------:|---------:|--------:|--------------:|---------:|",
    ]
    for r in rows:
        aug = r.get("aug_mode", "all")
        lines.append(
            f"| `{r['name']}` | {r['learning_rate']:g} | {r['batch_size']} | {r['dropout']} | {aug} "
            f"| {r['epochs_ran']} | {r['val_accuracy_best']:.4f} | **{r['test_accuracy']:.4f}** "
            f"| {r['test_f1']:.4f} | {r['train_val_acc_gap']:+.4f} | {r['val_loss_best']:.4f} |"
        )

    lines += [
        "",
        f"## Winner: `{winner['name']}`",
        "",
        f"- **Test accuracy:** {winner['test_accuracy']:.4f}",
        f"- **Val accuracy (best epoch):** {winner['val_accuracy_best']:.4f}",
        f"- **Test F1 / AUC:** {winner['test_f1']:.4f} / {winner['test_auc']:.4f}",
        f"- **Settings:** lr={winner['learning_rate']}, batch={winner['batch_size']}, "
        f"dropout={winner['dropout']}, aug=`{winner.get('aug_mode', 'all')}`, "
        f"epochs_requested={winner['epochs_requested']}",
        f"- **Train−val accuracy gap:** {winner['train_val_acc_gap']:+.4f}",
        "",
        "## What we learned",
        "",
    ]

    by_name = {r["name"]: r for r in rows}
    baseline = by_name.get("baseline")

    def delta(name: str) -> str:
        if not baseline or name not in by_name:
            return ""
        d = by_name[name]["test_accuracy"] - baseline["test_accuracy"]
        return f" ({d:+.4f} vs baseline)"

    lines += [
        "### Learning rate",
        "",
        f"- `lr=1e-2` (high): {by_name.get('lr_1e-2', {}).get('test_accuracy', 'n/a')}"
        f"{delta('lr_1e-2')}. Often less stable / higher val loss.",
        f"- `lr=1e-3` (baseline): strong default with ReduceLROnPlateau.",
        f"- `lr=1e-4` (low): {by_name.get('lr_1e-4', {}).get('test_accuracy', 'n/a')}"
        f"{delta('lr_1e-4')}. Slower; may under-train if epochs are short.",
        "",
        "### Batch size",
        "",
        f"- 32 / 64 / 128 were compared. Smaller batches can generalize slightly better but are noisier;",
        "  larger batches train faster per epoch on cached features.",
        "",
        "### Dropout",
        "",
        f"- `0.0`: less regularization — watch train/val gap.",
        f"- `0.3` (baseline): balanced.",
        f"- `0.5`: stronger regularization — may help if overfit appears.",
        "",
        "### Epochs",
        "",
        "- Short budgets (e.g. 5) can stop before the best `val_loss` plateau.",
        "- Longer budgets with early stopping are safer; best weights are restored automatically.",
        "",
        "### Data augmentation",
        "",
        "- **Full (6 variants)** vs **orig-only** vs **flips-only** / **light**.",
        "- Augmentation increases effective sample count and usually improves robustness;",
        "  orig-only is a useful ablation to quantify the gain.",
        "",
        "## Plots",
        "",
        "- `comparison_accuracy.png`",
        "- `comparison_loss_gap.png`",
        "- `comparison_lr_val_loss.png`",
        "",
        "## Reproduce",
        "",
        "```powershell",
        "python scripts/run_experiments.py",
        "```",
        "",
    ]
    path = out_dir / "EXPERIMENT_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Week 3 hyperparameter experiments")
    parser.add_argument("--skip-aug-extract", action="store_true", help="Skip non-all aug modes if cache missing")
    args = parser.parse_args()

    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tf.keras.utils.set_random_seed(SEED)

    print("Plastic-Pulse — hyperparameter / augmentation experiments")
    groups = collect_groups(AUGMENTED_DIR)
    splits = stratified_group_split(groups, TRAIN_RATIO, VAL_RATIO, SEED)
    split_files = {name: paths_for_split(groups, gids) for name, gids in splits.items()}

    feature_model = build_feature_model(BACKBONE)
    feature_model.trainable = False

    # Shared full-aug feature pack (reuses existing cache)
    print("\nLoading full-augmentation features...")
    feats_all = load_or_build_features(split_files, "all", batch_size=64, feature_model=feature_model)

    configs = [
        # name, lr, batch, epochs, dropout, patience, aug
        ("baseline", 1e-3, 64, 20, 0.3, 4, "all"),
        ("lr_1e-2", 1e-2, 64, 20, 0.3, 4, "all"),
        ("lr_1e-4", 1e-4, 64, 20, 0.3, 4, "all"),
        ("batch_32", 1e-3, 32, 20, 0.3, 4, "all"),
        ("batch_128", 1e-3, 128, 20, 0.3, 4, "all"),
        ("dropout_0", 1e-3, 64, 20, 0.0, 4, "all"),
        ("dropout_0.5", 1e-3, 64, 20, 0.5, 4, "all"),
        ("epochs_5", 1e-3, 64, 5, 0.3, 5, "all"),
        ("epochs_30", 1e-3, 64, 30, 0.3, 4, "all"),
        ("aug_orig", 1e-3, 64, 20, 0.3, 4, "orig"),
        ("aug_flips", 1e-3, 64, 20, 0.3, 4, "flips"),
        ("aug_light", 1e-3, 64, 20, 0.3, 4, "light"),
    ]

    feature_packs: dict[str, dict] = {"all": feats_all}
    for aug in ("orig", "flips", "light"):
        if any(c[-1] == aug for c in configs):
            print(f"\nBuilding features for aug={aug}...")
            try:
                feature_packs[aug] = load_or_build_features(
                    split_files, aug, batch_size=64, feature_model=feature_model
                )
            except Exception as exc:  # noqa: BLE001
                if args.skip_aug_extract:
                    print(f"  skip {aug}: {exc}")
                else:
                    raise

    rows: list[dict] = []
    for name, lr, batch, epochs, dropout, patience, aug in configs:
        if aug not in feature_packs:
            print(f"Skipping {name} (no features for aug={aug})")
            continue
        print(f"\n=== {name} ===")
        result = run_one(
            name,
            feature_packs[aug],
            learning_rate=lr,
            batch_size=batch,
            epochs=epochs,
            dropout=dropout,
            patience=patience,
        )
        result["aug_mode"] = aug
        # Drop bulky history from per-run files? keep for plots
        rows.append(result)
        (EXPERIMENTS_DIR / f"{name}.json").write_text(
            json.dumps({k: v for k, v in result.items() if k != "history"}, indent=2),
            encoding="utf-8",
        )

    winner = pick_winner(rows)
    plot_comparison(rows, EXPERIMENTS_DIR)
    report_path = write_report(rows, winner, EXPERIMENTS_DIR)

    # Enrich report narrative with concrete rankings
    ranked = sorted(rows, key=lambda r: -r["test_accuracy"])
    narrative = [
        "",
        "## Ranking by test accuracy",
        "",
    ]
    for i, r in enumerate(ranked, 1):
        mark = " ← best" if r["name"] == winner["name"] else ""
        narrative.append(
            f"{i}. `{r['name']}` — test {r['test_accuracy']:.4f}, "
            f"val {r['val_accuracy_best']:.4f}, gap {r['train_val_acc_gap']:+.4f}{mark}"
        )

    # Concrete takeaways from data
    takeaways = ["", "## Concrete takeaways", ""]
    if "baseline" in {r["name"] for r in rows}:
        base = next(r for r in rows if r["name"] == "baseline")
        for family, names in [
            ("Learning rate", ["lr_1e-2", "baseline", "lr_1e-4"]),
            ("Batch size", ["batch_32", "baseline", "batch_128"]),
            ("Dropout", ["dropout_0", "baseline", "dropout_0.5"]),
            ("Epoch budget", ["epochs_5", "baseline", "epochs_30"]),
            ("Augmentation", ["aug_orig", "aug_flips", "aug_light", "baseline"]),
        ]:
            subset = [next(r for r in rows if r["name"] == n) for n in names if any(r["name"] == n for r in rows)]
            if not subset:
                continue
            best = max(subset, key=lambda r: r["test_accuracy"])
            takeaways.append(
                f"- **{family}:** best was `{best['name']}` "
                f"(test {best['test_accuracy']:.4f})"
                + (f" vs baseline {base['test_accuracy']:.4f}" if best["name"] != "baseline" else " (= baseline)")
            )

    takeaways += [
        "",
        f"**Recommended production settings:** match `{winner['name']}` — "
        f"lr={winner['learning_rate']}, batch={winner['batch_size']}, "
        f"dropout={winner['dropout']}, augmentation=`{winner.get('aug_mode', 'all')}`, "
        f"epochs={winner['epochs_requested']} with early stopping.",
        "",
    ]
    with report_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(narrative + takeaways))

    summary = {
        "winner": {k: v for k, v in winner.items() if k != "history"},
        "experiments": [{k: v for k, v in r.items() if k != "history"} for r in rows],
        "ranking": [r["name"] for r in ranked],
    }
    (EXPERIMENTS_DIR / "experiment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nWinner: {winner['name']} (test_acc={winner['test_accuracy']:.4f})")
    print(f"Report: {report_path}")
    print(f"Summary JSON: {EXPERIMENTS_DIR / 'experiment_summary.json'}")


if __name__ == "__main__":
    main()
