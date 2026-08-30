# Plastic-Pulse Ocean Tracker

4-week virtual internship project: build a deep-learning image classifier that distinguishes **marine life** from **plastic debris** so autonomous drones can monitor and clean oceans without harming ecosystems.

**Progress (Weeks 1–4):** [docs/PROGRESS_SUMMARY.md](docs/PROGRESS_SUMMARY.md) · [print-friendly HTML](outputs/progress_summary.html) · [Week 2 architecture](outputs/week2/present.html) · [Week 3 train/eval](outputs/week3/present.html)

**Classifier:** [`models/classifier.py`](models/classifier.py)

**Data:** [augmented training zip](https://github.com/guhankarthick2/Plastic-Pulse-Ocean-Tracker/releases/download/week1-augmented-dataset/PlasticPulse_augmented_dataset.zip) (30,000 JPEGs, ~368 MB). Rebuild locally with `python scripts/package_dataset.py`.

## Week 1 — Data Foundations & Image Pre-processing

**Focus:** Preparing raw visual data for machine learning.

### Tasks

| Task | Status |
|------|--------|
| Curate a balanced dataset of Marine Life vs Plastic Debris from Kaggle | Done (2,500 / class) |
| Resize images to 224×224 | Done |
| Normalize pixel values to [0, 1] | Done (at load via /255) |
| Apply data augmentation (rotation, flipping) | Done (6 variants → 15,000 / class) |
| **Deliverable:** cleaned & augmented dataset ready for training | Done (`data/augmented/`) |

### Target size

- **2,500** curated images per class (`marine_life`, `plastic_debris`)
- After augmentation (6 variants each): **~15,000** images per class (**~30,000** total)

### Kaggle sources (free)

**Marine life**

- [Sea Animals Image Dataset](https://www.kaggle.com/datasets/vencerlanz09/sea-animals-image-dataste)
- [Marine Animal Images](https://www.kaggle.com/datasets/mikoajfish99/marine-animal-images)

**Plastic debris**

- [Garbage Images Dataset (2000/class)](https://www.kaggle.com/datasets/zlatan599/garbage-dataset-classification) — plastic class
- [Garbage Classification / TrashNet](https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification) — plastic class
- [Drinking Waste Classification](https://www.kaggle.com/datasets/arkadiyhacks/drinking-waste-classification) — PET/HDPE
- [Seaclear Marine Debris](https://www.kaggle.com/datasets/jocelyndumlao/seaclear-marine-debris-detection-and-segmentation)
- [Marine Debris Dataset](https://www.kaggle.com/datasets/sovitrath/marine-debris-dataset)

### One-time Kaggle API setup

1. Create a free Kaggle account (if needed).
2. Open [Kaggle Settings → API](https://www.kaggle.com/settings) and click **Create New Token**.
3. Save the downloaded `kaggle.json` to:

```text
C:\Users\<you>\.kaggle\kaggle.json
```

4. On each dataset page above, click **Download** once if prompted to accept the license/rules.

### Run Week 1

```powershell
cd Plastic-Pulse-Ocean-Tracker
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/run_week1.py
```

Or step-by-step:

```powershell
python scripts/curate_dataset.py --per-class 2500 --force
python scripts/preprocess_and_augment.py --augments-per-image 6
```

### Project layout

```text
Plastic-Pulse-Ocean-Tracker/
├── data/
│   ├── kaggle_cache/      # downloaded Kaggle zips/extracts
│   ├── raw/               # curated 2500/class
│   ├── processed/         # 224×224 cleaned
│   └── augmented/         # cleaned + flips/rotations (training set)
├── notebooks/
│   └── week1_data_foundations.ipynb
├── outputs/
│   ├── week1_augmentation_preview.png
│   ├── week1_dataset_summary.json
│   └── week1_data_sources.json
├── scripts/
│   ├── curate_dataset.py
│   ├── preprocess_and_augment.py
│   └── run_week1.py
└── requirements.txt
```

## Week 2 — Pretrained Feature Extractor + Custom Head

**Focus:** Transfer learning model architecture.

| Task | Status |
|------|--------|
| Implement pretrained MobileNetV2 / ResNet50 | Done |
| Use backbone as frozen feature extractor | Done |
| Custom head for Marine Life vs Plastic Debris | Done |
| Compile + inspect architecture | Done |

### Architecture

- **Backbone:** ImageNet-pretrained `MobileNetV2` (default) or `ResNet50` — **frozen**
- **Head:** `GlobalAveragePooling2D → Dropout → Dense(128, ReLU) → Dropout → Dense(1, sigmoid)`
- **Loss / metrics:** binary cross-entropy; accuracy, precision, recall, AUC
- **Labels:** `0 = marine_life`, `1 = plastic_debris`

### Build & inspect

```powershell
pip install -r requirements.txt
python scripts/build_model.py --backbone mobilenetv2 --save
# optional:
python scripts/build_model.py --backbone resnet50 --save
```

Artifacts land in `outputs/week2/` (summary `.txt`, architecture `.json`, optional plot) and the compiled model in `models/saved/`.

Notebook: `notebooks/week2_model_architecture.ipynb`

### Loading the Week 1 deliverable for training

```python
from pathlib import Path
import numpy as np
from PIL import Image

aug = Path("data/augmented")
X, y = [], []
for label, name in enumerate(["marine_life", "plastic_debris"]):
    for jpg in (aug / name).glob("*.jpg"):
        # Model Lambda layer expects roughly 0–255 RGB; do NOT divide here.
        arr = np.asarray(Image.open(jpg).convert("RGB"), dtype=np.float32)
        X.append(arr)
        y.append(label)

X = np.stack(X)  # (N, 224, 224, 3)
y = np.array(y)
```

## Week 3 — Train, Monitor, Evaluate

**Focus:** Fit the custom head, track train/val curves, evaluate on held-out test data, diagnose fit.

| Task | Status |
|------|--------|
| Train on prepared augmented dataset | Done |
| Monitor training & validation accuracy / loss | Done |
| Plot accuracy and loss graphs | Done |
| Evaluate on unseen test data | Done |
| Check overfitting / underfitting | Done (`good_fit`) |

### How it was trained

- **Split:** 70% / 15% / 15% by **source stem** (all 6 augmentations of one image stay in the same split — no leakage)
- **Backbone:** frozen MobileNetV2 (features cached once, then head trained — same math as end-to-end with a frozen extractor)
- **Callbacks:** EarlyStopping (`val_loss`, patience 4), ReduceLROnPlateau, CSV log
- **Best weights restored** from epoch 6

### Results (test set, 4,500 images — after tuning)

| Metric | Value |
|--------|------:|
| Accuracy | **99.47%** |
| Precision | 99.29% |
| Recall | 99.64% |
| F1 | 99.47% |
| AUC | 0.999 |
| Confusion | 2234 / 16 · 8 / 2242 |

**Fit check:** train/val accuracy gap ≈ **+0.001** → **good fit**. Best hyperparams from experiments: **dropout 0.5**, batch **64**, lr **1e-3**.

### Run Week 3

```powershell
pip install -r requirements.txt
python scripts/train_model.py --epochs 20 --batch-size 64 --dropout 0.5
# compare knobs:
python scripts/run_experiments.py
```

Artifacts: `outputs/week3/` (curves, confusion matrix, `WEEK3_REPORT.md`, JSON) and `models/saved/PlasticPulse_mobilenetv2_trained.keras`.

### Hyperparameter experiments

Ran 12 controlled runs (`scripts/run_experiments.py`) varying LR, batch size, dropout, epoch budget, and augmentation.

**Best on the fair full-aug test set (4,500 images):** `dropout=0.5`, `lr=1e-3`, `batch=64`, early stopping — **test acc 0.9949**.

Report: [`outputs/week3/experiments/EXPERIMENT_REPORT.md`](outputs/week3/experiments/EXPERIMENT_REPORT.md)

## Week 4 — OpenCV integration & live detection

Integrates the trained classifier with **OpenCV**: contour-based bounding boxes, label + confidence overlay, dashboard screenshots.

```powershell
# Held-out test images (default: 8 __orig samples)
python scripts/opencv_detect.py

# Webcam demo (Q quit, S save screenshot)
python scripts/opencv_detect.py --webcam

# Matplotlib grid for recording
python scripts/predict_demo.py --show

# Retrain for 100% train accuracy (trade-off: slightly lower test)
python scripts/train_model.py --epochs 30 --batch-size 64 --dropout 0.2
```

| Artifact | Path |
|----------|------|
| OpenCV script | `scripts/opencv_detect.py` |
| Dashboard | `outputs/week4/opencv/opencv_dashboard.jpg` |
| Report | `outputs/week4/WEEK4_REPORT.md` |

**OpenCV batch:** 8/8 correct on held-out test stems. **Retrain** (`dropout=0.2`): train **100%**, test **99.38%**.
