"""
Week 1 — Kaggle Dataset Curation
Plastic-Pulse Ocean Tracker

Downloads free high-quality Kaggle image datasets and builds a balanced
binary set:
  - marine_life   (~2500 images)
  - plastic_debris (~2500 images)

Requires Kaggle API credentials:
  1. https://www.kaggle.com/settings  ->  Account  ->  Create New Token
  2. Save the downloaded kaggle.json to:
       %USERPROFILE%\\.kaggle\\kaggle.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import zipfile
from pathlib import Path

from PIL import Image
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CACHE_DIR = PROJECT_ROOT / "data" / "kaggle_cache"
MANIFEST_PATH = PROJECT_ROOT / "outputs" / "week1_data_sources.json"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Marine-life sources (animals / underwater organisms only).
MARINE_DATASETS = [
    {
        "slug": "vencerlanz09/sea-animals-image-dataste",
        "note": "Sea Animals Image Dataset (multi-species marine creatures)",
        # Exclude non-animal folders if present in some mirrors.
        "exclude_name_substrings": ["seaweed", "coral", "plant"],
    },
    {
        "slug": "mikoajfish99/marine-animal-images",
        "note": "Marine Animal Images (fish, turtle, seal, jellyfish, etc.)",
        "exclude_name_substrings": [],
    },
]

# Plastic / debris sources. Prefer plastic-labeled folders and marine debris.
PLASTIC_DATASETS = [
    {
        "slug": "zlatan599/garbage-dataset-classification",
        "note": "Garbage Images Dataset (~2000+/class including plastic)",
        "include_name_substrings": ["plastic"],
        "exclude_name_substrings": ["metal", "glass", "cardboard", "paper", "trash"],
    },
    {
        "slug": "asdasdasasdas/garbage-classification",
        "note": "TrashNet / Garbage Classification (plastic class)",
        "include_name_substrings": ["plastic"],
        "exclude_name_substrings": ["metal", "glass", "cardboard", "paper", "trash"],
    },
    {
        "slug": "arkadiyhacks/drinking-waste-classification",
        "note": "Drinking waste: PET + HDPE plastic bottles",
        "include_name_substrings": ["pet", "hdpe", "hdpem"],
        "exclude_name_substrings": ["alucan", "glass", "yolo"],
    },
    {
        "slug": "jocelyndumlao/seaclear-marine-debris-detection-and-segmentation",
        "note": "Seaclear underwater marine debris imagery (filename cues only)",
        "include_name_substrings": [],
        "exclude_name_substrings": ["animal", "fish", "plant", "rov"],
        "prefer_name_substrings": [
            "plastic",
            "bottle",
            "bag",
            "litter",
            "trash",
            "waste",
            "rope",
            "cup",
            "wrapper",
        ],
    },
    {
        "slug": "sovitrath/marine-debris-dataset",
        "note": "Marine debris detection images",
        "include_name_substrings": [],
        "exclude_name_substrings": [],
    },
]


def ensure_kaggle_credentials() -> None:
    """Locate kaggle.json and export env vars for the Kaggle API client."""
    candidates = [
        Path(os.environ.get("KAGGLE_CONFIG_DIR", "")) / "kaggle.json" if os.environ.get("KAGGLE_CONFIG_DIR") else None,
        Path.home() / ".kaggle" / "kaggle.json",
        PROJECT_ROOT / "kaggle.json",
    ]
    cred_path = next((p for p in candidates if p and p.is_file()), None)
    if cred_path is None:
        raise FileNotFoundError(
            "Kaggle credentials not found.\n\n"
            "Setup steps:\n"
            "  1. Open https://www.kaggle.com/settings\n"
            "  2. Account section -> Create New API Token\n"
            "  3. Move the downloaded kaggle.json to:\n"
            f"       {Path.home() / '.kaggle' / 'kaggle.json'}\n"
            "  4. Re-run this script.\n"
        )

    # Ensure standard location for the kaggle package.
    std = Path.home() / ".kaggle" / "kaggle.json"
    if cred_path.resolve() != std.resolve():
        std.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cred_path, std)

    try:
        std.chmod(0o600)
    except OSError:
        pass

    with std.open(encoding="utf-8") as f:
        creds = json.load(f)
    if "username" not in creds or "key" not in creds:
        raise ValueError(f"Invalid kaggle.json at {std}: expected username and key fields.")

    os.environ["KAGGLE_USERNAME"] = creds["username"]
    os.environ["KAGGLE_KEY"] = creds["key"]


def get_api():
    ensure_kaggle_credentials()
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    return api


def download_dataset(api, slug: str) -> Path:
    """Download + unzip a Kaggle dataset into the local cache."""
    out_dir = CACHE_DIR / slug.replace("/", "__")
    marker = out_dir / ".download_complete"
    if marker.exists() and any(out_dir.rglob("*")):
        print(f"  [cache] {slug}")
        return out_dir

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"  [download] {slug}")
    try:
        api.dataset_download_files(slug, path=str(out_dir), quiet=False)
    except Exception as exc:  # noqa: BLE001
        print(f"  [skip] {slug}: {exc}")
        return out_dir

    # Unzip any archives
    for zpath in list(out_dir.glob("*.zip")):
        print(f"  [unzip] {zpath.name}")
        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(out_dir)
        zpath.unlink(missing_ok=True)

    marker.write_text("ok", encoding="utf-8")
    return out_dir


def iter_images(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS]


def path_matches(path: Path, include: list[str], exclude: list[str], prefer: list[str] | None = None) -> bool:
    text = str(path).lower().replace("\\", "/")
    if exclude and any(s in text for s in exclude):
        # Allow if an include token is more specific later in path (e.g. .../plastic/...)
        if not include or not any(s in text for s in include):
            return False
    if include and not any(s in text for s in include):
        # If prefer list exists and no include forced, fall through to prefer logic at call site.
        if prefer is None:
            return False
        return any(s in text for s in prefer)
    return True


def _relative_parts(path: Path, root: Path) -> list[str]:
    """Return lowercased path parts relative to the dataset root (avoids matching cache slug)."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    return [part.lower() for part in rel.parts]


