#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.data import (
    collect_images,
    collect_labels,
    check_image_label_consistency,
    validate_label_file,
)
from detection_dentaire.utils import save_json


RAW_CLASS_NAMES = {
    0: "Implant",
    1: "Prosthetic restoration",
    2: "Obturation",
    3: "Endodontic treatment",
    4: "Carious lesion",
    5: "Bone resorbtion",
    6: "Impacted tooth",
    7: "Apical periodontitis",
    8: "Root fragment",
    9: "Furcation lesion",
    10: "Apical surgery",
    11: "Root resorption",
    12: "Orthodontic device",
    13: "Surgical device",
}

PROCESSED_CLASS_NAMES = {
    0: "CARIES",
    1: "PERIAPICAL_PATHOLOGY",
    2: "PERIODONTAL_BONE",
    3: "IMPACTED_TOOTH",
    4: "ROOT_PATHOLOGY",
    5: "TREATED_TOOTH",
    6: "DEVICE_IMPLANT",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a YOLO dental dataset (raw or processed)."
    )
    parser.add_argument(
        "--root",
        type=str,
        required=True,
        help="Dataset root, e.g. data/raw/dataset_original or data/processed/dataset_7classes",
    )
    parser.add_argument(
        "--check-images",
        action="store_true",
        help="Open images with PIL to detect corrupt files.",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        default=None,
        help="Optional path to save the inspection report as JSON.",
    )
    return parser.parse_args()


def detect_dataset_layout(root: Path) -> tuple[dict[str, dict[str, Path]], dict[int, str], set[int]]:
    """
    Détecte automatiquement si le dataset est brut (valid) ou préparé (eval).
    """
    has_eval = (root / "eval").exists()
    has_valid = (root / "valid").exists()

    if has_eval:
        split_dirs = {
            "train": {
                "images": root / "train" / "images",
                "labels": root / "train" / "labels",
            },
            "eval": {
                "images": root / "eval" / "images",
                "labels": root / "eval" / "labels",
            },
            "test": {
                "images": root / "test" / "images",
                "labels": root / "test" / "labels",
            },
            "external": {
                "images": root / "test_alte_cabinete" / "Ext-validation" / "images",
                "labels": root / "test_alte_cabinete" / "Ext-validation" / "labels",
            },
        }
        class_names = PROCESSED_CLASS_NAMES
    elif has_valid:
        split_dirs = {
            "train": {
                "images": root / "train" / "images",
                "labels": root / "train" / "labels",
            },
            "valid": {
                "images": root / "valid" / "images",
                "labels": root / "valid" / "labels",
            },
            "test": {
                "images": root / "test" / "images",
                "labels": root / "test" / "labels",
            },
            "external": {
                "images": root / "test_alte_cabinete" / "Ext-validation" / "images",
                "labels": root / "test_alte_cabinete" / "Ext-validation" / "labels",
            },
        }
        class_names = RAW_CLASS_NAMES
    else:
        raise ValueError(
            "Unable to detect dataset layout. Expected either 'valid/' or 'eval/' under root."
        )

    allowed_classes = set(class_names.keys())
    return split_dirs, class_names, allowed_classes


def check_image_file(image_path: Path) -> tuple[bool, str | None, tuple[int, int] | None]:
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            size = img.size
        return True, None, size
    except (UnidentifiedImageError, OSError, ValueError) as e:
        return False, str(e), None


