from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .io import collect_images, collect_labels


def validate_yolo_record(
    cls_id: int,
    xc: float,
    yc: float,
    bw: float,
    bh: float,
    allowed_classes: set[int] | None = None,
) -> list[str]:
    """
    Valide un objet YOLO unique.
    Retourne une liste d'erreurs. Vide si tout est correct.
    """
    errors: list[str] = []

    if cls_id < 0:
        errors.append(f"class_id < 0 ({cls_id})")

    if allowed_classes is not None and cls_id not in allowed_classes:
        errors.append(f"class_id not allowed ({cls_id})")

    for name, value in [("x_center", xc), ("y_center", yc), ("width", bw), ("height", bh)]:
        if not (0.0 <= value <= 1.0):
            errors.append(f"{name} out of [0,1]: {value}")

    if bw <= 0.0 or bh <= 0.0:
        errors.append(f"width/height must be > 0, got width={bw}, height={bh}")

    x1 = xc - bw / 2.0
    y1 = yc - bh / 2.0
    x2 = xc + bw / 2.0
    y2 = yc + bh / 2.0

    if x1 < 0.0 or y1 < 0.0 or x2 > 1.0 or y2 > 1.0:
        errors.append(
            f"bbox corners out of [0,1]: x1={x1:.6f}, y1={y1:.6f}, x2={x2:.6f}, y2={y2:.6f}"
        )

    return errors


def validate_label_file(
    label_path: str | Path,
    allowed_classes: set[int] | None = None,
) -> dict:
    """
    Valide un fichier de labels YOLO complet.
    """
    label_path = Path(label_path)
    report = {
        "file": str(label_path),
        "valid": True,
        "empty": False,
        "num_objects": 0,
        "errors": [],
    }

    if not label_path.exists():
        report["valid"] = False
        report["errors"].append("label file not found")
        return report

    text = label_path.read_text(encoding="utf-8").strip()
    if not text:
        report["empty"] = True
        return report

    for line_no, line in enumerate(text.splitlines(), start=1):
        parts = line.strip().split()
        if len(parts) != 5:
            report["valid"] = False
            report["errors"].append(
                f"line {line_no}: expected 5 values, got {len(parts)}"
            )
            continue

        try:
            cls_id = int(float(parts[0]))
            xc = float(parts[1])
            yc = float(parts[2])
            bw = float(parts[3])
            bh = float(parts[4])
        except ValueError:
            report["valid"] = False
            report["errors"].append(f"line {line_no}: non numeric values")
            continue

        errors = validate_yolo_record(
            cls_id=cls_id,
            xc=xc,
            yc=yc,
            bw=bw,
            bh=bh,
            allowed_classes=allowed_classes,
        )
        if errors:
            report["valid"] = False
            for err in errors:
                report["errors"].append(f"line {line_no}: {err}")

        report["num_objects"] += 1

    return report


def check_image_label_consistency(
    image_dir: str | Path,
    label_dir: str | Path,
) -> dict:
    """
    Vérifie :
    - images sans label
    - labels sans image
    - doublons de stem
    """
    images = collect_images(image_dir)
    labels = collect_labels(label_dir)

    img_map = defaultdict(list)
    for p in images:
        img_map[p.stem].append(p)

    lbl_map = defaultdict(list)
    for p in labels:
        lbl_map[p.stem].append(p)

    missing_labels = sorted([stem for stem in img_map if stem not in lbl_map])
    orphan_labels = sorted([stem for stem in lbl_map if stem not in img_map])
    duplicate_image_stems = sorted([stem for stem, paths in img_map.items() if len(paths) > 1])
    duplicate_label_stems = sorted([stem for stem, paths in lbl_map.items() if len(paths) > 1])

    return {
        "num_images": len(images),
        "num_labels": len(labels),
        "missing_labels": missing_labels,
        "orphan_labels": orphan_labels,
        "duplicate_image_stems": duplicate_image_stems,
        "duplicate_label_stems": duplicate_label_stems,
    }