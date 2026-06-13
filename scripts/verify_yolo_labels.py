#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.data import collect_labels, validate_label_file
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
        description="Strict validation of YOLO label files."
    )
    parser.add_argument(
        "--root",
        type=str,
        required=True,
        help="Dataset root, e.g. data/raw/dataset_original or data/processed/dataset_7classes",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        default=None,
        help="Optional path to save the full validation report as JSON.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with non-zero code if invalid labels are found.",
    )
    return parser.parse_args()


def detect_dataset_layout(root: Path) -> tuple[dict[str, Path], dict[int, str], set[int]]:
    has_eval = (root / "eval").exists()
    has_valid = (root / "valid").exists()

    if has_eval:
        split_label_dirs = {
            "train": root / "train" / "labels",
            "eval": root / "eval" / "labels",
            "test": root / "test" / "labels",
            "external": root / "test_alte_cabinete" / "Ext-validation" / "labels",
        }
        class_names = PROCESSED_CLASS_NAMES
    elif has_valid:
        split_label_dirs = {
            "train": root / "train" / "labels",
            "valid": root / "valid" / "labels",
            "test": root / "test" / "labels",
            "external": root / "test_alte_cabinete" / "Ext-validation" / "labels",
        }
        class_names = RAW_CLASS_NAMES
    else:
        raise ValueError(
            "Unable to detect dataset layout. Expected either 'valid/' or 'eval/' under root."
        )

    return split_label_dirs, class_names, set(class_names.keys())


def validate_split(
    split_name: str,
    label_dir: Path,
    allowed_classes: set[int],
) -> dict[str, Any]:
    labels = collect_labels(label_dir)

    invalid_files = []
    empty_files = []
    total_objects = 0

    for label_path in labels:
        report = validate_label_file(label_path, allowed_classes=allowed_classes)

        if report["empty"]:
            empty_files.append(str(label_path))

        if not report["valid"]:
            invalid_files.append(
                {
                    "file": report["file"],
                    "errors": report["errors"],
                    "num_objects": report["num_objects"],
                }
            )

        total_objects += report["num_objects"]

    return {
        "split": split_name,
        "label_dir": str(label_dir),
        "num_label_files": len(labels),
        "num_objects": total_objects,
        "num_invalid_files": len(invalid_files),
        "num_empty_files": len(empty_files),
        "invalid_files": invalid_files,
        "empty_files": empty_files,
    }


def print_summary(root: Path, split_reports: list[dict[str, Any]]) -> None:
    print("=" * 100)
    print("YOLO LABEL VALIDATION REPORT")
    print("=" * 100)
    print(f"Root: {root}")

    total_invalid = 0
    total_empty = 0
    total_labels = 0
    total_objects = 0

    for rep in split_reports:
        total_invalid += rep["num_invalid_files"]
        total_empty += rep["num_empty_files"]
        total_labels += rep["num_label_files"]
        total_objects += rep["num_objects"]

        print("\n" + "-" * 100)
        print(f"SPLIT: {rep['split']}")
        print("-" * 100)
        print(f"Label files            : {rep['num_label_files']}")
        print(f"Objects                : {rep['num_objects']}")
        print(f"Invalid files          : {rep['num_invalid_files']}")
        print(f"Empty files            : {rep['num_empty_files']}")

        if rep["invalid_files"]:
            print("\nExamples of invalid files:")
            for item in rep["invalid_files"][:5]:
                print(f"  - {item['file']}")
                for err in item["errors"][:5]:
                    print(f"      * {err}")

    print("\n" + "=" * 100)
    print("[GLOBAL]")
    print("=" * 100)
    print(f"Total label files       : {total_labels}")
    print(f"Total objects           : {total_objects}")
    print(f"Total invalid files     : {total_invalid}")
    print(f"Total empty files       : {total_empty}")
    print("=" * 100)


def main() -> None:
    args = parse_args()
    root = Path(args.root)

    if not root.exists():
        raise FileNotFoundError(f"Dataset root not found: {root}")

    split_label_dirs, class_names, allowed_classes = detect_dataset_layout(root)

    split_reports = []
    total_invalid = 0

    for split_name, label_dir in split_label_dirs.items():
        rep = validate_split(
            split_name=split_name,
            label_dir=label_dir,
            allowed_classes=allowed_classes,
        )
        split_reports.append(rep)
        total_invalid += rep["num_invalid_files"]

    print_summary(root, split_reports)

    if args.save_json:
        save_json(
            {
                "root": str(root),
                "class_names": class_names,
                "splits": split_reports,
                "total_invalid_files": total_invalid,
            },
            args.save_json,
        )
        print(f"[OK] JSON saved to: {args.save_json}")

    if args.fail_on_error and total_invalid > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
