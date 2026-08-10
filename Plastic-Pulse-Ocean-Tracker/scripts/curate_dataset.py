"""
Week 1 — Dataset Curation
Plastic-Pulse Ocean Tracker

Builds a balanced binary classification dataset:
  - Marine Life
  - Plastic Debris

Strategy:
  1. Download open Wikimedia Commons images when network is available
  2. Fall back to procedurally generated class-labeled images so the
     pipeline always produces a usable training set
"""

from __future__ import annotations

import argparse
import hashlib
import io
import random
from pathlib import Path
from typing import Iterable

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Open / freely usable Wikimedia Commons sample URLs (marine life & plastic waste).
# These are starter seed images; the generator fills any shortfall for balance.
MARINE_LIFE_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Golf_von_Aqaba_Korallen.jpg/640px-Golf_von_Aqaba_Korallen.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Clown_fish_in_the_Andaman_Coral_Reef.jpg/640px-Clown_fish_in_the_Andaman_Coral_Reef.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Carassius_auratus_auratus.jpg/640px-Carassius_auratus_auratus.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Blue_tang_fish.jpg/640px-Blue_tang_fish.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Sea_turtle_swimming.jpg/640px-Sea_turtle_swimming.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Humpback_Whale_underwater_shot.jpg/640px-Humpback_Whale_underwater_shot.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Bottlenose_Dolphin_KSC04pd0178.jpg/640px-Bottlenose_Dolphin_KSC04pd0178.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Shark_Reef_Aquarium.jpg/640px-Shark_Reef_Aquarium.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Jellyfish_in_the_Monterey_Bay_Aquarium.jpg/640px-Jellyfish_in_the_Monterey_Bay_Aquarium.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Octopus_vulgaris.jpg/640px-Octopus_vulgaris.jpg",
]

PLASTIC_DEBRIS_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Plastic_pollution_in_Ghana.jpg/640px-Plastic_pollution_in_Ghana.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Plastic_waste_on_a_beach.jpg/640px-Plastic_waste_on_a_beach.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Marine_debris_on_Hawaii.jpg/640px-Marine_debris_on_Hawaii.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Plastic_bottles.jpg/640px-Plastic_bottles.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Trash_on_the_beach.jpg/640px-Trash_on_the_beach.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Plastic_bag_pollution.jpg/640px-Plastic_bag_pollution.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Ocean_plastic.jpg/640px-Ocean_plastic.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Beach_litter.jpg/640px-Beach_litter.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Plastic_pollution.jpg/640px-Plastic_pollution.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Microplastics.jpg/640px-Microplastics.jpg",
]

HEADERS = {
    "User-Agent": "PlasticPulseOceanTracker/1.0 (educational internship; week1-dataset)"
}


def ensure_dirs() -> None:
    (RAW_DIR / "marine_life").mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "plastic_debris").mkdir(parents=True, exist_ok=True)


