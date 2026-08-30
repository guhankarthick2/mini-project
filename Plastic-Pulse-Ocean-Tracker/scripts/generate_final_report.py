#!/usr/bin/env python3
"""Generate the final internship PDF report for Plastic-Pulse Ocean Tracker."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "outputs" / "FINAL_INTERNSHIP_REPORT.pdf"
OUT_HTML = ROOT / "outputs" / "FINAL_INTERNSHIP_REPORT.html"

# --- Edit these if needed before submission ---
STUDENT_NAME = "Guhan Karthick"
PROJECT_TITLE = "Plastic-Pulse Ocean Tracker"
MENTOR_NAME = "Virtual Internship Program Mentor"
INTERNSHIP_DURATION = "4 Weeks (August 2026)"
SUBMISSION_DATE = date.today().strftime("%B %d, %Y")

IMG = {
    "dashboard": ROOT / "outputs/week3/presentation/graph_summary_dashboard.png",
    "acc": ROOT / "outputs/week3/presentation/graph_accuracy_epochs.png",
    "loss": ROOT / "outputs/week3/presentation/graph_loss_epochs.png",
    "cm": ROOT / "outputs/week3/presentation/graph_confusion_matrix.png",
    "test": ROOT / "outputs/week3/presentation/graph_test_metrics.png",
    "exp": ROOT / "outputs/week3/presentation/graph_experiment_accuracy.png",
    "opencv": ROOT / "outputs/week4/opencv/opencv_dashboard.jpg",
    "demo": ROOT / "outputs/week4/demo_predictions.png",
}


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontSize=26,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0f4c75"),
            spaceAfter=14,
        ),
        "subtitle": ParagraphStyle(
            "CoverSub",
            parent=base["Normal"],
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1b4965"),
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f4c75"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1b4965"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10.5,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=10.5,
            leading=14,
            leftIndent=14,
            bulletIndent=0,
            spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontSize=8.5,
            leading=10,
            fontName="Courier",
            backColor=colors.HexColor("#f4f6f8"),
            leftIndent=8,
            rightIndent=8,
            spaceAfter=8,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=10,
        ),
        "toc": ParagraphStyle(
            "TOC",
            parent=base["Normal"],
            fontSize=11,
            leading=16,
            leftIndent=12,
        ),
    }


def img_block(path: Path, width: float = 6.5 * inch, caption: str = "") -> list:
    if not path.exists():
        return [Paragraph(f"[Missing image: {path.name}]", styles()["caption"])]
    im = Image(str(path))
    ratio = im.imageHeight / im.imageWidth
    im.drawWidth = width
    im.drawHeight = width * ratio
    if im.drawHeight > 7.5 * inch:
        im.drawHeight = 7.5 * inch
        im.drawWidth = im.drawHeight / ratio
    block = [Spacer(1, 6), im]
    if caption:
        block.append(Paragraph(caption, styles()["caption"]))
    return block


def cover(st):
    rows = [
        [Paragraph(PROJECT_TITLE, st["title"])],
        [Spacer(1, 0.3 * inch)],
        [Paragraph("Final Internship Project Report", st["subtitle"])],
        [Spacer(1, 0.6 * inch)],
        [Paragraph(f"<b>Student Name:</b> {STUDENT_NAME}", st["subtitle"])],
        [Paragraph(f"<b>Internship Duration:</b> {INTERNSHIP_DURATION}", st["subtitle"])],
        [Paragraph(f"<b>Mentor:</b> {MENTOR_NAME}", st["subtitle"])],
        [Paragraph(f"<b>Submission Date:</b> {SUBMISSION_DATE}", st["subtitle"])],
        [Spacer(1, 0.8 * inch)],
        [
            Paragraph(
                "Binary computer-vision classifier: <b>Marine Life</b> vs <b>Plastic Debris</b><br/>"
                "for ocean-monitoring autonomous drones",
                st["subtitle"],
            )
        ],
    ]
    t = Table([[r[0]] for r in rows], colWidths=[6.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return [Spacer(1, 1.2 * inch), t, PageBreak()]


def toc(st):
    items = [
        "1. Cover Page",
        "2. Table of Contents",
        "3. Introduction",
        "4. Dataset",
        "5. Methodology",
        "6. Implementation",
        "7. Results",
        "8. Challenges &amp; Learnings",
        "9. Conclusion &amp; Future Scope",
        "10. References",
        "11. Appendix",
    ]
    flow = [Paragraph("Table of Contents", st["h1"]), Spacer(1, 8)]
    for item in items:
        flow.append(Paragraph(item, st["toc"]))
    flow.append(PageBreak())
    return flow


def section_intro(st):
    return [
        Paragraph("3. Introduction", st["h1"]),
        Paragraph("Problem Statement", st["h2"]),
        Paragraph(
            "Ocean plastic pollution threatens marine ecosystems, while autonomous cleanup drones must "
            "avoid harming living animals. Manual monitoring does not scale across vast coastlines and "
            "open water. A reliable visual system is needed to distinguish <b>marine life</b> from "
            "<b>plastic debris</b> in underwater or surface imagery so drones can collect waste safely.",
            st["body"],
        ),
        Paragraph("Project Objective", st["h2"]),
        Paragraph(
            "Build a lightweight deep-learning image classifier using transfer learning that:",
            st["body"],
        ),
        Paragraph("• Curates a balanced, augmented training dataset from public Kaggle sources.", st["bullet"]),
        Paragraph("• Trains a frozen MobileNetV2 backbone with a custom binary classification head.", st["bullet"]),
        Paragraph("• Achieves high accuracy on held-out test data with diagnosed good generalization.", st["bullet"]),
        Paragraph("• Integrates with OpenCV for annotated bounding boxes and live demo screenshots.", st["bullet"]),
        Paragraph("Real-world Application", st["h2"]),
        Paragraph(
            "The model supports <b>Plastic-Pulse Ocean Tracker</b> — a drone-assist pipeline where "
            "cameras classify each frame before actuators trigger collection. Correctly ignoring fish, "
            "turtles, and other marine life while targeting bottles, bags, and floating debris reduces "
            "ecological harm. The MobileNetV2 design (~2.4M parameters, ~641 KB trainable head) is "
            "suitable for edge deployment on low-power drone hardware.",
            st["body"],
        ),
        PageBreak(),
    ]


def section_dataset(st):
    return [
        Paragraph("4. Dataset", st["h1"]),
        Paragraph("Source", st["h2"]),
        Paragraph(
            "Images were curated from free public Kaggle datasets (licenses remain with original authors). "
            "Scripts <font name='Courier'>curate_dataset.py</font> and "
            "<font name='Courier'>preprocess_and_augment.py</font> automate download, filtering, and balancing.",
            st["body"],
        ),
        Paragraph("<b>Marine life sources</b> (2,500 kept from 13,936 candidates):", st["body"]),
        Paragraph("• Sea Animals Image Dataset — 2,342 images", st["bullet"]),
        Paragraph("• Marine Animal Images — 158 images", st["bullet"]),
        Paragraph("<b>Plastic debris sources</b> (2,500 kept from 4,503 plastic-class candidates):", st["body"]),
        Paragraph("• Drinking Waste Classification (PET/HDPE) — 1,516", st["bullet"]),
        Paragraph("• Garbage Images Dataset (plastic class) — 818", st["bullet"]),
        Paragraph("• Garbage Classification / TrashNet (plastic class) — 166", st["bullet"]),
        Paragraph(
            "Published training zip: GitHub Release "
            "<i>PlasticPulse_augmented_dataset.zip</i> (~368 MB, 30,000 JPEGs).",
            st["body"],
        ),
        Paragraph("Classes", st["h2"]),
        Paragraph(
            "Binary classification: <b>marine_life</b> (label 0) and <b>plastic_debris</b> (label 1). "
            "Each class was balanced at every pipeline stage.",
            st["body"],
        ),
        Table(
            [
                ["Stage", "marine_life", "plastic_debris", "Total"],
                ["Curated raw", "2,500", "2,500", "5,000"],
                ["Processed (224×224)", "2,500", "2,500", "5,000"],
                ["Augmented training set", "15,000", "15,000", "30,000"],
            ],
            colWidths=[2.2 * inch, 1.2 * inch, 1.2 * inch, 0.9 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ]
            ),
        ),
        Spacer(1, 10),
        Paragraph("Pre-processing", st["h2"]),
        Paragraph("• Convert all images to RGB.", st["bullet"]),
        Paragraph("• Resize to 224×224 with aspect-preserving letterbox (black padding).", st["bullet"]),
        Paragraph("• Save as JPEG (quality 92) for the training corpus.", st["bullet"]),
        Paragraph(
            "• Augmentation: 6 variants per source — original, horizontal flip, vertical flip, "
            "+15° rotation, −15° rotation, +30° rotation.",
            st["bullet"],
        ),
        Paragraph(
            "• Split at <b>source-stem</b> level (70% / 15% / 15% train/val/test) so all augmentations "
            "of one photo stay in the same split — no data leakage.",
            st["bullet"],
        ),
        PageBreak(),
    ]


def section_methodology(st):
    return [
        Paragraph("5. Methodology", st["h1"]),
        Paragraph("Workflow", st["h2"]),
        Paragraph("Week 1 → Data curation, resize, augmentation (30k images).", st["bullet"]),
        Paragraph("Week 2 → Transfer-learning architecture (frozen MobileNetV2 + custom head).", st["bullet"]),
        Paragraph("Week 3 → Train head, monitor curves, evaluate, hyperparameter experiments.", st["bullet"]),
        Paragraph("Week 4 → OpenCV ROI detection + classifier overlay + dashboard screenshots.", st["bullet"]),
        Paragraph("Model Used", st["h2"]),
        Paragraph(
            "<b>Backbone:</b> ImageNet-pretrained MobileNetV2 (frozen, include_top=False).<br/>"
            "<b>Head:</b> GlobalAveragePooling2D → Dropout → Dense(128, ReLU) → Dropout → Dense(1, sigmoid).<br/>"
            "<b>Output:</b> Probability of plastic debris. Threshold 0.5 for class decision.<br/>"
            "<b>Parameters:</b> 2,422,081 total; 164,097 trainable (~6.8%).",
            st["body"],
        ),
        Paragraph("Tools &amp; Libraries", st["h2"]),
        Paragraph(
            "Python 3, TensorFlow/Keras 2.15+, OpenCV 4.8+, NumPy, Pillow, Matplotlib, scikit-learn, "
            "Kaggle API, tqdm, Jupyter notebooks.",
            st["body"],
        ),
        PageBreak(),
    ]


def section_implementation(st):
    code_snip = (
        "base = MobileNetV2(include_top=False, weights='imagenet')\n"
        "base.trainable = False\n"
        "x = GlobalAveragePooling2D()(base(x))\n"
        "x = Dropout(0.5)(x)\n"
        "x = Dense(128, activation='relu')(x)\n"
        "outputs = Dense(1, activation='sigmoid')(x)"
    )
    return [
        Paragraph("6. Implementation", st["h1"]),
        Paragraph("Training Process", st["h2"]),
        Paragraph(
            "1. Cache frozen MobileNetV2 features once for all splits (fast CPU training).<br/>"
            "2. Train only the Dense head with Adam optimizer.<br/>"
            "3. Callbacks: EarlyStopping (monitor val_loss, patience 4), ReduceLROnPlateau, CSVLogger.<br/>"
            "4. Restore best weights from lowest validation loss.<br/>"
            "5. Evaluate on 4,500-image held-out test set; plot confusion matrix and curves.",
            st["body"],
        ),
        Paragraph("Hyperparameters", st["h2"]),
        Table(
            [
                ["Parameter", "Recommended (best test)", "Week 4 retrain"],
                ["Learning rate", "1e-3", "1e-3"],
                ["Batch size", "64", "64"],
                ["Dropout", "0.5", "0.2"],
                ["Max epochs", "20 (+ early stop)", "30 (+ early stop @12)"],
                ["Dense units", "128", "128"],
                ["Backbone", "MobileNetV2 (frozen)", "MobileNetV2 (frozen)"],
            ],
            colWidths=[1.8 * inch, 2.2 * inch, 2.0 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            ),
        ),
        Spacer(1, 10),
        Paragraph(
            "Twelve controlled experiments (LR, batch, dropout, epochs, augmentation ablation) confirmed "
            "dropout=0.5 as best for generalization (test acc 99.49%).",
            st["body"],
        ),
        Paragraph("Code Overview", st["h2"]),
        Paragraph("<font name='Courier'>models/classifier.py</font> — model factory and compile.", st["bullet"]),
        Paragraph("<font name='Courier'>scripts/train_model.py</font> — train, evaluate, save artifacts.", st["bullet"]),
        Paragraph("<font name='Courier'>scripts/run_experiments.py</font> — hyperparameter grid.", st["bullet"]),
        Paragraph("<font name='Courier'>scripts/opencv_detect.py</font> — Canny/contour ROI + annotate.", st["bullet"]),
        Paragraph("Core architecture snippet:", st["body"]),
        Paragraph(f"<font name='Courier'>{code_snip.replace(chr(10), '<br/>')}</font>", st["code"]),
        PageBreak(),
    ]


def section_results(st):
    flow = [
        Paragraph("7. Results", st["h1"]),
        Paragraph("Performance Metrics", st["h2"]),
        Paragraph("<b>Primary model (dropout 0.5, best generalization):</b>", st["body"]),
        Table(
            [
                ["Metric", "Value"],
                ["Test accuracy", "99.47%"],
                ["Precision", "99.29%"],
                ["Recall", "99.64%"],
                ["F1 score", "99.47%"],
                ["AUC", "0.999"],
                ["Test errors", "24 / 4,500"],
                ["Confusion matrix", "TN=2234, FP=16, FN=8, TP=2242"],
                ["Fit diagnosis", "good_fit (train−val gap ≈ +0.001)"],
            ],
            colWidths=[2.0 * inch, 4.0 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            ),
        ),
        Spacer(1, 8),
        Paragraph(
            "<b>Week 4 retrain (dropout 0.2, train-accuracy priority):</b> train 100.0%, val 99.69%, "
            "test 99.38% (28 errors). OpenCV demo batch: 8/8 correct on unseen __orig test stems.",
            st["body"],
        ),
        Paragraph("Graphs", st["h2"]),
    ]
    for key, cap in [
        ("dashboard", "Figure 1 — Performance summary dashboard"),
        ("acc", "Figure 2 — Training & validation accuracy"),
        ("loss", "Figure 3 — Training & validation loss"),
        ("cm", "Figure 4 — Confusion matrix (test set)"),
        ("test", "Figure 5 — Test set metrics"),
        ("exp", "Figure 6 — Hyperparameter experiment comparison"),
    ]:
        flow.extend(img_block(IMG[key], caption=cap))
    flow.append(PageBreak())
    flow.append(Paragraph("Screenshots", st["h2"]))
    flow.extend(img_block(IMG["opencv"], caption="Figure 7 — OpenCV annotated dashboard (8/8 correct)"))
    flow.extend(img_block(IMG["demo"], caption="Figure 8 — Matplotlib prediction demo grid"))
    flow.append(Paragraph("Discussion", st["h2"]))
    flow.append(
        Paragraph(
            "Transfer learning on ImageNet features generalized strongly to marine vs plastic imagery. "
            "Stem-level splitting prevented augmentation leakage and produced trustworthy test scores. "
            "Dropout 0.5 minimized overfitting; the small train−val gap and test accuracy near validation "
            "confirm healthy fit. OpenCV contour boxes provide a practical demo layer without training a "
            "full object detector. Remaining errors (24–28) involve visually similar textures near the "
            "decision boundary.",
            st["body"],
        )
    )
    flow.append(PageBreak())
    return flow


def section_challenges(st):
    return [
        Paragraph("8. Challenges &amp; Learnings", st["h1"]),
        Paragraph(
            "<b>Dataset heterogeneity:</b> Kaggle sources varied in resolution and labeling; curation filters "
            "and class balancing were essential.",
            st["bullet"],
        ),
        Paragraph(
            "<b>Preprocessing consistency:</b> MobileNetV2 expects uint8 RGB with in-model preprocess "
            "(scale to [−1,1]); dividing by 255 before predict hurts accuracy.",
            st["bullet"],
        ),
        Paragraph(
            "<b>Leakage prevention:</b> Splitting by augmented filename stem, not individual files, was "
            "critical for honest evaluation.",
            st["bullet"],
        ),
        Paragraph(
            "<b>Regularization trade-off:</b> Lower dropout raised train accuracy to 100% but slightly "
            "reduced test performance — a clear bias–variance lesson.",
            st["bullet"],
        ),
        Paragraph(
            "<b>Classifier vs detector:</b> OpenCV heuristics give one box per frame; multi-object scenes "
            "would need YOLO/SSD or sliding windows.",
            st["bullet"],
        ),
        Paragraph(
            "<b>Key learning:</b> Frozen lightweight backbones plus a small custom head can reach "
            "production-quality binary accuracy on modest hardware when data is clean and splits are fair.",
            st["body"],
        ),
        PageBreak(),
    ]


def section_conclusion(st):
    return [
        Paragraph("9. Conclusion &amp; Future Scope", st["h1"]),
        Paragraph(
            "The Plastic-Pulse Ocean Tracker internship delivered a complete pipeline: balanced 30k-image "
            "dataset, MobileNetV2 transfer-learning classifier at <b>99.47% test accuracy</b>, twelve "
            "hyperparameter experiments, and OpenCV integration with perfect demo-batch results. The "
            "project demonstrates a viable vision module for drone-assisted ocean cleanup that protects "
            "marine life while targeting plastic waste.",
            st["body"],
        ),
        Paragraph("Future Scope", st["h2"]),
        Paragraph("• Fine-tune top MobileNetV2 layers with lr ≈ 1e−5 for hard misclassified pairs.", st["bullet"]),
        Paragraph("• Export TFLite / ONNX for on-drone edge inference.", st["bullet"]),
        Paragraph("• Replace contour ROI with MobileNet-SSD for multi-object detection.", st["bullet"]),
        Paragraph("• Collect real underwater drone footage to close the sim-to-real gap.", st["bullet"]),
        Paragraph("• Add temporal smoothing across video frames for stable drone decisions.", st["bullet"]),
        PageBreak(),
    ]


def section_references(st):
    return [
        Paragraph("10. References", st["h1"]),
        Paragraph("Datasets", st["h2"]),
        Paragraph("• Kaggle — Sea Animals Image Dataset (vencerlanz09)", st["bullet"]),
        Paragraph("• Kaggle — Marine Animal Images (mikoajfish99)", st["bullet"]),
        Paragraph("• Kaggle — Drinking Waste Classification (arkadiyhacks)", st["bullet"]),
        Paragraph("• Kaggle — Garbage Dataset Classification (zlatan599)", st["bullet"]),
        Paragraph("• Kaggle — Garbage Classification / TrashNet (asdasdasasdas)", st["bullet"]),
        Paragraph("Documentation", st["h2"]),
        Paragraph("• TensorFlow/Keras — MobileNetV2 API", st["bullet"]),
        Paragraph("• OpenCV — Canny edge detection & contour finding", st["bullet"]),
        Paragraph("• Project repository: github.com/guhankarthick2/Plastic-Pulse-Ocean-Tracker", st["bullet"]),
        Paragraph("Research Papers", st["h2"]),
        Paragraph("• Sandler et al., MobileNetV2: Inverted Residuals and Linear Bottlenecks (2018)", st["bullet"]),
        Paragraph("• He et al., Deep Residual Learning for Image Recognition (2015) — ResNet baseline", st["bullet"]),
        PageBreak(),
    ]


def section_appendix(st):
    ann = ROOT / "outputs/week4/opencv/annotated_marine_life_00002__orig.jpg"
    flow = [
        Paragraph("11. Appendix", st["h1"]),
        Paragraph("Additional Screenshots", st["h2"]),
    ]
    flow.extend(img_block(ann, width=4.5 * inch, caption="Appendix A — Sample annotated marine life detection"))
    flow.append(Paragraph("Code Snippets", st["h2"]))
    flow.append(
        Paragraph(
            "<font name='Courier'># Train recommended model<br/>"
            "python scripts/train_model.py --epochs 20 --batch-size 64 --dropout 0.5<br/><br/>"
            "# OpenCV detection demo<br/>"
            "python scripts/opencv_detect.py<br/><br/>"
            "# Run all hyperparameter experiments<br/>"
            "python scripts/run_experiments.py</font>",
            st["code"],
        )
    )
    return flow


def build_pdf():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    st = styles()
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"{PROJECT_TITLE} — Final Report",
        author=STUDENT_NAME,
    )
    story = []
    story.extend(cover(st))
    story.extend(toc(st))
    story.extend(section_intro(st))
    story.extend(section_dataset(st))
    story.extend(section_methodology(st))
    story.extend(section_implementation(st))
    story.extend(section_results(st))
    story.extend(section_challenges(st))
    story.extend(section_conclusion(st))
    story.extend(section_references(st))
    story.extend(section_appendix(st))
    doc.build(story)
    return OUT_PDF


if __name__ == "__main__":
    path = build_pdf()
    print(f"Generated: {path}")
