# Week 4 — OpenCV Integration & Live Detection

**Plastic-Pulse Ocean Tracker** · Marine Life vs Plastic Debris

## Goal

Integrate the trained Keras classifier with **OpenCV** for real-world inference: draw bounding boxes around detected subjects, overlay class labels with confidence scores, and save dashboard screenshots for submission.

---

## What was built

| Artifact | Description |
|----------|-------------|
| `scripts/opencv_detect.py` | OpenCV pipeline: ROI detection → classify → annotate → save |
| `scripts/inference_common.py` | Shared model loader + prediction helpers |
| `outputs/week4/opencv/` | Per-image annotated JPGs |
| `outputs/week4/opencv/opencv_dashboard.jpg` | Combined dashboard screenshot |
| `outputs/week4/opencv_results.json` | Machine-readable run summary |

### How it works

1. **Load model** — frozen MobileNetV2 + trained Dense head (rebuilds from head weights if full `.keras` fails to deserialize).
2. **Find subject region (OpenCV)** — Canny edges + morphological closing → largest contour → padded bounding rectangle. Falls back to a margin inset around the full frame when contours are weak.
3. **Classify ROI** — crop inside the box, resize to 224×224, run `model.predict` (MobileNetV2 preprocess runs inside the model).
4. **Annotate** — draw colored rectangle (green = Marine Life, orange = Plastic Debris), label bar with human-readable name + confidence %.
5. **Save** — individual `annotated_*.jpg` files plus a tiled `opencv_dashboard.jpg`.

### Commands

```powershell
# Default: 8 held-out test images (__orig only, never used in training)
python scripts/opencv_detect.py

# Custom images or folder
python scripts/opencv_detect.py --images path/to/a.jpg path/to/b.jpg
python scripts/opencv_detect.py --folder path/to/folder

# Webcam (press Q to quit, S to save screenshot)
python scripts/opencv_detect.py --webcam

# Video file
python scripts/opencv_detect.py --video path/to/clip.mp4
```

---

## Test images (unseen)

Samples were drawn from the **held-out test split** only (`__orig.jpg` stems — one per source image, never seen during training). Four marine + four plastic images.

### Results (initial model, dropout 0.5)

| Image | True class | Prediction | Confidence | Correct |
|-------|------------|------------|------------|---------|
| marine_life_00002__orig.jpg | marine_life | Marine Life | 100.0% | ✓ |
| marine_life_00008__orig.jpg | marine_life | Marine Life | 100.0% | ✓ |
| marine_life_00013__orig.jpg | marine_life | Marine Life | 100.0% | ✓ |
| marine_life_00014__orig.jpg | marine_life | Marine Life | 100.0% | ✓ |
| plastic_debris_00012__orig.jpg | plastic_debris | Plastic Debris | 100.0% | ✓ |
| plastic_debris_00014__orig.jpg | plastic_debris | Plastic Debris | 100.0% | ✓ |
| plastic_debris_00026__orig.jpg | plastic_debris | Plastic Debris | 100.0% | ✓ |
| plastic_debris_00027__orig.jpg | plastic_debris | Plastic Debris | 100.0% | ✓ |

**OpenCV batch accuracy: 8/8 (100%)**

All predictions were high-confidence (≥99.9%). Bounding boxes tracked the main subject via edge/contour detection; plastic debris with cluttered backgrounds sometimes received a near-full-frame box (expected for whole-image classifiers without a dedicated object detector).

---

## Observations

### What works well

- **Transfer learning generalizes** — even on unseen `__orig` test stems, the model labels correctly with very high confidence.
- **OpenCV ROI + classifier** — contour-based boxes give a convincing “detection” UI for internship demos without training YOLO/Faster R-CNN.
- **Consistent preprocessing** — uint8 RGB input with in-model MobileNetV2 preprocess avoids the common `/255` mistake.

### Limitations

- This is an **image classifier**, not an object detector. One box per frame assumes a single dominant subject; multi-object scenes would need a detection model or sliding-window search.
- **Bounding boxes are heuristic** (edges/contours), not learned. Unusual crops or empty water backgrounds may get a full-frame box.
- **24 errors remain on the full 4,500-image test set** (99.47% accuracy) — mostly near-boundary cases and visually similar marine/plastic textures.

### Improvements applied (training accuracy priority)

| Change | Rationale |
|--------|-----------|
| Retrain with **dropout 0.2** (was 0.5) | Less regularization → head can fit training data more tightly |
| **30 epochs** (was 14 early-stopped) | More capacity to converge toward 100% train accuracy |
| Keep **frozen MobileNetV2** + cached features | Fast iteration on CPU; same pipeline as Week 3 |
| EarlyStopping + ReduceLROnPlateau | Still guard against val loss spikes |

### Retrain results (`dropout=0.2`, early stop @ epoch 12)

| Metric | Before (dropout 0.5) | After (dropout 0.2) |
|--------|---------------------:|--------------------:|
| Train accuracy (final) | 99.87% | **100.00%** |
| Val accuracy (final) | 99.76% | 99.69% |
| Test accuracy | **99.47%** | 99.38% |
| Test errors | 24 / 4,500 | 28 / 4,500 |

Train accuracy reached **100%** on the final epoch batches; early stopping restored best val-loss weights from epoch 8. Test dropped slightly (~0.1 pp) — the expected trade-off when prioritizing train fit over dropout regularization.

> **Recommendation:** Use **dropout 0.5** for best test generalization (internship default). Use **dropout 0.2** when the rubric emphasizes maximizing training accuracy.

---

## Screenshots (submission)

| File | Description |
|------|-------------|
| `outputs/week4/opencv/opencv_dashboard.jpg` | Main dashboard — all 8 annotated images |
| `outputs/week4/opencv/annotated_*.jpg` | Individual annotated outputs |
| `outputs/week4/demo_predictions.png` | Matplotlib grid demo (`predict_demo.py`) |

---

## Next steps (optional)

- Fine-tune top MobileNetV2 layers with a very low learning rate (`1e-5`) for harder misclassified pairs.
- Export **TFLite** or **SavedModel** for edge deployment.
- Replace contour ROI with a lightweight detector (MobileNet-SSD) if true multi-box detection is required.
