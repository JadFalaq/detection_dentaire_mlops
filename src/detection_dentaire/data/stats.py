from __future__ import annotations

from collections import Counter
from pathlib import Path

from .checks import validate_label_file
from .io import collect_images, collect_labels, load_yolo_label_file


def compute_split_stats(
    image_dir: str | Path,
    label_dir: str | Path,
    class_names: dict[int, str] | None = None,
    allowed_classes: set[int] | None = None,
) -> dict:
    """
    Calcule les stats d'un split YOLO.
    """
    image_dir = Path(image_dir)
    label_dir = Path(label_dir)

    images = collect_images(image_dir)
    labels = collect_labels(label_dir)

    class_counts = Counter()
    images_per_class = Counter()
    invalid_label_files = []
    empty_label_files = []

    for label_path in labels:
        report = validate_label_file(label_path, allowed_classes=allowed_classes)

        if report["empty"]:
            empty_label_files.append(str(label_path))

        if not report["valid"]:
            invalid_label_files.append(
                {
                    "file": str(label_path),
                    "errors": report["errors"],
                }
            )

        # On essaye quand même de lire les records si possible
        try:
            records = load_yolo_label_file(label_path)
        except Exception:
            continue

        present_classes = set()
        for cls_id, _, _, _, _ in records:
            class_counts[cls_id] += 1
            present_classes.add(cls_id)

        for cls_id in present_classes:
            images_per_class[cls_id] += 1

    if class_names is None:
        class_names = {}

    return {
        "num_images": len(images),
        "num_labels": len(labels),
        "num_objects": int(sum(class_counts.values())),
        "num_invalid_label_files": len(invalid_label_files),
        "num_empty_label_files": len(empty_label_files),
        "class_counts": {
            class_names.get(cls_id, f"class_{cls_id}"): int(count)
            for cls_id, count in sorted(class_counts.items())
        },
        "images_per_class": {
            class_names.get(cls_id, f"class_{cls_id}"): int(count)
            for cls_id, count in sorted(images_per_class.items())
        },
        "invalid_label_files": invalid_label_files,
        "empty_label_files": empty_label_files,
    }


def aggregate_stats(split_stats: dict[str, dict]) -> dict:
    """
    Agrège les stats de plusieurs splits.
    """
    total_images = 0
    total_labels = 0
    total_objects = 0
    invalid_files = 0
    empty_files = 0
    class_counts = Counter()
    images_per_class = Counter()

    for _, stats in split_stats.items():
        total_images += stats.get("num_images", 0)
        total_labels += stats.get("num_labels", 0)
        total_objects += stats.get("num_objects", 0)
        invalid_files += stats.get("num_invalid_label_files", 0)
        empty_files += stats.get("num_empty_label_files", 0)

        for cls_name, count in stats.get("class_counts", {}).items():
            class_counts[cls_name] += count

        for cls_name, count in stats.get("images_per_class", {}).items():
            images_per_class[cls_name] += count

    return {
        "num_images": total_images,
        "num_labels": total_labels,
        "num_objects": total_objects,
        "num_invalid_label_files": invalid_files,
        "num_empty_label_files": empty_files,
        "class_counts": dict(class_counts),
        "images_per_class": dict(images_per_class),
    }