def _ocean_gradient(size: int, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    y = np.linspace(0.25, 0.9, size)[:, None]
    x = np.linspace(0.0, 1.0, size)[None, :]
    depth = y + 0.08 * np.sin(8 * x + seed)
    r = (20 + 40 * (1 - depth) + rng.normal(0, 4, (size, size))).clip(0, 255)
    g = (80 + 90 * (1 - depth) + rng.normal(0, 5, (size, size))).clip(0, 255)
    b = (140 + 90 * (1 - depth) + rng.normal(0, 6, (size, size))).clip(0, 255)
    arr = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def synthesize_marine_life(index: int, size: int = 320) -> Image.Image:
    """Procedural underwater scene with a fish-like subject."""
    img = _ocean_gradient(size, seed=1000 + index)
    draw = ImageDraw.Draw(img)
    rng = random.Random(1000 + index)

    # Soft light rays
    for _ in range(4):
        x0 = rng.randint(0, size)
        draw.line(
            [(x0, 0), (x0 + rng.randint(-40, 40), size)],
            fill=(180, 220, 255, 40),
            width=rng.randint(8, 18),
        )

    # Coral / rock accents
    for _ in range(rng.randint(3, 7)):
        cx, cy = rng.randint(10, size - 10), rng.randint(size // 2, size - 10)
        rw, rh = rng.randint(12, 40), rng.randint(20, 70)
        color = (
            rng.randint(160, 230),
            rng.randint(40, 120),
            rng.randint(60, 140),
        )
        draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=color)

    # Fish body
    fx, fy = rng.randint(size // 4, 3 * size // 4), rng.randint(size // 4, 2 * size // 3)
    body_w, body_h = rng.randint(45, 80), rng.randint(20, 35)
    body_color = (
        rng.randint(200, 255),
        rng.randint(100, 200),
        rng.randint(20, 80),
    )
    draw.ellipse(
        [fx - body_w, fy - body_h, fx + body_w, fy + body_h],
        fill=body_color,
    )
    # Tail
    tail = [
        (fx - body_w, fy),
        (fx - body_w - rng.randint(25, 45), fy - body_h),
        (fx - body_w - rng.randint(25, 45), fy + body_h),
    ]
    draw.polygon(tail, fill=body_color)
    # Eye
    draw.ellipse([fx + body_w // 3, fy - 6, fx + body_w // 3 + 10, fy + 4], fill=(20, 20, 20))

    return img.filter(ImageFilter.SMOOTH_MORE)


def synthesize_plastic_debris(index: int, size: int = 320) -> Image.Image:
    """Procedural ocean/beach scene with bottle / bag-like plastic objects."""
    img = _ocean_gradient(size, seed=2000 + index)
    draw = ImageDraw.Draw(img)
    rng = random.Random(2000 + index)

    # Surface foam / sand band
    for y in range(size - 40, size):
        shade = 180 + (y % 7)
        draw.line([(0, y), (size, y)], fill=(shade, shade - 20, 120))

    # Plastic bottles
    for _ in range(rng.randint(2, 5)):
        x, y = rng.randint(20, size - 40), rng.randint(40, size - 60)
        w, h = rng.randint(18, 32), rng.randint(45, 80)
        bottle = (
            rng.choice([(40, 160, 220), (230, 230, 240), (80, 200, 120), (240, 90, 70)])
        )
        draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=bottle)
        draw.rectangle([x + w // 3, y - 10, x + 2 * w // 3, y], fill=(200, 200, 200))
        # Cap
        draw.rectangle(
            [x + w // 3 - 2, y - 16, x + 2 * w // 3 + 2, y - 10],
            fill=rng.choice([(220, 50, 50), (40, 40, 40), (240, 200, 40)]),
        )

    # Floating bags / wrappers
    for _ in range(rng.randint(1, 3)):
        pts = []
        cx, cy = rng.randint(30, size - 30), rng.randint(30, size - 50)
        for _i in range(6):
            pts.append(
                (
                    cx + rng.randint(-35, 35),
                    cy + rng.randint(-25, 25),
                )
            )
        draw.polygon(pts, fill=rng.choice([(245, 245, 245), (180, 220, 255), (255, 240, 180)]))

    return img.filter(ImageFilter.SMOOTH)


def download_image(url: str, timeout: float = 20.0) -> Image.Image | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        return img
    except Exception:
        return None


def save_image(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="JPEG", quality=92)


def count_images(folder: Path) -> int:
    return len(list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png")))


def curate_class(
    class_name: str,
    urls: Iterable[str],
    synthesizer,
    target_count: int,
    force: bool = False,
) -> dict:
    out_dir = RAW_DIR / class_name
    out_dir.mkdir(parents=True, exist_ok=True)

    if force:
        for p in out_dir.glob("*"):
            if p.is_file():
                p.unlink()

    saved = 0
    failures = 0

    # Prefer real open images first
    for i, url in enumerate(tqdm(list(urls), desc=f"Download {class_name}", leave=False)):
        if count_images(out_dir) >= target_count:
            break
        img = download_image(url)
        if img is None:
            failures += 1
            continue
        digest = hashlib.md5(url.encode()).hexdigest()[:10]
        path = out_dir / f"{class_name}_wiki_{digest}.jpg"
        if not path.exists():
            save_image(img, path)
            saved += 1

    # Fill remaining slots with class-specific synthetic images
    existing = count_images(out_dir)
    need = max(0, target_count - existing)
    for i in tqdm(range(need), desc=f"Synthesize {class_name}", leave=False):
        img = synthesizer(existing + i)
        path = out_dir / f"{class_name}_synth_{existing + i:04d}.jpg"
        save_image(img, path)
        saved += 1

    return {
        "class": class_name,
        "total": count_images(out_dir),
        "newly_saved": saved,
        "download_failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Curate balanced Marine Life vs Plastic Debris dataset")
    parser.add_argument("--per-class", type=int, default=40, help="Target images per class")
    parser.add_argument("--force", action="store_true", help="Clear existing raw images first")
    args = parser.parse_args()

    ensure_dirs()
    print("Plastic-Pulse Ocean Tracker - Week 1 Dataset Curation")
    print(f"Target: {args.per_class} images per class\n")

    marine = curate_class(
        "marine_life",
        MARINE_LIFE_URLS,
        synthesize_marine_life,
        args.per_class,
        force=args.force,
    )
    plastic = curate_class(
        "plastic_debris",
        PLASTIC_DEBRIS_URLS,
        synthesize_plastic_debris,
        args.per_class,
        force=args.force,
    )

    print("\nCuration summary")
    print(f"  Marine Life     : {marine['total']} images")
    print(f"  Plastic Debris  : {plastic['total']} images")
    print(f"  Balanced        : {marine['total'] == plastic['total']}")
    print(f"  Raw data path   : {RAW_DIR}")


if __name__ == "__main__":
    main()
