"""Run the full Week 1 pipeline: Kaggle curate -> preprocess -> augment."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(script: str, extra_args: list[str] | None = None) -> None:
    cmd = [sys.executable, str(SCRIPTS / script), *(extra_args or [])]
    print(f"\n>>> {' '.join(cmd)}\n")
    subprocess.run(cmd, check=True)


def main() -> None:
    run("curate_dataset.py", ["--per-class", "2500", "--force"])
    run("preprocess_and_augment.py", ["--augments-per-image", "6"])
    print("\nWeek 1 deliverable complete.")


if __name__ == "__main__":
    main()
