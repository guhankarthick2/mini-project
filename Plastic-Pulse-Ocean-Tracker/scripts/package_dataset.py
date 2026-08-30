"""Zip data/augmented for a shareable internship data link."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUGMENTED_DIR = PROJECT_ROOT / "data" / "augmented"
README_SRC = PROJECT_ROOT / "docs" / "DATASET_README.md"
DEFAULT_OUT = PROJECT_ROOT / "outputs" / "share" / "PlasticPulse_augmented_dataset.zip"


def package(out_path: Path) -> dict:
    if not AUGMENTED_DIR.is_dir():
        raise FileNotFoundError(f"Missing {AUGMENTED_DIR}. Run scripts/run_week1.py first.")

    files = [p for p in AUGMENTED_DIR.rglob("*") if p.is_file()]
    if not files:
        raise FileNotFoundError(f"No files under {AUGMENTED_DIR}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_STORED) as zf:
        if README_SRC.exists():
            zf.write(README_SRC, arcname="README.md")
        for path in files:
            zf.write(path, arcname=str(Path("augmented") / path.relative_to(AUGMENTED_DIR)))

    counts = {}
    for cls in ("marine_life", "plastic_debris"):
        counts[cls] = sum(1 for p in files if p.parent.name == cls)

    return {
        "zip": str(out_path),
        "bytes": out_path.stat().st_size,
        "files": len(files),
        "counts": counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Zip the augmented training set")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    info = package(args.out.resolve())
    mb = info["bytes"] / (1024 * 1024)
    print("Packaged augmented dataset")
    print(f"  zip   : {info['zip']}")
    print(f"  size  : {mb:.1f} MB")
    print(f"  files : {info['files']}")
    for name, n in info["counts"].items():
        print(f"  {name}: {n}")


if __name__ == "__main__":
    main()
