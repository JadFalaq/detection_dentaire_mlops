#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.data import compute_split_stats, aggregate_stats
from detection_dentaire.utils import ensure_dir, save_json


CLASS_NAMES = {
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
        description="Compute class statistics for the 7-class YOLO dental dataset."
    )
    parser.add_argument(
        "--root",
        type=str,
        required=True,
        help="Root of processed dataset, e.g. data/processed/dataset_7classes",
    )
    parser.add_argument(
        "--save-csv",
        type=str,
        default=None,
        help="Optional path to save a CSV summary.",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        default=None,
        help="Optional path to save a JSON summary.",
    )
    return parser.parse_args()


def build_split_paths(root: Path) -> dict[str, dict[str, Path]]:
    return {
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


def print_split_stats(split_name: str, stats: dict) -> None:
    print("=" * 90)
    print(f"[{split_name.upper()}]")
    print("=" * 90)
    print(f"Images                 : {stats['num_images']}")
    print(f"Labels                 : {stats['num_labels']}")
    print(f"Objects                : {stats['num_objects']}")
    print(f"Invalid label files    : {stats['num_invalid_label_files']}")
    print(f"Empty label files      : {stats['num_empty_label_files']}")

    print("\nObjects per class:")
    for cls_name, count in stats["class_counts"].items():
        print(f"  - {cls_name:<22} : {count}")

    print("\nImages per class:")
    for cls_name, count in stats["images_per_class"].items():
        print(f"  - {cls_name:<22} : {count}")

    if stats["invalid_label_files"]:
        print("\nInvalid label files:")
        for item in stats["invalid_label_files"][:5]:
            print(f"  - {item['file']}")
            for err in item["errors"][:3]:
                print(f"      * {err}")


def build_csv_table(split_stats: dict[str, dict]) -> pd.DataFrame:
    rows = []

    for split_name, stats in split_stats.items():
        for cls_name, obj_count in stats["class_counts"].items():
            img_count = stats["images_per_class"].get(cls_name, 0)
            rows.append(
                {
                    "split": split_name,
                    "class_name": cls_name,
                    "object_count": obj_count,
                    "image_count": img_count,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    root = Path(args.root)

    if not root.exists():
        raise FileNotFoundError(f"Dataset root not found: {root}")

    split_paths = build_split_paths(root)
    allowed_classes = set(CLASS_NAMES.keys())

    split_stats: dict[str, dict] = {}

    for split_name, paths in split_paths.items():
        stats = compute_split_stats(
            image_dir=paths["images"],
            label_dir=paths["labels"],
            class_names=CLASS_NAMES,
            allowed_classes=allowed_classes,
        )
        split_stats[split_name] = stats
        print_split_stats(split_name, stats)
        print()

    global_stats = aggregate_stats(split_stats)

    print("=" * 90)
    print("[GLOBAL]")
    print("=" * 90)
    print(f"Images                 : {global_stats['num_images']}")
    print(f"Labels                 : {global_stats['num_labels']}")
    print(f"Objects                : {global_stats['num_objects']}")
    print(f"Invalid label files    : {global_stats['num_invalid_label_files']}")
    print(f"Empty label files      : {global_stats['num_empty_label_files']}")

    print("\nGlobal objects per class:")
    for cls_name, count in global_stats["class_counts"].items():
        print(f"  - {cls_name:<22} : {count}")

    print("\nGlobal images per class:")
    for cls_name, count in global_stats["images_per_class"].items():
        print(f"  - {cls_name:<22} : {count}")

    if args.save_json:
        save_json(
            {
                "root": str(root),
                "class_names": CLASS_NAMES,
                "splits": split_stats,
                "global": global_stats,
            },
            args.save_json,
        )
        print(f"\n[OK] JSON saved to: {args.save_json}")

    if args.save_csv:
        df = build_csv_table(split_stats)
        csv_path = Path(args.save_csv)
        ensure_dir(csv_path.parent)
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"[OK] CSV saved to: {args.save_csv}")


if __name__ == "__main__":
    main()
