# Plastic-Pulse Ocean Tracker

4-week virtual internship project: build a deep-learning image classifier that distinguishes **marine life** from **plastic debris** so autonomous drones can monitor and clean oceans without harming ecosystems.

## Week 1 — Data Foundations & Image Pre-processing

**Focus:** Preparing raw visual data for machine learning.

### Tasks completed

| Task | Status |
|------|--------|
| Curate a balanced dataset of Marine Life vs Plastic Debris | Done |
| Resize images to 224×224 | Done |
| Normalize pixel values to [0, 1] | Done |
| Apply data augmentation (rotation, flipping) | Done |
| **Deliverable:** cleaned & augmented dataset ready for training | Done |

### Project layout

```
Plastic-Pulse-Ocean-Tracker/
├── data/
│   ├── raw/               # curated class folders
│   ├── processed/         # 224×224 + normalized (.jpg + .npy)
│   └── augmented/         # cleaned + flipped/rotated training set
├── notebooks/
│   └── week1_data_foundations.ipynb
├── outputs/
│   ├── week1_augmentation_preview.png
│   └── week1_dataset_summary.json
├── scripts/
│   ├── curate_dataset.py
│   ├── preprocess_and_augment.py
│   └── run_week1.py
└── requirements.txt
```

### Quick start

```bash
cd Plastic-Pulse-Ocean-Tracker
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python scripts/run_week1.py
```

### What the pipeline does

1. **Curation** (`scripts/curate_dataset.py`)
   - Builds a balanced binary dataset under `data/raw/{marine_life,plastic_debris}`
   - Tries open Wikimedia Commons seed images, then fills remaining slots with class-specific synthetic scenes so the set stays balanced even offline

2. **Pre-processing** (`scripts/preprocess_and_augment.py`)
   - Resizes every image to **224×224** (letterboxed, not stretched)
   - Normalizes pixels to **[0, 1]** and saves float32 `.npy` tensors plus `.jpg` previews
   - Applies **horizontal flip, vertical flip, and ±15° / +30° rotations**
   - Writes the training-ready set to `data/augmented/`

3. **QA artifacts**
   - `outputs/week1_augmentation_preview.png` — visual grid of augmented samples
   - `outputs/week1_dataset_summary.json` — counts, pixel ranges, paths

### Loading the deliverable for Week 2 training

```python
from pathlib import Path
import numpy as np

aug = Path("data/augmented")
X, y = [], []
for label, name in enumerate(["marine_life", "plastic_debris"]):
    for npy in (aug / name).glob("*.npy"):
        X.append(np.load(npy))
        y.append(label)

X = np.stack(X)  # shape: (N, 224, 224, 3), dtype float32 in [0, 1]
y = np.array(y)
```

## Weeks 2–4 (upcoming)

- **Week 2:** Model architecture & training
- **Week 3:** Evaluation / confidence scores
- **Week 4:** Demo / deployment polish