def _parts_hit(parts: list[str], tokens: list[str]) -> bool:
    """True if any relative folder/file token matches (exact, stem, or prefix for HDPEM/PET)."""
    for part in parts:
        stem = Path(part).stem
        for tok in tokens:
            if part == tok or stem == tok:
                return True
            # Allow folder aliases like HDPEM ~= hdpe, PET bottles, etc.
            if len(tok) >= 3 and (part.startswith(tok) or stem.startswith(tok)):
                return True
    return False


def collect_candidates(cfg: dict, root: Path) -> list[Path]:
    """
    Filter images using folder/file name tokens relative to the dataset root.

    Matching uses path *parts* under the dataset root, not the absolute cache
    path, so tokens like 'net' cannot false-match 'detection' in the slug.
    """
    include = [s.lower() for s in cfg.get("include_name_substrings", [])]
    exclude = [s.lower() for s in cfg.get("exclude_name_substrings", [])]
    prefer = [s.lower() for s in cfg.get("prefer_name_substrings", [])] or None

    images = iter_images(root)
    if not include and prefer is None and not exclude:
        return images

    kept: list[Path] = []
    for p in images:
        parts = _relative_parts(p, root)
        hit_include = _parts_hit(parts, include) if include else False
        hit_exclude = _parts_hit(parts, exclude) if exclude else False
        hit_prefer = _parts_hit(parts, prefer) if prefer else False

        if include:
            if hit_include:
                kept.append(p)
            continue

        if prefer is not None:
            if hit_prefer and not hit_exclude:
                kept.append(p)
            continue

        if exclude and hit_exclude:
            continue
        kept.append(p)
    return kept


def is_valid_rgb(path: Path, min_side: int = 64) -> bool:
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            w, h = img.size
            return w >= min_side and h >= min_side
    except Exception:
        return False


def content_hash(path: Path, nbytes: int = 65536) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        h.update(f.read(nbytes))
        h.update(str(path.stat().st_size).encode())
    return h.hexdigest()


