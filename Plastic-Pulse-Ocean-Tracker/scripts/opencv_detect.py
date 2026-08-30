"""
Week 4 — OpenCV integration for Plastic-Pulse inference.

Loads the trained classifier, finds a subject region with OpenCV, draws a
bounding box, and overlays the class label + confidence. Supports still
images, folders, and optional webcam/video input.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from inference_common import (
    DEFAULT_MODEL,
    LABEL_DISPLAY,
    load_inference_model,
    predict_rgb,
    test_split_orig_samples,
)

OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "week4" / "opencv"

# BGR colors for OpenCV drawing
COLOR_MARINE = (86, 180, 60)
COLOR_PLASTIC = (40, 120, 255)
COLOR_TEXT_BG = (20, 20, 20)


def find_subject_box(bgr: np.ndarray) -> tuple[int, int, int, int]:
    """
    Estimate a bounding box around the main subject using OpenCV contours.
    Falls back to a padded full-frame box when contour detection is weak.
    """
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, 40, 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        if area >= 0.04 * h * w:
            x, y, bw, bh = cv2.boundingRect(cnt)
            pad = int(0.06 * max(bw, bh))
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(w, x + bw + pad)
            y2 = min(h, y + bh + pad)
            return x1, y1, x2, y2

    margin = int(0.04 * min(h, w))
    return margin, margin, w - margin, h - margin


def annotate_frame(
    bgr: np.ndarray,
    model,
    box: tuple[int, int, int, int] | None = None,
    true_class: str | None = None,
) -> tuple[np.ndarray, dict]:
    """Classify ROI, draw rectangle + label, return annotated BGR + metadata."""
    x1, y1, x2, y2 = box if box is not None else find_subject_box(bgr)
    roi_bgr = bgr[y1:y2, x1:x2]
    roi_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
    pred = predict_rgb(model, roi_rgb)

    color = COLOR_PLASTIC if pred["label"] == "plastic_debris" else COLOR_MARINE
    out = bgr.copy()
    cv2.rectangle(out, (x1, y1), (x2, y2), color, thickness=3)

    label_line = f"{pred['label_display']}  {pred['confidence']:.1%}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = max(0.55, min(1.0, out.shape[1] / 900))
    thickness = 2
    (tw, th), baseline = cv2.getTextSize(label_line, font, scale, thickness)
    ty = max(th + 8, y1 - 8)
    if ty - th - 8 < 0:
        ty = y1 + th + 12
    cv2.rectangle(out, (x1, ty - th - 6), (x1 + tw + 10, ty + baseline), COLOR_TEXT_BG, -1)
    cv2.putText(out, label_line, (x1 + 5, ty), font, scale, color, thickness, cv2.LINE_AA)

    meta = {
        **pred,
        "box": [int(x1), int(y1), int(x2), int(y2)],
        "true_class": true_class,
        "correct": true_class == pred["label"] if true_class else None,
    }
    return out, meta


def process_image(path: Path, model, out_dir: Path) -> dict:
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise FileNotFoundError(f"Could not read image: {path}")

    true_class = path.parent.name if path.parent.name in LABEL_DISPLAY else None
    annotated, meta = annotate_frame(bgr, model, true_class=true_class)
    meta["source"] = str(path)
    meta["filename"] = path.name

    out_path = out_dir / f"annotated_{path.stem}.jpg"
    cv2.imwrite(str(out_path), annotated)
    meta["annotated_path"] = str(out_path)
    return meta


def build_dashboard(results: list[dict], out_path: Path, cols: int = 4) -> None:
    """Tile annotated outputs into one dashboard screenshot."""
    images: list[np.ndarray] = []
    for r in results:
        img = cv2.imread(r["annotated_path"])
        if img is not None:
            images.append(img)

    if not images:
        return

    target_w = 480
    resized = []
    for img in images:
        h, w = img.shape[:2]
        scale = target_w / w
        resized.append(cv2.resize(img, (target_w, int(h * scale))))

    rows = (len(resized) + cols - 1) // cols
    row_heights = []
    for row_idx in range(rows):
        row_imgs = resized[row_idx * cols : (row_idx + 1) * cols]
        row_heights.append(max(im.shape[0] for im in row_imgs))

    canvas_h = sum(row_heights) + 60
    canvas_w = cols * target_w
    canvas = np.full((canvas_h, canvas_w, 3), 245, dtype=np.uint8)

    title = "Plastic-Pulse OpenCV Dashboard — Marine Life vs Plastic Debris"
    cv2.putText(
        canvas,
        title,
        (16, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (30, 30, 30),
        2,
        cv2.LINE_AA,
    )

    y = 50
    for row_idx in range(rows):
        row_imgs = resized[row_idx * cols : (row_idx + 1) * cols]
        row_h = row_heights[row_idx]
        x = 0
        for img in row_imgs:
            ih, iw = img.shape[:2]
            canvas[y : y + ih, x : x + iw] = img
            x += target_w
        y += row_h

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)


def run_webcam(model, camera_id: int = 0, save_path: Path | None = None) -> None:
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {camera_id}")

    print("Webcam running — press Q to quit, S to save screenshot")
    saved = False
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        annotated, _ = annotate_frame(frame, model)
        cv2.imshow("Plastic-Pulse OpenCV", annotated)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s") and save_path and not saved:
            cv2.imwrite(str(save_path), annotated)
            print(f"Saved screenshot: {save_path}")
            saved = True

    cap.release()
    cv2.destroyAllWindows()


def run_video(model, video_path: Path, out_path: Path, max_frames: int = 0) -> None:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(out_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h),
    )

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        annotated, _ = annotate_frame(frame, model)
        writer.write(annotated)
        frame_idx += 1
        if max_frames and frame_idx >= max_frames:
            break

    cap.release()
    writer.release()
    print(f"Saved annotated video: {out_path} ({frame_idx} frames)")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenCV detection demo for Plastic-Pulse")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument(
        "--images",
        nargs="*",
        type=Path,
        help="Image paths (default: held-out test __orig samples)",
    )
    parser.add_argument("--folder", type=Path, help="Run on all images in a folder")
    parser.add_argument("--webcam", action="store_true", help="Live webcam demo")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--video", type=Path, help="Annotate a video file")
    parser.add_argument("--per-class", type=int, default=4, help="Test samples per class")
    parser.add_argument("--out-dir", type=Path, default=OUTPUTS_DIR)
    parser.add_argument("--dashboard", type=Path, default=OUTPUTS_DIR / "opencv_dashboard.jpg")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "outputs" / "week4" / "opencv_results.json")
    args = parser.parse_args()

    if not args.model.is_file() and not (PROJECT_ROOT / "models" / "saved" / "PlasticPulse_mobilenetv2_head.keras").is_file():
        raise FileNotFoundError(
            f"Trained model not found. Run:\n"
            "  python scripts/train_model.py --epochs 30 --batch-size 64 --dropout 0.2"
        )

    print(f"Loading model: {args.model}")
    model = load_inference_model(args.model)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.webcam:
        run_webcam(model, args.camera, args.out_dir / "webcam_screenshot.jpg")
        return

    if args.video:
        out_video = args.out_dir / f"annotated_{args.video.stem}.mp4"
        run_video(model, args.video, out_video)
        return

    paths: list[Path] = []
    if args.images:
        paths = [p for p in args.images if p.is_file()]
    elif args.folder:
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        paths = sorted(p for p in args.folder.iterdir() if p.suffix.lower() in exts)
    else:
        paths = test_split_orig_samples(per_class=args.per_class)

    if not paths:
        raise FileNotFoundError("No images to process.")

    print(f"Processing {len(paths)} image(s) with OpenCV...")
    results: list[dict] = []
    for path in paths:
        meta = process_image(path, model, args.out_dir)
        mark = ""
        if meta.get("correct") is True:
            mark = "OK"
        elif meta.get("correct") is False:
            mark = "MISS"
        print(
            f"  [{mark}] {path.name}: {meta['label_display']} "
            f"({meta['confidence']:.1%}) box={meta['box']}"
        )
        results.append(meta)

    build_dashboard(results, args.dashboard)
    print(f"\nSaved dashboard: {args.dashboard}")

    known = [r for r in results if r.get("correct") is not None]
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_images": len(results),
        "n_with_labels": len(known),
        "accuracy": (
            sum(1 for r in known if r["correct"]) / len(known) if known else None
        ),
        "results": results,
        "dashboard": str(args.dashboard),
        "out_dir": str(args.out_dir),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved JSON report: {args.report}")

    if known:
        acc = summary["accuracy"]
        print(f"\nLabeled batch accuracy: {acc:.0%} ({sum(1 for r in known if r['correct'])}/{len(known)})")


if __name__ == "__main__":
    main()
