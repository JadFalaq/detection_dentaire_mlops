#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.data import (
    infer_label_path_from_image,
    load_yolo_label_file,
    annotate_yolo_image,
    save_image,
)
from detection_dentaire.utils import load_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize YOLO labels on a dental panoramic image."
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to the input image.",
    )
    parser.add_argument(
        "--label",
        type=str,
        default=None,
        help="Optional path to the YOLO label file. If omitted, it is inferred from the image path.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output path. If omitted, saves into dataset_7classes/images_with_labels/...",
    )
    parser.add_argument(
        "--data-config",
        type=str,
        default="configs/data.yaml",
        help="Path to data config file containing class names.",
    )
    parser.add_argument(
        "--thickness",
        type=int,
        default=2,
        help="Bounding box thickness.",
    )
    parser.add_argument(
        "--font-scale",
        type=float,
        default=0.6,
        help="Font scale for labels.",
    )
    return parser.parse_args()


def load_class_names(data_config_path: str | Path) -> dict[int, str]:
    cfg = load_yaml(data_config_path)
    names = cfg["classes"]["names"]

    class_names: dict[int, str] = {}
    for k, v in names.items():
        class_names[int(k)] = str(v)

    return class_names


def infer_output_path(image_path: Path) -> Path:
    """
    Example:
    data/processed/dataset_7classes/train/images/3.jpg
    ->
    data/processed/dataset_7classes/images_with_labels/train/3_labeled.jpg
    """
    parts = list(image_path.parts)

    if "dataset_7classes" not in parts:
        raise ValueError(
            "Cannot infer output path because 'dataset_7classes' is not in the image path. "
            "Use --output explicitly."
        )

    dataset_idx = parts.index("dataset_7classes")
    dataset_root = Path(*parts[: dataset_idx + 1])

    rel_after_root = Path(*parts[dataset_idx + 1 :])

    rel_parts = list(rel_after_root.parts)
    if "images" not in rel_parts:
        raise ValueError(
            "Cannot infer output path because 'images' is not in the image path. "
            "Use --output explicitly."
        )

    rel_parts.remove("images")
    rel_path_no_images = Path(*rel_parts)

    output_name = f"{rel_path_no_images.stem}_labeled.jpg"
    return dataset_root / "images_with_labels" / rel_path_no_images.with_name(output_name)


def main() -> None:
    args = parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    label_path = Path(args.label) if args.label else infer_label_path_from_image(image_path)
    if not label_path.exists():
        raise FileNotFoundError(f"Label file not found: {label_path}")

    output_path = Path(args.output) if args.output else infer_output_path(image_path)

    class_names = load_class_names(args.data_config)

    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"Failed to read image: {image_path}")

    records = load_yolo_label_file(label_path)

    annotated = annotate_yolo_image(
        image=image,
        records=records,
        class_names=class_names,
        thickness=args.thickness,
        font_scale=args.font_scale,
    )

    save_image(annotated, output_path)

    print(f"[OK] Image      : {image_path}")
    print(f"[OK] Label      : {label_path}")
    print(f"[OK] Objects    : {len(records)}")
    print(f"[OK] Saved to   : {output_path}")


if __name__ == "__main__":
    main()