def clear_class_dir(class_name: str) -> None:
    out = RAW_DIR / class_name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)


def copy_balanced(
    class_name: str,
    candidates: list[tuple[Path, str]],
    target: int,
    seed: int,
) -> dict:
    """Deduplicate, validate, shuffle, and copy up to `target` images."""
    rng = random.Random(seed)
    rng.shuffle(candidates)

    seen: set[str] = set()
    unique: list[tuple[Path, str]] = []
    for path, source in candidates:
        digest = content_hash(path)
        if digest in seen:
            continue
        seen.add(digest)
        unique.append((path, source))

    out_dir = RAW_DIR / class_name
    out_dir.mkdir(parents=True, exist_ok=True)

    saved = 0
    source_counts: dict[str, int] = {}
    rejected = 0

    for path, source in tqdm(unique, desc=f"Curate {class_name}"):
        if saved >= target:
            break
        if not is_valid_rgb(path):
            rejected += 1
            continue
        ext = path.suffix.lower()
        if ext not in {".jpg", ".jpeg"}:
            ext = ".jpg"
        dest = out_dir / f"{class_name}_{saved:05d}{ext}"
        try:
            if path.suffix.lower() in {".jpg", ".jpeg"}:
                shutil.copy2(path, dest)
            else:
                Image.open(path).convert("RGB").save(dest, format="JPEG", quality=92)
            saved += 1
            source_counts[source] = source_counts.get(source, 0) + 1
        except Exception:
            rejected += 1

    return {
        "class": class_name,
        "requested": target,
        "saved": saved,
        "unique_candidates": len(unique),
        "rejected": rejected,
        "sources": source_counts,
    }


def gather_class(api, class_name: str, dataset_cfgs: list[dict], target: int, seed: int) -> dict:
    print(f"\n=== Collecting {class_name} (target={target}) ===")
    candidates: list[tuple[Path, str]] = []
    download_log: list[dict] = []

    for cfg in dataset_cfgs:
        slug = cfg["slug"]
        root = download_dataset(api, slug)
        found = collect_candidates(cfg, root)
        print(f"  {slug}: {len(found)} candidate images")
        download_log.append(
            {
                "slug": slug,
                "note": cfg.get("note", ""),
                "candidates": len(found),
                "url": f"https://www.kaggle.com/datasets/{slug}",
            }
        )
        for p in found:
            candidates.append((p, slug))

    stats = copy_balanced(class_name, candidates, target, seed=seed)
    stats["datasets"] = download_log
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Curate ~2500/class Kaggle marine vs plastic dataset")
    parser.add_argument("--per-class", type=int, default=2500, help="Target images per class")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true", help="Clear existing raw class folders first")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    if args.force:
        clear_class_dir("marine_life")
        clear_class_dir("plastic_debris")

    api = get_api()

    marine = gather_class(api, "marine_life", MARINE_DATASETS, args.per_class, seed=args.seed)
    plastic = gather_class(api, "plastic_debris", PLASTIC_DATASETS, args.per_class, seed=args.seed + 1)

    summary = {
        "project": "Plastic-Pulse Ocean Tracker",
        "week": 1,
        "target_per_class": args.per_class,
        "balanced": marine["saved"] == plastic["saved"],
        "marine_life": marine,
        "plastic_debris": plastic,
        "raw_dir": str(RAW_DIR),
        "cache_dir": str(CACHE_DIR),
    }
    MANIFEST_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nCuration summary")
    print(f"  Marine Life    : {marine['saved']} / {args.per_class}")
    print(f"  Plastic Debris : {plastic['saved']} / {args.per_class}")
    print(f"  Balanced       : {marine['saved'] == plastic['saved']}")
    print(f"  Manifest       : {MANIFEST_PATH}")

    if marine["saved"] < args.per_class or plastic["saved"] < args.per_class:
        print(
            "\nWARNING: Could not reach the full target for one or both classes. "
            "Accept dataset licenses on Kaggle (dataset page -> Download) and re-run, "
            "or add more dataset slugs in this script."
        )


if __name__ == "__main__":
    main()
