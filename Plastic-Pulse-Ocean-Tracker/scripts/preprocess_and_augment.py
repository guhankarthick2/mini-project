"""
Week 1 — Image Pre-processing & Data Augmentation
Plastic-Pulse Ocean Tracker

Deliverable steps:
  1. Resize every image to 224x224
  2. Normalize pixel values to [0, 1] (documented; applied when saving .npy samples
     and when loading JPEGs via /255 in training code)
  3. Apply rotation / flip augmentation for robustness
  4. Export cleaned + augmented dataset ready for training

For large Kaggle-scale sets (~2500/class), JPEG is the primary on-disk format.
A small .npy sample set is written for QA so normalization can be verified.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
AUGMENTED_DIR = PROJECT_ROOT / "data" / "augmented"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

CLASSES = ("marine_life", "plastic_debris")
TARGET_SIZE = (224, 224)
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS)


def load_rgb(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def resize_image(img: Image.Image, size: tuple[int, int] = TARGET_SIZE) -> Image.Image:
    """Resize with aspect-preserving pad so subjects are not stretched."""
    return ImageOps.pad(img, size, method=Image.Resampling.BILINEAR, color=(0, 0, 0))


def normalize_to_unit(img: Image.Image) -> np.ndarray:
    """Convert uint8 RGB image to float32 array in [0, 1]."""
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return np.clip(arr, 0.0, 1.0)


def save_jpeg(img: Image.Image, path: Path, quality: int = 92) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="JPEG", quality=quality, optimize=True)


def clear_dir(folder: Path) -> None:
    if folder.exists():
        for p in folder.iterdir():
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                # safety: only clear flat class folders
                for child in p.rglob("*"):
                    if child.is_file():
                        child.unlink()
                for child in sorted(p.rglob("*"), reverse=True):
                    if child.is_dir():
                        child.rmdir()
                p.rmdir()
    folder.mkdir(parents=True, exist_ok=True)


def augment_variants(img: Image.Image) -> dict[str, Image.Image]:
    return {
        "orig": img,
        "hflip": ImageOps.mirror(img),
        "vflip": ImageOps.flip(img),
        "rot15": img.rotate(15, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=(0, 0, 0)),
        "rot_neg15": img.rotate(-15, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=(0, 0, 0)),
        "rot30": img.rotate(30, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=(0, 0, 0)),
    }


def process_class(
    class_name: str,
    augments_per_image: int,
    save_npy_samples: int,
    seed: int,
) -> dict:
    raw_dir = RAW_DIR / class_name
    processed_dir = PROCESSED_DIR / class_name
    augmented_dir = AUGMENTED_DIR / class_name
    clear_dir(processed_dir)
    clear_dir(augmented_dir)

    images = list_images(raw_dir)
    if not images:
        raise FileNotFoundError(
            f"No raw images found in {raw_dir}. Run scripts/curate_dataset.py first."
        )

    rng = random.Random(seed)
    npy_indices = set(rng.sample(range(len(images)), k=min(save_npy_samples, len(images))))

    processed_count = 0
    augmented_count = 0
    pixel_mins: list[float] = []
    pixel_maxs: list[float] = []

    for idx, img_path in enumerate(tqdm(images, desc=f"Process {class_name}")):
        img = load_rgb(img_path)
        resized = resize_image(img, TARGET_SIZE)
        normalized = normalize_to_unit(resized)

        stem = img_path.stem
        save_jpeg(resized, processed_dir / f"{stem}.jpg")
        if idx in npy_indices:
            np.save(processed_dir / f"{stem}.npy", normalized.astype(np.float32))

        processed_count += 1
        pixel_mins.append(float(normalized.min()))
        pixel_maxs.append(float(normalized.max()))

        variants = augment_variants(resized)
        chosen_names = list(variants.keys())[: max(1, augments_per_image)]
        for name in chosen_names:
            save_jpeg(variants[name], augmented_dir / f"{stem}__{name}.jpg")
            augmented_count += 1

    return {
        "class": class_name,
        "raw_images": len(images),
        "processed_images": processed_count,
        "augmented_images": augmented_count,
        "npy_qa_samples": len(npy_indices),
        "pixel_min": min(pixel_mins) if pixel_mins else None,
        "pixel_max": max(pixel_maxs) if pixel_maxs else None,
        "input_shape": [TARGET_SIZE[1], TARGET_SIZE[0], 3],
        "normalization_note": "JPEGs load as uint8; divide by 255.0 to obtain [0,1] float tensors",
    }


def make_preview_grid() -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 6, figsize=(14, 5))
    fig.suptitle("Week 1 Deliverable - Cleaned & Augmented Kaggle Samples (224x224)", fontsize=12)

    for row, class_name in enumerate(CLASSES):
        samples = sorted((AUGMENTED_DIR / class_name).glob("*__*.jpg"))[:6]
        for col in range(6):
            ax = axes[row, col]
            ax.axis("off")
            if col < len(samples):
                ax.imshow(Image.open(samples[col]))
                label = samples[col].stem.split("__")[-1]
                ax.set_title(f"{class_name}\n{label}", fontsize=8)

    out_path = OUTPUTS_DIR / "week1_augmentation_preview.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess and augment Ocean Tracker dataset")
    parser.add_argument("--augments-per-image", type=int, default=6)
    parser.add_argument("--npy-qa-samples", type=int, default=25, help="Normalized .npy samples per class for QA")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("Plastic-Pulse Ocean Tracker - Week 1 Pre-processing & Augmentation")
    print(f"Resize target : {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
    print("Normalize     : pixel values -> [0, 1] (via /255 at train time; .npy QA samples saved)")
    print("Augmentations : flip + rotation variants\n")

    stats = [
        process_class(name, args.augments_per_image, args.npy_qa_samples, seed=args.seed + i)
        for i, name in enumerate(CLASSES)
    ]
    preview = make_preview_grid()

    summary = {
        "project": "Plastic-Pulse Ocean Tracker",
        "week": 1,
        "deliverable": "cleaned_and_augmented_dataset",
        "target_size": list(TARGET_SIZE),
        "normalization": "uint8 JPEG on disk; float32 [0,1] via /255 (verified with .npy QA samples)",
        "augmentations": [
            "horizontal_flip",
            "vertical_flip",
            "rotate_+15",
            "rotate_-15",
            "rotate_+30",
        ],
        "classes": stats,
        "paths": {
            "raw": str(RAW_DIR),
            "processed": str(PROCESSED_DIR),
            "augmented": str(AUGMENTED_DIR),
            "preview": str(preview),
        },
    }

    summary_path = OUTPUTS_DIR / "week1_dataset_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nDeliverable ready")
    for s in stats:
        print(
            f"  {s['class']}: {s['processed_images']} cleaned -> "
            f"{s['augmented_images']} augmented | pixels in [{s['pixel_min']:.3f}, {s['pixel_max']:.3f}]"
        )
    print(f"  Preview grid : {preview}")
    print(f"  Summary JSON : {summary_path}")
    print(f"  Training set : {AUGMENTED_DIR}")


if __name__ == "__main__":
    main()