def inspect_split(
    split_name: str,
    image_dir: Path,
    label_dir: Path,
    class_names: dict[int, str],
    allowed_classes: set[int],
    check_images: bool,
) -> dict[str, Any]:
    images = collect_images(image_dir)
    labels = collect_labels(label_dir)

    consistency = check_image_label_consistency(image_dir, label_dir)

    corrupt_images = []
    valid_images = 0
    image_sizes: dict[str, int] = {}

    if check_images:
        for image_path in images:
            ok, err, size = check_image_file(image_path)
            if ok:
                valid_images += 1
                if size is not None:
                    key = f"{size[0]}x{size[1]}"
                    image_sizes[key] = image_sizes.get(key, 0) + 1
            else:
                corrupt_images.append({"file": str(image_path), "error": err})
    else:
        valid_images = len(images)

    class_counts: dict[str, int] = {name: 0 for name in class_names.values()}
    images_per_class: dict[str, int] = {name: 0 for name in class_names.values()}
    invalid_label_files = []
    empty_label_files = []
    total_objects = 0

    for label_path in labels:
        report = validate_label_file(label_path, allowed_classes=allowed_classes)

        if report["empty"]:
            empty_label_files.append(str(label_path))

        if not report["valid"]:
            invalid_label_files.append(
                {
                    "file": report["file"],
                    "errors": report["errors"],
                }
            )

        text = label_path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        present_classes = set()

        for line in text.splitlines():
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            try:
                cls_id = int(float(parts[0]))
            except ValueError:
                continue

            if cls_id in class_names:
                cls_name = class_names[cls_id]
                class_counts[cls_name] += 1
                total_objects += 1
                present_classes.add(cls_name)

        for cls_name in present_classes:
            images_per_class[cls_name] += 1

    return {
        "split": split_name,
        "image_dir": str(image_dir),
        "label_dir": str(label_dir),
        "num_images": len(images),
        "num_labels": len(labels),
        "num_valid_images": valid_images,
        "num_corrupt_images": len(corrupt_images),
        "num_missing_labels": len(consistency["missing_labels"]),
        "num_orphan_labels": len(consistency["orphan_labels"]),
        "num_duplicate_image_stems": len(consistency["duplicate_image_stems"]),
        "num_duplicate_label_stems": len(consistency["duplicate_label_stems"]),
        "num_invalid_label_files": len(invalid_label_files),
        "num_empty_label_files": len(empty_label_files),
        "num_objects": total_objects,
        "class_counts": class_counts,
        "images_per_class": images_per_class,
        "missing_labels": consistency["missing_labels"],
        "orphan_labels": consistency["orphan_labels"],
        "duplicate_image_stems": consistency["duplicate_image_stems"],
        "duplicate_label_stems": consistency["duplicate_label_stems"],
        "corrupt_images": corrupt_images,
        "invalid_label_files": invalid_label_files,
        "empty_label_files": empty_label_files,
        "image_sizes": image_sizes,
    }


def print_report(root: Path, split_reports: list[dict[str, Any]], class_names: dict[int, str]) -> None:
    print("=" * 100)
    print("YOLO DATASET INSPECTION REPORT")
    print("=" * 100)
    print(f"Root       : {root}")
    print(f"Classes    : {len(class_names)}")

    print("\nClass mapping:")
    for cls_id, cls_name in class_names.items():
        print(f"  {cls_id:>2} -> {cls_name}")

    for rep in split_reports:
        print("\n" + "-" * 100)
        print(f"SPLIT: {rep['split']}")
        print("-" * 100)
        print(f"Images                 : {rep['num_images']}")
        print(f"Labels                 : {rep['num_labels']}")
        print(f"Valid images           : {rep['num_valid_images']}")
        print(f"Corrupt images         : {rep['num_corrupt_images']}")
        print(f"Missing labels         : {rep['num_missing_labels']}")
        print(f"Orphan labels          : {rep['num_orphan_labels']}")
        print(f"Duplicate image stems  : {rep['num_duplicate_image_stems']}")
        print(f"Duplicate label stems  : {rep['num_duplicate_label_stems']}")
        print(f"Invalid label files    : {rep['num_invalid_label_files']}")
        print(f"Empty label files      : {rep['num_empty_label_files']}")
        print(f"Total objects          : {rep['num_objects']}")

        print("\nObjects per class:")
        for cls_name, count in rep["class_counts"].items():
            print(f"  - {cls_name:<22} : {count}")

        print("\nImages per class:")
        for cls_name, count in rep["images_per_class"].items():
            print(f"  - {cls_name:<22} : {count}")

        if rep["num_invalid_label_files"] > 0:
            print("\nInvalid label files:")
            for item in rep["invalid_label_files"][:5]:
                print(f"  - {item['file']}")
                for err in item["errors"][:3]:
                    print(f"      * {err}")

        if rep["num_corrupt_images"] > 0:
            print("\nCorrupt images:")
            for item in rep["corrupt_images"][:5]:
                print(f"  - {item['file']} | {item['error']}")

    print("\n" + "=" * 100)


def main() -> None:
    args = parse_args()
    root = Path(args.root)

    if not root.exists():
        raise FileNotFoundError(f"Dataset root not found: {root}")

    split_dirs, class_names, allowed_classes = detect_dataset_layout(root)

    split_reports = []
    for split_name, dirs in split_dirs.items():
        rep = inspect_split(
            split_name=split_name,
            image_dir=dirs["images"],
            label_dir=dirs["labels"],
            class_names=class_names,
            allowed_classes=allowed_classes,
            check_images=args.check_images,
        )
        split_reports.append(rep)

    print_report(root, split_reports, class_names)

    if args.save_json:
        save_json(
            {
                "root": str(root),
                "class_names": class_names,
                "splits": split_reports,
            },
            args.save_json,
        )
        print(f"[OK] JSON saved to: {args.save_json}")


if __name__ == "__main__":
    main()
