# Plastic-Pulse Ocean Tracker — Augmented Training Set

Binary image set for **Marine Life vs Plastic Debris**.

| Item | Value |
|------|--------|
| Images | 30,000 JPEG (15,000 per class) |
| Size | 224×224 RGB |
| Labels | `marine_life` = 0 · `plastic_debris` = 1 |
| Augmentation | original, hflip, vflip, +15°, −15°, +30° (6× each of 2,500 curated images/class) |

## Layout

```text
README.md
augmented/marine_life/*.jpg
augmented/plastic_debris/*.jpg
```

Filenames look like `{source_stem}__{orig|hflip|vflip|rot15|rot_neg15|rot30}.jpg`.

## Load with Keras

JPEGs are uint8. The Plastic-Pulse MobileNetV2 model applies official preprocess internally, so pass **0–255** RGB (do **not** divide by 255 before `fit` / `predict`).

```python
from tensorflow.keras.utils import image_dataset_from_directory

ds = image_dataset_from_directory(
    "augmented",
    labels="inferred",
    label_mode="binary",
    class_names=["marine_life", "plastic_debris"],  # 0, 1
    image_size=(224, 224),
    batch_size=32,
    shuffle=True,
)
```

When building tensors yourself, `/255` yields **[0, 1]** float images (used for Week 1 QA only).

## Source datasets (Kaggle)

This pack is a **curated, resized, augmented derivative**. Original licenses stay with the authors.

**Marine life**

- https://www.kaggle.com/datasets/vencerlanz09/sea-animals-image-dataste
- https://www.kaggle.com/datasets/mikoajfish99/marine-animal-images

**Plastic debris** (plastic / PET / HDPE classes only)

- https://www.kaggle.com/datasets/zlatan599/garbage-dataset-classification
- https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification
- https://www.kaggle.com/datasets/arkadiyhacks/drinking-waste-classification

Project: https://github.com/guhankarthick2/Plastic-Pulse-Ocean-Tracker  
Download: https://github.com/guhankarthick2/Plastic-Pulse-Ocean-Tracker/releases/download/week1-augmented-dataset/PlasticPulse_augmented_dataset.zip
