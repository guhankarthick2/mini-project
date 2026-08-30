# Week 3 — Training & Evaluation Report

**Plastic-Pulse Ocean Tracker** · backbone `mobilenetv2` (frozen) + custom Dense head

## Dataset split (stem-level, no augmentation leakage)

| Split | Stems | Images | marine_life | plastic_debris |
|-------|------:|-------:|------------:|---------------:|
| Train | 3500 | 21000 | 10500 | 10500 |
| Val   | 750 | 4500 | 2250 | 2250 |
| Test  | 750 | 4500 | 2250 | 2250 |

## Training

- Epochs ran: **12** (requested 30; early stopping on `val_loss`)
- Final train accuracy / loss: **1.0000** / **0.0002**
- Final val accuracy / loss: **0.9969** / **0.0129**
- Best val accuracy: **0.9976** (epoch 6)

Plots: `accuracy_curve.png`, `loss_curve.png`, `train_val_curves.png`

## Test set (unseen)

| Metric | Value |
|--------|------:|
| Accuracy | 0.9938 |
| Precision | 0.9916 |
| Recall | 0.9960 |
| F1 | 0.9938 |
| AUC | 0.9985455802469135 |
| Loss | 0.0518 |

Confusion matrix:

```
[[2231, 19], [9, 2241]]
```

## Overfitting / underfitting

**Status: `good_fit`**

Train/val gap is small (+0.003), val accuracy 0.997, test accuracy 0.994 — generalization looks healthy.

Train−val accuracy gap: **+0.0031**

## Artifacts

- Trained model: `PlasticPulse_mobilenetv2_trained.keras`
- Results JSON: `week3_training_results.json`
- CSV log: `training_log.csv`
