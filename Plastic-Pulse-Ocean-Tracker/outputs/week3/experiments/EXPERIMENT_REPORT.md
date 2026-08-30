# Week 3 — Hyperparameter & Augmentation Experiments

Plastic-Pulse Ocean Tracker · frozen MobileNetV2 features + trainable Dense head

Same stem-level **70 / 15 / 15** split (seed 42) for every run. EarlyStopping restores best `val_loss` weights.

> **Compare carefully:** runs with `aug=all` share the same 4,500-image test set.  
> `aug_orig` / `aug_flips` / `aug_light` use fewer images per split, so their absolute test accuracy is not perfectly comparable to the full-aug baseline — use them as an **augmentation ablation**, not a raw leaderboard.

## Results table

| Experiment | LR | Batch | Dropout | Aug | Epochs ran | Val acc | Test acc | Test F1 | Train−val gap | Val loss | Test N |
|------------|---:|------:|--------:|-----|----------:|--------:|---------:|--------:|--------------:|---------:|-------:|
| `baseline` | 0.001 | 64 | 0.3 | all (6) | 9 | 0.9973 | 0.9942 | 0.9942 | +0.0010 | 0.0111 | 4500 |
| `lr_1e-2` | 0.01 | 64 | 0.3 | all | 8 | 0.9973 | 0.9944 | 0.9945 | +0.0000 | 0.0102 | 4500 |
| `lr_1e-4` | 0.0001 | 64 | 0.3 | all | 15 | 0.9962 | 0.9933 | 0.9933 | +0.0020 | 0.0107 | 4500 |
| `batch_32` | 0.001 | 32 | 0.3 | all | 5 | 0.9960 | 0.9933 | 0.9933 | −0.0063 | 0.0129 | 4500 |
| `batch_128` | 0.001 | 128 | 0.3 | all | 7 | 0.9962 | 0.9927 | 0.9927 | +0.0011 | 0.0093 | 4500 |
| `dropout_0` | 0.001 | 64 | 0.0 | all | 6 | 0.9964 | 0.9922 | 0.9922 | +0.0022 | 0.0139 | 4500 |
| `dropout_0.5` | 0.001 | 64 | **0.5** | all | 13 | 0.9969 | **0.9949** | 0.9949 | +0.0003 | **0.0086** | 4500 |
| `epochs_5` | 0.001 | 64 | 0.3 | all | 5 | 0.9973 | 0.9942 | 0.9942 | +0.0010 | 0.0111 | 4500 |
| `epochs_30` | 0.001 | 64 | 0.3 | all | 9 | 0.9973 | 0.9942 | 0.9942 | +0.0010 | 0.0111 | 4500 |
| `aug_orig` | 0.001 | 64 | 0.3 | orig only | 9 | 0.9987 | 0.9933 | 0.9933 | −0.0001 | 0.0086 | 750 |
| `aug_flips` | 0.001 | 64 | 0.3 | orig+h/vflip | 5 | 0.9982 | 0.9951 | 0.9951 | −0.0185 | 0.0090 | 2250 |
| `aug_light` | 0.001 | 64 | 0.3 | +rot15 | 5 | 0.9977 | 0.9933 | 0.9933 | −0.0125 | 0.0086 | 3000 |

## Ranking (full-aug only — fair comparison)

| Rank | Experiment | Test acc | Notes |
|-----:|------------|---------:|-------|
| 1 | **`dropout_0.5`** | **0.9949** | Best among same test set; lowest val loss |
| 2 | `lr_1e-2` | 0.9944 | Slightly above baseline; watch stability |
| 3 | `baseline` / `epochs_5` / `epochs_30` | 0.9942 | Early stopping makes 5 vs 30 equivalent |
| 4 | `lr_1e-4` / `batch_32` | 0.9933 | Slower LR or noisier batches |
| 5 | `batch_128` | 0.9927 | Faster epochs, slightly worse gen. |
| 6 | `dropout_0` | 0.9922 | Worst — no regularization hurts |

## What worked best

### Recommended production settings (full 6-variant dataset)

| Knob | Best value | Why |
|------|------------|-----|
| **Learning rate** | `1e-3` (or `1e-2` with ReduceLROnPlateau) | `1e-3` is stable; `1e-2` edged +0.0002 but `1e-4` was slower/worse |
| **Batch size** | **64** | Beat 32 and 128 on the fair test set |
| **Dropout** | **0.5** | Best test acc + lowest val loss among full-aug runs |
| **Epochs** | **20 with early stopping** (patience 4) | Same result as 5 or 30 once best weights are restored |
| **Augmentation** | Keep **all 6 variants** for training volume; flips alone were competitive in the ablation | Orig-only was slightly weaker; full set remains the robust default |

### Learning rate

- **`1e-2`:** test 0.9944 (+0.0002 vs baseline) — OK with LR scheduling  
- **`1e-3`:** strong default  
- **`1e-4`:** test 0.9933 (−0.0009) — needs more epochs; not worth it here  

### Batch size

- **64 best** among {32, 64, 128}  
- 32: noisier, stopped early  
- 128: slightly worse test accuracy  

### Dropout

- **0.5 best** (test 0.9949, val loss 0.0086)  
- 0.3 baseline: 0.9942  
- 0.0 worst: 0.9922 — confirms regularization helps  

### Epochs

- With early stopping, requesting 5 / 20 / 30 converged to the **same** restored checkpoint for the baseline config  
- Prefer a generous max epoch + early stop over a hard short budget  

### Data augmentation ablation

| Mode | Train images | Test acc | Takeaway |
|------|-------------:|---------:|----------|
| orig only | 3,500 | 0.9933 | Already strong (MobileNetV2 features) |
| flips (orig+h+v) | 10,500 | 0.9951* | Strong; *smaller test set |
| light (+rot15) | 14,000 | 0.9933* | No clear gain over flips |
| all 6 variants | 21,000 | 0.9942–0.9949 | Best fair full-pipeline setting with dropout 0.5 |

Rotations (±15°, +30°) did not clearly beat flips-only in this ablation; they still add diversity for drone viewpoints, so **keeping all 6 for the main model is reasonable**. The biggest hyperparameter win on the full set was **raising dropout to 0.5**.

## Plots

- `comparison_accuracy.png` — val vs test accuracy by experiment  
- `comparison_loss_gap.png` — val loss & train/val gap  
- `comparison_lr_val_loss.png` — LR family val-loss curves  

## Reproduce

```powershell
cd Plastic-Pulse-Ocean-Tracker
.\.venv\Scripts\Activate.ps1
python scripts/run_experiments.py
```

Train the recommended full-data model:

```powershell
python scripts/train_model.py --epochs 20 --batch-size 64 --dropout 0.5 --learning-rate 0.001
```
